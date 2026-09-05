---
title: "Open API 接口"
source_url: "https://open.workbuddy.cn/docs/openapi"
source_type: "official-mirror"
group: "开发"
fetched_at: "2026-09-05T08:48:20+00:00"
official_updated_at: null
source_sha256: "4b48a31290a81658954415f707fa022e8be9408cd754186cf5d5bb136e6065d2"
tags: ["workbuddy", "official", "openapi"]
---

> 官方文档镜像 · [原文](https://open.workbuddy.cn/docs/openapi) · [文档目录](../wiki/index.md) · [开发路线](../wiki/development-map.md)

<a id="open-api-接口"></a>



# Open API 接口

本章节汇总当前开放的接口，按能力分为认证授权、个人资料、本地助理、云端任务、ACP 通道、会话产物和兑换码核销。开发者可先根据业务目标选择对应分类，再结合接口的权限要求、请求参数和响应结构完成接入。

- 认证授权 API：完成用户授权并换取访问凭证。
- 个人资料 API：获取用户的昵称和头像、校验调用方提供的手机号
- 本地助理 API：查询 PC 端本地助理状态、发送消息和查询消息历史。
- 云端任务 API：创建、查询云端任务，并获取任务对应的 ACP 连接信息。
- ACP 通道：建立云端任务的实时双向通信通道，并进行协议消息交互。
- 会话产物：查询云端会话产生的计划、任务、媒体和总结等产物。
- 兑换码核销 API：通过兑换码或卡券为当前授权用户发放积分。

---



<a id="认证授权-api"></a>



## 认证授权 API



<a id="概述"></a>



### 概述

WorkBuddy 开放平台基于 OAuth 2.1 授权码流程实现第三方应用授权。开发者通过 `/authorize` 端点引导用户完成授权，使用授权码在 `/token` 端点换取访问凭证（`access_token`）和刷新凭证（`refresh_token`），后续调用 Open API 时使用 `access_token` 进行鉴权。

本章节包含两个核心端点：

- 「请求用户授权」— 引导用户在浏览器中完成授权
- 「换取访问凭证」— 用授权码或刷新凭证换 access_token



<a id="请求用户授权"></a>



### 请求用户授权

引导用户在浏览器中访问授权页面，用户确认后平台回调返回 Authorization Code。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | GET <https://www.workbuddy.cn/openapi/v2/authorize> |
| HTTP Method | GET（浏览器重定向） |
| 权限要求 | 无需 access_token；client_id 需为已注册应用 |



<a id="查询参数"></a>



#### 查询参数

| 名称 | 类型 | 必填 | 示例值 | 描述 |
| --- | --- | --- | --- | --- |
| response_type | String | 是 | code | 固定值 code，表示授权码模式 |
| client_id | String | 是 | app_7a3f2b... | 应用注册后获得的客户端 ID |
| redirect_uri | String | 是 | <https://example.com/callback> | 回调地址，需要与应用已绑定的回调地址一致 |
| scope | String | 否 | user.task.readable user.task.invokable | 请求的权限范围，多个 scope 以空格分隔。必须在应用已绑定的 Scope 集合内，不传则默认权限范围为应用注册绑定的权限集 |
| state | String | 建议 | a1b2c3_random_xyz | 随机字符串，用于防 CSRF 攻击和回调状态保持。回调时原样返回 |



<a id="请求示例"></a>



#### 请求示例



```
GET /openapi/v2/authorize?response_type=code&client_id=app_7a3f2b1c&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&scope=user.task.readable%20user.localassistant.readable&state=a1b2c3_random_xyz HTTP/1.1
Host: www.workbuddy.cn
Accept: text/html
```





<a id="回调响应"></a>



#### 回调响应

用户确认授权后，平台将重定向至 redirect_uri，携带以下参数：

| 名称 | 类型 | 示例值 | 描述 |
| --- | --- | --- | --- |
| code | String | auth_c0d3_xyz789 | 授权码，一次性使用，有效期 10 分钟 |
| state | String | a1b2c3_random_xyz | 与请求中的 state 一致。应用应校验该值以防范 CSRF 攻击 |



```
GET https://example.com/callback?code=auth_c0d3_xyz789&state=a1b2c3_random_xyz
```





<a id="换取-access-token"></a>



### 换取 Access Token

使用授权码换取 access_token

| 项目 | 内容 |
| --- | --- |
| HTTP URL | POST <https://www.workbuddy.cn/openapi/v2/token> |
| HTTP Method | POST |
| Content-Type | application/x-www-form-urlencoded |
| 权限要求 | 无（使用 client_secret 进行应用身份验证） |



<a id="请求体"></a>



#### 请求体

| 名称 | 类型 | 必填 | 示例值 | 描述 |
| --- | --- | --- | --- | --- |
| grant_type | String | 是 | authorization_code | 固定值 authorization_code |
| code | String | 是 | auth_c0d3_xyz789 | 上一步获取的授权码，一次性使用 |
| client_id | String | 是 | app_7a3f2b1c | 应用 ID |
| client_secret | String | 是 | sk_live_abc123... | 应用密钥，严禁在前端或客户端代码中暴露 |
| redirect_uri | String | 是 | <https://example.com/callback> | 必须与/authorize 获取授权码阶段回调地址参数完全一致（字节级） |



<a id="请求示例-1"></a>



#### 请求示例



```
POST /openapi/v2/token HTTP/1.1
Host: www.workbuddy.cn
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=AUTH_CODE_xxx&redirect_uri=https%3A%2F%2Fpartner.example.com%2Fcallback&client_id=cb_abc123&client_secret=YOUR_APP_SECRET
```





<a id="响应体"></a>



#### 响应体

| 名称 | 类型 | 示例值 | 描述 |
| --- | --- | --- | --- |
| access_token | String | eyJhbGciOiJSUzI1NiIs... | 访问令牌，用于调用 Open API |
| token_type | String | Bearer | 令牌类型，固定值 Bearer |
| expires_in | Number | 3600 | access_token 有效期，单位：秒 |
| refresh_token | String | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9… | 刷新令牌，用于在 access_token 过期后获取新令牌。仅在 authorization_code 模式下返回 |
| scope | String | user.profile.readable task.write | 实际授予的权限范围 |
| open_id | String | op_9f8e7d6c5b4a | 用户的open_id |



```json
{
  "access_token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type":"Bearer","expires_in":3600,
  "refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope":"user.profile.readable task.write",
  "open_id":"op_9f8e7d6c5b4a"
}
```





<a id="刷新-access-token"></a>



### 刷新 Access Token

使用refresh_token 刷新 access_token

| 项目 | 内容 |
| --- | --- |
| HTTP URL | POST <https://www.workbuddy.cn/openapi/v2/token> |
| HTTP Method | POST |
| Content-Type | application/x-www-form-urlencoded |
| 权限要求 | 无 |



<a id="请求体-1"></a>



#### 请求体

| 名称 | 类型 | 必填 | 示例值 | 描述 |
| --- | --- | --- | --- | --- |
| grant_type | String | 是 | refresh_token | 固定值 refresh_token |
| refresh_token | String | 是 | def50200a1b2... | 上一次获取的 refresh_token |
| client_id | String | 是 | app_7a3f2b1c | 应用 ID |
| client_secret | String | 是 | sk_live_abc123... | 应用密钥，严禁在前端或客户端代码中暴露 |



<a id="请求示例-2"></a>



#### 请求示例



```
POST /openapi/v2/token HTTP/1.1
Host: www.workbuddy.cn
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=refresh_token&refresh_token=wbjt_xxxxxxxxxxxxx&client_id=cb_xxxxxxxxxxxxx&client_secret=xxxxxxxxxxxxx
```





<a id="响应体-1"></a>



#### 响应体

| 名称 | 类型 | 示例值 | 描述 |
| --- | --- | --- | --- |
| access_token | String | eyJhbGciOiJSUzI1NiIs... | 访问令牌，用于调用 Open API |
| token_type | String | Bearer | 令牌类型，固定值 Bearer |
| expires_in | Number | 3600 | access_token 有效期，单位：秒 |
| refresh_token | String | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9… | 刷新令牌，用于在 access_token 过期后获取新令牌。仅在 authorization_code 模式下返回 |
| scope | String | user.profile.readable task.write | 实际授予的权限范围 |
| open_id | String | op_9f8e7d6c5b4a | 用户的open_id |



```json
{
  "access_token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type":"Bearer","expires_in":3600,
  "refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope":"user.profile.readable task.write",
  "open_id":"op_9f8e7d6c5b4a"
}
```





<a id="个人资料-api"></a>



## 个人资料 API



<a id="概述-1"></a>



### 概述

个人资料API



<a id="获取用户资料"></a>



### 获取用户资料

获取用户的昵称和头像

| 项目 | 内容 |
| --- | --- |
| HTTP URL | GET [https://www.workbuddy.cn/openapi/v2/user/profile](https://www.workbuddy.cn/openapi/v2/localassistant) |
| HTTP Method | GET |
| 权限要求 | user.profile.readable |



<a id="请求报文"></a>



#### 请求报文



```
GET /openapi/v2/user/profile HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer <access_token>
Accept: application/json
```





<a id="响应报文"></a>



#### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Cache-Control: private, no-store

{
"nickname": "张三",
"avatar": "https://example.com/avatar.png"
}
```





<a id="响应-data"></a>



#### 响应 data

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| nickname | String | 当前用户的昵称 |
| avatar | String | 当前用户的头像 |



<a id="验证用户联系方式"></a>



### 验证用户联系方式

验证调用方提供的手机号是否与当前授权用户绑定的个人手机号一致。接口只返回匹配结果，不会返回用户真实手机号或脱敏手机号。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | GET [https://www.workbuddy.cn/openapi/v2/user/phoneverification](https://www.workbuddy.cn/openapi/v2/localassistant) |
| HTTP Method | GET |
| 权限要求 | user.contact.readable |



<a id="请求报文-1"></a>



#### 请求报文



```
POST /openapi/v2/user/phoneverification HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json

{
"phone_number": "+8613812345678"
}

手机号格式要求：
- 中国大陆手机号支持 13812345678 或 +8613812345678。
- 支持空格、短横线和括号等常见分隔形式。
- 香港、澳门手机号必须明确携带 +852 或 +853。
- 不接受未携带国家码的 8 位号码，避免地区歧义。
```





<a id="响应报文-1"></a>



#### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{
"matched": true
}
```





<a id="响应-data-1"></a>



#### 响应 data

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| matched | Boolean | 手机号是否匹配 |

---



<a id="本地助理-api"></a>



## 本地助理 API



<a id="概述-2"></a>



### 概述

本地助理 API 用于与已连接 WorkBuddy 的 PC 端本地助理进行消息交互，包括查询在线状态、发送消息和查询消息历史。



<a id="查询本地助理在线状态"></a>



### 查询本地助理在线状态

查询当前用户的 PC 端本地助理是否在线。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | GET <https://www.workbuddy.cn/openapi/v2/localassistant> |
| HTTP Method | GET |
| 权限要求 | user.localassistant.readable |



<a id="请求报文-2"></a>



#### 请求报文



```
GET /openapi/v2/localassistant HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```





<a id="响应报文-2"></a>



#### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 74

{"code":0,"msg":"success","request_id":"a1b2c3d4e5","data":{"online":true}}
```





<a id="响应-data-2"></a>



#### 响应 data

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| online | bool | 当前用户的 PC 端本地助理是否在线 |



<a id="发送消息给本地助理"></a>



### 发送消息给本地助理

向 PC 端本地助理发送消息，触发助理执行任务。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | POST <https://www.workbuddy.cn/openapi/v2/localassistant/message> |
| HTTP Method | POST |
| 权限要求 | user.localassistant.invokable |
| Content-Type | application/json |



<a id="请求报文-3"></a>



#### 请求报文



```
POST /openapi/v2/localassistant/message HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept: application/json
Content-Length: 52

{"content":"帮我查一下今天的日程","msg_type":"text"}
```



回答 AskQuestion 时 content 仍是字符串，内部承载序列化 JSON：



```
POST /openapi/v2/localassistant/message HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept: application/json

{"content":"{\"outcome\":\"selected\",\"requestId\":\"chatcmpl-tool-eaa8e54c031f49ebaa16708e74f487b8\",\"answers\":{\"q_0\":\"来道单选\"}}","msg_type":"permission_response"}
```





<a id="请求-body"></a>



#### 请求 body

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| content | string | 是 | 消息内容。msg_type 为 text 时为普通文本，如"帮我查一下今天的日程"；msg_type 为 permission_response 时为序列化 JSON 字符串 |
| msg_type | string | 是 | 消息类型。允许 text（普通文本）与 permission_response（回答 AskQuestion / 工具审批）。permission_response 时 content 仍为字符串，内部 JSON 字段见下表 |



<a id="permissionresponse-的-content-json"></a>



#### permission_response 的 content JSON

注意：content 的类型仍然是字符串，内部承载序列化后的 JSON。

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| outcome | string | 是 | 选择结果。回答问卷时为 selected |
| requestId | string | 是 | 待回答的问卷或工具审批请求 ID，须与下行 permission 请求一致 |
| answers | object | 是 | 问卷答案。key 为 q_0、q_1…；单选值为字符串，多选值为字符串数组，例如 `{"q_0":"来道单选"}` |



<a id="响应报文-3"></a>



### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 87

{"code":0,"msg":"success","request_id":"a1b2c3d4e5","data":{"message_id":"msg-001"}}
```





<a id="响应-data-3"></a>



#### 响应 data

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| message_id | string | 新建消息的 ID，如 msg-001 |



<a id="查询本地助理消息历史"></a>



### 查询本地助理消息历史

查询当前用户本地助理的消息历史，支持分页查询和增量查询。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | GET <https://www.workbuddy.cn/openapi/v2/localassistant/message> |
| HTTP Method | GET |
| 权限要求 | user.localassistant.readable |



<a id="请求报文分页模式"></a>



#### 请求报文（分页模式）



```
GET /openapi/v2/localassistant/message?limit=20&offset=0 HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```





<a id="请求报文增量模式"></a>



#### 请求报文（增量模式）



```
GET /openapi/v2/localassistant/message?message_id=msg-001 HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```





<a id="查询参数-1"></a>



#### 查询参数

| 参数 | 类型 | 含义 |
| --- | --- | --- |
| limit | int | 分页模式：每页条数，默认 20，上限 100 |
| offset | int | 分页模式：偏移量，默认 0 |
| message_id | string | 增量模式：仅返回该消息之后产生的消息（用于轮询助理回复） |

传 message_id 时使用增量模式；不传时使用分页模式。



<a id="响应报文-4"></a>



#### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 396

{"code":0,"msg":"success","request_id":"a1b2c3d4e5","data":{"messages":[{"message_id":"msg-001","role":"user","content":["帮我查一下今天的日程"],"msg_type":"text","created_at":"2026-07-30T10:00:00Z","attachments":[],"metadata":{"msgType":"text"}},{"message_id":"msg-002","role":"assistant","content":["你今天有3个日程..."],"msg_type":"text","created_at":"2026-07-30T10:00:05Z","attachments":[],"metadata":{"msgType":"text"}}]}}
```





<a id="响应-data-4"></a>



#### 响应 data

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| messages | array | 消息列表 |



<a id="messages-单条消息元素"></a>



#### messages[] 单条消息元素

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| message_id | string | 消息 ID |
| role | string | 角色：user（用户）/ assistant（助理） |
| content | array | 消息内容，恒为数组（无值给 []，不省 key） |
| msg_type | string | 消息类型，从下游 metadata 的 msgType 提取 |
| created_at | string | 创建时间（ISO8601，如 2026-07-30T10:00:00Z） |
| attachments | array | 附件列表，恒为数组（无值给 []） |
| metadata | object | 元数据，恒为对象（无值给 {}） |

---



<a id="云端任务-api"></a>



## 云端任务 API



<a id="概述-3"></a>



### 概述

云端任务 API 用于创建和查询云端任务，并返回 ACP 连接地址和鉴权 token，以便与云端会话建立实时通信。



<a id="创建云端任务"></a>



### 创建云端任务

创建云端任务，支持与 WorkBuddy 移动端或小程序会话打通，返回 task_id、ACP link 和 token。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | POST <https://www.workbuddy.cn/openapi/v2/tasks> |
| HTTP Method | POST |
| 权限要求 | user.task.invokable |



<a id="请求报文-4"></a>



#### 请求报文



```
POST /openapi/v2/tasks HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "prompt": "帮我看下明天的天气如何",
  "name": "明天天气"
}
```





<a id="请求体-2"></a>



#### 请求体

| 参数 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| prompt | string | 是 | 任务的初始指令，用于创建会话、生成标题与初始状态 |
| name | string | 否 | 任务名称；不传由服务端按 prompt 生成 |



<a id="响应报文-5"></a>



#### 响应报文



```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "task_id": "2076261663968759808",
  "status": "working",
  "name": "明天天气",
  "link": "https://acp.workbuddy.cn/sessions/2076261663968759808",
  "token": "sk-sandbox-xxxxxxxxxxxxxxxxxxxx",
  "expire_at": 1786087200,
  "sandboxLink": "https://sandbox.example.com/e2b/abc123",
  "sandboxDataLink": "https://sandbox-data.example.com/e2b/abc123"
}
```





<a id="响应体-2"></a>



#### 响应体

| 字段 | 类型 | 必返 | 含义 |
| --- | --- | --- | --- |
| task_id | string | 是 | 任务 ID，实际对应 agentserver conversation ID |
| status | string | 是 | 任务/会话当前状态 |
| name | string | 否 | 任务或会话名称 |
| link | string | 否 | ACP 连接地址，用于连接任务沙箱 |
| token | string | 否 | ACP 网关鉴权凭据 |
| expire_at | integer | 否 | token 过期时间，Unix 秒级时间戳 |
| sandboxLink | string | 否 | 沙箱控制面访问地址 |
| sandboxDataLink | string | 否 | 沙箱数据面访问地址 |



<a id="status-字段枚举"></a>



#### status 字段枚举

| 状态 | 含义 |
| --- | --- |
| CREATING | 正在创建任务和沙箱 |
| idle | 空闲，等待执行 |
| planning | 正在规划 |
| working | 正在执行 |
| pending | 暂停或等待外部输入 |
| completed | 已完成 |
| failed | 执行失败 |
| archived | 已归档 |
| deleted | 已删除 |



<a id="查询云端任务列表"></a>



### 查询云端任务列表

查询当前用户创建的云端任务列表，支持分页查询。返回任务基本信息和 ACP Link，不返回 ACP Token 及其过期时间。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | GET <https://www.workbuddy.cn/openapi/v2/tasks> |
| HTTP Method | GET |
| 权限要求 | user.task.readable |



<a id="请求报文-5"></a>



#### 请求报文



```
GET /openapi/v2/tasks?page=1&size=20 HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```





<a id="查询参数-2"></a>



#### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 含义 |
| --- | --- | --- | --- | --- |
| page | integer | 否 | 1 | 页码；非整数或小于 1 时按 1 处理 |
| size | integer | 否 | 20 | 每页数量；非整数或小于 1 时按 20 处理，最大为 100，超过 100 时按 100 处理 |



<a id="响应报文-6"></a>



#### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "tasks": [
    {
      "task_id": "2076261663968759808",
      "status": "working",
      "name": "明天天气",
      "link": "https://acp.workbuddy.cn/sessions/2076261663968759808",
      "created_at": "2026-08-04T10:30:00Z",
      "updated_at": "2026-08-04T10:35:00Z"
    },
    {
      "task_id": "2076261663968759809",
      "status": "completed",
      "name": "日程整理",
      "link": "https://acp.workbuddy.cn/sessions/2076261663968759809",
      "created_at": "2026-08-03T08:00:00Z",
      "updated_at": "2026-08-03T09:00:00Z"
    }
  ],
  "total": 2,
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 2
  }
}
```





