#!/usr/bin/env bash
# 安装/更新 opencode-zh 汉化插件到本地 OpenCode。
#
# 用法:
#   bash scripts/install.sh            # 本地路径直接安装（开发/验证用）
#   bash scripts/install.sh <git URL>  # 从 git 安装（发布后使用）
#
# 说明:
#   OpenCode 2.0.30 的 `opencode plugin add` 对纯 TUI 插件存在 bug（Host.resolve
#   对缺失的 server/rpc 入口会因 ResolveMessage 不是 Error 子类而 rethrow）。
#   本脚本绕过该 bug：直接编辑 cli.json 的 plugins 数组指向本地插件目录。
#   插件目录必须包含 server.js / rpc.js 占位入口（已随插件提供），否则
#   Host.resolve 会因缺失入口而 rethrow。
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLI_JSON="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/cli.json"

# 校验插件目录关键文件
for f in package.json tui.js translate.js dict.json server.js rpc.js; do
  if [ ! -f "$PLUGIN_DIR/$f" ]; then
    echo "错误: 缺少插件文件 $f（应位于 $PLUGIN_DIR）" >&2
    exit 1
  fi
done

# 用 python 编辑 JSON（保持格式与幂等，仅在真正写入时备份）
python3 - "$CLI_JSON" "$PLUGIN_DIR" <<'PY'
import json, sys, shutil, datetime
path, plugin_dir = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(path, encoding="utf-8"))
except FileNotFoundError:
    d = {}
plugins = d.get("plugins", [])
if plugin_dir in plugins:
    print(f"✓ 插件已在 plugins 列表中: {plugin_dir}")
    sys.exit(0)
# 真正修改前才备份
if d:
    backup = f"{path}.bak-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy(path, backup)
    print(f"已备份: {backup}")
plugins.append(plugin_dir)
d["plugins"] = plugins
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"✓ 已写入 plugins 条目: {plugin_dir}")
PY

echo ""
echo "✓ 安装完成。重启 opencode 即可生效（插件加载日志见 /tmp/opencode-zh-plugin.log）。"
echo "  验证: 打开 opencode，命令面板/对话框标题应为中文。"
echo "  卸载: 从 $CLI_JSON 的 plugins 数组中移除本插件路径。"
