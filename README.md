# LLM 应用工程实践 · 从 Python 到 RAG / Agent

## 我在做什么

把大模型应用开发涉及的知识拆成 12 个可独立运行、可单独验证的模块。每个模块都有说明文档、可运行脚本、我的改造与验收标准。

- 每个模块的 `README.md` 写了：目标 / 知识点 / 怎么跑 / 我的改造 / 踩过的坑

## 阅读顺序

语言基础类为01~03目录；大模型应用基础为04~12目录；**综合项目**见 `projects/`

## 进度

图例：✅ 已完成 ｜ 🚧 进行中 ｜ 🏗 重写中（已学完，按本仓库规范重写）｜ ⏳ 未开始

| # | 模块 | 状态 | 一句话 |
|---|---|---|---|
| 01 | [Python 核心](01_python_core/) | 🏗 | 语法 → 函数 → OOP → 异常 → 生成器 → 文件 IO → 分层小项目 |
| 02 | [MySQL](02_mysql/) | 🏗 | SQL、事务、索引，以及 pymysql 参数化访问 |
| 03 | [网络与并发](03_network_concurrency/) | 🏗 | Socket 编程、多进程/多线程、并发服务器、HTTP 服务 |
| 04 | [大模型基础](04_llm_basics/) | 🏗 | API 调用、结构化输出、Function Calling |
| 05 | [RAG](05_rag/) | 🏗 | 解析分块 → 向量库 → 检索 → 重排 → 评测 |
| 06 | [提示工程](06_prompt_engineering/) | 🏗 | 提示词优化、CoT、自洽性、注入攻击与防御 |
| 07 | [LangChain](07_langchain/) | 🚧 | 模型 I/O、解析器、检索器、Memory、LCEL |
| 08 | [多模态](08_multimodal/) | ⏳ | 图像问答、语音、文生图 |
| 09 | [智能体](09_agent/) | ⏳ | ReAct、Plan-and-Execute、工具、记忆、评估 |
| 10 | [LangGraph](10_langgraph/) | ⏳ | 图与状态、条件边、人工介入、多智能体 |
| 11 | [微调](11_finetune/) | ⏳ | LoRA / SFT 与前后对比 |
| 12 | [服务化](12_fastapi_service/) | ⏳ | FastAPI 把 RAG / Agent 包成 HTTP 服务 |
| — | [projects](projects/) | ⏳ | 综合项目与作品 |

## 目录

```
README.md            本文件
common/              公共代码：密钥加载、模型客户端
docs/                学习路线、复盘笔记
01_python_core/      ...
12_fastapi_service/
projects/
```

每个模块内部的编号即学习顺序（`01_`、`02_` …）。模块说明在各自的 `README.md`。

## 快速开始

```powershell
git clone <本仓库地址> llm-app-dev-journey
cd llm-app-dev-journey

python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Git Bash: source .venv/Scripts/activate

pip install -r requirements.txt
Copy-Item .env.example .env           # 填入自己的 DEEPSEEK_API_KEY / VOLC_API_KEY

python common\config.py               # 自检配置（密钥、路径锚定）

# 各模块脚本见对应 README；05_rag/01_naive_rag/native_rag.py 当前为 WIP（依赖已装、检索链路待接）
```

脚本里需要引用 `common/` 时，在开头加 5 行「向上找仓库根」的引导，见 [common/README.md](common/README.md)。

## 约定

- **目录**：顶层 `01_`~`12_` 是模块，模块内 `01_`、`02_` 是学习顺序；文件名用英文小写下划线。
- **密钥**：只放 `.env`，代码里一律 `from common.config import ...`。
- **提交**：`<type>(<module>): <做了什么>`，例如 `feat(05_rag): 手写句子级分块 + 前向重叠`。
- **注释**：写"为什么"，不写"是什么"；




