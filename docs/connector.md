---
title: "连接器"
source_url: "https://open.workbuddy.cn/docs/connector"
source_type: "official-mirror"
group: "开发"
fetched_at: "2026-09-05T08:48:20+00:00"
official_updated_at: null
source_sha256: "020d19e61f53bff5326e61e6cc3f8671d3c9780c17af4a57ba254cd0baf41c0c"
tags: ["workbuddy", "official", "connector"]
---

> 官方文档镜像 · [原文](https://open.workbuddy.cn/docs/connector) · [文档目录](../wiki/index.md) · [开发路线](../wiki/development-map.md)

<a id="连接器"></a>



# 连接器



<a id="选择接入方式"></a>



## 选择接入方式

连接器是 WorkBuddy 的能力扩展接口。用户安装连接器后，即可通过自然语言调用第三方服务。WorkBuddy 支持两种接入方式：

| 方案 | 适用场景 | 说明 |
| --- | --- | --- |
| MCP + Skill（推荐） | 已有 API 服务，或可以开发 MCP Server | 基于 MCP 协议暴露工具；远程服务优先采用 HTTPS 的 SSE 或 streamableHttp |
| CLI + Skill | 已有成熟的命令行工具 | WorkBuddy 负责安装和调度 CLI；CLI 自行管理登录态和凭证 |

如果服务可以通过网络 API 提供能力，优先选择 MCP + Skill；只有在已有稳定、跨平台 CLI 的情况下，才选择 CLI + Skill。一个连接器只能选择一种方案，二者不可混用。

若服务要求用户自行填写 Access Token 或 API Key 等长期凭证，而非走 OAuth，请使用 MCP 方案的用户自填 Token 模式，详见下文「用户自填 Token 模式」。



<a id="mcp-skill-接入"></a>



## MCP + Skill 接入



<a id="基础结构"></a>



### 基础结构



```text
your-connector/
├── connector-meta.json          # 连接器元信息（必须）
├── mcp.json                     # MCP Server 连接配置（必须）
├── icon.svg                     # 市场图标（必须）
└── skills/                      # AI 使用说明（可选）
    └── {skill-name}/
        └── SKILL.md
```





<a id="mcp-server-要求"></a>



### MCP Server 要求

- 遵循 MCP 稳定协议版本；
- 远程服务使用 HTTPS，支持 SSE 或 streamableHttp；本地进程可使用 stdio；
- 工具名称、描述、参数和返回值应清晰、稳定，便于 AI 正确选择和调用；
- 返回可读错误信息，并设置合理超时，单次请求建议在 30 秒内响应；
- 服务保持稳定可达，建议可用性不低于 99.9%；
- 涉及用户数据时必须提供认证鉴权，并遵循最小权限原则；
- 一个连接器只配置一个 MCP Server。

开发资源：

- MCP 协议规范：<https://modelcontextprotocol.io/>
- Python SDK：<https://github.com/modelcontextprotocol/python-sdk>
- TypeScript SDK：<https://github.com/modelcontextprotocol/typescript-sdk>



<a id="mcpjson"></a>



### mcp.json

远程 MCP 示例：



```json
{
  "mcpServers": {
    "your-service": {
      "type": "streamableHttp",
      "url": "https://mcptokenSchema 字段.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${SERVICE_TOKEN}"
      },
      "timeout": 30000
    }
  }
}
```



stdio MCP 示例：



```json
{
  "mcpServers": {
    "your-service": {
      "type": "stdio",
      "command": "npx",
      "args": ["your-mcp-package"],
      "runtime": {
        "type": "node",
        "version": "20"
      },
      "npmRegistry": "https://registry.npmmirror.com"
    }
  }
}
```



常用字段：

| 字段 | 必填条件 | 最低版本 | 说明 |
| --- | --- | --- | --- |
| mcpServers | 必填 | 基础 | 顶层配置；仅配置一个 Server |
| type | 远程服务必填 | 基础 | sse、streamableHttp 或 stdio；stdio 可由 command 推断 |
| url | SSE/streamableHttp 必填 | 基础 | 生产环境必须使用 HTTPS |
| command | stdio 必填 | 基础 | 启动命令，如 npx、uvx、node |
| args | 可选 | 基础 | 启动参数数组 |
| headers / env | 可选 | 基础 | `${VAR_NAME}` 变量引用，不得写入真实凭证 |
| timeout | 可选 | 基础 | 连接超时，默认 30000 毫秒 |
| cwd | 可选 | 4.22.15 | stdio 子进程工作目录 |
| disabledTools | 可选 | 4.22.15 | 不向 AI 暴露的工具列表 |
| runtime | 可选 | 5.0.0 | stdio 运行时声明，目前仅支持 `{ "type": "node", "version"?: string }` |
| npmRegistry / npmRegistries | 可选 | 5.0.0 | npm 镜像，仅在声明 `runtime.type: "node"` 时生效；数组形式按序回退 |
| staticEnv / staticHeaders | 可选 | 5.0.0 | 固定环境变量与请求头，不展示给用户且不可编辑 |
| preAuth | 可选 | 5.0.0 | 顶层字段，仅支持 `"cli"`；连接前先执行同目录 cli.json 的认证流程 |

「最低版本」标注该字段自哪个 WorkBuddy 版本起生效，标「基础」表示长期支持。使用带版本号的字段时，须在 `connector-meta.json` 中声明对应的 `minWorkbuddyVersion`。



<a id="cli-skill-接入"></a>



## CLI + Skill 接入



<a id="基础结构-1"></a>



### 基础结构



```text
your-cli-connector/
├── connector-meta.json          # 连接器元信息（必须，type 为 cli）
├── cli.json                     # CLI 安装与认证配置（必须）
├── icon.svg                     # 市场图标（必须）
└── skills/
    └── {skill-name}/
        └── SKILL.md             # CLI 使用说明（强烈推荐）
```



CLI 工具没有标准的工具描述协议，AI 需要依赖 Skill 了解可用命令和参数，因此本方案强烈推荐提供 Skill 文件。



<a id="cli-开发要求"></a>



### CLI 开发要求

- 至少支持 macOS 和 Linux，建议同时支持 Windows；
- 提供非交互式安装方式，以及明确的 auth、status、unAuth 命令；
- auth 成功后由 CLI 自行持久化登录态，status 只检查状态且不产生副作用，unAuth 负责撤销或清理登录态；
- 命令应返回明确退出码和可读错误信息，业务结果优先使用 JSON；
- 不要依赖用户机器预装的 Node.js、Python 或全局包；依赖运行时时应在 cli.json 中声明 runtime；
- 凭证与 CLI 安装目录分离，不得把密钥写入安装包、Skill 或配置样例。



<a id="clijson"></a>



### cli.json



```json
{
  "runtime": {
    "type": "node",
    "version": "20"
  },
  "init": {
    "darwin": "npm install -g your-cli",
    "linux": "npm install -g your-cli",
    "win32": "npm install -g your-cli"
  },
  "auth": {
    "darwin": "your-cli auth login",
    "linux": "your-cli auth login",
    "win32": "your-cli.cmd auth login"
  },
  "unAuth": {
    "darwin": "your-cli auth logout",
    "linux": "your-cli auth logout",
    "win32": "your-cli.cmd auth logout"
  },
  "status": {
    "darwin": "your-cli auth status",
    "linux": "your-cli auth status",
    "win32": "your-cli.cmd auth status"
  },
  "statusMatch": "Logged in",
  "authUrlDomain": "example.com"
}
```



常用字段：

| 字段 | 必填 | 最低版本 | 说明 |
| --- | --- | --- | --- |
| init.{platform} | 是 | 基础 | 各平台安装命令，平台名为 darwin、linux、win32 |
| auth | 按需 | 基础 | 登录命令；单步为平台命令对象，多步为数组 |
| unAuth.{platform} | 有认证时必填 | 基础 | 登出或清理授权命令 |
| status.{platform} | 有认证时必填 | 基础 | 无副作用的认证状态检查命令 |
| statusMatch / statusMatchJson | 二选一 | 基础 / 4.24.0 | 判断已登录状态的文本正则或 JSON 条件，后者优先 |
| authUrlDomain | 浏览器授权时建议 | 基础 | 限定 WorkBuddy 可提取并打开的认证域名 |
| env | 可选 | 4.22.0 | 向命令注入固定环境变量，可使用 `$HOME` 或 `${HOME}` |
| runtime | 依赖运行时时建议 | 4.22.0 / 5.0.0 | 声明 Node.js 或 Python 运行时及版本，Python 自 5.0.0 起支持 |
| npmRegistry / npmRegistries | 可选 | 4.22.0 / 4.24.0 | npm 镜像，数组形式按序回退 |
| versionCheck | 可选 | 4.24.0 | 检查 CLI 最低版本，版本过低时重新执行安装 |
| authWaitForExit | 可选 | 4.22.0 | 提取到认证 URL 后不终止子进程，等待 CLI 自行退出 |
| authQrModal | 可选 | 4.22.0 | 使用内嵌弹窗展示认证链接，与 authDeviceFlow 互斥 |
| authSuppressBrowser | 可选 | 4.22.8 | 不由 WorkBuddy 打开浏览器，交由 CLI 自行处理 |
| authDeviceFlow | 可选 | 5.0.0 | OAuth 2.0 Device Flow（RFC 8628）配置，与 authQrModal 互斥 |



<a id="运行时托管与安装位置"></a>



### 运行时托管与安装位置

对于依赖 Node.js 或 Python 的 CLI，建议在 `cli.json` 中声明 `runtime`。WorkBuddy 会准备对应运行时并注入命令环境，用户无需预先安装；同时 npm 与 pip 的安装位置和缓存会隔离到 WorkBuddy 管理目录，不会污染用户系统环境。

| 声明 | WorkBuddy 行为 | 开发者注意事项 |
| --- | --- | --- |
| `runtime.type: "node"` | 准备托管 Node.js，将 npm 全局安装目录与缓存指向 WorkBuddy 管理目录，并把 bin 目录加入 PATH | `npm install -g <package>` 可直接使用，但不要假设写入用户系统的全局目录，也不要依赖用户的 `~/.npmrc` |
| `runtime.type: "python"` | 准备托管 Python 并激活 WorkBuddy 管理的虚拟环境，pip 与缓存均与用户系统隔离 | 建议使用 `python -m pip install <package>`；不要使用 `pip install --user`，也不要依赖用户系统 Python |
| 未声明 runtime | 沿用用户系统环境和 PATH | 仅当 CLI 不依赖 Node/Python 时使用，需自行保证依赖可用 |

安装路径由 WorkBuddy 管理，开发者不应在命令中写死绝对路径。凭证与授权文件则完全由 CLI 自行管理：WorkBuddy 只负责调度 auth、status、unAuth，不会迁移或清理 CLI 的凭证文件，因此凭证应与运行时安装目录分离存放。



<a id="认证流程与关键约束"></a>



### 认证流程与关键约束

用户点击「连接」后，WorkBuddy 依次执行：检查安装（未安装则执行 init）、执行 status 判断登录态；未登录时执行 auth，从命令输出中提取认证 URL 并打开浏览器，随后每 3 秒轮询一次 status，最长等待 5 分钟。

关键约束：WorkBuddy 在提取到认证 URL 后会立即终止 auth 子进程，因此 auth 子进程本身不能作为 OAuth 回调的接收方。可选用以下任一方案：

| 方案 | 复杂度 | 适用场景 |
| --- | --- | --- |
| 后台 Daemon 接收回调 | 中 | CLI 已有常驻进程机制，Daemon 在 auth 退出后继续接收回调并持久化 Token |
| Device Code Flow（推荐） | 低 | 认证服务器支持 RFC 8628；无需本地回调，建议同时配置 `authDeviceFlow` |
| 服务端 Token 存储 | 中 | 自建认证服务，授权结果存于服务端，由 status 拉取到本地 |

auth 命令输出要求：

- 在 stdout 或 stderr 中输出完整的 https:// 认证 URL，并在 10 秒内输出；
- URL 前后需有空白字符分隔，不能被引号或尖括号包裹，否则会被截断；
- 不得进入交互式输入等待（执行环境没有 TTY），也不应自行打开浏览器而不输出 URL。

各命令超时与判定规则：

| 命令 | 超时 | 判定与要求 |
| --- | --- | --- |
| init | 5 分钟 | 安装可能涉及较大下载，需支持非交互式执行 |
| auth | 10 秒 | 只需输出认证 URL，不需等待用户完成授权 |
| status | 10 秒 | 退出码 0 且输出匹配 `statusMatch` 时视为已登录；须幂等、无副作用，并读取持久化状态 |
| unAuth | 30 秒 | 清理本地凭证及远端会话；未登录时也应正常返回 |
| 认证轮询 | 5 分钟 | 每 3 秒执行一次 status，超时则标记连接失败 |

WorkBuddy 重启后会自动执行 status 恢复连接，但不会重新执行 auth，因此 CLI 的登录态必须跨进程重启有效。



<a id="连接器元信息"></a>



## 连接器元信息

`connector-meta.json` 用于注册连接器，并在市场中展示名称、描述和使用示例。



```json
{
  "name": "任务管理",
  "name_zh": "任务管理",
  "name_en": "Task Manager",
  "description": "Create and manage tasks in WorkBuddy.",
  "description_zh": "通过自然语言创建、查询和更新任务。",
  "description_en": "Create, query, and update tasks with natural language.",
  "source": "task-manager",
  "type": "mcp",
  "version": "1.0.0",
  "examples_zh": [
    "创建一个明天下午到期的评审任务",
    "列出本周尚未完成的任务"
  ],
  "examples_en": [
    "Create a review task due tomorrow afternoon",
    "List unfinished tasks for this week"
  ]
}
```



| 字段 | 必填 | 最低版本 | 说明 |
| --- | --- | --- | --- |
| name / name_en | 是 | 基础 | 默认名称和英文名称；可补充 name_zh |
| description / description_zh / description_en | 是 | 基础 | 简明说明核心能力和适用场景，建议 20～100 字 |
| source | 是 | 基础 | 全局唯一标识，只能使用小写字母、数字和连字符 |
| type | 可选 | 基础 | mcp（默认）、cli 或 skill-only；CLI 方案必须设为 cli |
| version | 建议 | 基础 | 语义化版本号，每次更新递增 |
| examples_zh / examples_en | 是 | 4.24.0 | 中英文使用示例，建议各 2～5 条 |
| auth_mode | MCP 按需 | 基础 | 省略、server-side、gateway 或 token |
| minWorkbuddyVersion | 使用新字段时必填 | 4.22.12 | 连接器要求的最低 WorkBuddy 版本 |
| maxWorkbuddyVersion | 可选 | 4.22.12 | 支持的最高版本，用于紧急停用 |
| name_map / description_map | 可选 | 5.2.0 | 按环境或账号形态覆盖名称与描述 |

名称应简明、可识别，描述应直接说明用户能完成什么任务，示例应使用用户真实会说的自然语言。

展示优先级：名称为 name_map（命中环境）> name_zh > name_en > name，描述同理回退到 description_zh、description_en、description。



<a id="版本兼容性"></a>



### 版本兼容性

不同 WorkBuddy 客户端支持的配置字段不同。使用较新字段时必须声明 `minWorkbuddyVersion`，否则低版本客户端可能拉取到不兼容的配置。若同时使用多个新特性，取其中最高版本作为声明值。

| 字段或能力 | 最低版本 |
| --- | --- |
| type: skill-only、auth_mode: server-side、cli.json 的 unAuth / statusMatch / authUrlDomain | 基础 |
| cli.json 的 runtime / npmRegistry / env、authWaitForExit / authQrModal、auth_mode: gateway | 4.22.0 |
| cli.json 的 authSuppressBrowser | 4.22.8 |
| minWorkbuddyVersion / maxWorkbuddyVersion | 4.22.12 |
| mcp.json 的 cwd / disabledTools | 4.22.15 |
| auth_mode: token 及 token-schema.json | 4.23.0 |
| name_zh / name_en、examples_zh / examples_en、statusMatchJson / versionCheck / npmRegistries、多步 auth 数组 | 4.24.0 |
| cli.json 的 authDeviceFlow 与 Python 运行时、mcp.json 的 preAuth / runtime / staticEnv / staticHeaders | 5.0.0 |
| name_map / description_map | 5.2.0 |

低于所声明版本的客户端：从未启用过该连接器时不展示；已启用或曾连接过则降级置灰并提示升级。



<a id="skill-文件"></a>



## Skill 文件

Skill 用于指导 AI 正确使用连接器。MCP 已提供标准工具描述时可选；CLI 方案强烈推荐提供。

Skill 的目录和 `SKILL.md` 格式参见本页「开发—技能」。能力较多时可拆分为多个 Skill，每个放置在独立子目录下，WorkBuddy 会全部加载。编写时重点说明：

- 每个 MCP Tool 或 CLI 命令的用途；
- 参数名称、类型、是否必填和默认值；
- 典型调用示例及返回格式；
- 认证前置条件、错误场景和恢复方式；
- 高风险操作需要的确认规则。



<a id="认证与凭证"></a>



## 认证与凭证

| 场景 | 接入方式 | 是否打开浏览器 |
| --- | --- | --- |
| MCP Server 自带 OAuth 或无需认证 | `auth_mode` 省略，按标准 MCP 流程连接 | 需授权时会打开 |
| WorkBuddy 云端托管 OAuth | 使用 server-side 或 gateway，接入前与 WorkBuddy 团队确认 | 需授权时会打开 |
| 用户自行填写 Access Token / API Key | 使用 `auth_mode: "token"`，并提供 token-schema.json 描述表单 | 不打开 |
| CLI 登录 | 通过 cli.json 的 auth、status、unAuth 管理，凭证由 CLI 自行安全存储 | 取决于 CLI 认证方式 |

安全要求：

- 不得在 connector-meta.json、mcp.json、cli.json、Skill 或示例中硬编码真实 Token、密钥；
- 仅申请完成业务所需的最小权限；
- 远程 MCP 使用 HTTPS；
- 敏感凭证字段应使用密码类型，日志和错误信息中不得输出完整凭证；
- 授权失效时应返回可识别错误，并引导用户重新连接。



<a id="mcp-oauth-流程"></a>



### MCP OAuth 流程

当 MCP Server 需要访问用户私有数据并采用 OAuth 时，WorkBuddy 内置的 OAuth 管理器会自动完成客户端侧流程，采用 OAuth 2.1 + PKCE，并以公共客户端身份接入（不持有 client_secret）。开发者只需实现服务端端点。

整体流程：首次请求未携带 Token 返回 401 → 发现元数据 → 动态客户端注册 → 打开浏览器授权 → 校验 state 并交换 Token → 携带 Bearer Token 正常调用。

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| /.well-known/oauth-protected-resource | GET | 返回 resource 地址与 authorization_servers 列表 |
| /.well-known/oauth-authorization-server | GET | 返回 issuer、各端点地址与支持的 scope |
| /oauth/register | POST | 动态客户端注册（RFC 7591），需接受公共客户端并回显 redirect_uris |
| /oauth/authorize | GET | 授权端点，须支持 `code_challenge_method: S256` |
| /oauth/token | POST | 校验 `code_verifier` 并签发 access_token 与 refresh_token，须支持 refresh_token 授权类型 |

服务端行为要求：

- 必须支持 PKCE（`S256`），授权码一次性使用且有效期约 10 分钟；
- redirect_uri 需按字符串精确匹配，优先支持 WorkBuddy 私有协议回调 `workbuddy://workbuddy/mcp/connector%3A<source>/oauth/callback`；
- 若平台仅允许 HTTP/HTTPS 回调，则应允许本机回环地址 `http://127.0.0.1:{动态端口}/oauth/callback`，WorkBuddy 会在私有协议被拒绝时自动回退一次；
- 动态注册响应除 client_id 外必须回显 redirect_uris，否则后续流程无法继续；
- access_token 建议有效期 1 小时，refresh_token 建议不少于 30 天，过期后 WorkBuddy 会引导用户重新授权；
- 所有 OAuth 服务端端点强制使用 HTTPS，并遵循 OAuth 2.1 标准错误格式。

access_token 过期时，WorkBuddy 会自动使用 refresh_token 续期并重试原请求，此过程对用户透明。



<a id="用户自填-token-模式"></a>



### 用户自填 Token 模式

当第三方服务不提供 OAuth，仅提供 Personal Access Token、API Key，或需要用户指定私有部署地址时，使用 `auth_mode: "token"`。WorkBuddy 会弹出表单收集凭证，凭证仅保存在用户本机并在连接时注入，不经过云端，整个过程不打开浏览器。该模式需声明 `minWorkbuddyVersion` 不低于 4.23.0。

本模式需额外提供 `token-schema.json` 描述表单字段，并在 `mcp.json` 中用 `${VAR}` 占位引用。占位符名称必须与表单字段的 key 完全一致（区分大小写）：

| MCP 传输类型 | 凭证注入位置 | 典型写法 |
| --- | --- | --- |
| stdio | env（环境变量） | `"env": { "API_KEY": "${API_KEY}" }` |
| sse / streamableHttp | headers 或 url | `"Authorization": "Bearer ${API_KEY}"` |

`token-schema.json` 示例：



```json
{
  "title": "服务对接配置",
  "title_en": "Service Configuration",
  "description": "连接您的账号以调用服务。凭证仅存储在本机 ~/.workbuddy 目录下。",
  "description_en": "Connect your account. Credentials are stored locally only.",
  "docUrl": "https://example.com/docs/api-token",
  "docLabel": "如何获取 Access Token？",
  "fields": [
    {
      "key": "API_KEY",
      "label": "Access Token",
      "type": "password",
      "required": true,
      "placeholder": "在个人中心 → 开放平台 → API 中生成",
      "description": "用于访问服务 OpenAPI 的个人访问令牌。"
    },
    {
      "key": "API_BASE_URL",
      "label": "API 基础地址",
      "label_en": "API Base URL",
      "type": "text",
      "required": true,
      "defaultValue": "https://api.example.com",
      "description": "私有部署可改为内网地址。"
    }
  ]
}
```



| 字段 | 必填 | 说明 |
| --- | --- | --- |
| title | 是 | 表单标题 |
| description | 是 | 表单说明，建议明确告知凭证的存储位置以消除用户顾虑 |
| docUrl / docLabel | 可选 | 凭证获取文档链接及其显示文案，会渲染为表单内的可点击链接 |
| fields | 是 | 字段列表，至少一项 |
| fields[].key | 是 | 字段键名，对应 `mcp.json` 中 `${VAR}` 的名称，区分大小写 |
| fields[].label | 是 | 输入框标签 |
| fields[].type | 是 | text 或 password，敏感凭证一律使用 password |
| fields[].required | 是 | 是否必填，未填写时表单会拦截提交 |
| fields[].placeholder | 可选 | 占位提示，建议指明凭证获取路径或示例值 |
| fields[].defaultValue | 可选 | 初始值，用户可修改；Base URL 类字段建议提供 |
| fields[].description | 可选 | 字段下方的辅助说明 |

多语言文案通过新增 `_en` 后缀的平行字段实现，例如 `title_en`、`label_en`。原字段必须保持字符串类型，不可改为对象，否则低版本客户端将无法渲染。

同一服务若需同时提供 OAuth 与 Token 两种方式，必须使用两个不同的 source 分别提交，作为两个独立的连接器。



<a id="图标规范"></a>



## 图标规范

| 项目 | 要求 |
| --- | --- |
| 格式 | SVG（推荐）、PNG 或 JPG |
| 文件名 | icon.svg、icon.png 或 icon.jpg |
| 尺寸 | PNG/JPG 建议 64×64 px |
| 背景 | 建议透明 |
| 风格 | 简洁清晰，小尺寸下可辨识 |



<a id="提交前检查"></a>



## 提交前检查

- 已选择 MCP 或 CLI 接入方案，目录结构符合规范；
- source 使用 kebab-case 且保持全局唯一；
- 连接器名称、说明和中英文示例填写完整；
- MCP 仅配置一个 Server，远程地址使用 HTTPS；
- 或 CLI 已验证安装、认证、状态检查、登出和跨平台行为；
- CLI 方案已验证登录态跨重启有效，且 unAuth 能正确清理授权；
- 涉及 OAuth 时已实现元数据发现、动态注册与 PKCE 校验，并接受约定的回调地址；
- 使用自填 Token 模式时，`${VAR}` 占位符与表单字段 key 一一对应，敏感字段为 password 类型；
- Skill 能准确指导 AI 调用全部核心能力；
- 未在任何文件中写入真实凭证；
- 图标清晰可辨，版本号和最低 WorkBuddy 版本声明正确；
- 已覆盖超时、授权失效、参数错误等常见异常。

准备完成后，将连接器目录打包并提交 WorkBuddy 团队审核。审核通过后，连接器将进入连接器市场；后续更新重新提交审核即可，通常在 10～15 分钟内同步生效。
