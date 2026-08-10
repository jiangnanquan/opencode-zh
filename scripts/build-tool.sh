#!/bin/bash
# 编译 opencode-cli 汉化工具（来自汉化项目 1186258278/OpenCodeChineseTranslation 的 cli-go）
# 产物: <skill>/tools/opencode-cli
# 需要: go 1.26+；网络需要代理（proxy.golang.org 被墙）
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_CLONE="${TMPDIR:-/tmp}/opencode-cli-src"

# 1. 克隆汉化项目（仅 cli-go）
if [ -d "$TMP_CLONE/cli-go" ]; then
  echo "✓ 使用已有源码: $TMP_CLONE"
else
  echo "克隆汉化项目源码..."
  git clone --depth 1 https://github.com/1186258278/OpenCodeChineseTranslation.git "$TMP_CLONE"
fi

# 2. 编译
echo "编译 opencode-cli..."
export https_proxy=http://127.0.0.1:7892 http_proxy=http://127.0.0.1:7892
cd "$TMP_CLONE/cli-go"
go build -o "$SKILL_DIR/tools/opencode-cli" .
echo "✓ 已生成: $SKILL_DIR/tools/opencode-cli"
"$SKILL_DIR/tools/opencode-cli" --version
