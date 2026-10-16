// opencode TUI 汉化插件：在渲染层按词典翻译界面文字，不改二进制。
//
// 拦截点：
// - TextBuffer.setStyledText：chunk 级替换（所有文本渲染的主路径）
// - InputRenderable / TextareaRenderable 的 placeholder 访问器
//
// 任何 hook 失败都只写日志并降级，不影响 TUI 启动。
import { Plugin } from "@opencode/plugin/tui"
import * as core from "@opentui/core"
import { appendFileSync, existsSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { createTranslator, parseDictionary } from "./translate.js"

const LOG = "/tmp/opencode-zh-plugin.log"
const AUDIT = "/tmp/opencode-zh-audit.log"

function log(msg) {
  try {
    appendFileSync(LOG, `[${new Date().toISOString()}] ${msg}\n`)
  } catch {
    // 日志失败不影响主流程
  }
}

function configDir() {
  const base = process.env.XDG_CONFIG_HOME || join(process.env.HOME || "", ".config")
  return join(base, "opencode")
}

function loadDictionary() {
  const builtin = parseDictionary(JSON.parse(readFileSync(new URL("./dict.json", import.meta.url), "utf8")))
  let overrides = {}
  const overridesPath = join(configDir(), "opencode-zh-overrides.json")
  if (existsSync(overridesPath)) {
    try {
      overrides = parseDictionary(JSON.parse(readFileSync(overridesPath, "utf8")))
      log(`已加载覆盖词典：${Object.keys(overrides).length} 条`)
    } catch (e) {
      log(`覆盖词典解析失败，回退内置词典：${String(e)}`)
    }
  }
  return createTranslator(builtin, overrides)
}

/** 包装原型访问器 setter；成功则把恢复函数压入 restore。 */
function patchSetter(Cls, prop, transform, label, restore) {
  if (!Cls?.prototype) {
    log(`${label}：类不存在，跳过`)
    return
  }
  const desc = Object.getOwnPropertyDescriptor(Cls.prototype, prop)
  if (!desc?.set || !desc.configurable) {
    log(`${label}：不是可写访问器，跳过`)
    return
  }
  const original = desc.set
  Object.defineProperty(Cls.prototype, prop, {
    ...desc,
    set(value) {
      try {
        if (typeof value === "string") value = transform(value)
      } catch {
        // 降级为原值
      }
      return original.call(this, value)
    },
  })
  restore.push(() => Object.defineProperty(Cls.prototype, prop, desc))
  log(`${label}：注册成功`)
}

/** 包装原型方法；成功则把恢复函数压入 restore。 */
function patchMethod(Cls, method, before, label, restore) {
  if (typeof Cls?.prototype?.[method] !== "function") {
    log(`${label}：方法不存在，跳过`)
    return
  }
  const original = Cls.prototype[method]
  Cls.prototype[method] = function (...args) {
    try {
      before(...args)
    } catch {
      // 降级为原逻辑
    }
    return original.apply(this, args)
  }
  restore.push(() => {
    Cls.prototype[method] = original
  })
  log(`${label}：注册成功`)
}

export default Plugin.define({
  id: "opencode-zh",
  setup(context) {
    const restore = []
    try {
      const translator = loadDictionary()
      const audit = context?.options?.audit === true
      const seen = new Set()
      log(`setup：内置词典 ${translator.size} 条，审计模式 ${audit ? "开" : "关"}`)

      const auditText = (text) => {
        if (!audit) return
        if (typeof text !== "string" || text.length > 120 || !/[A-Za-z]{3}/.test(text)) return
        if (/[\u4e00-\u9fff]/.test(text)) return // 已含中文的不记
        if (translator.translate(text) !== text) return // 已命中词典的不记
        if (seen.has(text)) return
        seen.add(text)
        try {
          appendFileSync(AUDIT, text + "\n")
        } catch {
          // 忽略审计写盘失败
        }
      }

      patchMethod(
        core.TextBuffer,
        "setStyledText",
        (styled) => {
          const chunks = styled?.chunks
          translator.applyChunks(chunks)
          if (audit && Array.isArray(chunks)) {
            for (const chunk of chunks) auditText(chunk?.text)
          }
        },
        "TextBuffer.setStyledText",
        restore,
      )

      const placeholderTransform = (value) => {
        auditText(value)
        return translator.translate(value)
      }
      patchSetter(core.InputRenderable, "placeholder", placeholderTransform, "InputRenderable.placeholder", restore)
      patchSetter(core.TextareaRenderable, "placeholder", placeholderTransform, "TextareaRenderable.placeholder", restore)
    } catch (e) {
      log(`setup 失败：${String(e)}`)
    }
    return () => {
      for (const fn of restore.reverse()) {
        try {
          fn()
        } catch {
          // 忽略清理失败
        }
      }
    }
  },
})
