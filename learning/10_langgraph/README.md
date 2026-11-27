# 10 · LangGraph

> 状态：⏳ 未开始 ｜ 前置：09_agent

## 这个模块解决什么问题

Agent 一旦有分支、循环、人工确认，用链就写不下去了。LangGraph 用"状态 + 图"来编排：
节点是函数、边是流转条件、状态在节点间传递，还能中断、恢复、回放。

## 知识点（计划）

- [ ] 为什么需要图：链的局限（无循环、无分支、无中断）
- [ ] `StateGraph`、`State`、`Node`、`Edge`、`compile`
- [ ] `MessagesState` 与自定义状态、Reducer（状态怎么合并）
- [ ] 条件边（`add_conditional_edges`）与循环
- [ ] Checkpoint：中断与恢复、失败重跑
- [ ] Human-in-the-loop：人工审批节点
- [ ] 多智能体协作：Supervisor / 分工模式
- [ ] 并行执行：Send / Map-Reduce（上一个知识点）
- [ ] 综合案例：多智能体客服系统（压轴，见 `06_customer_service_agent/`，前置 01~05 含并行执行）

## 目录（计划）

| 子目录 | 内容 |
|---|---|
| `01_basic_graph/` | 最小图、节点与边 |
| `02_state_reducer/` | 状态合并、条件边、循环 |
| `03_human_in_loop/` | 中断、恢复、人工审批 |
| `04_multi_agent/` | 多智能体协作模式（Supervisor / 分工） |
| `05_case_diagnosis/` | 自选案例：售后工单流转（含人工审批中断与恢复） |
| `06_customer_service_agent/` | 综合案例：电商售后多智能体客服（LangGraph 收尾，串起 01~05） |

## 怎么跑

当前各子目录均为骨架（`06_customer_service_agent/` 已有脚本但接入待修）。脚本跑通后在此补命令与实测数字，未实测一律写「待测」。

依赖见根 `requirements.txt`；`10_langgraph` 需 langgraph 1.x（0.4.x 无 `langgraph.runtime` / `Runtime` / `context=`）。

## 验收标准（能脱稿讲清）

1. 图执行时状态怎么在节点间流动？Reducer 不写会出什么问题。
2. 条件边怎么写？循环怎么设终止条件。
3. Checkpoint 存的是什么？为什么它能做"中断-恢复"。
4. 什么场景必须 Human-in-the-loop，工程上怎么实现审批。
5. 多智能体和"一个 Agent 多个工具"的取舍。
6. 画出你那个诊断流程的图，说明每个节点的输入输出。

## 我的改造 / 踩坑

- 计划：用 SFC 状态机的思路设计诊断流程，再把每个状态映射成 LangGraph 的节点。
- （学到再补）