<a id="响应字段"></a>



#### 响应字段

| 字段 | 类型 | 必有 | 含义 |
| --- | --- | --- | --- |
| tasks | array | 是 | 当前分页的任务列表 |
| tasks[].task_id | string | 是 | 任务 ID，对应云端会话 ID |
| tasks[].status | string | 是 | 任务当前状态 |
| tasks[].name | string | 否 | 任务名称 |
| tasks[].link | string | 否 | ACP 直连地址 |
| tasks[].created_at | string | 否 | 创建时间，ISO 8601 格式 |
| tasks[].updated_at | string | 否 | 最后更新时间，ISO 8601 格式 |
| total | integer | 是 | 符合条件的任务总数 |
| pagination | object | 是 | 分页信息 |
| pagination.page | integer | 是 | 当前页码 |
| pagination.size | integer | 是 | 当前每页数量 |
| pagination.total | integer | 是 | 符合条件的任务总数 |

注意：列表接口不会返回 token 和 expire_at。如需获取任务的 ACP Token，请调用 GET /openapi/v2/tasks/{task_id}。



<a id="查询云端任务"></a>



### 查询云端任务

查询任务状态，并获取新的 ACP link/token。响应 200 OK。创建任务后若响应暂时没有 link 或 token，可轮询该接口直到补齐。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | GET [https://www.workbuddy.cn/openapi/v2/tasks/{task_id}](https://www.workbuddy.cn/openapi/v2/tasks/%7Btask_id%7D) |
| HTTP Method | GET |
| 权限要求 | user.task.readable |



<a id="请求报文-6"></a>



#### 请求报文



```
GET /openapi/v2/tasks/2076261663968759808 HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```





<a id="路径参数"></a>



#### 路径参数

| 参数 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| task_id | string | 是 | 创建任务时返回的 task_id |



<a id="响应报文-7"></a>



#### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "task_id": "2076261663968759808",
  "status": "working",
  "name": "明天天气",
  "link": "https://acp.workbuddy.cn/sessions/2076261663968759808",
  "token": "sk-sandbox-xxxxxxxxxxxxxxxxxxxx",
  "expire_at": 1786087200,
  "sandboxLink": "https://sandbox.example.com/e2b/abc123",
  "sandboxDataLink": "https://sandbox-data.example.com/e2b/abc123"
}
```





<a id="响应体-3"></a>



#### 响应体

| 字段 | 类型 | 必返 | 含义 |
| --- | --- | --- | --- |
| task_id | string | 是 | 任务 ID，实际对应 agentserver conversation ID |
| status | string | 是 | 任务/会话当前状态 |
| name | string | 否 | 任务或会话名称 |
| link | string | 否 | ACP 连接地址，用于连接任务沙箱 |
| token | string | 否 | ACP 网关鉴权凭据 |
| expire_at | integer | 否 | token 过期时间，Unix 秒级时间戳 |
| sandboxLink | string | 否 | 沙箱控制面访问地址 |
| sandboxDataLink | string | 否 | 沙箱数据面访问地址 |



<a id="status-字段枚举-1"></a>



#### status 字段枚举

| 状态 | 含义 |
| --- | --- |
| CREATING | 正在创建任务和沙箱 |
| idle | 空闲，等待执行 |
| planning | 正在规划 |
| working | 正在执行 |
| pending | 暂停或等待外部输入 |
| completed | 已完成 |
| failed | 执行失败 |
| archived | 已归档 |
| deleted | 已删除 |

---



<a id="acp-使用说明"></a>



### ACP 使用说明



<a id="发起对话"></a>



#### 发起对话

使用 ACP 通道发起对话；创建或查询任务拿到 link 与 token 后，通过它们与云端会话通信。ACP（Agent Client Protocol）基于 SSE 长连接 + JSON-RPC 2.0，采用双通道模型：一条 GET SSE 长连接用于接收服务端推送（流式回答、通知），POST 请求用于发送 JSON-RPC 调用，两者通过同一个连接标识关联。



<a id="建连与鉴权"></a>



#### 建连与鉴权

1. 接收通道：GET {link}，请求头带 Authorization: Bearer {token} 与 Accept: text/event-stream，建立一条 SSE 长连接用于接收服务端消息。响应头中的 Acp-Connection-Id 是本次连接的标识。
2. 发送通道：POST {link}，请求头带 Authorization: Bearer {token}、Content-Type: application/json，并回传 Acp-Connection-Id 以关联到上面的 SSE 连接；Body 为 JSON-RPC 请求。调用的返回结果（含流式回答）会通过 SSE 通道异步推回。
3. token：仅用于 ACP 通道鉴权，因 Agent 底层沙箱环境差异 token 有效期存在不同，通常为 3 天、不过也有可能很短，调用方如果遇到 ACP 的请求出现 401，可以使用 GET /tasks/{task_id} 获取新的 token。



<a id="对话流程json-rpc"></a>



#### 对话流程（JSON-RPC）

1. initialize：协商协议版本与客户端能力，建连后首先调用一次。
2. session/load：加载已创建的会话，params.sessionId 传创建任务返回的 task_id。
3. session/prompt：发送提问，params.prompt 为 ContentBlock 数组（每个元素含 type=text 与 text 字段，见下方示例）。追问时复用同一 sessionId 再次调用即可。

完整调用示例（建连后按顺序依次发送，返回结果与流式回答均通过 SSE 通道推回）：



```
// 1) initialize — 协商协议版本与客户端能力，建连后先调用一次
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": 1,
    "clientCapabilities": {
      "fs": { "readTextFile": false, "writeTextFile": false }
    }
  }
}

