# 踩坑记录与故障排查

## 已踩过的坑（历史沉淀）

### 1. 旧汉化项目停更根因（2026-03 起）
`1186258278/OpenCodeChineseTranslation` 的 nightly 流水线用
`git clone --depth 200` 浅克隆 + `git rev-list --count` 计算上游差异，
commit 数超过 200 后 rev-list 必然失败，错误被 `|| echo "0"` 吞掉 →
COMMIT_COUNT 恒为 0 → 永久跳过构建。修复：用 GitHub API compare 接口替代。

### 2. 旧配置全部失效原因
旧版 TUI 在 `packages/opencode/src/cli/cmd/tui/`，v1.18.x 重构为独立包
`packages/tui/src/`。文件路径全变但界面文案大多保留——`migrate_i18n.py`
实测可找回 77%（308/405 条）。

### 3. 简单单词规则误伤（最危险）
迁移的宽容匹配会把 `native`、`delete`、`interrupted` 这类单词生成「简单单词规则」，
工具按单词边界匹配，命中 `@typescript/native-preview`、SQL 类型 `"delete"` 等代码标识符，
导致 bun install 失败 / 运行逻辑损坏。**必须删除所有纯小写简单单词规则**。

### 4. macOS 26 代码签名
Bun 编译产物是 `linker-signed` adhoc 签名，macOS 26+ 的 taskgated 启动即
SIGKILL（`zsh: killed`、崩溃报告 `Taskgated Invalid Signature`）。
部署前必须：`codesign --force -s - <二进制>`（deploy.sh 已内置）。
注意：构建脚本内的 smoke test 不能作为签名有效依据。

### 5. 同文案多文件副本
同一 UI 文案可能出现在多个文件（如 `title="Switch org"` 在
`dialog-console-org.tsx` 和 `app.tsx` 各一处）。补充规则后要全文搜索确认
没有其他副本遗漏。

### 6. tarball 无 git 仓库
官方源码用 tarball 下载（codeload），构建脚本执行 `git branch --show-current`
会失败。必须设置 `OPENCODE_VERSION=<版本号>` 环境变量跳过。

### 7. 跨平台交叉构建不可行
bun 1.3.8 无 `windows-aarch64` target，`bun install` 解析失败。只构建
当前平台（darwin-arm64）。

## 故障排查

| 症状 | 原因 | 解决 |
|---|---|---|
| `zsh: killed` | 签名无效 | `codesign --force -s - ~/.opencode/bin/opencode` |
| apply 显示「0 成功 42 跳过」 | 用了内置旧配置（外部目录没找到） | 确认 `opencode-i18n/` 在项目根、`OPENCODE_PROJECT_DIR` 正确 |
| `@typescript/原生-preview failed to resolve` | 毒规则（简单单词） | 删配置里的规则 + 恢复源码 |
| 构建报「不是 git 仓库」 | 缺 OPENCODE_VERSION | `export OPENCODE_VERSION=1.18.16` |
| 二进制搜不到中文字符串 | Bun 编译压缩存储，grep 不可靠 | 以源码 grep + 实际运行验收为准 |
