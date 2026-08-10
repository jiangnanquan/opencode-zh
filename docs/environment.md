# 本机环境备忘（内部文档，不面向公开仓库读者）

## 网络

- `github.com` 直连超时（被限制）；以下域名可直连：
  `codeload.github.com`、`raw.githubusercontent.com`、`api.github.com`、
  `release-assets.githubusercontent.com`
- macOS 系统代理：`127.0.0.1:7892`（HTTP/HTTPS/SOCKS），shell 未默认启用，需要时：

  ```bash
  export https_proxy=http://127.0.0.1:7892 http_proxy=http://127.0.0.1:7892
  ```

- 常见需要代理的场景：
  - go 依赖下载（proxy.golang.org 被墙）
  - `bun install` 失败或极慢时
  - `gh` 设备码授权（github.com/login/device 需要走代理）

## 工具链

- bun 1.3.13（fnm 管理，PATH 可用）
- go 1.26.4（/opt/homebrew/bin/go）
- gh CLI 已登录（jiangnanquan），token 含 repo/workflow/admin:public_key

## 构建目录

- 官方源码：`~/opencode-zh-build/opencode-dev`（dev 分支 tarball 解压）
- 干净副本（误伤对比用）：`~/opencode-zh-build/opencode-clean/opencode-dev`
- 构建日志：`/tmp/opencode-build-full.log`
