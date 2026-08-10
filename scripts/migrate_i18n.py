#!/usr/bin/env python3
"""汉化配置增量迁移：在指定版本的官方源码中重定位现有翻译规则。

用法:
  python3 scripts/migrate_i18n.py <官方源码目录> [旧配置目录]

默认旧配置目录为 ./i18n/opencode-i18n（项目自带），输出覆盖写回该目录。

匹配策略:
  1. 精确匹配（原 find 字符串完整出现在新源码）
  2. 宽松匹配（提取 find 中引号包裹的英文核心，如 title="Select agent" -> "Select agent"）

注意:
  - 匹配命中 ≠ 一定安全。迁移后必须执行 scripts/check-misreplacements.sh 甄别误伤。
  - 未命中的规则会打印，人工决定是否补写。
"""
import json
import os
import re
import sys

DEFAULT_SRC = os.path.expanduser("~/opencode-zh-build/opencode-dev")
DEFAULT_I18N = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "i18n", "opencode-i18n")

def load_source_files(src_dir):
    """收集新源码所有文本文件内容"""
    files = {}
    for root, dirs, names in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".git", "test", "e2e")]
        for n in names:
            if n.endswith((".ts", ".tsx", ".js", ".json", ".md")):
                p = os.path.join(root, n)
                try:
                    with open(p, encoding="utf-8", errors="ignore") as f:
                        files[p] = f.read()
                except Exception:
                    pass
    return files

def find_rule(files, find):
    """精确匹配，失败则宽松匹配；返回新文件路径或 None"""
    for p, content in files.items():
        if find in content:
            return p
    m = re.search(r'"([A-Za-z][A-Za-z0-9 _./\'-]{3,})"', find)
    core = m.group(1) if m else None
    if core:
        for p, content in files.items():
            if core in content:
                return p
    return None

def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    i18n_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_I18N
    if not os.path.isdir(src_dir):
        print(f"错误: 源码目录不存在: {src_dir}", file=sys.stderr)
        sys.exit(1)

    files = load_source_files(os.path.join(src_dir, "packages"))
    print(f"扫描新源码文件: {len(files)} 个")

    new_configs = {}  # new_rel_path -> {find: to}
    total = matched = 0
    unmatched = []

    for root, dirs, names in os.walk(i18n_dir):
        for n in names:
            if not n.endswith(".json") or n == "config.json":
                continue
            cfg = json.load(open(os.path.join(root, n), encoding="utf-8"))
            for find, to in cfg.get("replacements", {}).items():
                total += 1
                hit = find_rule(files, find)
                if hit:
                    matched += 1
                    rel = hit.replace(src_dir + "/", "")
                    new_configs.setdefault(rel, {})[find] = to
                else:
                    unmatched.append(find)

    print(f"总规则: {total}, 命中: {matched}, 未命中: {len(unmatched)} ({len(unmatched)*100//max(total,1)}%)")
    print(f"命中文件数: {len(new_configs)}")
    if unmatched:
        print("\n=== 未命中规则（人工决定是否补写） ===")
        for f in unmatched[:40]:
            print(f"  {f[:90]}")

    # 写回配置（按新路径分类）
    for rel, rules in new_configs.items():
        if "dialog" in rel:
            cat = "dialogs"
        elif "/routes" in rel or "route" in os.path.basename(rel):
            cat = "routes"
        elif "component" in rel or "sidebar" in rel or "feature-plugins" in rel:
            cat = "components"
        else:
            cat = "common"
        cat_dir = os.path.join(i18n_dir, cat)
        os.makedirs(cat_dir, exist_ok=True)
        fname = rel.replace("packages/", "").replace("/", "_").replace(".tsx", ".json").replace(".ts", ".json")
        doc = {"file": rel, "description": f"自动迁移: {rel}", "replacements": rules}
        with open(os.path.join(cat_dir, fname), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    # 删除旧配置目录中未被覆盖的残留（新版本路径变了，旧文件已无意义）
    print(f"\n生成配置文件: {len(new_configs)} 个 -> {i18n_dir}")

if __name__ == "__main__":
    main()
