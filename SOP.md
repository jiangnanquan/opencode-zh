# OpenCode CLI 汉化 SOP（参考手册）

> 本文档是 [SKILL.md](SKILL.md) 的**详细参考**：格式规范、红线案例、历史踩坑与故障排查。
> 执行流程以 SKILL.md 为准；本文档用于理解细节、排查问题。
> 维护者只需维护：`opencode-i18n/` 配置包 + `scripts/` 工具 + 本文档。

---

## 0. 任务定义

**目标**：将 opencode（terminal AI coding agent，官方仓库 `anomalyco/opencode`）的 **CLI/TUI 界面文字**
翻译为简体中文，其余一切保持不变。

**产出**：
1. 汉化配置包（JSON 规则集，位于 `opencode-i18n/`）
2. 汉化后的 opencode 二进制（darwin-arm64）
3. 部署到 `~/.opencode/bin/opencode`（该目录需在 PATH 中）

**版本策略**：版本号严格跟随官方（当前官方 dev 分支 = v1.18.23）。
汉化版 `opencode --version` 显示官方版本号，不发明任何自己的版本号。

---

## 1. 红线清单（最高优先级，违反即返工）

汉化是「字符串替换」，但**只允许替换 UI 展示文本**。以下内容一律禁止改动，
即使替换后"看起来没坏"——它们会影响程序逻辑：

| 红线 | 案例 | 后果 |
|---|---|---|
| TypeScript 类型/联合类型的字符串字面量 | `"Unknown"` → `"未知"` | 类型判断失效，运行逻辑错乱 |
| SQL/数据库操作类型 | `"select" \| "update" \| "delete" \| "insert"` 中的 `"delete"` → `"删除"` | 数据库操作无法识别 |
| npm 包名 / 依赖声明 | `@typescript/native-preview` → `@typescript/原生-preview` | bun install 解析依赖直接失败 |
| AI prompt 模板（发给模型的指令文本） | `add "(Recommended)" at the end of the label` | 改变 AI 行为/解析 |
| 代码标识符、变量名、函数名、命令名 | `describe: "list sessions"` 的 key 不变但 value 可改 | — |
| 错误日志的英文模板（可改但无意义，建议保留） | `failed to list agents from ${x}` | 中英混杂，无价值 |
| **纯小写简单单词规则**（工具按单词边界匹配） | `"native"→"原生"` 会命中 `@typescript/native-preview` 的 native；`"delete"→"删除"` 会命中 SQL 类型 `"delete"` | 配置迁移的宽容匹配会生成这类规则，必须删除——简单单词规则只允许带代码上下文（如 `title="Select agent"`） |

**判断方法**：如果一段文本出现在「引用、字符串字面量赋值给类型/枚举/常量/命令」的位置，
且不是用户可见的界面文案（title/label/placeholder/button 文本/菜单项/提示信息），则不改。

**只改这些**：JSX 属性文本（`title=`、`placeholder=`、`label=`、`aria-label=`）、
对话框文字、命令面板条目、菜单项、按钮文字、toast/状态提示、帮助文本、快捷键面板说明。

---

## 2. 官方源码地图（v1.18.x 结构）

```
packages/
├── tui/src/                  ← ★ CLI 界面主战场（独立 workspace 包）
│   ├── app.tsx               命令面板、快捷键注册
│   ├── component/            对话框组件（dialog-agent.tsx / dialog-mcp.tsx / dialog-model.tsx …）
│   ├── routes/session/       会话页（index.tsx / permission.tsx / question.tsx …）
│   ├── feature-plugins/      侧边栏等插件面板（sidebar/、system/）
│   ├── ui/                   通用 UI（dialog-select / dialog-prompt / dialog-confirm …）
│   └── prompt/               输入框提示
├── opencode/src/cli/          CLI 命令层（cmd/run.ts 等，少量 UI 文本）
└── script/src/index.ts       构建脚本（含 bun 版本检查，构建工具会 patch 它）
```

注意：早期版本（≤2026-03）TUI 在 `packages/opencode/src/cli/cmd/tui/`，
v1.18.x 已重构为独立包 `packages/tui/src/`。**不要按旧路径找文件**。

---

## 3. 工具链（本项目自带）

| 工具 | 来源 | 用途 |
|---|---|---|
| `tools/opencode-cli` | 汉化项目 `1186258278/OpenCodeChineseTranslation` 的 `cli-go` 编译产物 | `apply` 应用汉化、`build` 本地构建 |
| bun | 版本 ≥1.3（与官方构建要求兼容即可） | opencode 官方构建工具链 |
| go | 版本 ≥1.26 | 编译 opencode-cli（仅首次需要） |

opencode-cli 关键命令：
```bash
# 打汉化补丁（配置来自 OPENCODE_PROJECT_DIR/opencode-i18n 或内置资源）
OPENCODE_PROJECT_DIR=<项目根> OPENCODE_SOURCE_DIR=<官方源码> opencode-cli apply
# 构建单平台
OPENCODE_SOURCE_DIR=<官方源码> opencode-cli build --platform darwin-arm64 --deploy=false
# 验证配置
opencode-cli verify
```