// 2) session/load — 加载已创建的会话，sessionId 传创建任务返回的 task_id
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "session/load",
  "params": {
    "sessionId": "2076261663968759808",
    "cwd": "/workspace",
    "mcpServers": []
  }
}

// 3) session/prompt — 发送提问，prompt 为 ContentBlock 数组；追问时复用同一 sessionId 再次调用
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "session/prompt",
  "params": {
    "sessionId": "2076261663968759808",
    "prompt": [{ "type": "text", "text": "帮我看下明天的天气如何" }]
  }
}
```





<a id="接收服务端消息"></a>



#### 接收服务端消息

服务端通过 SSE 通道回推两类 JSON-RPC 消息：

- Notification（无 id）：单向推送，用于流式回答、状态变化、扩展事件等，客户端不需要应答。
- Server-to-Client Request（有 id）：需要客户端在超时前通过 SSE 关联的 Acp-Connection-Id 回一条 response，用于需要用户参与的交互（工具授权确认、AskUserQuestion 等）。

| 类型 | 方法 | 用途 |
| --- | --- | --- |
| Notification | session/update | 流式增量：对话内容、工具调用、任务规划、会话状态 |
| Request（需应答） | session/request_permission | 需要用户交互的确认：工具执行授权、AskUserQuestion |
| Response（对 session/prompt） | — | 一轮 prompt 的最终结束标记：stopReason + usage |

任务完成判定：session/prompt 的 response 是"本轮结束"的权威信号；result.stopReason 表示结束原因（end_turn / max_tokens / max_turn_requests / refusal / cancelled）。



<a id="扩展方法说明"></a>



#### 扩展方法说明

除标准 ACP 方法外，服务端还会通过 SSE 通道下推以 _codebuddy.ai/ 为前缀的扩展 JSON-RPC notification，用于承载 ACP 标准协议未定义的会话资产（如产物、断点、命令等）。这些消息：

- 遵循 JSON-RPC 2.0 规范（无 id、无需应答）
- 客户端未识别的方法可安全忽略，不影响标准协议流程
- 不在 ACP 官方协议（[agentclientprotocol.com](http://agentclientprotocol.com)）中定义，是 WorkBuddy 云端对 ACP 的私有扩展

当前对接方最需要关注的扩展方法：

| 方法 | 用途 |
| --- | --- |
| _codebuddy.ai/artifact | 产物（计划 / 任务清单 / 媒体 / 总结）增量推送 |

产物 notification 示例：



```
{
  "jsonrpc": "2.0",
  "method": "_codebuddy.ai/artifact",
  "params": {
    "sessionId": "2076261663968759808",
    "event": "created",
    "artifact": {
      "type": "media",
      "uri": "agent:///artifacts/output.png",
      "mimeType": "image/png",
      "size": 102400
    }
  }
}
```



三种 event 值：

- created：新增产物，artifact 为完整对象。
- updated：产物变更，artifact 为完整对象（整体覆盖，非 diff）。
- deleted：产物移除，artifact 仅保证 type 与 uri 字段。

客户端应以 artifact.uri 为主键做本地 upsert / delete；重复收到 created 视为等价于 updated。



<a id="产物列表-api"></a>



#### 产物列表 API

SSE 通道推送的是增量事件；如需一次性获取会话内所有历史产物（如首屏渲染、状态恢复），可通过 REST 接口 GET /api/session/artifacts 拉取。SSE 与 REST 数据同源，二者可组合使用（首屏 REST 拉全量 + 后续 SSE 增量）。

| 项目 | 内容 |
| --- | --- |
| HTTP URL | GET {sandbox_url}/api/session/artifacts |
| 请求方法 | GET |
| 鉴权方式 | Header: Authorization: Bearer {task_ticket} |
| Content-Type | application/json |

其中 sandbox_url 由「创建云端任务」/「查询云端任务」接口返回的 link 字段去掉末尾 /acp 路径段得到。例如 link = "[https://65225-xxx.ap-guangzhou.agentos-run.net/acp"，则](https://65225-xxx.ap-guangzhou.agentos-run.net/acp%22%EF%BC%8C%E5%88%99) sandbox_url = "[https://65225-xxx.ap-guangzhou.agentos-run.net"。](https://65225-xxx.ap-guangzhou.agentos-run.net%22%E3%80%82)

鉴权凭证 task_ticket 与 ACP 通道共用同一份；task_ticket 过期返回 HTTP 401，此时调用「查询云端任务」接口换取新的 task_ticket 后重试。



<a id="查询参数-3"></a>



##### 查询参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| sessionId | string | 否 | 目标会话 ID。单 session 沙箱可省略（自动使用当前活跃会话）；多 session 场景必填。 |
| type | string | 否 | 按产物类型过滤，允许值：plan / tasks / media / overview。省略则返回全部类型。 |
| startMs | int64 | 否 | 仅返回 updatedAt >= startMs 的记录（epoch 毫秒）。省略或 0 表示不限下界。 |
| endMs | int64 | 否 | 仅返回 updatedAt <= endMs 的记录（epoch 毫秒）。省略或 0 表示不限上界。 |
| limit | int | 否 | 分页大小，取值 [1, 500]。省略或 0 表示不分页，一次返回全部。 |
| offset | int | 否 | 分页偏移，取值 >= 0，默认 0。 |



<a id="请求示例-3"></a>



##### 请求示例



```
# 拉取当前会话的全部产物
curl -H "Authorization: Bearer {task_ticket}" \
     "{sandbox_url}/api/session/artifacts"

