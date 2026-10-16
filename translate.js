// 运行时翻译核心：以完整字符串精确匹配为主，另加受控的动态模板规则。
// 供 TUI 插件（tui.js）使用；保持无宿主依赖，便于单元测试。

// 动态模板规则：含 ${} 占位符的运行时串（如 "Agent not found: foo"、"5m ago"）
// 无法精确匹配，用正则处理。每条：{ re: RegExp, replace: (m) => string }
const DYNAMIC_RULES = [
  // "Agent not found: <id>" → "未找到智能体: <id>"
  { re: /^Agent not found: (.+)$/, replace: (m) => `未找到智能体: ${m[1]}` },
  // "~3 lines" → "约3行"
  { re: /^~(\d+) lines$/, replace: (m) => `约${m[1]}行` },
  // "5m ago" / "3h ago" / "2d ago"
  { re: /^(\d+)m ago$/, replace: (m) => `${m[1]}分钟前` },
  { re: /^(\d+)h ago$/, replace: (m) => `${m[1]}小时前` },
  { re: /^(\d+)d ago$/, replace: (m) => `${m[1]}天前` },
  // "What's new in 2.0.30" → "v2.0.30 新特性与亮点"
  { re: /^What's new in (.+)$/, replace: (m) => `v${m[1]} 新特性与亮点` },
  // "This will always allow <action> for this project."
  { re: /^This will always allow (.+) for this project\.$/, replace: (m) => `对于当前项目，将始终允许执行 ${m[1]}。` },
  // "+3 more" → "+还有 3 条"
  { re: /^\+(\d+) more$/, replace: (m) => `+还有 ${m[1]} 条` },
]

// 工具回合摘要（如 "1 command, 3 edits, 2 thoughts"）是运行时按数量拼接的整串，
// 精确匹配无法覆盖。规则只匹配「数字 + 固定词表（可复数）」的逗号分隔串。
const SUMMARY_UNITS = {
  command: "个命令",
  edit: "处编辑",
  thought: "条思考",
  read: "次读取",
  tool: "个工具",
  instruction: "条指令",
}
const SUMMARY_TOKEN = "\\d+ (?:commands?|edits?|thoughts?|reads?|tools?|instructions?)"
const SUMMARY_RE = new RegExp(`^(?:\\+ )?${SUMMARY_TOKEN}(?:, ${SUMMARY_TOKEN})*$`)
const SUMMARY_PART_RE = /^(\d+) (command|edit|thought|read|tool|instruction)s?$/

function translateSummary(text) {
  if (!SUMMARY_RE.test(text)) return null
  const prefix = text.startsWith("+ ") ? "+ " : ""
  const body = prefix ? text.slice(2) : text
  const parts = body.split(", ").map((part) => {
    const m = SUMMARY_PART_RE.exec(part)
    return `${m[1]} ${SUMMARY_UNITS[m[2]]}`
  })
  return prefix + parts.join("，")
}

/**
 * @param {Record<string,string>} entries   内置词典
 * @param {Record<string,string>} overrides 用户覆盖词典（优先）
 */
export function createTranslator(entries = {}, overrides = {}) {
  const base = new Map(Object.entries(entries))
  const over = new Map(Object.entries(overrides))

  const resolve = (text) => {
    if (over.has(text)) return over.get(text)
    const hit = base.get(text)
    if (hit !== undefined) return hit
    // 动态模板规则
    for (const rule of DYNAMIC_RULES) {
      const m = rule.re.exec(text)
      if (m) return rule.replace(m)
    }
    const summary = translateSummary(text)
    return summary === null ? text : summary
  }

  return {
    size: base.size,
    /** 精确匹配翻译；非字符串或未命中原样返回。 */
    translate(text) {
      if (typeof text !== "string") return text
      return resolve(text)
    },
    /** 就地翻译 styled.chunks；返回替换数。任何异常都吞掉，不影响渲染。 */
    applyChunks(chunks) {
      if (!Array.isArray(chunks)) return 0
      let n = 0
      try {
        for (const chunk of chunks) {
          if (!chunk || typeof chunk.text !== "string") continue
          const next = resolve(chunk.text)
          if (next !== chunk.text) {
            chunk.text = next
            n++
          }
        }
      } catch {
        // 渲染路径上的异常必须静默降级
      }
      return n
    },
  }
}

/** 校验词典 JSON 形状（{ version, entries }），返回 entries；非法抛 Error。 */
export function parseDictionary(json) {
  if (!json || typeof json !== "object" || Array.isArray(json)) throw new Error("词典必须是对象")
  const entries = json.entries
  if (!entries || typeof entries !== "object" || Array.isArray(entries)) throw new Error("词典缺少 entries 对象")
  for (const [key, value] of Object.entries(entries)) {
    if (typeof value !== "string") throw new Error(`词条 ${key} 的译文不是字符串`)
  }
  return entries
}