opencode-cli 源码（如需重新编译）：
```bash
cd <汉化项目>/cli-go && go build -o tools/opencode-cli .
# 注意：go 依赖下载走 proxy.golang.org，被墙时需要代理环境变量
```

---

## 4. 完整工作流

### 4.1 获取官方源码（最新 dev 分支）

```bash
mkdir -p ~/opencode-zh-build && cd ~/opencode-zh-build
curl -sL -o opencode-dev.tar.gz \
  "https://codeload.github.com/anomalyco/opencode/tar.gz/refs/heads/dev"
tar xzf opencode-dev.tar.gz
# 解压出 opencode-dev/ 目录（无 .git，构建时需 OPENCODE_VERSION 环境变量）
# 确认版本：
grep '"version"' opencode-dev/packages/cli/package.json
```

> 网络提示：下载源码走 `codeload.github.com`（`github.com` 在部分地区可能直连超时，
> 此时请自行配置 HTTP 代理环境变量后重试，如 `export https_proxy=http://<代理>:<端口>`）。

### 4.2 生成/更新汉化配置（核心步骤）

两个来源，取其一：

**A. 全新汉化（首次或覆盖不全时）**：
1. 扫描 UI 字符串：在 `packages/tui/src/` 与 `packages/opencode/src/cli/` 中，
   按第 1 节「只改这些」的标准收集界面文案（建议逐文件：`component/`、`routes/session/`、
   `ui/`、`app.tsx`、`feature-plugins/`）。
2. 为每个目标文件写配置 JSON（格式见第 5 节），放入 `opencode-i18n/<分类>/`。
3. 分类目录：`dialogs/`（对话框）、`components/`（组件/侧边栏）、`routes/`（路由页）、`common/`（其余）。

**B. 增量迁移（已有配置时的快速更新）**：
1. 用 `scripts/migrate_i18n.py` 把旧配置的每条规则在新源码里重定位
   （精确匹配 → 失败则提取引号内英文核心再宽松匹配）。
2. 检查迁移结果统计：命中率 ≥70% 可接受；未命中规则人工决定是否补写。

### 4.3 应用汉化

```bash
OPENCODE_PROJECT_DIR=<skill 目录> \
OPENCODE_SOURCE_DIR=<官方源码> \
  tools/opencode-cli apply
```

预期输出：`文件: N 成功, 0 跳过, 少量失败`、`替换: X/Y 成功`。
**注意：apply 对"目标文件不存在"只算跳过不报错，必须看统计数字确认命中率。**

### 4.4 误伤甄别（必做！）

```bash
# 用干净源码对比所有改动
mkdir -p ~/opencode-zh-build/opencode-clean
tar xzf ~/opencode-zh-build/opencode-dev.tar.gz -C ~/opencode-zh-build/opencode-clean
diff -rq ~/opencode-zh-build/opencode-clean/opencode-dev/packages \
          <源码>/packages 2>/dev/null | grep -v node_modules
```

对每个差异文件：
- 位于 `tui/src/` 的 UI 文件 → 正常汉化 ✓
- 其余位置（core/、effect-drizzle/、cli/cmd 的 .ts、test/.spec 等）→ **逐条检查**
  是否踩中第 1 节红线。红线命中 → 恢复原样（用 `sed` 把误翻译改回英文）。

已知高危位置（历次踩坑）：
- `packages/core/src/location-mutation.ts`（"Unknown" 类型值）
- `packages/effect-drizzle-sqlite/src/sqlite-core/effect/session.ts`（"delete" SQL 类型）
- `packages/core/src/tool/question.ts`（prompt 模板）
- `packages/opencode/src/cli/cmd/run.ts`（错误日志）
- 任何 `package.json`（依赖名）

### 4.5 本地构建

```bash
OPENCODE_PROJECT_DIR=<skill 目录> \
OPENCODE_SOURCE_DIR=<官方源码> \
OPENCODE_VERSION=<官方版本号，如 1.18.23> \
  tools/opencode-cli build --platform darwin-arm64 --deploy=false
```

要点：
- `OPENCODE_VERSION` **必填**：源码是 tarball（无 .git），构建脚本会执行
  `git branch --show-current` 检测 channel，没有它直接报 "不是 git 仓库"。
  填官方版本号后 channel=latest，且产物版本号跟随官方。
- bun 版本检查：构建工具自动 patch `packages/script/src/index.ts` 放宽版本检查
  （bun 版本略低于官方要求时会打印 warning，属正常，可继续构建）。
- 依赖安装：首次构建 `bun install` 约 1-2 分钟（4693 packages）；网络必要时走代理。
- 产物路径：`<源码>/packages/opencode/dist/opencode-darwin-arm64/bin/opencode`。

### 4.6 部署

```bash
mkdir -p ~/.opencode/bin
cp <源码>/packages/opencode/dist/opencode-darwin-arm64/bin/opencode ~/.opencode/bin/opencode
chmod +x ~/.opencode/bin/opencode
```

### 4.7 验收

