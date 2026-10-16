#!/usr/bin/env python3
"""OpenCode 2.0.x 汉化配置批量升级脚本。
自动清理废弃配置、对齐 2.0.x 新增 UI 模块、修复因主题与组件结构演进导致的未命中规则。
"""

import json
import os
import re

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_DIR = os.path.join(SKILL_ROOT, "opencode-i18n")
SRC_DIR = os.path.expanduser("~/opencode-zh-build/opencode-dev")

def remove_obsolete_configs():
    obsolete_files = [
        "components/tui_src_feature-plugins_home_tips.json",
        "components/tui_src_feature-plugins_home_tips-view.json",
        "components/tui_src_feature-plugins_system_which-key.json",
        "components/tui_src_feature-plugins_sidebar_lsp.json",
        "common/opencode_src_cli_cmd_session.json",
        "common/app_src_i18n_en.json",
        "dialogs/tui_src_component_dialog-tag.json",
        "dialogs/tui_src_routes_session_dialog-subagent.json",
        "dialogs/tui_src_component_dialog-move-session.json",
        "dialogs/tui_src_component_dialog-console-org.json",
        "dialogs/tui_src_component_dialog-workspace-list.json",
        "dialogs/tui_src_component_dialog-workspace-create.json",
        "dialogs/tui_src_component_dialog-provider.json",
        "dialogs/tui_src_routes_session_dialog-fork-from-timeline.json",
        "routes/tui_src_routes_session_question.json",
    ]
    for rel in obsolete_files:
        full = os.path.join(I18N_DIR, rel)
        if os.path.exists(full):
            os.remove(full)
            print(f"✓ 移除废弃配置: {rel}")

