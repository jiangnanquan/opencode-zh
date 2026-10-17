# opencode-zh — OpenCode CLI 简体中文汉化

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](#)
[![OpenCode](https://img.shields.io/badge/OpenCode-v2.0.x%20(v2.0.32)-brightgreen.svg)](#)

> 一个 **OpenCode TUI 汉化插件**：在渲染层按词典精确匹配翻译界面文字，**零侵入、跟随官方版本、无需重新编译**。只做 UI 汉化，不碰模型配置与 AI 行为。

## 这是什么

- **汉化插件**：`tui.js`（渲染层 hook）+ `translate.js`（翻译器）+ `dict.json`（1498 条词典）
- **一键安装**：`bash scripts/install.sh` 写入 `~/.config/opencode/cli.json`，重启即生效
- **零侵入**：运行时 hook `@opentui/core` 的渲染主路径，不改二进制、不重编译
- **跟随官方**：官方升级后通常只需更新词典，无需重新编译重签名（已验证兼容至 `v2.0.32`）
- **AI 友好**：整个仓库是 skill（`SKILL.md` 为唯一入口），任何 AI agent 按它即可独立维护

## 安装

```bash
git clone https://github.com/jiangnanquan/opencode-zh.git
cd opencode-zh
bash scripts/install.sh    # 写入 cli.json，重启 opencode 生效
```

部署后运行 `opencode`，命令面板、对话框标题、按钮等应为中文。

**验证与排查：**
查看插件初始化日志，确认各 Hook 拦截点正常注册：
```bash
cat /tmp/opencode-zh-plugin.log
```

## 个性化与高级配置

- **自定义词典覆盖**：可在 `~/.config/opencode/opencode-zh-overrides.json` 中配置个性化键值对，插件加载时会自动优先合并覆盖内置词典。
- **未翻译词条捕获（审计模式）**：在插件选项中开启 `audit: true`，运行时未翻译的英文文案会自动收集至 `/tmp/opencode-zh-audit.log`，方便快速定位新增词条。

## 更新词典（官方升级或补词后）

```bash
python3 scripts/extract_dict.py   # 从 opencode-i18n 提取自产词条 → dict-own.json
python3 scripts/build-dict.py     # 融合社区词典 + 自产词典 → dict.json
bash scripts/install.sh           # 重新安装（幂等）
```

## 项目结构

```
opencode-zh/              ← 仓库根 = 插件包根
├── SKILL.md              ★ 唯一入口（AI agent 维护入口）
├── package.json          插件元数据
├── tui.js                ★ 渲染层 hook
├── translate.js          精确匹配翻译器
├── dict.json             ★ 运行时词典（1498 条）
├── server.js / rpc.js    占位入口（绕过 OpenCode 2.0.30 的 Host.resolve bug）
├── opencode-i18n/        自产词条源（444 条源码规则）
├── scripts/              install.sh / extract_dict.py / build-dict.py
├── SOP.md                参考手册（原理、格式、踩坑）
└── PITFALLS.md           踩坑记录与故障排查
```

## 技术原理

运行时 hook `@opentui/core` 的渲染主路径，按「完整字符串精确匹配」翻译：

- `TextBuffer.setText` / `TextBuffer.setStyledText` —— 文本渲染主路径
- `InputRenderable.placeholder` / `TextareaRenderable.placeholder` —— 输入框占位符

只按完整字符串匹配（不按单词边界），天然规避「简单单词误伤」；hook 失效静默降级回英文。

## 限制与通用性

- **覆盖边界**：少数走自定义 framebuffer 渲染的组件（如 `FadeInText`）不经过 hook，其文本仍是英文
- **平台无关**：插件是纯运行时 JS，任何平台（macOS/Linux/Windows）均可安装
- **模型名与专有概念**（Warp 等）按约定不汉化

## 关联项目

- [opencode](https://github.com/anomalyco/opencode) — 被汉化的官方项目
- [opencode-zh-hans](https://github.com/xlht4106/opencode-zh-hans) — 同范式的社区汉化插件（词典来源之一）
- [OpenCodeChineseTranslation](https://github.com/1186258278/OpenCodeChineseTranslation) — 早期源码编译式汉化项目（旧路线参考）