```bash
~/.opencode/bin/opencode --version        # 应显示官方版本号（如 1.18.23）
# 运行 opencode，抽查：命令面板（Ctrl+P）、对话框标题、侧边栏、帮助文本应为中文
# 确认英文残留仅出现在：AI 对话内容、错误日志、少数未覆盖的二级菜单
```

---

## 5. 汉化配置格式

```json
{
  "file": "packages/tui/src/component/dialog-agent.tsx",
  "description": "智能体选择对话框",
  "replacements": {
    "title=\"Select agent\"": "title=\"选择智能体\"",
    "Filter agents": "筛选智能体"
  }
}
```

- `file`：相对于官方仓库根的路径。**必须以 `packages/` 开头**（工具会为其他路径自动补
  `packages/opencode/` 前缀，跨包路径必须写全）。
- `replacements`：key 是源码中的原文（可含代码上下文如 `title="..."`，更精准；
  纯单词 key 会按单词边界匹配），value 是中文译文。
- 配置按分类放子目录（`dialogs/`、`components/`、`routes/`、`common/`），
  子目录任意，`apply` 会递归扫描所有 `.json`。
- 配置可以用「外部目录」模式（项目根下 `opencode-i18n/`）或编译进 opencode-cli
  （`cli-go/internal/core/assets/opencode-i18n/`）。维护时用外部目录模式即可。

---

## 6. 已知事实与坑（历史沉淀）

1. **旧汉化项目停更原因**（`1186258278/OpenCodeChineseTranslation`）：
   GitHub Actions nightly 流水线的 diff 计算用 `git clone --depth 200` 浅克隆 +
   `git rev-list --count`，上游 commit 数超过 200 后 rev-list 必然失败，
   错误被 `|| echo "0"` 吞掉 → COMMIT_COUNT 恒为 0 → 永久跳过构建（2026-03-11 起）。
   若需修复：用 GitHub API `compare` 接口替代 rev-list 即可（社区已有修复版 fork，
   或按此思路自行修复）。
2. **旧汉化配置失效原因**：旧版 TUI 在 `packages/opencode/src/cli/cmd/tui/`，
   v1.18.x 重构为独立包 `packages/tui/src/`，文件路径全变但**界面文案大多保留**
   ——迁移命中率实测 77%（308/405），自动迁移 + 人工补写即可。
3. **跨平台交叉构建**（GitHub Actions 全平台矩阵）在官方 v1.18.x 上不可行：
   `bun install` 会解析到 `bun-windows-aarch64` 目标，bun 1.3.8 无该构建 → 失败。
   只构建本机平台（darwin-arm64）即可。
4. **opencc / 翻译一致性**：译文沿用旧汉化项目的中文习惯（如「智能体」而非「代理」、
   「会话」而非「聊天」），保持新旧版本体验一致。
5. **构建产物体积**：汉化后单二进制约 100-200MB，属正常（Bun 编译产物）。
6. **代码签名（必做！）**：Bun 编译产物是 `linker-signed` 的 adhoc 签名，macOS 26+
   的 taskgated 会拒绝启动（`zsh: killed` / `SIGKILL (Code Signature Invalid)` /
   崩溃报告 `Taskgated Invalid Signature`）。**部署前必须重签**：
   ```bash
   codesign --force -s - <二进制路径>
   ```
   `deploy.sh` 已内置该步骤。验证：`opencode --version` 正常输出即 OK。
   （注意：构建脚本内的 smoke test 可能不受影响，不能作为签名有效的依据。）

---

## 7. 环境要求

**软件**：
- bun ≥1.3（opencode 官方构建工具链；版本略低于官方要求时构建工具会自动放宽检查）
- go ≥1.26（仅首次编译 `tools/opencode-cli` 时需要）
- curl / tar（下载与解压官方源码）

**网络**：
- 必须可访问：`codeload.github.com`（源码下载）、`raw.githubusercontent.com`、
  `api.github.com`、npm registry（`bun install`）
- 部分地区 `github.com` 直连超时 → 自行配置代理后重试

**约定目录**（脚本默认值，可按需修改）：
- `~/opencode-zh-build/` — 官方源码下载与解压目录（含 `opencode-dev/` 源码、
  `opencode-clean/` 干净副本）
- `~/.opencode/bin/` — 汉化版部署目录（需加入 PATH）

---

## 8. 常用命令速查

```bash
# 全部流程（源码已下载并解压到 ~/opencode-zh-build/opencode-dev 时）
export OPENCODE_PROJECT_DIR=<skill 目录>
export OPENCODE_SOURCE_DIR=~/opencode-zh-build/opencode-dev
export OPENCODE_VERSION=1.18.23            # ← 每次换源码版本时更新！

tools/opencode-cli apply                    # 1. 应用汉化（看命中统计！）
bash scripts/check-misreplacements.sh       # 2. 误伤甄别
tools/opencode-cli build --platform darwin-arm64 --deploy=false   # 3. 构建
bash scripts/deploy.sh                      # 4. 部署
~/.opencode/bin/opencode --version          # 5. 验收
```