# 仅拉取媒体类产物，分页
curl -H "Authorization: Bearer {task_ticket}" \
     "{sandbox_url}/api/session/artifacts?type=media&limit=50&offset=0"

# 增量拉取（配合本地记录的 lastUpdatedAt）
curl -H "Authorization: Bearer {task_ticket}" \
     "{sandbox_url}/api/session/artifacts?startMs=1730000000000"
```





<a id="响应报文-8"></a>



##### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 0,
  "msg": "success",
  "data": {
    "sessionId": "2076261663968759808",
    "artifacts": [
      {
        "sessionId": "2076261663968759808",
        "event": "created",
        "artifact": { /* Artifact 对象，见下方字段说明 */ },
        "md5": "3f2a...",
        "url": "https://.../artifacts/output.png"
      }
    ],
    "pagination": {
      "total": 123,
      "returned": 50,
      "limit": 50,
      "offset": 0,
      "hasMore": true
    },
    "filter": { "type": "media", "startMs": 0, "endMs": 0 }
  }
}
```





<a id="响应字段顶层"></a>



##### 响应字段（顶层）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 业务状态码，0 表示成功。 |
| msg | string | 业务状态描述。 |
| data.sessionId | string | 本次查询命中的会话 ID。 |
| data.artifacts | array | 产物记录数组，元素为 Entry。 |
| data.pagination | object | 分页信息。 |
| data.filter | object | 本次请求生效的过滤条件（回显）。 |



