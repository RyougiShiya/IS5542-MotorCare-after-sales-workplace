# MotorCare

IS5542 Generative AI for Business 课程演示项目。面向售后工程师和维修人员，结合故障描述、图片与精简维修知识，为 BLM230-A2 电机 + BMUD30-C2 驱动器提供 AL46、AL30、AL28 初步排查。所有建议需工程师复核。

## 功能

- 中英文界面与回答、最多3张图片/工单、多轮补充（最多12轮）。
- 故障排查与工单记录标签页；生成、更新、复制记录。
- Motor/Driver兼容选择；当前只支持上述一组。
- 演示工具默认隐藏：Alt/Option + Shift + D显示或隐藏，Esc关闭；标题栏可拖动。
- 服务端范围提示、明显越权文本筛查、调用频率与用量限制。

## 本地运行

需要Python 3.12和可访问的MiMo接口。Gradio本地运行不需要购买Hugging Face计划。API请求仍需要网络并可能产生模型费用。

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

## 演示

1. 唤出演示工具，选择案例并发送。
2. 收到回答后点击补充信息按钮，再发送，观察分析更新。
3. 点击整理工单记录，查看结果；后续新增信息需更新记录。
4. 切换有内容的工单时先确认清空。

本上传版AL46带自制模拟报警示意图；AL30/AL28为文字案例。厂商原图、产品照片与完整PDF手册不包含在仓库中。可以上传自行取得使用权限的现场图片，不能用本模拟演示宣称真实照片识别准确率。

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

## 上传GitHub

建议先创建私有仓库。上传本目录内文件与文件夹，保持app.py和README.md在仓库根目录。不要只上传ZIP；网页上传时确认motorcare/和data/目录保留。.env.example应上传，.env绝不能上传。不要使用本机完整项目覆盖本精简包。

本仓库没有声明开源许可证；如需授予外部复用权，由项目作者另行选择许可证。资料出处见data/knowledge_base/sources.json。
