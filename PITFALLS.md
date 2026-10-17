# 踩坑记录与故障排查

## 当前路线（插件式 hook）踩坑

### 1. OpenCode 2.0.30 的 Host.resolve bug（最关键）

`opencode plugin add` 对纯 TUI 插件（只有 `./tui` 导出、无 server 入口）报
`ResolveMessage: Cannot find module '.../server'`。

**根因**：`packages/plugin/src/host.ts` 的 `Host.resolve` 里，`Bun.resolveSync` 对缺失模块抛的
`ResolveMessage` **不是 `Error` 子类**（`instanceof Error === false`），而 catch 逻辑第一条件就是
`!(error instanceof Error)` → 直接 rethrow，而非按预期 catch 后返回 undefined。

**影响**：所有纯 TUI 插件（含社区 `opencode-zh-hans`）在 2.0.30 上都无法用 `opencode plugin add`
安装。

**绕过**：插件目录提供 `server.js` + `rpc.js` 占位（导出空 `Plugin.define`），让 `Host.resolve`
的 server/tui/rpc 三入口都能解析、不 rethrow；再用 `scripts/install.sh` 直接编辑 cli.json 的
plugins 数组指向本地目录（绕过 `plugin add` 命令）。

**相关 issue**：[#52300](https://github.com/anomalyco/opencode/issues/52300)。

### 2. 覆盖边界：自定义 framebuffer 渲染组件

`FadeInText` / `MaskedTextRenderable` / `shimmer-text` / `title-shimmer` 等组件继承
`TextRenderable` 但通过 `drawTextBuffer` 直接操作 framebuffer，**不经过
`TextBuffer.setText/setStyledText`**，其文本不被 hook 覆盖，仍是英文。

**识别**：`grep -rn "extends.*Renderable" packages/tui/src/` 找自定义 Renderable。

**处理**：接受为设计边界，后续按需补 hook 或补词典。

### 3. `setText` 是按值传递，before 钩子无法改写实参

`TextBuffer.setText(text)` 的 `text` 是按值传递，普通的 before 钩子（`before(...args)`）无法改写
原方法收到的实参。必须用「改写第一个参数后再调原方法」的包装（见 `tui.js` 的 `patchTextMethod`）。

### 4. 词典 key 必须是「渲染层完整字符串」

运行时 `TextBuffer` 收到的 chunk.text 是「拼接后的完整串」，可能含前导空格、`\n`、状态标记
（如 `" New session"`、`"\n\n**Session ID:** "`）。词典 key 必须与之一一对应，否则无法命中。
参考社区词典（`opencode-zh-hans/dict.json`）的 key 形态。

## 故障排查

| 症状 | 原因 | 解决 |
|---|---|---|
| 插件日志无 setup 记录 | 插件未加载 | 检查 cli.json 的 plugins 数组是否含本插件路径；看 reconcile 日志 plugins 数是否 +1 |
| `Unterminated string literal` | tui.js 语法错误（转义破坏） | `node --check tui.js` 校验 |
| `Cannot find module '.../server'` | Host.resolve bug（缺占位入口） | 确认 server.js / rpc.js 存在 |
| 界面仍是英文 | hook 未生效或词典缺词 | 看 `/tmp/opencode-zh-plugin.log` 是否注册成功；开审计模式（options.audit=true）看未命中文本 |
| 某词条不翻译 | 词典 key 与运行时字符串不一致 | 开审计模式抓未命中文本，核对完整字符串（含空格/换行） |

---

## 旧路线（源码 AST 编译）踩坑（已停用，历史存档）

以下为早期「源码 AST 汉化 + Bun 重编译」路线的踩坑，随路线切换已停用，仅存档供参考。

### 旧坑 1：简单单词规则误伤
源码替换的宽容匹配会把 `native`、`delete` 生成「简单单词规则」，按单词边界命中
`@typescript/native-preview`、SQL 类型 `"delete"`，导致 bun install 失败 / 逻辑损坏。

### 旧坑 2：macOS 26 代码签名
Bun 编译产物是 `linker-signed` adhoc 签名，macOS 26+ taskgated 启动即 SIGKILL，需
`codesign --force -s - <二进制>`。

### 旧坑 3：旧配置失效
旧 TUI 在 `packages/opencode/src/cli/cmd/tui/`，v1.18.x 重构为独立包 `packages/tui/src/`，
文件路径全变但文案大多保留。

### 旧坑 4：启动卡在「Loading plugins…」
见下（该坑在新旧路线下都适用）。

## 启动卡在「Loading plugins…」—— 与汉化无关（跨路线通用）

OpenCode V2 引入插件系统后，TUI 启动会执行插件协调（reconcile），`plugins.ready()` 就绪前
`startup-loading.tsx` 一直显示「Loading plugins…」。若外部插件（cli.json 的 plugins 数组，或
`.config/opencode/plugins/` 下的旧 `.js`）加载/安装卡住，界面会永久停留此提示。

**根因定位**：看日志 `~/.local/share/opencode/log/opencode.log`，找
`plugin operation stalled ... stage=prepare ... install=true`（npm 安装网络超时）或
`failed to load plugin ... Plugin must export a default definition`（1.x 旧插件不兼容 V2）。

**解决**：
- 移除 `~/.config/opencode/cli.json` 中卡住的插件条目；
- 清理 `~/.cache/opencode/npm/<pkg>/` 下的 `.staging-*` 空目录残留；
- 或临时 `opencode --pure`（官方「不加载外部插件」启动参数）验证。