<a id="entry-字段dataartifacts"></a>



##### Entry 字段（data.artifacts[]）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| sessionId | string | 所属会话 ID。 |
| event | string | 产物最近一次变更事件，取值 created / updated / deleted。 |
| artifact | object | 产物本体（结构见下方 Artifact 字段）。 |
| md5 | string | 产物内容 md5（可选，用于去重/秒传）。 |
| url | string | 媒体类产物的直接访问 URL（可选，仅 artifact.type = media 时返回）。 |



<a id="artifact-公共字段"></a>



##### Artifact 公共字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| type | string | 判别式，取值 plan / tasks / media / overview。 |
| uri | string | 产物唯一标识。云端形如 agent:///artifacts/plan.md，本地形如 file:///…。跨消息以此为主键。 |
| name | string | 资源名（如文件名）。 |
| title | string | 显示标题。 |
| description | string | 描述文本。 |
| mimeType | string | MIME 类型。 |
| createdAt | int64 | 创建时间（epoch 毫秒）。 |
| updatedAt | int64 | 最近更新时间（epoch 毫秒）。 |



<a id="artifact-分类型字段"></a>



##### Artifact 分类型字段

type = plan（计划文档，Markdown）：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| text | string | 当前 Markdown 全文。 |
| version | int | 版本号（每次更新递增）。 |
| previousText | string | 上一版全文，可用于展示 diff。 |
| enableEdit | bool | 是否允许前端编辑回写。 |



