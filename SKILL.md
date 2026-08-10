---
name: opencode-zh
description: OpenCode CLI 界面汉化（简体中文）。下载官方最新源码 → 应用汉化包 → 误伤甄别 → 本地构建 darwin-arm64 → 部署到 ~/.opencode/bin。版本号严格跟随官方。适用场景：「汉化 opencode」「更新 opencode 汉化版」「重新生成汉化包」「opencode 中文界面」。只做 CLI UI 汉化，不碰 AI 行为、配置、插件等其他事项。
---

# OpenCode CLI 汉化（简体中文）

把 opencode（terminal AI coding agent，官方仓库 `anomalyco/opencode`）的 **CLI/TUI 界面文字**
汉化为简体中文并构建部署。**只做这一件事**：UI 汉化。其余（模型配置、工作流、agent 行为）不负责。

## 快速开始（一条命令）

```bash
bash scripts/localize.sh
```

脚本自动执行完整流程：下载官方最新源码 → 迁移汉化配置 → 应用 → 误伤甄别 → 构建 → 部署到 `~/.opencode/bin`。适用于日常「官方更新后重新汉化」。

## 手动流程（分步执行，便于调试）

### 0. 准备

- 汉化工具 `tools/opencode-cli`（缺失时先 `bash scripts/build-tool.sh`）
- 网络：`github.com` 在部分地区直连超时，环境要求见 SOP 第 7 节

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
python3 scripts/migrate_i18n.py ~/opencode-zh-build/opencode-dev
```

- 命中率 ≥70% 可接受；未命中规则打印后人工决定补写
- 迁移后配置写回 `opencode-i18n/`（注意：迁移可能生成「简单单词」毒规则，见步骤 4）

### 3. 应用汉化

```bash
export OPENCODE_PROJECT_DIR=<本目录> OPENCODE_SOURCE_DIR=~/opencode-zh-build/opencode-dev
tools/opencode-cli apply
```

**必须检查命中统计**：预期 `文件: N 成功`、`替换: X/Y 成功`。全 0 说明配置路径失效。

### 4. 误伤甄别（必做）

```bash
bash scripts/check-misreplacements.sh
```

对列出的非 `tui/src` 改动逐条确认。**红线命中立即恢复**（见下方红线清单）。

### 5. 构建 + 部署 + 验收

```bash
export OPENCODE_VERSION=$VERSION
tools/opencode-cli build --platform darwin-arm64 --deploy=false
bash scripts/deploy.sh          # 含 codesign 重签（macOS 26 必须）
opencode --version              # 验收：显示官方版本号
```

## 红线清单（违反即坏，违反即返工）

只改 UI 展示文本（JSX 文本属性、对话框、菜单、按钮、toast、帮助文本）。**禁止**：

| 红线 | 案例 | 后果 |
|---|---|---|
| TS 类型字符串字面量 | `"Unknown"` → `"未知"` | 类型判断失效 |
| SQL/数据库操作类型 | `"delete"` → `"删除"` | 数据库操作无法识别 |
| npm 包名/依赖声明 | `@typescript/native-preview` | bun install 直接失败 |
| AI prompt 模板 | `add "(Recommended)"...` | 改变 AI 行为 |
| **纯小写简单单词规则**（工具按单词边界匹配） | `"native"→"原生"` 命中包名里的 native | 必须删除，只允许带代码上下文的规则 |

## 汉化包（`opencode-i18n/`）

- 44 个 JSON 配置，按源码位置分类：`dialogs/`（对话框）、`components/`（组件/侧边栏）、`routes/`（路由页）、`common/`（其余）
- 格式：`{"file": "<仓库相对路径>", "replacements": {"原文": "译文"}}`，`file` 必须以 `packages/` 开头
- 分类目录可任意调整，apply 会递归扫描
- 更新官方源码后**不要手工改配置**，用 `scripts/migrate_i18n.py` 重定位

## 详细参考

- `SOP.md` — 完整操作规程、格式规范、环境要求、历史踩坑记录（执行前通读）
- `PITFALLS.md` — 红线案例与故障排查

## 项目维护原则

1. 只维护：汉化包（`opencode-i18n/`）、脚本（`scripts/`）、文档
2. 版本号严格跟随官方，不发明自己的版本号
3. 模型名、专有概念（Warp 等）不汉化
4. 给其他 AI agent 交付时：让它读本文件（SKILL.md）即可独立完成整个流程
