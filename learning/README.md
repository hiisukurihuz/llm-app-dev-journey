# learning · 学习过程

> 这一层是**按知识点编号的学习记录**：12 个模块，每个有目标 / 知识点 / 怎么跑 / 我的改造 / 踩过的坑。
> 想看成品项目请回到上一级 [`projects/`](../projects/)；根 [`README.md`](../README.md) 是整个仓库的门面。
> 目录整体下沉到 `learning/` 后，从仓库根执行脚本时命令要带 `learning\` 前缀。

## 阅读顺序

语言基础类为 01~03；大模型应用基础为 04~12；**综合项目**见 [`../projects/`](../projects/)。
模块内部的编号（`01_`、`02_` …）即学习顺序；「前置」写在各模块 README 顶部。

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
| 12 | [服务化](12_fastapi_service/) | 🚧 | FastAPI 把 RAG / Agent 包成 HTTP 服务；已跑通电商商品管理综合案例（MySQL + 原生前端 CRUD） |

> 进度按「模块」记，不按目录数记：不少子目录还是骨架（只有规划、无脚本），这是学习过程的真实状态，不是交付清单。

## 目录

```
01_python_core/      ...
12_fastapi_service/
```

每个模块的说明在各自的 `README.md`。公共代码在 [`../common/`](../common/)：密钥加载与模型客户端；引用方式见 [`../common/README.md`](../common/README.md)。

## 约定

- 模块用 `01_`~`12_` 编号（学习顺序），模块内子目录同样用 `01_`、`02_`。
- 密钥只放仓库根的 `.env`，脚本里一律 `from common.config import ...`，不在模块内复制 `global_var.py`。
- 注释写「为什么」，不写「是什么」；未实测的数字写「待测」，不填估算值。
