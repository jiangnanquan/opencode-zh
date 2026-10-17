# OpenCode CLI 汉化 SOP（参考手册）

> 本文档是 [SKILL.md](SKILL.md) 的**详细参考**：技术原理、词典格式、踩坑记录与故障排查。
> 执行流程以 SKILL.md 为准；本文档用于理解细节、排查问题。

---

## 0. 任务定义

**目标**：将 opencode（terminal AI coding agent，官方仓库 `anomalyco/opencode`）的 **TUI 界面文字**
翻译为简体中文，其余一切保持不变。

**技术路线**：TUI 渲染层运行时 hook 插件（零侵入，不重编译）。与 Claude Code 的 Mods 运行时
钩子同范式——在渲染主路径上按词典精确匹配翻译，hook 失效静默降级。

**产出**：
1. 运行时词典 `dict.json`（`{ version, entries: { "原文": "译文" } }`）
2. 插件 `tui.js`（hook）+ `translate.js`（翻译器）+ `package.json` + 占位入口
3. 安装到 `~/.config/opencode/cli.json` 的 `plugins` 数组

**版本策略**：插件版本号独立于官方（当前 `2.0.0`）；官方升级后通常只需更新词典，无需重新编译。

---

## 1. 红线清单（最高优先级）

汉化只做「完整字符串 → 中文」的精确匹配翻译。**禁止**：

| 红线 | 案例 | 后果 |
|---|---|---|
| 单词边界匹配 | `"delete"` 命中 `@typescript/native-preview` 里的 native、SQL 类型 `"delete"` | 破坏依赖/逻辑 |
| 宽泛正则替换 | 正则匹配代码标识符、路径 | 误伤 |
| 翻译模型名/专有概念 | `Warp`、`Designer`、模型名 → 中文 | 无法识别 |
| 翻译 AI prompt 模板 | 改变发给模型的指令 | 改变 AI 行为 |

**判断方法**：词典 key 必须是「用户可见的完整 UI 文案」（标题、按钮、菜单项、toast、帮助文本、
占位符），value 是其中文。动态正则规则（`5m ago` 等）必须逐条审，只匹配「数字 + 固定词表」的
受控形态。

> 为什么 hook 方案天然安全：精确匹配只命中「完全等于 key 的完整字符串」，不按单词边界，
> 因此不会误伤 `native`、`delete` 这类单词。这是相较旧「源码 AST 替换」路线的根本优势。

---

## 2. 技术原理

### 2.1 渲染层 hook 点

`tui.js` 在插件 `setup` 阶段，hook `@opentui/core` 的渲染主路径（全部 try/catch 静默降级）：

| hook 点 | 签名 | 覆盖 |
|---|---|---|
| `TextBuffer.setText(text)` | `(string) => void` | 纯文本（无样式），覆盖大部分 UI 文案 |
| `TextBuffer.setStyledText(StyledText)` | `(StyledText) => void` | 带样式文本，`styled.chunks[].text` 就地替换 |
| `InputRenderable.placeholder` | setter 访问器 | 单行输入框占位符 |
| `TextareaRenderable.placeholder` | setter 访问器 | 多行输入框占位符 |

> `setText` 是按值传递，需用「改写实参再调原方法」的包装（`patchTextMethod`），而非
> 普通 before 钩子（后者无法改写实参）。`setStyledText` 传对象引用，可 `applyChunks` 就地改。

### 2.2 翻译器

`translate.js` 的 `createTranslator(entries, overrides)` 返回 `{ translate, applyChunks }`：
- `translate(text)`：精确匹配（overrides 优先 > 内置 > 动态正则规则 > 工具摘要规则）
- `applyChunks(chunks)`：就地翻译 `chunks[].text`，吞异常

动态正则规则处理「含变量」的运行时串（如 `Agent not found: <id>`、`5m ago`、`~3 lines`），
工具摘要规则处理「`1 command, 3 edits` → `1 个命令，3 处编辑`」。

### 2.3 词典格式

```json
{ "version": 1, "entries": { "Select agent": "选择智能体", "5m ago": "5分钟前" } }
```

- key 是**渲染层实际拿到的完整字符串**（可能含前导空格、`\n`、状态标记）
- value 是中文译文
- 用户覆盖词典 `~/.config/opencode/zh-overrides.json` 优先于内置词典

---

## 3. 词典构建流程

### 3.1 自产词条提取

`scripts/extract_dict.py` 从 `opencode-i18n/` 的 444 条「带上下文源码规则」提取「纯字符串 → 译文」：

- 裸文本（`Could not load skills` → `无法加载技能`）直接作为词条
- 带上下文（`title="Select agent"`）提取引号内 / JSX 文本，key/value 按位置配对
- 译文不含中文的配对丢弃（避免「键位 → 键位」假词条）
- 含 `${}` 模板的（`${minutes}m ago`）无法精确匹配，归入动态正则规则（人工维护在 translate.js）

### 3.2 融合社区词典

