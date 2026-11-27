# 07 · LangChain

> 状态：🚧 进行中 ｜ 前置：06_prompt_engineering

## 这个模块解决什么问题

把 `04`~`06` 里手写的东西换成框架写法，然后回答一个问题：
**LangChain 到底替我做了什么？哪些地方它做得比我好，哪些地方反而更绕？**

学这个模块的正确姿势是：先手写（04/05/06 已经做过），再用框架重写一遍，做对比。

## 知识点

- [x] LangChain 是什么、核心抽象（Model / Prompt / OutputParser / Retriever / Memory）
- [x] 三种 Message 与 `invoke` / `stream` / `batch`
- [x] `PromptTemplate`：占位符、默认值、JSON 双花括号
- [x] `ChatPromptTemplate`：system / human / ai 组合
- [ ] `OutputParser`：列表、枚举、日期、自定义、Pydantic
- [ ] 文档加载（PDFLoader）与文本切分（`RecursiveCharacterTextSplitter`）
- [ ] 检索器：Chroma retriever、`MultiQueryRetriever`、`EnsembleRetriever`（BM25 + 向量）
- [ ] Memory：Buffer / Window / TokenBuffer / Summary
- [ ] LCEL 与 Runnable：`|` 管道、`RunnablePassthrough`、`RunnableLambda`
- [ ] 把 `05_rag` 的裸 RAG 改写成链，对比代码量

## 目录

| 子目录 | 内容 |
|---|---|
| `01_model_io/` | 三种 Message、PromptTemplate、ChatPromptTemplate |
| `02_output_parser/` | 五种解析器 |
| `03_document_loader/` | PDF 加载与切分 |
| `04_retriever/` | 本地检索 / MultiQuery / 混合检索 |
| `05_memory/` | 四种记忆 + 摘要策略 |
| `06_lcel/` | LCEL 链路与 RAG 改写 |

## 怎么跑

```powershell
cd D:\PythonProject\llm-app-dev-journey
python learning\07_langchain\01_model_io\demo01_quick_start.py
```

脚本开头加 5 行"向上找仓库根"的引导，再 `from common.llm import chat_model`——
这样 `07` 和 `05` 用同一份密钥配置，不再各存一份 `global_var.py`。

## 验收标准（能脱稿讲清）

1. LangChain 的 `Chain` 和 `Runnable` 是什么关系？`|` 做了什么。
2. `PromptTemplate` 和 `ChatPromptTemplate` 分别用在什么场景。
3. 带结构的输出为什么要用 OutputParser？它比"手动 `json.loads`"多做了什么。
4. `MultiQueryRetriever` 解决什么问题？代价是什么（多几次模型调用）。
5. Memory 的四种实现分别怎么截断上下文，各自适合什么对话。
6. **同一套 RAG：手写版 vs LangChain 版，代码行数、可读性、可调试性各差在哪。**
   （这道题能答好，比会用框架更值钱）

## 我的改造 / 踩坑

- 现有 3 个 demo 从 `6.langchain/` 迁入，`env_test.py` 删除。
- 计划：给 `06_lcel/` 写一个"同一份 RAG 的两种实现"对比，放进 `docs/notes/`。
- （继续补）
