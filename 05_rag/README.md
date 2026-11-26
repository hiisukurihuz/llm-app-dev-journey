# 05 · RAG 检索增强生成

> 状态：🏗 重写中 ｜ 前置：04_llm_basics

## 这个模块解决什么问题

让模型回答"它没学过的东西"：把私有文档切成块、转成向量、存进向量库，
提问时先检索再生成。**这是目前简历上最能撑起一次深聊的模块，也是本仓库的重点。**

## 知识点

- [x] RAG 是什么、为什么需要它（知识截止 / 幻觉 / 私有数据）
- [x] Embedding：文本变向量的原理，为什么能用余弦相似度衡量语义
- [x] 向量数据库（ChromaDB）：集合、增、删、改、查
- [x] 语义检索：`query` → 向量 → TopK → 距离/相似度排序
- [x] PDF 文本抽取（pdfminer）、段落合并、行末连字符处理
- [x] 分块策略：句子级切分、前向重叠、长度上限
- [x] 检索结果拼进 Prompt 的方法与"只依据资料回答"的约束
- [x] Rerank：CrossEncoder 精排，召回之后再排序
- [ ] Multi-Query / RAG Fusion
- [ ] 评测：Recall@K、答案准确性、延迟

## 目录

| 子目录 | 内容 |
|---|---|
| `01_naive_rag/` | 最小 RAG：一段文本 → 检索 → 拼上下文 → 生成 |
| `02_pdf_parse_chunk/` | PDF 解析、段落合并、句子级分块 |
| `03_vectordb/` | 相似度计算、Chroma 增删改查 |
| `04_rerank/` | 完整 RAG + CrossEncoder 重排 |
| `data/` | 示例文档（原始 PDF 不入库，见 `data/README.md`） |
| `tests/` | 单测与评测集，3 个必测点见 `tests/README.md` |

## 怎么跑

已跑通：`01_naive_rag/native_rag.py`（2026-11-26 实测 `exit 0`）。需 `.env` 配好 `DEEPSEEK_API_KEY` / `VOLC_API_KEY`，依赖见根 `requirements.txt`。

```powershell
python 05_rag\01_naive_rag\native_rag.py
```

一个程序里跑两条路径做对照：全量上下文直接生成、RAG 检索（embedding → 余弦相似度 → `TOP_K=3` 截断 → 拼回 Prompt 再生成），输出为对照答案、TopK 相似度列表、RAG 生成答案三段。`04_rerank/demo15_cross_encoder.py` 尚未落地；Recall@K、token 对比等实测数字待测，未实测一律写「待测」。

## 验收标准

1. 完整链路六步：解析 → 分块 → 向量化 → 入库 → 检索 → 生成，每步的输入输出是什么。
2. `chunk_size` 和 `overlap` 怎么定？小了会怎样、大了会怎样？你最后为什么选这个值。
3. 为什么要 Rerank？向量召回和 CrossEncoder 打分的区别在哪？
4. 检索不准时，你的排查顺序是什么（分块 → 向量模型 → TopK → Prompt）？
5. 怎么抑制幻觉？"答案必须带出处"在工程上怎么实现？
6. 你的评测集有几条、怎么标注、Recall@3 从多少提升到多少。

## 我的改造 / 踩坑

- **避免重复调用、控制 token 成本**：客户端构造与所有 API 调用收进 `main()` 并加 `if __name__ == "__main__"` 守卫——顶层写法下模块每被 `import` 一次就会重发整库 embedding 与生成请求，既重复计费、又让模块无法被测试安全导入；检索结果按 `TOP_K` 截断后才拼进 Prompt，控制送入上下文的 token 量。取舍：全量上下文那一路刻意保留作对照（会多付一次调用），目的是讲清「检索到底改变了什么」，生产里不会两条路径并存。
- 分块加了长度上限与句子边界对齐，避免切断语义。
- 检索 TopK 从 3 调到 5 后召回有提升——评测集与实测数字待测，暂不填结论值。
- （继续补：Chroma 的 embedding_function 必须与入库时一致，否则查询结果毫无意义）
