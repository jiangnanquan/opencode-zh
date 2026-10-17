---
name: q-zh-opencode
description: OpenCode CLI 界面汉化（简体中文）——TUI 渲染层 hook 插件，零侵入、跟随官方版本、无需重新编译。适用场景：「汉化 opencode」「更新 opencode 汉化版」「opencode 中文界面」。只做 CLI/TUI UI 汉化，不碰 AI 行为、配置、插件等其他事项。
---

# OpenCode CLI 汉化（简体中文）

把 opencode（terminal AI coding agent，官方仓库 `anomalyco/opencode`）的 **TUI 界面文字**汉化为
简体中文。**技术路线**：TUI 渲染层运行时 hook 插件——在 `@opentui/core` 的渲染主路径上按词典
精确匹配翻译，**不改二进制、不重编译、跟随官方版本**（与 Claude Code 的 Mods 运行时钩子同范式）。

**只做这一件事**：UI 汉化。其余（模型配置、工作流、agent 行为）不负责。

## 快速使用

```bash
# 安装/更新汉化插件（写入 ~/.config/opencode/cli.json 的 plugins 数组）
bash scripts/install.sh

# 重启 opencode 即生效
opencode
```

插件加载日志见 `/tmp/opencode-zh-plugin.log`。验证：命令面板、对话框标题、按钮等应为中文。

## 项目结构

```
opencode-zh/              ← 仓库根 = 插件包根
├── SKILL.md              ★ 唯一入口（AI agent 读它即可完成全部工作）
├── package.json          插件元数据（exports "./tui"）
├── tui.js                ★ 渲染层 hook（TextBuffer.setText / setStyledText / placeholder）
├── translate.js          精确匹配翻译器（含动态正则规则）
├── dict.json             ★ 运行时词典（1498 条，融合社区 + 自产）
├── server.js / rpc.js    占位入口（绕过 OpenCode 2.0.30 的 Host.resolve bug）
├── opencode-i18n/        自产词条源（444 条源码规则，构建输入）
├── scripts/
│   ├── install.sh        ★ 一键安装/更新
│   ├── extract_dict.py   自产规则 → 纯字符串词条（dict-own.json）
│   └── build-dict.py     融合社区词典 + 自产词典 → dict.json
├── SOP.md                参考手册（格式规范、环境、踩坑）
├── PITFALLS.md           踩坑记录与故障排查
└── README.md             面向人类的项目说明
```

## 更新词典（官方升级或补词后）

```bash
# 1. 从 opencode-i18n 的源码规则提取纯字符串词条 → dict-own.json
python3 scripts/extract_dict.py

# 2. 融合社区词典（默认 /tmp/oc-zh-hans-ref/dict.json）与自产词典 → dict.json
python3 scripts/build-dict.py

# 3. 重新安装（install.sh 幂等）
bash scripts/install.sh
```

社区词典获取（一次性）：`gh api` 拉取 `xlht4106/opencode-zh-hans` 的 `dict.json`，
放到 `/tmp/oc-zh-hans-ref/dict.json`（或 `scripts/build-dict.py` 的第一个参数）。

## 汉化原理（简要）

1. `tui.js` 在插件 `setup` 阶段 hook `@opentui/core` 的渲染主路径：
   - `TextBuffer.setText(text)` —— 纯文本渲染（无样式，覆盖大部分 UI 文案）
   - `TextBuffer.setStyledText(StyledText)` —— 带样式文本（`styled.chunks[].text`）
   - `InputRenderable.placeholder` / `TextareaRenderable.placeholder` —— 输入框占位符
2. `translate.js` 做**完整字符串精确匹配**（词典 `{ "原文": "译文" }`），另加受控的
   动态正则规则（如 `5m ago` → `5分钟前`）。
3. 只按完整字符串匹配，不按单词边界，**天然规避「简单单词误伤」**（不会误翻包名/类型）。
4. hook 失效时静默降级回英文，不崩溃。

## 已知边界

hook 方案无法覆盖 100% 界面文本：少数走自定义 framebuffer 渲染的组件（如 `FadeInText`/
`MaskedTextRenderable`）不经过 `TextBuffer`，其文本仍是英文。这是接受的设计边界，
通过补词典 / 补 hook 逐步收敛。

## 红线（违反即坏）

只改 UI 展示文本。**禁止**改动：模型名、专有概念（Warp 等）、代码标识符、AI prompt 模板。
词典只做「完整字符串 → 中文」映射，不做任何单词边界或正则的宽泛替换（动态正则规则需逐条审）。

## 详细参考

- `SOP.md` —— 完整操作规程、格式规范、环境要求、历史踩坑记录
- `PITFALLS.md` —— 红线案例与故障排查
