# 原文待核对事项

以下是自动检查发现的链接异常，属于原网页内容；镜像保留原样。开发时请结合接口标题、参数表和平台实际行为核对。

检查范围是链接文字与目标的差异，以及文件名被识别为域名；这不是完整的官方文档技术审校。

| 页面 | 类型 | 原文链接文字 | 原文目标 |
| --- | --- | --- | --- |
| [技能](../docs/skill.md) | `filename_linked_as_domain` | SKILL.md | `http://SKILL.md` |
| [技能](../docs/skill.md) | `filename_linked_as_domain` | SKILL.md | `http://SKILL.md` |
| [技能](../docs/skill.md) | `filename_linked_as_domain` | SKILL.md | `http://SKILL.md` |
| [技能](../docs/skill.md) | `filename_linked_as_domain` | SKILL.md | `http://SKILL.md` |
| [Open API 接口](../docs/openapi.md) | `url_label_target_mismatch` | https://www.workbuddy.cn/openapi/v2/user/profile | `https://www.workbuddy.cn/openapi/v2/localassistant` |
| [Open API 接口](../docs/openapi.md) | `url_label_target_mismatch` | https://www.workbuddy.cn/openapi/v2/user/phoneverification | `https://www.workbuddy.cn/openapi/v2/localassistant` |

`filename_linked_as_domain` 表示原文将 `SKILL.md` 链接成了 HTTP 域名，它不作为可下载的技能附件。

返回 [文档索引](index.md) · [开发对象关系](development-map.md) · [同步报告](../SYNC_REPORT.md)。
