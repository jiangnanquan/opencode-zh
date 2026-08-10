#!/bin/bash
# opencode-zh 一键汉化：下载官方最新源码 → 迁移配置 → 应用 → 甄别 → 构建 → 部署
# 用法: bash scripts/localize.sh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_ROOT="$HOME/opencode-zh-build"
SRC_DIR="$BUILD_ROOT/opencode-dev"
TARBALL="$BUILD_ROOT/opencode-dev.tar.gz"
TOOL="$SKILL_DIR/tools/opencode-cli"

step() { echo ""; echo "===== $1 ====="; }

# 0. 工具检查
if [ ! -x "$TOOL" ]; then
  echo "⚠️  缺少 tools/opencode-cli，先编译：bash scripts/build-tool.sh"
  exit 1
fi

# 1. 下载官方最新源码
step "1/6 获取官方最新源码 (dev)"
mkdir -p "$BUILD_ROOT"
curl -sL --connect-timeout 15 --max-time 300 -o "$TARBALL" \
  "https://codeload.github.com/anomalyco/opencode/tar.gz/refs/heads/dev"
rm -rf "$SRC_DIR"
tar xzf "$TARBALL" -C "$BUILD_ROOT"
SRC_DIR="$BUILD_ROOT/$(tar tzf "$TARBALL" | head -1 | cut -d/ -f1)"
VERSION=$(grep '"version"' "$SRC_DIR/packages/cli/package.json" | head -1 | sed -E 's/.*"([0-9.]+)".*/\1/')
echo "官方版本: $VERSION"

# 2. 迁移汉化配置
step "2/6 迁移汉化配置"
python3 "$SKILL_DIR/scripts/migrate_i18n.py" "$SRC_DIR" || echo "⚠️  迁移有未命中，继续（人工补写）"

# 3. 应用汉化
step "3/6 应用汉化"
export OPENCODE_PROJECT_DIR="$SKILL_DIR" OPENCODE_SOURCE_DIR="$SRC_DIR"
"$TOOL" apply | grep -E "使用|文件:|替换:" || true

# 4. 误伤甄别
step "4/6 误伤甄别（红线命中需人工确认并恢复）"
bash "$SKILL_DIR/scripts/check-misreplacements.sh" "$SRC_DIR" || true

# 5. 构建
step "5/6 构建 darwin-arm64（约 10-30 分钟）"
export OPENCODE_VERSION="$VERSION"
"$TOOL" build --platform darwin-arm64 --deploy=false

# 6. 部署
step "6/6 部署到 ~/.opencode/bin"
OPENCODE_SOURCE_DIR="$SRC_DIR" bash "$SKILL_DIR/scripts/deploy.sh" "$SRC_DIR"

echo ""
echo "✅ 完成！官方版本 $VERSION 汉化版已部署。运行 opencode 验收。"
