# MotorCare

**中文** | [English](README.en.md)

**面向工业电机售后场景的多模态 AI 故障排查辅助原型。**

MotorCare 将故障描述、报警图片与维修知识结合起来，帮助售后工程师和维修人员整理故障线索、确定后续检查方向，并生成便于交接的工单记录。用户可以在多轮对话中补充现场情况和检查结果，让分析随信息更新。

项目使用 Python、Gradio 和 MiMo API 构建，是 **IS5542 Generative AI for Business** 的课程项目，当前以本地演示为主要使用方式。

## 支持范围

| 项目 | 当前支持 |
| --- | --- |
| 电机 | BLM230-A2 |
| 驱动器 | BMUD30-C2 |
| 报警 | AL46、AL30、AL28 |
| 语言 | 中文、英文 |

当前知识库针对上述设备组合与报警范围。分析结果用于辅助排查，须由具备相关能力的工程师复核。

## 功能

- 中英文界面与回答、最多3张图片/工单、多轮补充（最多12轮）。
- 故障排查与工单记录标签页；生成、更新、复制记录。
- Motor/Driver兼容选择；当前只支持上述一组。
- 服务端范围提示、明显越权文本筛查、调用频率与用量限制。

## 工作流程

1. 选择电机、兼容驱动器和界面语言。
2. 输入故障现象，按需上传报警或现场图片。
3. 查看 AI 对现有线索的分析、排查建议和待补充信息。
4. 补充检查结果，继续分析。
5. 整理工单记录，复核后复制用于交接。

Python 后端将用户输入、对话上下文和精简知识库发送给 MiMo 模型，并通过 Gradio 展示结果。图片和故障描述会发送至所配置的外部 API，请仅使用有权提供的资料。

## 快速开始

需要 Python 3.12、Git，以及支持图片输入的 MiMo API 配置。模型请求需要网络连接，可能产生 API 费用。

```bash
git clone https://github.com/RyougiShiya/IS5542-MotorCare-after-sales-workplace.git
cd IS5542-MotorCare-after-sales-workplace
```

```bash
conda create -n motorcare python=3.12 -y
conda activate motorcare
```

进入包含app.py的项目目录后：

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows命令提示符可用 `copy .env.example .env`。
编辑本地.env，填写：

```dotenv
MIMO_BASE_URL=你的MiMo接口地址
MIMO_API_KEY=你的密钥
MIMO_MODEL=mimo-v2.6-flash
```

不要把占位文字直接用于运行。模型需支持图片输入；地址与模型以你账户实际可用配置为准。不要提交.env。

```bash
python app.py
```

打开终端打印的地址，以实际端口为准。默认只在本机监听，不生成公共链接。

## 更换模型（通过 `.env` 配置）

本项目默认使用 **MiMo**，示例模型为 `mimo-v2.6-flash`。如果需要使用其他模型或服务商，且其接口兼容下述请求格式，可以仅修改项目根目录的 `.env`，无需修改 Python 代码。

### 修改方法

1. 停止正在运行的应用（在启动终端中按 `Ctrl+C`）。
2. 编辑 `.env`，替换以下三个配置项的值：

```dotenv
MIMO_BASE_URL=https://your-provider.example/v1
MIMO_API_KEY=your_provider_api_key
MIMO_MODEL=your_vision_model_id
```

| 配置项 | 填写内容 |
| --- | --- |
| `MIMO_BASE_URL` | 服务商提供的 OpenAI 兼容 API 基础地址，按其文档填写；不要填写网页聊天地址，也不要自行追加 `/chat/completions` |
| `MIMO_API_KEY` | 对应服务商的 API 密钥 |
| `MIMO_MODEL` | 该接口实际支持且账户有权调用的模型 ID |

以上地址和密钥仅为占位示例。**配置项名称保持 `MIMO_` 前缀不变，只替换等号右侧的值**；该前缀是当前程序读取的名称，不要求服务商必须为 MiMo。保留 `.env` 中其他配置，无需更改知识库或界面代码。

