#!/usr/bin/env python3
"""从 opencode-i18n 的源码规则里提取「纯字符串 → 译文」运行时词典。

现有规则是「带代码上下文的源码片段 → 带上下文译文」，如：
  "title=\"Select agent\"" -> "title=\"选择智能体\""

运行时 hook 需要的是渲染层拿到的纯字符串精确匹配：
  "Select agent" -> "选择智能体"

提取策略（key 与 value 上下文对称，字符串一一对应）：
  1. 提取 key 中所有「引号包裹的字符串字面量」与「JSX 文本节点」→ 英文串列表
  2. 提取 value 中所有同类 → 中文串列表
  3. 若两侧列表长度相同，按序配对成 { 英文: 中文 }
  4. 长度不同或无法提取的，打印出来人工核对

输出：
  - plugin/dict-own.json        最终自产词典 { entries: {...} }
  - /tmp/own-extract-unmatched.txt  未能自动配对的规则清单（人工核对）
"""
import json
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_DIR = os.path.join(ROOT, "opencode-i18n")
OUT = os.path.join(ROOT, "dict-own.json")
UNMATCHED = "/tmp/own-extract-unmatched.txt"

# 提取一个字符串里所有「用户可见字符串」候选。
# 按优先级：引号字符串 > JSX 文本节点 > 裸文本。
def extract_strings(s: str):
    out = []
    # 1) 双引号字符串字面量（跳过含 ${ 的模板，那些是动态模板）
    for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', s):
        body = m.group(1)
        # 跳过明显的属性名/键名（后面紧跟 = 或 : 且值在引号外的场景），
        # 这里简单保留所有，由配对阶段过滤
        out.append(("quote", body))
    # 2) JSX 文本节点 <tag ...>text</tag> 或 <tag>text</tag>
    for m in re.finditer(r'>([^<>{}]+)</', s):
        body = m.group(1).strip()
        if body and not re.fullmatch(r'\s*', body):
            out.append(("jsx", body))
    return out

def is_code_context(s: str):
    """判断一个字符串是否纯代码上下文（不该作为译文词条）。"""
    # 含 JSX 属性/标签、三元、函数调用、模板占位等，说明还没提纯
    return bool(re.search(r'[<>{}=()$?]', s))

def is_plain_text(s: str):
    """判断整条规则是否「裸文本」（无引号/JSX/代码符号，就是纯英文→中文）。"""
    return not re.search(r'["<>{}()=$?;]', s)

def main():
    pairs = {}
    unmatched = []
    total_rules = 0
    auto = 0

    for f in sorted(glob.glob(os.path.join(I18N_DIR, "**", "*.json"), recursive=True)):
        d = json.load(open(f, encoding="utf-8"))
        for k, v in d.get("replacements", {}).items():
            total_rules += 1

            # 裸文本：整条规则就是纯英文→中文短语，直接作为词条
            if is_plain_text(k) and is_plain_text(v) and re.search(r'[a-zA-Z]', k) and re.search(r'[\u4e00-\u9fff]', v):
                pairs[k.strip()] = v.strip()
                auto += 1
                continue

            en = extract_strings(k)
            zh = extract_strings(v)

            # 只取纯字符串（quote/jsx），且长度相同才能一一配对
            en_pure = [body for kind, body in en]
            zh_pure = [body for kind, body in zh]

            if en_pure and len(en_pure) == len(zh_pure):
                for e, z in zip(en_pure, zh_pure):
                    # 译文侧必须含中文，否则是「键位→键位」之类的假配对，丢弃
                    if not re.search(r'[\u4e00-\u9fff]', z):
                        continue
                    # 跳过纯代码/占位符（不该进词典）
                    if is_code_context(e) or is_code_context(z):
                        continue
                    # 跳过英文侧本身就是占位/动态
                    if re.search(r'\$\{|\{\{|<|>|=>|return|if\s*\(', e):
                        continue
                    pairs[e] = z
                    auto += 1
            else:
                unmatched.append((f, k, v))

    # 去重后输出
    entries = dict(sorted(pairs.items()))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "entries": entries}, fh, ensure_ascii=False, indent=2)

    with open(UNMATCHED, "w", encoding="utf-8") as fh:
        fh.write(f"未能自动配对的规则：{len(unmatched)} 条\n\n")
        for f, k, v in unmatched:
            fh.write(f"文件: {f}\n  原文: {k}\n  译文: {v}\n\n")

    print(f"总规则数: {total_rules}")
    print(f"自动配对词条数: {auto}")
    print(f"去重后词典条目: {len(entries)}")
    print(f"未能配对: {len(unmatched)} 条（见 {UNMATCHED}）")
    print(f"输出: {OUT}")

if __name__ == "__main__":
    main()
