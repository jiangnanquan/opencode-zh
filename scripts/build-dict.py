#!/usr/bin/env python3
"""融合社区词典与自产词典，生成插件运行时词典 plugin/dict.json。

融合策略：
  1. 基础 = 社区词典（opencode-zh-hans 的 dict.json，1454 条，贴合运行时真实形态）
  2. 自产词典（dict-own.json，从 opencode-i18n 规则提取）覆盖同名词条，
     保持本项目一贯的翻译习惯（智能体/服务商/差异视图 等）
  3. 输出 { version, entries }，entries 按 key 排序

动态正则规则（含 ${} 占位符、运行时无法精确匹配的）单独记录在
plugin/dict.json 的 sibling 文件 dict-dynamic.json 中，由 translate.js 加载。

用法：
  python3 scripts/build-dict.py [社区dict.json路径] [自产dict-own.json路径]
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_DIR = ROOT
DEFAULT_COMMUNITY = os.path.expanduser("/tmp/oc-zh-hans-ref/dict.json")
DEFAULT_OWN = os.path.join(ROOT, "dict-own.json")
OUT = os.path.join(ROOT, "dict.json")

def main():
    community_path = os.sys.argv[1] if len(os.sys.argv) > 1 else DEFAULT_COMMUNITY
    own_path = os.sys.argv[2] if len(os.sys.argv) > 2 else DEFAULT_OWN

    community = json.load(open(community_path, encoding="utf-8"))["entries"]
    own = json.load(open(own_path, encoding="utf-8"))["entries"]

    merged = dict(community)  # 基础
    merged.update(own)         # 自产覆盖，保持本项目翻译习惯

    entries = dict(sorted(merged.items()))
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "entries": entries}, fh, ensure_ascii=False, indent=2)

    overlap = set(community) & set(own)
    conflicts = sum(1 for k in overlap if community[k] != own[k])
    print(f"社区词条: {len(community)}")
    print(f"自产词条: {len(own)}（其中 {len(set(own) - set(community))} 条为社区没有的增量）")
    print(f"融合后总词条: {len(entries)}")
    print(f"重叠词条: {len(overlap)}，其中以自产覆盖的冲突: {conflicts}")
    print(f"输出: {OUT}")

if __name__ == "__main__":
    main()