3. 保存文件并重新启动：

```bash
python app.py
```

仅刷新网页不会重新加载配置。如果启动环境中已设置同名环境变量，需同步更新或移除它们；当前 `.env` 加载方式不会覆盖已有环境变量。

### 接口兼容要求

仅替换 `.env` 的前提是目标服务支持当前程序发送的完整请求：

- OpenAI 兼容的 **Chat Completions** 接口及 `system` 消息。
- 多模态 `image_url` 输入，包括内嵌图片数据（data URL）。
- `response_format={"type":"json_object"}` 的 JSON 输出模式。
- `max_completion_tokens` 参数。
- `thinking={"type":"disabled"}` 参数，或者能够安全忽略该字段。

**OpenAI 兼容不代表所有参数都兼容。** 如果服务商拒绝上述字段、只提供其他 API 格式，或模型不支持图片，则不能保证仅修改 `.env` 就可运行，可能需要适配请求代码。其他服务商尚未逐一验证。

切换后建议依次检查：文字案例、带图片案例、多轮补充、中英文回答和工单记录生成。能连接接口并不代表诊断质量与原模型一致；不同服务商的计费与数据处理政策也可能不同。请勿将包含真实密钥的 `.env` 提交到仓库。

## 示例案例

按 **Alt/Option + Shift + D** 打开或隐藏示例面板，按 **Esc** 关闭。面板可通过标题栏拖动。

1. 唤出演示工具，选择案例并发送。
2. 收到回答后点击补充信息按钮，再发送，观察分析更新。
3. 点击整理工单记录，查看结果；后续新增信息需更新记录。
4. 切换有内容的工单时先确认清空。

仓库内的 AL46 案例附有自制模拟报警示意图；AL30、AL28 为文字案例。厂商原图、产品照片与完整PDF手册不包含在仓库中。可以上传自行取得使用权限的现场图片，不能用本模拟演示宣称真实照片识别准确率。

## 目录与维护

- app.py：启动入口。
- motorcare/：模型服务、UI、路径和防护；assets/含CSS/JS。
- data/knowledge_base/：chunks.json双语知识、sources.json来源、answer_policy.json规则。
- data/cases/：cases.json为正式案例入口，images/保存案例图片；路径相对于data/cases。
- scripts/：离线检查。

新增知识时登记来源和唯一编号，保持中英文范围一致。新增报警还需同步engine.py支持范围、answer_policy.json、cases.json及ui.py双语按钮顺序，并进行模型回归。当前全部精简知识随提示提供，没有向量数据库或检索式RAG。

## 离线检查

```bash
python scripts/check_project.py
python scripts/check_workspace.py
python scripts/check_security.py
```

这些检查不调用模型；不能替代真实API和浏览器验收。

## 配置与限制

默认每分钟6次、滚动24小时60次模型调用，含摘要及失败请求；可通过.env中的MOTORCARE_CALLS_PER_MINUTE和MOTORCARE_CALLS_PER_24H配置。计数保存在var/usage.sqlite3，不含工单或密钥。同一磁盘重启保留计数，容器重建/清空磁盘会丢失，不是账户费用硬上限。适用于单实例。

默认MOTORCARE_HOST=127.0.0.1。公开绑定必须配置MOTORCARE_USERNAME和至少12字符的MOTORCARE_PASSWORD；正式上线仍需HTTPS和访问验证。提示词和启发式筛查不保证防住所有注入攻击。不要提供无认证的本地隧道。

工单只在会话中保存，不是持久化工单管理系统。Word/PDF导出未实现，目前支持复制。项目不是厂商官方产品，不承诺诊断或修复结果。

## 资料来源与许可

维修知识来源见 [sources.json](data/knowledge_base/sources.json)。厂商资料及商标的权利归各自权利人所有。

本仓库尚未提供开源许可证。公开可见不代表已授予复制、修改或分发许可；如需复用，请先联系项目作者确认授权范围。
