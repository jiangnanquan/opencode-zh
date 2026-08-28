#!/bin/bash
# 误伤甄别：对比「干净源码」与「已汉化源码」，列出所有改动文件，标出高风险位置。
# 用法: bash scripts/check-misreplacements.sh [源码目录]
# 默认源码目录: ~/opencode-zh-build/opencode-dev
# 需要 ~/opencode-zh-build/opencode-dev.tar.gz（干净副本来源，脚本自动解压）

set -u
SRC_DIR="${1:-$HOME/opencode-zh-build/opencode-dev}"
BUILD_DIR="$(dirname "$SRC_DIR")"
TARBALL="$BUILD_DIR/opencode-dev.tar.gz"
CLEAN_DIR="$BUILD_DIR/opencode-clean"

if [ ! -d "$SRC_DIR" ]; then
  echo "错误: 源码目录不存在: $SRC_DIR" >&2
  exit 1
fi

if [ -d "$CLEAN_DIR" ]; then
  rm -rf "$CLEAN_DIR"
fi
mkdir -p "$CLEAN_DIR"
if [ -f "$TARBALL" ]; then
  tar xzf "$TARBALL" -C "$CLEAN_DIR"
  CLEAN_PKG_DIR=$(find "$CLEAN_DIR" -mindepth 1 -maxdepth 1 -type d | head -1)/packages
else
  echo "警告: 找不到 $TARBALL，无法对比，跳过。" >&2
  exit 0
fi

echo "=== 改动文件列表（干净 vs 汉化） ==="
diff -rq "$CLEAN_PKG_DIR" "$SRC_DIR/packages" 2>/dev/null \
  | grep -v node_modules

echo ""
echo "=== 高风险位置检查（若以下路径出现在改动列表中，逐条人工确认） ==="
RISK_PATTERNS=(
  "core/src/location-mutation"
  "effect-drizzle"
  "core/src/tool/question"
  "cli/cmd/run"
  "package.json"
  "script/src/index.ts"
  "temporary.ts"
)
for pat in "${RISK_PATTERNS[@]}"; do
  diff -rq "$CLEAN_PKG_DIR" "$SRC_DIR/packages" 2>/dev/null \
    | grep -v node_modules | grep -q "$pat" && echo "  ⚠️  $pat  有改动，检查是否误伤"
done

echo ""
echo "=== 中文残留检查（在非 tui/src 的代码文件中搜中文，误伤信号） ==="
find "$SRC_DIR/packages" -name "*.ts" -o -name "*.tsx" 2>/dev/null \
  | grep -v node_modules | grep -v "/tui/src/" | grep -v "/app/src/" \
  | grep -v "/web/" | grep -v "/console/" | grep -v "/test" \
  | while read -r f; do
      if grep -qP '[\x{4e00}-\x{9fff}]' "$f" 2>/dev/null; then
        hits=$(grep -cP '[\x{4e00}-\x{9fff}]' "$f")
        echo "  ⚠️  $f ($hits 处中文)"
      fi
    done

echo ""
echo "=== 完成。逐条确认以上改动，红线命中则 sed 恢复原样 ==="
echo "红线: TS 类型字面量 / SQL 操作类型 / 包名依赖 / prompt 模板 / 错误日志模板（详见 SOP.md 第 1 节）"