<a id="type-tasks任务清单"></a>



##### type = tasks（任务清单）：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| tasks | array | 任务数组，元素含 id / content / status（pending / in_progress / completed / cancelled）/ order。 |
| enableEdit | bool | 是否允许前端编辑回写。 |



<a id="type-media媒体文件"></a>



##### type = media（媒体文件）：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| mimeType | string | 文件 MIME 类型，如 image/png / video/mp4 / audio/mpeg。 |
| size | int64 | 文件字节数。 |
| contentType | string | 粗分类：image / video / audio / document 等。 |
| width | int | 图片 / 视频宽度（像素）。 |
| height | int | 图片 / 视频高度（像素）。 |

媒体文件的下载：优先使用 Entry 层的 url 字段；若未提供，可将 uri 中的 agent:/// 替换为 {sandbox_url}/ 后请求（复用同一份 task_ticket 鉴权）。



<a id="type-overview任务总结markdown"></a>



##### type = overview（任务总结，Markdown）：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| text | string | 总结 Markdown 全文。 |



<a id="错误响应"></a>



##### 错误响应

| HTTP | code | 典型场景与说明 |
| --- | --- | --- |
| 200 | 0 | 成功。 |
| 400 | 1 | 参数非法。典型消息：sessionId is required（多 session 未指定）；invalid type（超出白名单）；startMs / endMs / limit / offset 越界或类型错误。 |
| 401 | — | task_ticket 缺失、无效或已过期。调用「查询云端任务」接口换新后重试。 |
| 404 | 1 | 会话不存在（会话已结束或 sessionId 错误）。 |

