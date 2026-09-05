# WorkBuddy 开发文档知识库

将 [WorkBuddy 官方开放文档](https://open.workbuddy.cn/docs) 保存为可追溯、可增量更新的 Markdown 知识库，供 Skill、连接器、Buddy 应用和第三方应用开发使用。

- **查规范**：[官方文档索引](wiki/index.md)，包含完整目录和章节入口。
- **选路线**：[开发对象与能力关系](wiki/development-map.md)。
- **开始开发**：[Skill 开发指南](guides/skill-development.md)、[连接器接入指南](guides/connector-development.md)、[应用开发指南](guides/app-development.md)。
- **查完整性**：[同步报告](SYNC_REPORT.md)、[原文待核对事项](wiki/source-notes.md)。
- **找素材**：[图片与附件索引](assets/README.md)。

## 在 Codex 中使用（快速开始）

1. 下载本仓库，或执行 `git clone https://github.com/maris205/buddy_dev_md.git`。
2. 在 Codex 中打开你要开发的项目，并确保当前任务能读取知识库所在目录。
3. 复制下面的提示词，把路径和需求改成自己的即可：

```text
请参考本地 WorkBuddy 知识库：D:\paper\buddy_dev_md。
先读该目录的 AGENTS.md、README.md 和 wiki/development-map.md，
再按任务读取相关 docs/ 官方规范和 guides/ 开发指南，不必一次读取全库。
字段、目录结构、鉴权和接口以 docs/ 原文为依据，注明参考文件；
文档缺失或矛盾时明确指出，需要最新规范时核查 source_url。

我要开发：【具体的 Skill、连接器或应用需求】。
代码放在：【开发项目的绝对路径】。
```

仅阅读文档不需要安装 Python 依赖或配置 MCP。使用 Git 克隆的副本可通过 `git pull` 更新；要检查官网变化，见下方“更新与验证”。

### 使用 workbuddy-dev Skill（推荐）

仓库已附带 [workbuddy-dev Skill](.agents/skills/workbuddy-dev/SKILL.md)。在 Codex 中打开本仓库后即可使用；如果没有出现在技能列表中，重新打开 Codex。

```text
使用 $workbuddy-dev 帮我开发一个 WorkBuddy Skill，用于把会议记录整理成行动清单。
代码放在我的开发项目中。
```

**希望在其他项目中使用**，可向 Codex 发送下面这句话安装一次：

```text
使用 $skill-installer 安装这个技能：
https://github.com/maris205/buddy_dev_md/tree/main/.agents/skills/workbuddy-dev
```

安装后直接调用 `$workbuddy-dev`；有本地知识库时附上路径，例如“知识库在 `D:\paper\buddy_dev_md`”。没有本地副本时，技能会按需读取 GitHub 文档，需要网络访问。技能本身没有运行依赖，也不复制整库图片和附件。

独立安装的技能与知识库分别更新；仓库内置技能随 `git pull` 更新。Codex 技能发现机制参见 [OpenAI 官方 Skill 指南](https://learn.chatgpt.com/docs/build-skills)。

## 内容边界

`docs/` 是官方正文镜像，不把整理者的建议写进规范。`wiki/` 和 `guides/` 是基于原文整理的阅读路径与开发建议，每篇给出来源。示例代码和附件按原样保存，尚未通过真实 WorkBuddy 运行、登录授权或发布审核验证。

“完整”指抓取时官网**中文文档目录，以及正文链接新发现的本站 `/docs` 页面**。不递归抓取外部 MCP 网站、开放平台控制台、登录后资料或其他语言版本。文档入口是概述页面的别名，归并为 `docs/what-is-open-platform.md`。

官方页面未提供明确的更新时间，`official_updated_at` 保持 `null`。`fetched_at` 表示当前正文版本的抓取时间；最新在线检查时间保存在 `.sync/manifest.json`。HTTP `Last-Modified` 不当作官方编辑时间。

## 在 Obsidian 和 GitHub 中阅读

在 Obsidian 选择“打开文件夹作为仓库”，打开此仓库根目录，从 `README.md` 或 `wiki/index.md` 开始。使用标准 Markdown 相对链接，可直接在 GitHub 阅读；Obsidian 会据此形成关系图与反向链接，无需插件。

官方镜像包含 frontmatter 标签和原始标题锚点。章节索引保留官网锚点，个别阅读器对 HTML 锚点的支持不同，可从文档大纲进入同名章节。`.sync/` 为点目录，通常不出现在 Obsidian 的内容浏览中。

## 更新与验证

需要 Python 3.10 或更高版本。推荐使用独立虚拟环境。

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/sync_docs.py
python scripts/verify_docs.py
```

Windows 机器上如 `python` 指向旧版本，可使用 `py -3.10` 创建虚拟环境。脚本读取标准代理环境变量及 Python 可识别的系统代理；仓库中不保存本机代理、令牌或 GitHub 凭证。

```bash
# 无网络重建：使用已保存的 HTML 和资源
python scripts/sync_docs.py --offline
python scripts/verify_docs.py

# 重新检查原 URL 下的图片和附件是否更新
python scripts/sync_docs.py --refresh-assets
python scripts/verify_docs.py
```

每次在线同步都会读取最新官方目录，并检查页面正文；有 ETag/Last-Modified 时使用条件请求。正文哈希不变时保留该版本的原始快照和抓取时间，避免站点运行时数据制造无意义差异。资源默认按 URL 缓存，`--refresh-assets` 可重新验证。

失败项写入报告并以非零退出码返回，旧文件保留以便核查。同步不是全库事务：遇到部分失败时请先处理报告，不要把残留旧文件视为本次成功。官网结构变化导致目录或图片无法准确解析时会报错，不会静默跳过。

校验器离线核对：目录覆盖、快照及资源哈希、正文可见文字、标题顺序、代码块内容、表格单元格、图片顺序、本地文件和章节链接。结果写入 `.sync/validation.json`。它不调用 Open API、不执行附件，也不验证示例代码的业务正确性。

```bash
git diff --stat
git diff -- docs/ wiki/ guides/ SYNC_REPORT.md
git add .
git commit -m "docs: refresh WorkBuddy documentation"
git push origin main
```

更新工具与 Git 发布分开执行，便于在推送前查看差异。未配置定时抓取任务。

## 目录

```text
docs/           官方页面的 Markdown 镜像
assets/         原始图片、ZIP 模板等附件与索引
wiki/           目录、概念关联和原文问题记录
guides/         按开发任务组织的阅读路径和检查清单
scripts/        同步与离线校验工具
.sync/          页面清单、哈希、原始 HTML、抓取和验证报告
```

后续新增经过真实运行验证的最小示例时，再建立 `examples/`，并记录环境、步骤、输出和验证日期。

## 来源与权利

这是个人维护的非官方整理库。官方文档、图片、附件及其中示例的权利归原作者和相应权利人所有；本仓库不对这些来源内容重新授予开源许可。每篇保留原文链接，资源映射见 `.sync/manifest.json`。若文档与平台当前行为不一致，以平台最新文档和实际验证为依据，并保留差异记录。
