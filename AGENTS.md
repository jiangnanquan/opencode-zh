# AGENTS.md — 给 AI Agent 的速览

你的任务：**只对 opencode CLI/TUI 的界面文字做简体中文汉化**，构建 darwin-arm64 汉化版并部署到 `~/.opencode/bin/opencode`。版本号严格跟随官方。

**完整规程见 [SOP.md](SOP.md)，执行任何操作前必须先读它。** 以下是摘要：

## 工作流（5 步）

1. **源码**：`~/opencode-zh-build/opencode-dev`（官方 dev 分支 tarball，版本见 `packages/cli/package.json`）
2. **汉化配置**：本目录 `i18n/opencode-i18n/`（JSON 规则集；版本更新时用 `scripts/migrate_i18n.py` 增量迁移）
3. **应用**：`OPENCODE_PROJECT_DIR=/Users/jnq/Dev/Private/opencode-zh OPENCODE_SOURCE_DIR=~/opencode-zh-build/opencode-dev tools/opencode-cli apply`（**必须检查命中统计**）
4. **误伤甄别**：`bash scripts/check-misreplacements.sh`（对照干净源码 diff，红线位置逐条检查）
5. **构建+部署**：`OPENCODE_VERSION=<官方版本号> tools/opencode-cli build --platform darwin-arm64 --deploy=false && bash scripts/deploy.sh`

## 红线（违反即返工）

只改 UI 展示文本。**禁止改动**：TS 类型字符串字面量（如 `"Unknown"`）、SQL 操作类型（`"delete"`）、
npm 包名/依赖声明（`@typescript/native-preview`）、AI prompt 模板、错误日志模板。
误改会在 `bun install` 或运行时炸掉。详见 SOP 第 1 节。

## 网络

本机 `github.com` 直连超时；`codeload.github.com`/`raw.githubusercontent.com`/`api.github.com` 可直连。
必要时用系统代理：`export https_proxy=http://127.0.0.1:7892 http_proxy=http://127.0.0.1:7892`
（go 依赖下载走 proxy.golang.org 也必须代理）。

## 版本号

汉化版版本 = 官方版本（构建时必须传 `OPENCODE_VERSION`，否则构建脚本报 "不是 git 仓库"）。
