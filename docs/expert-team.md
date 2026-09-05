---
title: "专家团"
source_url: "https://open.workbuddy.cn/docs/expert-team"
source_type: "official-mirror"
group: "开发"
fetched_at: "2026-09-05T08:48:20+00:00"
official_updated_at: null
source_sha256: "d060471a47f09f7a94b87832147d8c0c6b9e8280822931d9e6df1433aeb3c432"
tags: ["workbuddy", "official", "expert-team"]
---

> 官方文档镜像 · [原文](https://open.workbuddy.cn/docs/expert-team) · [文档目录](../wiki/index.md) · [开发路线](../wiki/development-map.md)

<a id="专家团"></a>



# 专家团



<a id="基础结构"></a>



## 基础结构



```
my-team/
├── .codebuddy-plugin/
│   └── plugin.json              # ★ 配置文件（必须）
├── avatars/                     # ★ 头像目录（必须）
│   ├── team.png                 #    团队头像
│   ├── team-lead.png            #    主理人头像
│   ├── member-a.png             #    成员头像
│   └── member-b.png             #    成员头像
├── agents/                      # ★ Agent 定义（必须）
│   ├── {team}-team-lead.md      #    主理人（名称须加专家团前缀，不可用通用 team-lead）
│   ├── member-a.md              #    成员 A
│   └── member-b.md              #    成员 B
├── skills/                      #    共享技能（可选）
│   └── {skill-name}/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── templates/
├── .mcp.json                    #    内置 MCP / 连接器依赖声明（可选，见第六节）
├── bin/                         #    可执行文件（可选）
├── settings.json                # ★ 设置主理人（必须）
└── README.md                    #    说明文档（推荐）
```





<a id="配置文件"></a>



## 配置文件

plugin.json 是专家团的核心配置文件，包含运行配置和市场展示信息。



<a id="示例"></a>



### 示例



```
{
  "name": "trading-agent",
  "version": "1.0.0",
  "description": "13 specialized roles collaborate across 5 phases for stock investment analysis",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "agents": [
    "./agents/trading-team-lead.md",
    "./agents/market-analyst.md",
    "./agents/fundamentals-analyst.md",
    "./agents/news-analyst.md",
    "./agents/sentiment-analyst.md",
    "./agents/bull-researcher.md",
    "./agents/bear-researcher.md",
    "./agents/research-manager.md",
    "./agents/trader.md",
    "./agents/aggressive-risk-analyst.md",
    "./agents/conservative-risk-analyst.md",
    "./agents/neutral-risk-analyst.md",
    "./agents/risk-manager.md"
  ],
 
  "expertType": "team",
  "agentName": "trading-team-lead",
  "teamInfo": {
    "leadAgent": "trading-team-lead",
    "memberAgents": [
      "market-analyst", "fundamentals-analyst", "news-analyst", "sentiment-analyst",
      "bull-researcher", "bear-researcher", "research-manager", "trader",
      "aggressive-risk-analyst", "conservative-risk-analyst", "neutral-risk-analyst", "risk-manager"
    ]
  },
 
  "displayName": { "en": "Trading Analysis Team", "zh": "交易分析团队" },
  "profession": { "en": "A-Share / HK / US Stock Investment Analysis Team", "zh": "A股/港股/美股投资分析团队" },
  "displayDescription": {
    "en": "13 specialized roles collaborate across 5 phases: technical, fundamental, news & sentiment analysis → bull-bear debate → trading decision → 3-way risk assessment → final report, delivering BUY/SELL/HOLD recommendations with actionable plans",
    "zh": "13位专业角色分5阶段协作完成投资分析：技术面、基本面、新闻面、情绪面数据采集 → 多空辩论 → 交易决策 → 三方风险评估 → 最终报告，输出 BUY/SELL/HOLD 建议及完整操作方案"
  },
  "avatar": "avatars/team.png",
  "categoryId": "08-FinanceInvestment",
  "defaultInitPrompt": {
    "zh": "帮我分析下XX股票该不该买",
    "en": "Should I buy Maotai? Please analyze."
  },
  "plugin": "trading-agent",
  "tags": [
    { "en": "Stock Analysis", "zh": "股票分析" },
    { "en": "Investment", "zh": "投资决策" },
    { "en": "Risk Assessment", "zh": "风险评估" },
    { "en": "Bull-Bear Debate", "zh": "多空辩论" }
  ],
  "quickPrompts": [
    { "en": "Should I buy Maotai?", "zh": "帮我分析下XX该不该买" },
    { "en": "Analyze Tesla stock", "zh": "帮我分析XX的投资价值" },
    { "en": "Review my portfolio risk", "zh": "评估下我的持仓风险" }
  ],
  "members": [
    { "id": "trading-team-lead", "name": {"en":"Captain","zh":"队长"}, "profession": {"en":"Team Lead & Orchestrator","zh":"主理人"}, "avatar": "avatars/team-lead.png", "role": "lead" },
    { "id": "market-analyst", "name": {"en":"Marco","zh":"Marco"}, "profession": {"en":"Technical Analyst","zh":"技术分析师"}, "avatar": "avatars/market-analyst.png", "role": "member" },
    { "id": "fundamentals-analyst", "name": {"en":"Fiona","zh":"Fiona"}, "profession": {"en":"Fundamentals Analyst","zh":"基本面分析师"}, "avatar": "avatars/fundamentals-analyst.png", "role": "member" },
    { "id": "news-analyst", "name": {"en":"Nina","zh":"Nina"}, "profession": {"en":"News Analyst","zh":"新闻分析师"}, "avatar": "avatars/news-analyst.png", "role": "member" },
    { "id": "sentiment-analyst", "name": {"en":"Stella","zh":"Stella"}, "profession": {"en":"Sentiment Analyst","zh":"情绪分析师"}, "avatar": "avatars/sentiment-analyst.png", "role": "member" },
    { "id": "bull-researcher", "name": {"en":"Bruno","zh":"Bruno"}, "profession": {"en":"Bull Researcher","zh":"多头研究员"}, "avatar": "avatars/bull-researcher.png", "role": "member" },
    { "id": "bear-researcher", "name": {"en":"Barry","zh":"Barry"}, "profession": {"en":"Bear Researcher","zh":"空头研究员"}, "avatar": "avatars/bear-researcher.png", "role": "member" },
    { "id": "research-manager", "name": {"en":"Reed","zh":"Reed"}, "profession": {"en":"Research Manager","zh":"研究主管"}, "avatar": "avatars/research-manager.png", "role": "member" },
    { "id": "trader", "name": {"en":"Tyler","zh":"Tyler"}, "profession": {"en":"Trader","zh":"交易员"}, "avatar": "avatars/trader.png", "role": "member" },
    { "id": "aggressive-risk-analyst", "name": {"en":"Aiden","zh":"Aiden"}, "profession": {"en":"Aggressive Risk Analyst","zh":"激进风险分析师"}, "avatar": "avatars/aggressive-risk-analyst.png", "role": "member" },
    { "id": "conservative-risk-analyst", "name": {"en":"Clara","zh":"Clara"}, "profession": {"en":"Conservative Risk Analyst","zh":"保守风险分析师"}, "avatar": "avatars/conservative-risk-analyst.png", "role": "member" },
    { "id": "neutral-risk-analyst", "name": {"en":"Noel","zh":"Noel"}, "profession": {"en":"Neutral Risk Analyst","zh":"中性风险分析师"}, "avatar": "avatars/neutral-risk-analyst.png", "role": "member" },
    { "id": "risk-manager", "name": {"en":"Rex","zh":"Rex"}, "profession": {"en":"Risk Manager","zh":"风险主管"}, "avatar": "avatars/risk-manager.png", "role": "member" }
  ]
}
```





<a id="字段说明"></a>



### 字段说明



<a id="基础字段"></a>



#### 基础字段

| **字段** | **必填** | **类型** | **说明** |
| --- | --- | --- | --- |
| name | ✅ | string | 专家唯一标识（小写字母 + 连字符，如 "design-experts"） |
| expertType | ✅ | string | 填"team" |
| version | ✅ | string | 版本号（语义化版本，如 "1.0.0"） |
| description | ✅ | string | 英文简短描述（一句话） |
| author | ✅ | object | {name, email} 作者信息 |
| agents | ✅ | string[] | Agent 定义文件路径列表（如 ["./agents/my-expert.md"]） |
| agentName | ✅ | string | 主Agent 的名称（对应 agents/ 下的 MD 文件名，不含 .md） |
| teamInfo | ✅ | object | 见下方 |
| skills | 否 | string[] | 技能目录路径列表（如 ["./skills/my-skill"]） |
| homepage | 否 | string | 项目主页 URL |
| license | 否 | string | 许可证 |
| keywords | 否 | string[] | 搜索标签 |

**teamInfo 结构**：



```
{
  "leadAgent": "主 Agent 名称",
  "memberAgents": ["成员A名称", "成员B名称", "..."]
}
```





<a id="展示字段"></a>



#### 展示字段

| **字段** | **必填** | **类型** | **说明** |
| --- | --- | --- | --- |
| displayName | ✅ | {en, zh} | 市场展示名称 |
| profession | ✅ | {en, zh} | 职业头衔：必须与 displayName 保持一致 |
| displayDescription | ✅ | {en, zh} | 市场展示描述：中文字数须在 40-50 字之间，突出专家团的核心能力 |
| avatar | ✅ | string | 头像路径（相对路径，如 "avatars/expert.png"） |
| categoryId | ✅ | string | 行业分类 |
| defaultInitPrompt | ✅ | {en, zh} | 用户首次对话时的默认提示语。必须与 quickPrompts 的第一条保持一致 |
| plugin | ✅ | string | 关联的 Plugin 名称（与 name 字段值一致） |
| tags | ✅ | {en, zh}[] | 专家擅长领域标签（固定 3 个），用于搜索和市场展示 |
| quickPrompts | ✅ | {en, zh}[] | 推荐提示词（固定 3 个），展示在专家卡片上引导用户快速提问 |



<a id="专家团成员字段"></a>



#### 专家团成员字段

| **字段** | **必填** | **类型** | **说明** |
| --- | --- | --- | --- |
| members | ✅ | array | 所有团队成员列表（含主理人） |

每个成员对象：

| **字段** | **必填** | **类型** | **说明** |
| --- | --- | --- | --- |
| id | ✅ | string | 成员标识（对应 Agent MD 文件名，不含 .md） |
| name | ✅ | {en, zh} | 成员名称 |
| profession | ✅ | {en, zh} | 成员职业头衔 |
| avatar | ✅ | string | 成员头像路径 |
| role | ✅ | string | "lead"（主理人）或 "member"（成员） |



<a id="agent定义文件"></a>



## Agent定义文件



<a id="主agent示例文件"></a>



### 主Agent示例文件



```
---
name: trading-team-lead
description: Trading analysis team lead - orchestrates 5-phase investment analysis workflow
displayName:
  en: "He"
  zh: "何执舟"
profession:
  en: "Chief Strategist"
  zh: "首席策略官"
maxTurns: 200
---
 
# 交易分析团队 - 主理人
 
你是交易分析专家团的主理人，负责协调 12 位专业角色按照标准流程完成投资分析。
 
**你不直接做投资分析**，而是：
1. 确认分析目标（标的、分析深度）
2. 按阶段调度成员执行
3. 收集各成员产出，传递给下一阶段
4. 整合最终报告
 
## 团队协作机制（铁律）
 
你必须走正式的**团队协作流程**，严禁简化或跳过：
 
1. **建立团队**：任务开始时由主理人亲自创建本次任务的团队（建议命名 `trading-<标的简称>`），明确本次协作的边界与上下文。**团队创建（TeamCreate）必须且只能由主理人执行，严禁委派任何成员创建团队**
2. **调度成员**：按 SOP 阶段将每位团队成员拉入协作、下发独立任务；团队成员作为独立协作方基于分析任务输出专业产出，不得由主理人代写
3. **消息中转**：成员的产出需回传给你，由你汇总、转交给下一阶段成员；所有跨成员的信息流必须经主理人中转，不得互相直连
4. **成员结论为准**：任何专业产出（技术分析/财报分析/多空论证/风险诊断/交易决策）必须由对应成员输出后再采信，主理人只做编排与汇编
 
### 严禁行为
- ❌ 禁止跳过"建立团队"的正式流程，直接自己模拟成员发言或并行写出多角色内容
- ❌ 禁止自己代写任何团队成员的专业产出
- ❌ 禁止未完成前序阶段就跳到后续阶段
- ❌ 禁止让成员互相直连通信，所有跨成员信息流必须经主理人中转
- ❌ 禁止 spawn 主理人自己
 
## 团队成员
 
### 数据采集组
| 成员 | 名字 | 职责 |
|------|------|------|
| market-analyst | Marco | 技术分析：K线形态、均线系统、量价关系、技术指标 |
| fundamentals-analyst | Fiona | 基本面分析：财报分析、估值模型、行业对比 |
| news-analyst | Nina | 新闻分析：政策新闻、行业动态、公司公告 |
| sentiment-analyst | Stella | 情绪分析：市场情绪指标、资金流向、社交媒体舆情 |
 
### 研究辩论组
| 成员 | 名字 | 职责 |
|------|------|------|
| bull-researcher | Bruno | 多头研究：寻找看涨论据 |
| bear-researcher | Barry | 空头研究：寻找看跌论据 |
| research-manager | Reed | 研究主管：综合多空观点，形成研究结论 |
 
### 交易决策组
| 成员 | 名字 | 职责 |
|------|------|------|
| trader | Tyler | 交易员：制定具体交易计划（入场点、止损、止盈、仓位） |
 
### 风险评估组
| 成员 | 名字 | 职责 |
|------|------|------|
| aggressive-risk-analyst | Aiden | 激进风险分析：评估激进策略的风险收益 |
| conservative-risk-analyst | Clara | 保守风险分析：评估保守策略的风险收益 |
| neutral-risk-analyst | Noel | 中性风险分析：评估中性策略的风险收益 |
| risk-manager | Rex | 风险主管：综合三方风险评估，给出最终风控建议 |
 
## 标准工作流程（SOP）
 
### Phase 1: 数据采集
并行调用 market-analyst、fundamentals-analyst、news-analyst、sentiment-analyst。
 
### Phase 2: 多空辩论
调用 bull-researcher 和 bear-researcher，然后调用 research-manager 综合观点。
 
### Phase 3: 交易决策
调用 trader，基于研究结论制定具体交易计划。
 
### Phase 4: 风险评估
并行调用三方风险分析师，然后调用 risk-manager 综合评估。
 
### Phase 5: 最终报告
综合所有分析结果，输出 BUY/SELL/HOLD 建议及完整操作方案。
 
## 协作规则
1. **正式团队协作流程**：所有成员调度必须经过"建立团队 → 调度成员 → 成员回传"流程
2. **信息传递**：每阶段结束后，将完整产出原文传递给下一阶段成员
3. **进度通报**：每完成一个阶段向用户简要通报
4. **语言一致**：所有输出使用与用户原始需求相同的语言
5. **子任务命名**：调度每位成员时，在 Agent 工具的 `name` 参数中传入该成员的角色名称（中文）
6. **决策果断**：研究主管和风险主管必须给出明确 Buy/Sell/Hold，不得以"双方都有道理"为由默认 Hold
```





<a id="成员agent示例"></a>



### 成员Agent示例

agents/market-analyst.md：



```
---
name: market-analyst
description: Technical analyst - analyzes charts, indicators, and price patterns
displayName:
  en: "Marco"
  zh: "Marco"
profession:
  en: "Technical Analyst"
  zh: "技术分析师"
maxTurns: 50
---
 
# 技术分析师 - Marco
 
你是一位经验丰富的技术分析师，擅长通过图表和技术指标分析股票走势。
 
## 分析维度
1. **K线形态**：识别头肩顶/底、双顶/底、三角形、旗形等
2. **均线系统**：MA5/10/20/60/120/250 的排列关系和金叉死叉
3. **量价关系**：成交量配合价格走势的背离或确认
4. **技术指标**：MACD、RSI、KDJ、布林带等
 
## 输出格式
- 当前趋势判断（上升/下降/震荡）
- 关键支撑位和压力位
- 技术指标信号汇总
- 技术面综合评分（1-10）
- 短期/中期/长期技术展望
```





<a id="关于工具"></a>



### 关于工具

开发者不可自行添加 tools：所有工具权限由系统统一分配。

系统内置工具（仅供了解，由系统自动分配）：

| **工具** | **说明** |
| --- | --- |
| Read | 读取文件 |
| Write | 写入文件 |
| Grep | 搜索文件内容 |
| Glob | 按模式查找文件 |
| Bash | 执行命令行命令 |
| WebSearch | 搜索互联网 |
| WebFetch | 获取网页内容 |
| AgentTool | 调用其他 Agent（主Agent可用） |
| SendMessage | 发送消息（主Agent可用） |



<a id="内置-mcp-与连接器依赖可选"></a>



## 内置 MCP 与连接器依赖（可选）

专家可以声明它运行时依赖的 MCP 服务或 WorkBuddy 已有连接器。声明后，用户在召唤该专家（或专家团）前，WorkBuddy 会弹出内联引导卡片，逐个引导用户完成连接；连接完成后才进入对话。专家内置的 MCP 在连接后会统一在「连接器 → 自定义连接器」中管理。

简单专家不需要依赖声明。只有当专家必须调用外部 MCP 工具或企业连接器才能工作时，才声明依赖。



<a id="声明方式"></a>



### 声明方式

依赖通过 plugin.json 的 dependencies 字段声明，或放在插件根目录的 .mcp.json 文件中。

方式一：plugin.json 内声明（推荐）



```
{
  "dependencies": {
    "mcpServers": "./.mcp.json",
    "connectors": ["tencent-docs", "feishu"]
  }
}
```



| **字段** | **类型** | **说明** |
| --- | --- | --- |
| dependencies.mcpServers | string | string[] |
| dependencies.connectors | string[] | 依赖的 WorkBuddy 已有连接器 ID 列表（如 "tencent-docs"） |

**方式二：插件根目录 .mcp.json 文件**

当 plugin.json 未声明 dependencies.mcpServers 时，系统会自动读取插件根目录下的 .mcp.json 作为兜底。文件格式与标准 MCP 配置一致，每个 server 下可附加 x-workbuddy 元信息（见 6.3）：



```
{
  "mcpServers": {
    "huijin-workflow": {
      "url": "https://huijin-workflow.mcp.example.com",
      "x-workbuddy": {
        "displayName": { "zh": "汇金流程 MCP", "en": "Huijin Workflow MCP" },
        "description": { "zh": "连接后可查询流程列表、待办流程单并创建流程单。", "en": "..." },
        "icon": "./avatars/huijin.svg",
        "auth": { "type": "oauth" }
      }
    }
  }
}
```





<a id="mcp-服务配置"></a>



### MCP 服务配置

mcpServers 下每个 server 的基础字段遵循标准 MCP 协议：

| 字段 | 说明 |
| --- | --- |
| url | 远程 MCP（SSE / Streamable HTTP）服务地址 |
| type | 传输类型，如 "http"；远程 SSE 可省略 |
| headers | 请求头。Token 类型鉴权时在此用 ${VAR} 占位（见 6.4），如 { "Authorization": "Bearer ${SIYUAN_TOKEN}" } |
| x-workbuddy | WorkBuddy 私有展示与鉴权元信息（见 6.3），不会写入用户最终的连接器配置 |



<a id="x-workbuddy-元信息"></a>



### x-workbuddy 元信息

x-workbuddy 描述这个 MCP 在引导卡片上如何展示、以何种方式鉴权。所有文案字段支持中英双语。

| **字段** | **类型** | **说明** |
| --- | --- | --- |
| displayName | LocalizedString | 卡片标题展示名称。不填时回退到 server 名 |
| description | LocalizedString | 卡片描述文案。不填时回退到 url |
| icon | string | 卡片图标。支持网络地址（https://）、data: URL，或相对插件根目录的本地路径（如 "./avatars/xxx.svg"，推荐放在 avatars/）。设置 icon 后头像背景透明；不设置则用展示名首字符 + 散列底色生成占位 |
| auth.type | string | 鉴权方式："oauth" / "token" / "none" |
| auth.tokenSchema | object | 当 auth.type 为 "token" 时，描述需要用户填写的凭据表单（见 6.4） |

LocalizedString 约定：所有文案字段可写纯字符串或 { zh, en } 双语对象。写双语对象时，WorkBuddy 按用户当前界面语言展示，缺失语言回退 zh → en；写纯字符串则中英文环境一致展示。该约定与专家 displayName / profession 完全一致。



<a id="token-类型鉴权"></a>



### Token 类型鉴权

当 MCP 需要用户提供 API Token / Key 才能连接时，用 auth.type: "token" + tokenSchema 声明一个表单。用户点击「连接」时会弹出统一的 Token 授权弹窗，填写后系统将值回填到 headers 中的 ${VAR} 占位并完成连接。



```
{
  "mcpServers": {
    "siyuan": {
      "type": "http",
      "url": "http://127.0.0.1:36796/mcp",
      "headers": {
        "Authorization": "Bearer ${SIYUAN_TOKEN}"
      },
      "x-workbuddy": {
        "displayName": { "zh": "思源笔记 MCP", "en": "SiYuan Note MCP" },
        "description": { "zh": "连接后可读取和操作本地思源笔记内容。", "en": "..." },
        "auth": {
          "type": "token",
          "tokenSchema": {
            "title": { "zh": "配置思源访问 Token", "en": "Configure SiYuan Token" },
            "description": { "zh": "请输入思源笔记 API Token。", "en": "..." },
            "docUrl": "https://example.com/guide",
            "docLabel": { "zh": "如何获取 Token?", "en": "How to get a token?" },
            "fields": [
              {
                "key": "SIYUAN_TOKEN",
                "label": { "zh": "思源 Token", "en": "SiYuan Token" },
                "placeholder": { "zh": "请输入 API Token", "en": "Enter API token" },
                "type": "password",
                "required": true,
                "description": { "zh": "将写入 Authorization Header", "en": "..." }
              }
            ]
          }
        }
      }
    }
  }
}
```



tokenSchema 字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| title | LocalizedString | 弹窗标题 |
| description | LocalizedString | 弹窗说明文案 |
| docUrl | string | 「如何获取」帮助文档链接（非文案，不做本地化） |
| docLabel | LocalizedString | 帮助链接展示文案 |
| fields | array | 表单字段列表，见下 |

fields 每项：

| **字段** | **类型** | **说明** |
| --- | --- | --- |
| key | string | 字段标识，对应 headers 中的 ${key} 占位（非文案） |
| label | LocalizedString | 字段标签 |
| placeholder | LocalizedString | 输入框占位提示 |
| type | string | "text" 或 "password"（敏感凭据用 password） |
| required | boolean | 是否必填 |
| description | LocalizedString | 字段下方补充说明 |



<a id="连接器依赖"></a>



### 连接器依赖

若专家依赖的是 WorkBuddy 已上架的连接器（而非自带 MCP），在 dependencies.connectors 中列出连接器 ID 即可。引导卡片的名称、描述、图标由该连接器自身提供，无需在专家包内重复声明。



```
{
  "dependencies": {
    "connectors": ["tencent-docs"]
  }
}
```





<a id="注意事项"></a>



### 注意事项

- x-workbuddy 是 WorkBuddy 私有字段，连接后写入用户「自定义连接器」的配置中会被剥离，不会污染用户本地 mcp.json
- 已连接过的依赖再次召唤同名专家时不会重复引导
- Token 填写后由用户本地保存，专家包内严禁硬编码任何真实 Token / 密钥
- icon 相对路径基于「该 MCP 声明文件所在目录」解析；放在插件根目录的 .mcp.json 用 ./avatars/xxx.svg 即指向插件根的 avatars/



<a id="头像规范"></a>



## 头像规范

| 项目 | 要求 |
| --- | --- |
| 格式 | PNG（推荐）或 JPG |
| 尺寸 | 512×512 px（正方形） |
| 大小 | 单张不超过 500KB |
| 风格 | 统一的漫画/插画风格，专业自然 |
| 内容 | 符合角色定位，不含违规内容 |



<a id="存放位置"></a>



### 存放位置

所有头像放在 avatars/ 目录下，plugin.json 中使用相对路径引用：



```
avatars/
├── team.png                # 团队头像
├── team-lead.png           # 主理人头像
├── market-analyst.png      # 成员头像
├── fundamentals-analyst.png
└── ...
```





<a id="模板文件"></a>



## 模板文件

下载文件：trading-team.zip

下载链接: [https://codebuddy-platform-1258344699.cos.ap-beijing.myqcloud.com/open/static/files/trading-team.zip](../assets/e9b934822ad9-trading-team.zip)

---
