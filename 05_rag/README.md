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
| `data/` | 示例文档 `handbook.pdf` |
| `tests/` | 至少 3 个 pytest |

## 怎么跑

```powershell
cd D:\PythonProject\llm-app-dev-journey
python 05_rag\04_rerank\demo15_cross_encoder.py
```

首次运行会下载 `cross-encoder/ms-marco-MiniLM-L-6-v2` 权重（约 80MB），已加入 `.gitignore`，不会进仓库。

## 验收标准

1. 完整链路六步：解析 → 分块 → 向量化 → 入库 → 检索 → 生成，每步的输入输出是什么。
2. `chunk_size` 和 `overlap` 怎么定？小了会怎样、大了会怎样？你最后为什么选这个值。
3. 为什么要 Rerank？向量召回和 CrossEncoder 打分的区别在哪？
4. 检索不准时，你的排查顺序是什么（分块 → 向量模型 → TopK → Prompt）？
5. 怎么抑制幻觉？"答案必须带出处"在工程上怎么实现？
6. 你的评测集有几条、怎么标注、Recall@3 从多少提升到多少。

## 我的改造 / 踩坑

- 分块加了长度上限与句子边界对齐，避免切断语义。
- 检索 TopK 从 3 调到 5 后召回有提升（具体数字在 `05_eval/` 里）。
- （继续补：Chroma 的 embedding_function 必须与入库时一致，否则查询结果毫无意义）