`scripts/build-dict.py` 融合：
1. 基础 = 社区词典（`opencode-zh-hans` 的 `dict.json`，1454 条，贴合运行时真实形态）
2. 自产词典覆盖同名词条（保持本项目翻译习惯：智能体/服务商/差异视图 等）
3. 输出排序后的 `dict.json`

社区词典获取：`gh api repos/xlht4106/opencode-zh-hans/contents/dict.json --jq '.content' | base64 -d`
（或 `git clone` 后取 `dict.json`）。

---

## 4. 安装与验证

### 4.1 安装

```bash
bash scripts/install.sh          # 写入 cli.json 的 plugins 数组（幂等）
# 或 git 发布后：opencode plugin add "opencode-zh@git+https://github.com/<org>/opencode-zh"
```

### 4.2 验证

```bash
# 重启 opencode，观察插件加载日志
cat /tmp/opencode-zh-plugin.log
# 期望输出：
#   setup：内置词典 1498 条
#   TextBuffer.setText：注册成功
#   TextBuffer.setStyledText：注册成功
#   InputRenderable.placeholder：注册成功
#   TextareaRenderable.placeholder：注册成功

# 或看 reconcile 日志，plugins 数应从 12（纯内置）增至 13（含 opencode-zh）
grep "reconciliation completed" ~/.local/share/opencode/log/opencode.log | tail -1
```

验收标准：命令面板、对话框标题、按钮、帮助文本为中文；英文残留仅出现在少数走自定义
framebuffer 渲染的组件、AI 对话内容、错误日志。

---

## 5. 已知坑与历史沉淀

### 5.1 OpenCode 2.0.30 的 Host.resolve bug（重要）

`packages/plugin/src/host.ts` 的 `Host.resolve` 对「缺失 server/rpc 入口」的插件，会因
`Bun.resolveSync` 抛出的 `ResolveMessage` **不是 `Error` 子类**而 rethrow（catch 里的
`!(error instanceof Error)` 判断失效），导致 `opencode plugin add` 对纯 TUI 插件报
`Cannot find module '.../server'`。

**影响**：所有纯 TUI 插件（包括社区 `opencode-zh-hans`）在 2.0.30 上都无法通过
`opencode plugin add` 安装。

**绕过**：插件目录提供 `server.js` + `rpc.js` 占位入口（导出一个空 `Plugin.define`），
让 `Host.resolve` 三个入口都能解析、不 rethrow；再直接用 `install.sh` 编辑 cli.json
的 plugins 数组指向本地目录（绕过 `plugin add` 命令）。

**相关官方 issue**：[#52300](https://github.com/anomalyco/opencode/issues/52300)（本地目录插件
忽略 package.json exports，且无根入口被静默跳过）。

### 5.2 覆盖边界

hook 方案无法覆盖 100%：走自定义 framebuffer 渲染的组件（`FadeInText` /
`MaskedTextRenderable` / `shimmer-text` / `title-shimmer` 等，继承自 `TextRenderable`
但通过 `drawTextBuffer` 直接操作 framebuffer）不经过 `TextBuffer.setText/setStyledText`，
其文本仍是英文。这是接受的设计边界。

### 5.3 旧路线停用原因（历史，供参考）

早期（≤ v1.18.x / 2.0 前）采用「源码 AST 汉化 + Bun 重编译」：
- 每次官方升级需重拉源码、迁移配置、误伤甄别、重编译、重签名，维护成本高
- 简单单词规则易误伤（`native`/`delete` 命中包名/SQL 类型）
- macOS 26 需 `codesign` 重签 Bun 产物

OpenCode V2 引入插件系统后，改用「运行时 hook 插件」路线，上述问题全部消除。
旧路线相关脚本（build-tool.sh / deploy.sh / localize.sh / check-misreplacements.sh /
migrate_i18n.py / upgrade_to_2_0.py / tools/opencode-cli）已删除。

---

## 6. 环境要求

- 无需 Bun / Go / 编译工具链（纯运行时 JS 插件）
- 网络：安装时无需网络（本地路径）；如需 `git+` 安装需可访问 git 仓库
- 约定目录：`~/.config/opencode/cli.json`（TUI 配置，含 plugins 数组）

## 7. 常用命令速查

```bash
bash scripts/install.sh                        # 安装/更新（幂等）
python3 scripts/extract_dict.py                # 自产规则 → dict-own.json
python3 scripts/build-dict.py                  # 融合 → dict.json
cat /tmp/opencode-zh-plugin.log                # 查看 hook 注册结果
grep "reconciliation completed" ~/.local/share/opencode/log/opencode.log | tail -1  # 看 plugins 数
```

## 8. 交付闭环

1. 词典/插件改动后，本地 `bash scripts/install.sh` 并重启 opencode 验证；
2. 规范提交：`feat(opencode-zh): ...` 或 `fix(opencode-zh): ...`；
3. **主动质询**：「已完成 opencode-zh 本地提交，是否立即推送至远程仓库（git push）？」，
   人类授权后方可执行 `git push`。
