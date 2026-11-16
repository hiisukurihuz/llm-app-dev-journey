# notes · 复盘笔记

命名：`YYYYMMDD-主题.md`，例如 `20261120-chunk-size-ab.md`。

## 模板

```markdown
# 标题：一句话说清这篇解决什么问题

## 背景
在做什么任务，遇到了什么现象。

## 现象 / 报错
原始输出、截图、复现步骤。

## 排查过程
我按什么顺序试了哪些可能，哪些被排除，为什么。

## 结论
最终原因是什么。

## 怎么改的
关键代码 3-5 行（不要贴整个文件）。

## 数字
改前 vs 改后的指标对比。

## 留给下次的经验
一句话。
```

## 建议优先写的 5 篇

1. `chunk-size-ab.md` —— 分块参数怎么定，A/B 对比结果
2. `rerank-vs-none.md` —— 加 Rerank 前后召回率变化
3. `langchain-vs-handwritten.md` —— 同一套 RAG 两种实现的代码量与可维护性
4. `agent-tool-failure.md` —— 工具调用失败的几种情况与处理
5. `house-mis-bugs.md` —— 房产项目三个 bug 的排查过程