错误响应体格式：



```
{
  "code": 1,
  "msg": "invalid type: xxx (allowed: plan|tasks|media|overview)"
}
```





<a id="使用建议"></a>



##### 使用建议

- 首屏渲染：进入会话时调用一次 REST 接口拉取全量产物，按 artifact.uri 建立本地索引。
- 增量更新：订阅 SSE _codebuddy.ai/artifact 通知，按 event 对本地索引执行 upsert / delete。
- 会话恢复：REST 首屏 + SSE 增量的组合天然幂等，无需专门实现"恢复分支"，同 uri 直接覆盖即可。

---



<a id="核销兑换码-api"></a>



## 核销兑换码 API



<a id="概述-4"></a>



### 概述

通过核销兑换码或卡券，为当前授权用户发放积分（credits）。接口支持单码模式和双码模式。



<a id="核销兑换码"></a>



### 核销兑换码

| 项目 | 内容 |
| --- | --- |
| HTTP URL | POST <https://www.workbuddy.cn/openapi/v2/redemptions> |
| HTTP Method | POST |
| 权限要求 | user.credit.exchange |
| Content-Type | application/json |



<a id="请求报文场景-a兑换码"></a>



#### 请求报文（场景 A：兑换码）



```
POST /openapi/v2/redemptions HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept: application/json
Content-Length: 78

{"code":"CODE-OPER-8888","request_id":"550e8400-e29b-41d4-a716-446655440000"}
```





