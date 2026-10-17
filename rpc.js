// server 端占位入口：本插件是纯 TUI 插件，无需 server 逻辑。
// 提供此文件仅为绕过 OpenCode 2.0.30 Host.resolve 对缺失入口的 ResolveMessage
// rethrow bug（ResolveMessage 不是 Error 子类，绕过了 catch 保护）。
import { Plugin } from "@opencode/plugin"

export default Plugin.define({
  id: "opencode-zh",
  setup() {
    // 无 server 端逻辑
  },
})