def save_config(category, filename, file_rel_path, description, replacements):
    cat_dir = os.path.join(I18N_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    target = os.path.join(cat_dir, filename)
    doc = {
        "file": file_rel_path,
        "description": description,
        "replacements": replacements,
    }
    with open(target, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"✓ 保存配置: {category}/{filename} ({len(replacements)} 条规则)")

def update_keybind_config():
    keybind_path = os.path.join(SRC_DIR, "packages/tui/src/config/keybind.ts")
    if not os.path.exists(keybind_path):
        print("未找到 keybind.ts，跳过")
        return
    src = open(keybind_path, encoding="utf-8").read()
    pattern = r"keybind\((.+?),\s*\"([^\"]+)\"\)"
    matches = re.findall(pattern, src)

    translations = {
        "Leader key for keybind combinations": "组合快捷键前缀引导键 (Leader)",
        "Exit the application": "退出应用程序",
        "Clear the screen in mini": "在 mini 模式下清屏",
        "Toggle debug panel": "切换调试面板",
        "Toggle console": "切换控制台",
        "Open scrap screen": "打开便签页面",
        "Toggle animations": "切换动画效果",
        "Toggle file context": "切换文件上下文",
        "Toggle diff wrapping": "切换差异换行",
        "Toggle paste summary": "切换粘贴摘要",
        "List available commands": "列出可用命令",
        "Open help dialog": "打开帮助对话框",
        "Open documentation": "打开文档",
        "Open settings": "打开设置",
        "Pair device": "配对设备",
        "Restart service": "重启服务",
        "Reload configuration": "重新加载配置",
        "Open diff viewer": "打开差异查看器",
        "Close diff viewer": "关闭差异查看器",
        "Close diff viewer item": "关闭差异项",
        "Toggle diff viewer item": "展开/折叠差异项",
        "Expand diff viewer item": "展开差异项",
        "Expand all diff viewer folders": "展开所有差异文件夹",
        "Collapse diff viewer item": "折叠差异项",
        "Switch diff viewer focus": "切换差异查看器焦点",
        "Jump to next diff hunk": "跳转到下一个差异块",
        "Jump to previous diff hunk": "跳转到上一个差异块",
        "Jump to next diff file": "跳转到下一个差异文件",
        "Jump to previous diff file": "跳转到上一个差异文件",
        "Toggle diff viewer file tree": "切换差异文件树",
        "Toggle single patch view": "切换单补丁视图",
        "Switch diff viewer source": "切换差异查看器来源",
        "Toggle diff viewer split or unified view": "切换差异分屏/统一视图",
        "Move diff viewer down": "差异视图向下移动",
        "Move diff viewer up": "差异视图向上移动",
        "Page diff viewer down": "差异视图向下翻页",
        "Page diff viewer up": "差异视图向上翻页",
        "Scroll diff viewer down half a page": "差异视图向下滚动半页",
        "Scroll diff viewer up half a page": "差异视图向上滚动半页",
        "Go to the start of the diff": "跳转到差异开头",
        "Go to the end of the diff": "跳转到差异末尾",
        "Deprecated: file tree is mouse-controlled": "已弃用：文件树改由鼠标控制",
        "Deprecated: keyboard navigation always controls the diff": "已弃用：键盘导航始终控制差异",
        "Toggle diff viewer full screen": "切换差异视图全屏",
        "Toggle selected diff file reviewed": "切换标记所选文件为已审查",
        "Focus session pane": "聚焦会话面板",
        "Focus right pane": "聚焦右侧面板",
        "Select terminal": "选择终端",
        "Toggle terminal pane": "切换终端面板",
        "Close terminal pane": "关闭终端面板",
        "Copy session ID": "复制会话 ID",
        "Manage workspaces": "管理工作区",
        "Open recent sessions and projects": "打开最近会话与项目",
        "Switch to next open session tab": "切换到下一个会话标签页",
        "Switch to previous open session tab": "切换到上一个会话标签页",
        "Close open session tab": "关闭当前会话标签页",
        "Reopen closed session tab": "重新打开关闭的会话标签页",
        "Switch to next unread session tab": "切换到下一个未读会话标签页",
        "Switch to previous unread session tab": "切换到上一个未读会话标签页",
        "Open external editor": "打开外部编辑器",
        "List available themes": "列出可用主题",
        "Switch between light and dark theme mode": "在浅色与深色主题模式间切换",
        "Lock or unlock theme mode": "锁定或解锁主题模式",
        "Toggle sidebar": "切换侧边栏",
        "Toggle session scrollbar": "切换会话滚动条",
        "View status": "查看状态",
        "New session": "新建会话",
        "Clear session": "清空会话",
        "Cancel current operation": "取消当前操作",
        "Cycle between AI models": "轮换 AI 模型",
        "Cycle backwards between AI models": "反向轮换 AI 模型",
        "Cycle between favorite AI models": "轮换收藏的 AI 模型",
        "Cycle backwards between favorite AI models": "反向轮换收藏的 AI 模型",
        "List available AI models": "列出可用的 AI 模型",
        "Cycle between model variants": "轮换模型变体",
        "Switch model variant": "切换模型变体",
        "List available sessions": "列出历史会话",
        "Switch to parent session": "切换到父会话",
        "Navigate to previous message": "导航到上一条消息",
        "Navigate to next message": "导航到下一条消息",
        "Select message above": "选择上方消息",
        "Select message below": "选择下方消息",
        "Select message": "选择消息",
        "Close message details": "关闭消息详情",
        "Select first message in session": "选择会话第一条消息",
        "Select last message in session": "选择会话最后一条消息",
        "Scroll session down half a page": "会话向下滚动半页",
        "Scroll session up half a page": "会话向上滚动半页",
        "Scroll session down a full page": "会话向下滚动整页",
        "Scroll session up a full page": "会话向上滚动整页",
        "Scroll session to the very bottom": "会话滚动到最底部",
        "Scroll session to the very top": "会话滚动到最顶端",
        "Cycle between subagents": "轮换子智能体",
        "Cycle backwards between subagents": "反向轮换子智能体",
        "List available agents": "列出可用智能体",
        "List available MCP servers": "列出可用 MCP 服务器",
        "Open file search": "打开文件搜索",
        "Compact session": "压缩当前会话",
        "Undo last message": "撤销上一条消息",
        "Redo reverted message": "重做撤销的消息",
        "Export session": "导出当前会话",
        "Toggle thinking visibility in messages": "切换消息中思考过程的显示",
        "Toggle markdown concealment in messages": "切换消息中 Markdown 标记的隐藏",
        "Move cursor left in prompt": "在输入框中向左移动光标",
        "Move cursor right in prompt": "在输入框中向右移动光标",
        "Move cursor down in prompt": "在输入框中向下移动光标",
        "Move cursor up in prompt": "在输入框中向上移动光标",
        "Move to beginning of line in prompt": "在输入框中移动到行首",
        "Move to end of line in prompt": "在输入框中移动到行尾",
        "Move backward one word in prompt": "在输入框中向后移动一个词",
        "Move forward one word in prompt": "在输入框中向前移动一个词",
        "Clear input buffer in prompt": "清空输入框内容",
        "Delete character before cursor in prompt": "删除光标前的一个字符",
        "Delete character after cursor in prompt": "删除光标后的一个字符",
        "Delete word before cursor in prompt": "删除光标前的一个词",
        "Delete word after cursor in prompt": "删除光标后的一个词",
        "Delete to start of line in prompt": "删除到行首",
        "Delete to end of line in prompt": "删除到行尾",
        "Paste clipboard contents into prompt": "将剪贴板内容粘贴到输入框",
        "Submit input in prompt": "提交输入框内容",
        "Insert newline in prompt": "在输入框中换行",
        "Show input history in prompt": "在输入框中显示输入历史",
        "Navigate backward in input history": "向前查看输入历史",
        "Navigate forward in input history": "向后查看输入历史",
        "Stash current input prompt": "暂存当前输入内容",
        "Apply stashed input prompt": "恢复暂存的输入内容",
    }

    replacements = {}
    for d, desc in matches:
        d_clean = d.strip()
        zh_desc = translations.get(desc)
        if not zh_desc:
            if desc.startswith("Switch to tab "):
                tab_num = desc.replace("Switch to tab ", "")
                zh_desc = f"切换至标签页 {tab_num}"
            elif desc.startswith("Switch to session in quick slot "):
                slot_num = desc.replace("Switch to session in quick slot ", "")
                zh_desc = f"切换至快速槽位 {slot_num} 的会话"
            else:
                zh_desc = desc
        find_str = f'keybind({d_clean}, "{desc}")'
        rep_str = f'keybind({d_clean}, "{zh_desc}")'
        replacements[find_str] = rep_str

    save_config("common", "tui_src_config_keybind.json", "packages/tui/src/config/keybind.ts", "快捷键与命令描述", replacements)

def update_app_config():
    replacements = {
        'title: "Show command palette"': 'title: "显示命令面板"',
        'title: "Switch session"': 'title: "切换会话"',
        'title: "New session"': 'title: "新建会话"',
        'title: "Clear session"': 'title: "清空会话"',
        'title: "Open session or project"': 'title: "打开会话或项目"',
        'title: "Next tab"': 'title: "下一个标签页"',
        'title: "Previous tab"': 'title: "上一个标签页"',
        'title: "Next unread tab"': 'title: "下一个未读标签页"',
        'title: "Previous unread tab"': 'title: "上一个未读标签页"',
        'title: "Close tab"': 'title: "关闭标签页"',
        'title: "Reopen closed tab"': 'title: "重新打开关闭的标签页"',
        'title: "Switch model"': 'title: "切换模型"',
        'title: "Model cycle"': 'title: "轮换模型"',
        'title: "Model cycle reverse"': 'title: "反向轮换模型"',
        'title: "Favorite cycle"': 'title: "轮换收藏模型"',
        'title: "Favorite cycle reverse"': 'title: "反向轮换收藏模型"',
        'title: "Switch agent"': 'title: "切换智能体"',
        'title: "MCP servers"': 'title: "MCP 服务器"',
        'title: "Agent cycle"': 'title: "轮换智能体"',
        'title: "Variant cycle"': 'title: "轮换模型变体"',
        'title: "Switch model variant"': 'title: "切换模型变体"',
        'title: "No variants available"': 'title: "无可用变体"',
        'message: "The current model does not support any variants."': 'message: "当前模型不支持任何变体。"',
        'title: "Agent cycle reverse"': 'title: "反向轮换智能体"',
        'title: "Connect an integration"': 'title: "连接集成"',
        'title: "Show release highlights"': 'title: "显示版本亮点"',
        'title: "Open settings"': 'title: "打开设置"',
        'title: "View status"': 'title: "查看状态"',
        'title: "Update OpenCode"': 'title: "更新 OpenCode"',
        'title: "Pair device"': 'title: "配对设备"',
        'title: "Restart service"': 'title: "重启服务"',
        'title: "Reload configuration"': 'title: "重新加载配置"',
        'title: "View debug info"': 'title: "查看调试信息"',
        'title: "Switch theme"': 'title: "切换主题"',
        'title: "Help"': 'title: "帮助"',
        'title: "Open docs"': 'title: "打开文档"',
        'title: "Exit the app"': 'title: "退出应用"',
        'title: "Toggle debug panel"': 'title: "切换调试面板"',
        'title: "Toggle console"': 'title: "切换控制台"',
        'title: "Suspend terminal"': 'title: "挂起终端"',
        'title: terminalTitleEnabled() ? "Disable terminal title" : "Enable terminal title"': 'title: terminalTitleEnabled() ? "禁用终端标题" : "启用终端标题"',
        'title: (config.data.animations ?? true) ? "Disable animations" : "Enable animations"': 'title: (config.data.animations ?? true) ? "禁用动画" : "启用动画"',
        'title: (config.data.prompt?.editor ?? true) ? "Disable file context" : "Enable file context"': 'title: (config.data.prompt?.editor ?? true) ? "禁用文件上下文" : "启用文件上下文"',
        'title: (config.data.diffs?.wrap ?? "word") === "word" ? "Disable diff wrapping" : "Enable diff wrapping"': 'title: (config.data.diffs?.wrap ?? "word") === "word" ? "禁用差异换行" : "启用差异换行"',
        'title: pasteSummaryEnabled() ? "Disable paste summary" : "Enable paste summary"': 'title: pasteSummaryEnabled() ? "禁用粘贴摘要" : "启用粘贴摘要"',
        'title: "MCP server needs authentication"': 'title: "MCP 服务器需要认证"',
        'message: "Run /mcps to view details."': 'message: "运行 /mcps 查看详情。"',
    }
    save_config("common", "tui_src_app.json", "packages/tui/src/app.tsx", "TUI 主应用命令与全局事件", replacements)

def update_toast_config():
    replacements = {
        '+{props.pending} more': '+还有 {props.pending} 条',
    }
    save_config("common", "tui_src_ui_toast.json", "packages/tui/src/ui/toast.tsx", "通知提示条", replacements)

def update_permission_util_config():
    replacements = {
        'if (option === "once") return "Allow once"': 'if (option === "once") return "仅允许一次"',
        'if (option === "always") return "Always allow"': 'if (option === "always") return "始终允许"',
        'if (option === "reject") return "Reject"': 'if (option === "reject") return "拒绝"',
        'if (option === "confirm") return "Confirm"': 'if (option === "confirm") return "确认"',
        'return "Cancel"': 'return "取消"',
        'title: "Shell command"': 'title: "Shell 命令"',
        'title: "Continue after repeated failures"': 'title: "连续失败后继续重试"',
        'lines: ["This keeps the session running despite repeated failures."]': 'lines: ["即使连续失败仍保持会话继续运行。"]',
        'return ["This will always allow the following patterns for this project.", ...save.map((item) => `- ${item}`)]': 'return ["对于当前项目，将始终允许以下规则匹配项：", ...save.map((item) => `- ${item}`)]',
        'return [`This will always allow ${input.action} for this project.`]': 'return [`对于当前项目，将始终允许执行 ${input.action}。`]',
    }
    save_config("common", "tui_src_util_permission.json", "packages/tui/src/util/permission.ts", "权限选项与提示文案", replacements)

def update_permission_route_config():
    replacements = {
        '<text fg={theme.text.muted}>No diff provided</text>': '<text fg={theme.text.muted}>未提供差异内容</text>',
    }
    save_config("routes", "tui_src_routes_session_permission.json", "packages/tui/src/routes/session/permission.tsx", "会话权限确认弹窗", replacements)

def update_session_index_config():
    replacements = {
        'pending="Preparing write…"': 'pending="正在准备写入…"',
        'pending="Finding files…"': 'pending="正在查找文件…"',
        'pending="Reading file…"': 'pending="正在读取文件…"',
        'pending="Searching content…"': 'pending="正在搜索内容…"',
        'pending="Fetching from the web…"': 'pending="正在抓取网页…"',
        'pending="Searching web…"': 'pending="正在搜索网络…"',
        'pending="Delegating…"': 'pending="正在委派任务…"',
        'pending="Asking questions…"': 'pending="正在提问…"',
        'pending="Loading skill…"': 'pending="正在加载技能…"',
        'pending="Notice"': 'pending="提示"',
        'if (next === "hide") return "Collapse thinking"': 'if (next === "hide") return "折叠思考过程"',
        'return "Expand thinking"': 'return "展开思考过程"',
        'or /redo to restore': '或 /redo 恢复',
    }
    save_config("routes", "tui_src_routes_session_index.json", "packages/tui/src/routes/session/index.tsx", "会话主界面", replacements)

def update_dialog_mcp_config():
    replacements = {
        'return <>Connecting …</>': 'return <>正在连接 …</>',
        '<span style={{ attributes: TextAttributes.BOLD }}>Connected ✓</span>': '<span style={{ attributes: TextAttributes.BOLD }}>已连接 ✓</span>',
        'return <>Failed !</>': 'return <>连接失败 !</>',
        'return <>Sign in required →</>': 'return <>需要登录认证 →</>',
        'return <>Disabled ○</>': 'return <>已禁用 ○</>',
        'if (status === "connected") return "disconnect"': 'if (status === "connected") return "断开连接"',
        'if (status === "failed") return "retry"': 'if (status === "failed") return "重试"',
        'if (status === "needs_auth") return "sign in"': 'if (status === "needs_auth") return "登录认证"',
        'return "connect"': 'return "连接"',
        'title="MCP servers"': 'title="MCP 服务器"',
        'title: "view error"': 'title: "查看错误"',
    }
    save_config("dialogs", "tui_src_component_dialog-mcp.json", "packages/tui/src/component/dialog-mcp.tsx", "MCP 服务器管理对话框", replacements)

def update_dialog_status_config():
    replacements = {
        'header={<DialogHeader title="Status" />}': 'header={<DialogHeader title="状态" />}',
        '<text fg={theme.text.base}>No MCP servers</text>': '<text fg={theme.text.base}>无 MCP 服务器</text>',
        '<Match when={item.status.status === "connected"}>Connected</Match>': '<Match when={item.status.status === "connected"}>已连接</Match>',
        '<Match when={item.status.status === "disabled"}>Disabled in configuration</Match>': '<Match when={item.status.status === "disabled"}>已在配置中禁用</Match>',
    }
    save_config("dialogs", "tui_src_component_dialog-status.json", "packages/tui/src/component/dialog-status.tsx", "状态概览对话框", replacements)

def update_dialog_debug_config():
    replacements = {
        '<DialogHeader title="Debug" />': '<DialogHeader title="调试信息" />',
        'title: "Copy debug info"': 'title: "复制调试信息"',
        'title: copied() ? "✓ copied" : "copy"': 'title: copied() ? "✓ 已复制" : "复制"',
        'message: "Debug info copied to clipboard"': 'message: "调试信息已复制到剪贴板"',
        '<text fg={theme.text.muted}>Share this when reporting an issue.</text>': '<text fg={theme.text.muted}>提交问题反馈时请附带此信息。</text>',
    }
    save_config("dialogs", "tui_src_component_dialog-debug.json", "packages/tui/src/component/dialog-debug.tsx", "调试信息对话框", replacements)

def update_dialog_session_rename_config():
    replacements = {
        'title="Rename session"': 'title="重命名会话"',
        'placeholder="Session title"': 'placeholder="会话标题"',
        'Failed to rename session:': '重命名会话失败：',
    }
    save_config("dialogs", "tui_src_component_dialog-session-rename.json", "packages/tui/src/component/dialog-session-rename.tsx", "会话重命名对话框", replacements)

def update_dialog_skill_config():
    replacements = {
        'title="Skills"': 'title="技能列表"',
        '<text fg={theme.text.muted}>No skills available</text>': '<text fg={theme.text.muted}>无可用技能</text>',
        'Could not load skills': '无法加载技能',
        '<text fg={theme.text.muted}>Close and reopen Skills to try again.</text>': '<text fg={theme.text.muted}>关闭并重新打开技能对话框重试。</text>',
        '<text fg={theme.text.muted}>Loading skills…</text>': '<text fg={theme.text.muted}>正在加载技能…</text>',
        '<text fg={theme.text.muted}>No skills found</text>': '<text fg={theme.text.muted}>未找到匹配技能</text>',
    }
    save_config("dialogs", "tui_src_component_dialog-skill.json", "packages/tui/src/component/dialog-skill.tsx", "技能选择对话框", replacements)

def update_dialog_model_config():
    replacements = {
        'return "Select model"': 'return "选择模型"',
        'footer: free(model) ? "Free" : undefined': 'footer: free(model) ? "免费" : undefined',
        'toOptions(favorites, "Favorites")': 'toOptions(favorites, "收藏模型")',
        '"Recent",': '"最近使用",',
        'title: connected() ? "Connect an integration" : "View all integrations"': 'title: connected() ? "连接新集成" : "查看全部集成"',
        'description: favorite ? "(Favorite)" : undefined': 'description: favorite ? "(已收藏)" : undefined',
    }
    save_config("dialogs", "tui_src_component_dialog-model.json", "packages/tui/src/component/dialog-model.tsx", "模型选择对话框", replacements)

def update_dialog_alert_config():
    replacements = {
        'title: "Confirm alert"': 'title: "确认警报"',
        '<text fg={theme.text.action.primary.focused}>ok</text>': '<text fg={theme.text.action.primary.focused}>确定</text>',
    }
    save_config("dialogs", "tui_src_ui_dialog-alert.json", "packages/tui/src/ui/dialog-alert.tsx", "警报对话框", replacements)

def update_dialog_export_options_config():
    replacements = {
        'header={<DialogHeader title="Export session" />}': 'header={<DialogHeader title="导出会话" />}',
        '<text fg={overlayTheme.text.base}>Copy</text>': '<text fg={overlayTheme.text.base}>复制</text>',
        '>\n              Export\n            </text>': '>\n              导出\n            </text>',
        '<text fg={theme.text.base}>Export as:</text>': '<text fg={theme.text.base}>导出格式：</text>',
        'title: "Next export option"': 'title: "下一个导出选项"',
        'title: "Select export option"': 'title: "选择导出选项"',
        '>\n              Include thinking\n            </text>': '>\n              包含思考过程\n            </text>',
        '>\n              Include tools\n            </text>': '>\n              包含工具调用\n            </text>',
        '>\n              Sanitize sensitive data\n            </text>': '>\n              脱敏敏感数据\n            </text>',
    }
    save_config("dialogs", "tui_src_ui_dialog-export-options.json", "packages/tui/src/ui/dialog-export-options.tsx", "导出会话选项对话框", replacements)

def update_dialog_select_config():
    replacements = {
        '<text fg={theme.text.muted}>No results found</text>': '<text fg={theme.text.muted}>未找到匹配结果</text>',
        'title: "Next item"': 'title: "下一项"',
        'title: "Previous item"': 'title: "上一项"',
        'title: "Select item"': 'title: "选择该项"',
    }
    save_config("dialogs", "tui_src_ui_dialog-select.json", "packages/tui/src/ui/dialog-select.tsx", "通用选择器对话框", replacements)

def update_prompt_autocomplete_config():
    replacements = {
        'if (store.visible === "command") return "No matching commands"': 'if (store.visible === "command") return "未找到匹配命令"',
        'if (files.loading) return "Searching…"': 'if (files.loading) return "正在搜索…"',
        'if (fileSearch.failed) return "Could not search directories. Keep typing to try again."': 'if (fileSearch.failed) return "无法搜索目录，请继续输入以重试。"',
        'return "No matching directories"': 'return "未找到匹配目录"',
        'if (fileSearch.failed) return "Could not search files. Keep typing to try again."': 'if (fileSearch.failed) return "无法搜索文件，请继续输入以重试。"',
        'return "No matching files, agents, or references"': 'return "未找到匹配的文件、智能体或引用"',
    }
    save_config("components", "tui_src_component_prompt_autocomplete.json", "packages/tui/src/component/prompt/autocomplete.tsx", "输入框自动补全", replacements)

def update_sidebar_footer_config():
    replacements = {
        '<b>Getting started</b>': '<b>快速入门</b>',
        '<text fg={props.context.theme.text.muted}>OpenCode includes free models so you can start immediately.</text>': '<text fg={props.context.theme.text.muted}>OpenCode 内置免费模型，您可以立即开始使用。</text>',
        '<text fg={props.context.theme.text.base}>Connect provider</text>': '<text fg={props.context.theme.text.base}>连接服务商</text>',
    }
    save_config("components", "tui_src_feature-plugins_sidebar_footer.json", "packages/tui/src/feature-plugins/sidebar/footer.tsx", "侧边栏底部快速入门与连接提示", replacements)

def update_sidebar_mcp_config():
    replacements = {
        '<Match when={item.status.status === "failed"}>Error</Match>': '<Match when={item.status.status === "failed"}>错误</Match>',
        '<Match when={item.status.status === "disabled"}>Disabled</Match>': '<Match when={item.status.status === "disabled"}>已禁用</Match>',
        '<Match when={item.status.status === "needs_auth"}>Sign in</Match>': '<Match when={item.status.status === "needs_auth"}>登录认证</Match>',
    }
    save_config("components", "tui_src_feature-plugins_sidebar_mcp.json", "packages/tui/src/feature-plugins/sidebar/mcp.tsx", "侧边栏 MCP 状态显示", replacements)

def update_prompt_index_config():
    replacements = {
        'title: "Exit shell mode"': 'title: "退出 Shell 模式"',
        'message: "This prompt cannot be queued"': 'message: "此提示词无法加入队列"',
    }
    save_config("components", "tui_src_component_prompt_index.json", "packages/tui/src/component/prompt/index.tsx", "输入框组件", replacements)

def update_diff_viewer_config():
    replacements = {
        '<text fg={theme.text.muted}>No files</text>': '<text fg={theme.text.muted}>无文件差异</text>',
    }
    save_config("components", "tui_src_feature-plugins_system_diff-viewer-file-tree.json", "packages/tui/src/feature-plugins/system/diff-viewer-file-tree.tsx", "差异查看器文件树", replacements)

    replacements_main = {
        '{branches.loading\n          ? "Loading branches…"': '{branches.loading\n          ? "正在加载分支…"',
        '<text fg={theme.text.muted}>Loading diff…</text>': '<text fg={theme.text.muted}>正在加载差异…</text>',
        '<text fg={theme.text.muted}>No changes to show</text>': '<text fg={theme.text.muted}>无变更内容</text>',
        '<text fg={theme.text.muted}>Remembered until the TUI exits</text>': '<text fg={theme.text.muted}>将在 TUI 退出前保持记住状态</text>',
    }
    save_config("components", "tui_src_feature-plugins_system_diff-viewer.json", "packages/tui/src/feature-plugins/system/diff-viewer.tsx", "差异查看器主体", replacements_main)

def update_system_plugins_config():
    replacements = {
        'title="Plugins"': 'title="插件"',
        'title: "Toggle internal plugins"': 'title: "切换内置插件显示"',
        'checking() ? "checking for updates" : "check for updates"': 'checking() ? "正在检查更新" : "检查更新"',
        'title: "view error"': 'title: "查看错误"',
        'title: "update"': 'title: "更新"',
    }
    save_config("components", "tui_src_feature-plugins_system_plugins.json", "packages/tui/src/feature-plugins/system/plugins.tsx", "系统插件列表与管理", replacements)

def add_new_v2_dialogs():
    # 1. DialogIntegration
    save_config(
        "dialogs",
        "tui_src_component_dialog-integration.json",
        "packages/tui/src/component/dialog-integration.tsx",
        "服务商集成与认证对话框",
        {
            'title="Connect an integration"': 'title="连接集成"',
            'title="Rename account"': 'title="重命名账户"',
            'placeholder="Account name"': 'placeholder="账户名称"',
            'placeholder="API key"': 'placeholder="API 密钥"',
            'placeholder="Authorization code"': 'placeholder="授权码"',
            'closeLabel="esc close"': 'closeLabel="esc 关闭"',
            'message="Connecting…"': 'message="正在连接…"',
            'message="Starting command…"': 'message="正在启动命令…"',
            'message="Waiting for command to finish…"': 'message="正在等待命令执行完成…"',
            'message="Starting authorization…"': 'message="正在启动授权…"',
            'message="Opening link…"': 'message="正在打开链接…"',
            'placeholder="Type your own answer"': 'placeholder="输入您自己的回答"',
        }
    )

    # 2. DialogWorkspaces (Worktrees)
    save_config(
        "dialogs",
        "tui_src_component_dialog-workspaces.json",
        "packages/tui/src/component/dialog-workspaces.tsx",
        "工作树(Worktrees)管理对话框",
        {
            'title="Worktrees"': 'title="工作树"',
            'Could not load worktrees': '无法加载工作树',
            '<text fg={theme.text.muted}>Loading worktrees…</text>': '<text fg={theme.text.muted}>正在加载工作树…</text>',
            '<text fg={theme.text.muted}>No worktrees available</text>': '<text fg={theme.text.muted}>无可用工作树</text>',
            '<text fg={theme.text.muted}>No worktrees found</text>': '<text fg={theme.text.muted}>未找到匹配工作树</text>',
            'title: "move"': 'title: "移动"',
            'title: "new"': 'title: "新建"',
            'title: "delete"': 'title: "删除"',
            'title: "refresh"': 'title: "刷新"',
        }
    )

    # 3. DialogOpen
    save_config(
        "dialogs",
        "tui_src_component_dialog-open.json",
        "packages/tui/src/component/dialog-open.tsx",
        "打开会话或项目对话框",
        {
            'placeholder={projectID() ? "Search worktrees…" : "Search sessions and projects…"}': 'placeholder={projectID() ? "搜索工作树…" : "搜索会话与项目…"}',
            '<text fg={theme.text.muted}>No recent sessions or projects</text>': '<text fg={theme.text.muted}>无最近会话或项目</text>',
            '<Spinner color={theme.text.muted}>Loading worktrees…</Spinner>': '<Spinner color={theme.text.muted}>正在加载工作树…</Spinner>',
            '<Spinner color={theme.text.muted}>Refreshing sessions and projects…</Spinner>': '<Spinner color={theme.text.muted}>正在刷新会话与项目…</Spinner>',
            'title: "Show project worktrees"': 'title: "显示项目工作树"',
        }
    )

    # 4. DialogHighlights
    save_config(
        "dialogs",
        "tui_src_component_dialog-highlights.json",
        "packages/tui/src/component/dialog-highlights.tsx",
        "版本亮点对话框",
        {
            'header={<DialogHeader title={`What\'s new in ${props.version}`} />}': 'header={<DialogHeader title={`v${props.version} 新特性与亮点`} />}',
            'title: "Close highlights"': 'title: "关闭亮点"',
            '<text fg={theme.text.action.primary.focused}>ok</text>': '<text fg={theme.text.action.primary.focused}>确定</text>',
        }
    )


def update_local_context_config():
    doc = {
        "file": "packages/tui/src/context/local.tsx",
        "description": "本地状态与模型选择提示",
        "replacements": {
            "message: `Agent not found: ${id}`": "message: `未找到智能体: ${id}`",
            "message: \"Add a favorite model to use this shortcut\"": "message: \"添加收藏模型以使用此快捷方式\"",
            "model: \"No provider selected\"": "model: \"未选择提供商\"",
            "provider: \"Connect a provider\"": "provider: \"连接提供商\""
        }
    }
    save_config("common", "tui_src_context_local.json", "packages/tui/src/context/local.tsx", "本地状态与模型选择提示", doc["replacements"])

def main():
    print("=== 开始更新 OpenCode 2.0.x 汉化配置 ===")
    remove_obsolete_configs()
    update_keybind_config()
    update_app_config()
    update_toast_config()
    update_local_context_config()
    update_permission_util_config()
    update_permission_route_config()
    update_session_index_config()
    update_dialog_mcp_config()
    update_dialog_status_config()
    update_dialog_debug_config()
    update_dialog_session_rename_config()
    update_dialog_skill_config()
    update_dialog_model_config()
    update_dialog_alert_config()
    update_dialog_export_options_config()
    update_dialog_select_config()
    update_prompt_autocomplete_config()
    update_sidebar_footer_config()
    update_sidebar_mcp_config()
    update_prompt_index_config()
    update_diff_viewer_config()
    update_system_plugins_config()
    add_new_v2_dialogs()
    print("=== 配置更新完成 ===")

if __name__ == "__main__":
    main()
