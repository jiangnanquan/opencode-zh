---
name: opencode-zh
description: OpenCode CLI 界面汉化（简体中文）。下载官方最新源码 → 应用汉化包 → 误伤甄别 → 本地构建 darwin-arm64 → 部署到 ~/.opencode/bin。版本号严格跟随官方。适用场景：「汉化 opencode」「更新 opencode 汉化版」「重新生成汉化包」「opencode 中文界面」。只做 CLI UI 汉化，不碰 AI 行为、配置、插件等其他事项。
---

# OpenCode CLI 汉化（简体中文）

将 opencode（terminal AI coding agent，仓库 `anomalyco/opencode`）的 **CLI/TUI 界面文字**
汉化为简体中文并构建部署。**只做这一件事**：UI 汉化。其余一切（模型配置、工作流、
agent 行为等）不负责，交给使用者自己的 agent。

## 重要原则

1. **版本跟随官方**：汉化版 `opencode --version` 显示官方版本号（如 1.18.16）。
   构建时必须传 `OPENCODE_VERSION`，否则构建脚本报 "不是 git 仓库"。
2. **只改 UI 展示文本**：JSX 文本属性（title/placeholder/label）、对话框文字、命令面板、
   菜单项、按钮、toast、帮助文本。
3. **红线（违反即坏）**：TS 类型字符串字面量（`"Unknown"`）、SQL 操作类型（`"delete"`）、
   npm 包名/依赖声明（`@typescript/native-preview`）、AI prompt 模板、错误日志模板。
   误伤后 `bun install` 或运行会直接炸。

## 文件位置（本 skill 目录内）

- `i18n/opencode-i18n/` — 汉化配置包（JSON 规则集，含全部已翻译条目）
- `scripts/migrate_i18n.py` — 官方更新后增量迁移配置（旧规则在新源码重定位）
- `scripts/check-misreplacements.sh` — 误伤甄别（对照干净源码 + 红线扫描）
- `scripts/deploy.sh` — 部署到 `~/.opencode/bin/opencode`
- `SOP.md` — 完整操作规程（细节参考，执行前通读）
- `tools/opencode-cli` — 汉化应用/构建工具（首次需按 `scripts/build-tool.sh` 编译，或从
  汉化项目 `1186258278/OpenCodeChineseTranslation` 的 release 下载 darwin-arm64 版）

## 工作流

### 1. 获取官方最新源码

```bash
mkdir -p ~/opencode-zh-build && cd ~/opencode-zh-build
curl -sL -o opencode-dev.tar.gz "https://codeload.github.com/anomalyco/opencode/tar.gz/refs/heads/dev"
tar xzf opencode-dev.tar.gz
VERSION=$(grep '"version"' opencode-dev/packages/cli/package.json | head -1 | sed -E 's/.*"([0-9.]+)".*/\1/')
echo "官方版本: $VERSION"
```

### 2. 更新汉化配置（官方更新后必做）

```bash
python3 <skill>/scripts/migrate_i18n.py ~/opencode-zh-build/opencode-dev
```

命中率 ≥70% 可接受；未命中规则人工决定补写。迁移会写回 `<skill>/i18n/opencode-i18n/`。

### 3. 应用汉化

```bash
export OPENCODE_PROJECT_DIR=<skill目录> OPENCODE_SOURCE_DIR=~/opencode-zh-build/opencode-dev
<skill>/tools/opencode-cli apply
```

**必须看命中统计**：预期 `文件: N 成功`、`替换: X/Y 成功`。全 0 说明配置路径失效。

### 4. 误伤甄别（必做）

```bash
bash <skill>/scripts/check-misreplacements.sh
```

逐条确认列出的非 `tui/src` 改动；红线命中用 sed 恢复原样。

### 5. 构建 + 部署 + 验收

```bash
export OPENCODE_VERSION=$VERSION
<skill>/tools/opencode-cli build --platform darwin-arm64 --deploy=false
bash <skill>/scripts/deploy.sh
~/.opencode/bin/opencode --version   # 应显示官方版本号
```

## 环境备忘

- 本机 `github.com` 直连超时；`codeload.github.com` / `raw.githubusercontent.com` /
  `api.github.com` / `release-assets.githubusercontent.com` 可直连。
- 系统代理 `127.0.0.1:7892`（HTTP/HTTPS/SOCKS）：
  `export https_proxy=http://127.0.0.1:7892 http_proxy=http://127.0.0.1:7892`
  （go 依赖 proxy.golang.org、bun install 失败时必用）。
- 跨平台交叉构建不可行（bun 1.3.8 无 windows-aarch64 target），只构建 darwin-arm64。
- 旧版配置失效原因：v1.18.x 把 TUI 从 `packages/opencode/src/cli/cmd/tui/`
  重构到独立包 `packages/tui/src/`，界面文案大多保留，迁移可找回。