<a id="请求报文场景-b提货券"></a>



#### 请求报文（场景 B：提货券）



```
POST /openapi/v2/redemptions HTTP/1.1
Host: www.workbuddy.cn
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept: application/json
Content-Length: 102

{"gift_key":"GK-000001","gift_code":"CODE-XXX","request_id":"550e8400-e29b-41d4-a716-446655440000"}
```





<a id="请求-body-1"></a>



#### 请求 body

| 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| code | string | 单码模式必填 | 运营平台兑换码，如 CODE-OPER-8888；1-64 字符 |
| gift_key | string | 双码模式必填 | 云平台卡号（卡 key），如 GK-000001；6-64 字符 |
| gift_code | string | 双码模式必填 | 云平台卡密；8-64 字符 |
| request_id | string | 是 | 幂等/防重请求号，长度 8-64（示例为 UUID） |



<a id="响应报文-9"></a>



#### 响应报文



```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 158

{"status":"success","flow_no":"flow-2026072912345","credits":100,"open_id":"pairwise-open-id-xxx"}
```





<a id="响应字段-1"></a>



#### 响应字段

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| status | string | 核销结果状态，如 success |
| flow_no | string | 核销流水号，如 flow-2026072912345 |
| credits | int64 | 本次核销发放的积分 |
| open_id | string | 领取用户的 open_id（pairwise，按应用维度隔离） |

返回码

| 状态码 | 说明 |
| --- | --- |
| 200 | 核销成功 |



<a id="返回码规范"></a>



## 返回码规范

所有 Open API 遵循统一的返回码规范。调用接口出现异常时，可根据 HTTP 状态码、业务码和排查建议定位问题。

| HTTP 状态码 | 业务码 | 描述 | 排查建议 |
| --- | --- | --- | --- |
| 200 | success | 请求成功 | 暂无 |
| 201 | success | 请求成功 | 暂无 |
| 400 | invalid_request | 请求参数错误（缺参/格式非法/body 解析失败/参数越权组合） | 确认传入的参数是否合法、必填是否补齐 |
| 400 | unsupported_grant_type | 不支持的 grant_type | 使用受支持的 grant_type |
| 400 | unsupported_response_type | response_type 非 code | 固定使用 response_type=code |
| 400 | invalid_grant | 授权码/refresh_token 失效或不匹配；核销码已用/过期/耗尽 | 重新走授权流换新码；核销类视为终态勿重试 |
| 400 | invalid_scope | 应用无绑定 scope 或请求 scope 越权 | 给应用绑定 scope，请求 scope 收敛到绑定集内 |
| 400 | authorization_pending | 设备授权轮询中，用户尚未操作 | 按 interval 正常轮询等待 |
| 400 | slow_down | 设备授权轮询过快 | 轮询间隔增加 5 秒后再试 |
| 400 | expired_token | device_code 过期/已消费 | 重新发起 device_auth 获取新 device_code |
| 401 | invalid_token | 鉴权未通过（缺 Bearer / 验签失败 / 缺 subject·client） | 确认鉴权三元组合法有效、token 未过期 |
| 401 | invalid_client | 应用凭据无效或状态非 active | 核对 client_id/client_secret 及应用状态 |
| 401 | unauthorized_client | 应用状态非 active（device_auth 场景） | 确认应用已启用 |
| 401 | Unauthorized | paysign 缺登录态（uid 为空） | 确认已登录并带上有效登录态 |
| 403 | access_denied | 不允许访问该资源（未授权 / 应用非 active / 下游 403） | 确认是否拥有合法权限、用户已授权该应用 |
| 403 | insufficient_scope | token scope 不满足端点要求 | 按 WWW-Authenticate 提示补足 scope |
| 403 | forbidden | LocalAssistant 身份缺失或下游 401/403 | 检查 token；确已授权仍 403 则带 request_id 反馈 |
| 403 | PermissionDenied | paysign 的 X-Service-Id 不在白名单 | 使用已登记的 X-Service-Id 或联系平台加白 |
| 404 | not_found / not found | 访问的资源不存在（应用/会话/批次/兑换码/消息） | 确认资源标识正确、未被删除 |
| 409 | invalid_request | 资源状态冲突（device user_code 已处理，防重复） | 该请求已处理，勿重复提交 |
| 412 | invalid_request | 前置条件不满足（scene=client 但用户无 active 授权） | 先完成用户对应用的授权再取 code |
| 429 | rate_limited | 请求数超过限制，收到 429 时按指数退避重试（1s → 2s → 4s） | 请求超频，降低调用频率、退避重试 |
| 500 | server_error / server error / InternalServerError | 服务内部错误 | 服务端错误，携带 request_id 联系开发者 |
| 502 | server error | LocalAssistant 下游异常（非 401/403/404） | 服务端/下游问题，重试并反馈 request_id |
| 503 | server_error / temporarily unavailable / InternalServerError | 服务处于不可用状态（依赖客户端未配置 / 业务暂不可用） | 服务端配置缺失或临时不可用，联系开发者 |

---
