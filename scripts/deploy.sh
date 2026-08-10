#!/bin/bash
# 部署汉化版 opencode 到 ~/.opencode/bin/opencode
# 用法: bash scripts/deploy.sh [源码目录]
# 默认源码目录: ~/opencode-zh-build/opencode-dev
set -euo pipefail

SRC_DIR="${1:-$HOME/opencode-zh-build/opencode-dev}"
ARTIFACT="$SRC_DIR/packages/opencode/dist/opencode-darwin-arm64/bin/opencode"

if [ ! -f "$ARTIFACT" ]; then
  echo "错误: 构建产物不存在: $ARTIFACT" >&2
  echo "请先构建: OPENCODE_VERSION=<版本号> tools/opencode-cli build --platform darwin-arm64 --deploy=false" >&2
  exit 1
fi

mkdir -p "$HOME/.opencode/bin"
cp "$ARTIFACT" "$HOME/.opencode/bin/opencode"
chmod +x "$HOME/.opencode/bin/opencode"

# 关键：Bun 编译产物是 linker-signed 的 adhoc 签名，macOS 26+ 的 taskgated 会拒绝
# （SIGKILL: Code Signature Invalid）。必须用标准 adhoc 重新签名。
codesign --force -s - "$HOME/.opencode/bin/opencode" 2>/dev/null && echo "✓ 已重新签名 (adhoc)"

echo "✓ 已部署: $HOME/.opencode/bin/opencode"
"$HOME/.opencode/bin/opencode" --version
