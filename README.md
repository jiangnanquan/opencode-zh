# opencode-zh — OpenCode CLI 汉化项目

对 [opencode](https://github.com/anomalyco/opencode)（terminal AI coding agent）的 CLI/TUI
界面进行简体中文汉化。**版本号严格跟随官方**（汉化版 `opencode --version` 显示官方版本号）。

## 这是什么

一个「汉化包 + SOP」项目。维护者只需维护本目录：

```
opencode-zh/
├── SOP.md                 ★ 完整操作规程（交付给任何 AI agent 执行的提示词）
├── AGENTS.md              给 AI agent 的速览（进入目录自动读取）
├── i18n/opencode-i18n/    ★ 汉化配置包（JSON 规则集，59 个文件）
├── scripts/
│   ├── migrate_i18n.py            配置增量迁移（旧规则 → 新版本源码重定位）
│   ├── check-misreplacements.sh   误伤甄别（对照干净源码）
│   └── deploy.sh                  部署到 ~/.opencode/bin
├── tools/                 opencode-cli（汉化应用/构建工具，见下）
└── docs/                  踩坑记录
```

## 快速使用

```bash
# 完整流程见 SOP.md。5 步摘要：
export OPENCODE_PROJECT_DIR=/Users/jnq/Dev/Private/opencode-zh
export OPENCODE_SOURCE_DIR=~/opencode-zh-build/opencode-dev
export OPENCODE_VERSION=1.18.16        # 随官方版本更新

tools/opencode-cli apply                                          # 1 应用汉化
bash scripts/check-misreplacements.sh                             # 2 误伤甄别
tools/opencode-cli build --platform darwin-arm64 --deploy=false   # 3 构建
bash scripts/deploy.sh                                            # 4 部署
~/.opencode/bin/opencode --version                                # 5 验收
```

## 当前状态

- 最新汉化版：**v1.18.16**（2026-08-10 构建，跟随官方 dev 分支）
- 已部署：`~/.opencode/bin/opencode`（`opencode --version` → `1.18.16`）
- 汉化覆盖：308 条规则、48 个文件，273 处替换生效；误伤甄别通过（非 UI 代码 0 中文残留）

## 背景（历史）

- 社区汉化项目 [1186258278/OpenCodeChineseTranslation](https://github.com/1186258278/OpenCodeChineseTranslation)
  因 nightly 流水线 bug 自 2026-03-11 起停更，且配置针对旧版 TUI（`src/cli/cmd/tui/`），
  对 v1.18.x（TUI 重构到 `packages/tui/src/`）全部失效。
- 本项目的 i18n 配置即由旧项目配置**自动迁移**而来（405 条规则 → 308 条在新版源码定位，
  273/301 处替换生效），并修正了迁移引入的误伤。
- 部署位置 `~/.opencode/bin` 已在用户 `~/.zshrc` 的 PATH 中。

> 本机环境细节（网络、工具链、构建目录）见 `docs/environment.md`。
