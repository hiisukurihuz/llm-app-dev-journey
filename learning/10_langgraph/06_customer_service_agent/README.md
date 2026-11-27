# 06 · 综合案例：电商售后多智能体客服

> 状态：⏳ 代码待填充（本目录先建骨架，脚本手写填入）｜ 前置：`01`~`05`（含并行执行 / Map-Reduce）
> 定位：LangGraph 全部讲完后的**压轴综合案例**，把前面每个知识点串成一条能跑通、能中断恢复的流程。

## 这个案例解决什么问题

一个入口进来的用户问题，先判意图，再分到 5 条互不交叉的专家分支；每个专家只绑定本领域工具，工具结果回灌后再组织回答。涉及投诉时暂停图执行、等人工审批，审批通过才继续处理。会话状态与长期记忆落 SQLite，进程重启可续接。

## 串起了哪些知识点

| 知识点 | 本案例的落点 |
|---|---|
| `StateGraph` / 自定义 `AgentState` / `add_messages` | 意图、审批状态与消息列表在同一状态里流转 |
| `add_conditional_edges` + 循环 | 意图路由；专家 ⇄ `ToolNode` 直到不再请求工具 |
| `checkpointer`（`SqliteSaver`） | 按 `thread_id` 存会话，支持中断后恢复 |
| `interrupt()` / `Command(resume=...)` | 投诉分支的人工审批节点 |
| `bind_tools` 按角色隔离 + 分支专属 `ToolNode` | 避免专家越权调用无关工具 |
| `Runtime[CustomerContext]` + `SqliteStore` | 按 `user_id` 隔离的长期记忆（跨会话复用） |
| 并行执行（上一个知识点） | 本案例未使用，作为前置；`04_multi_agent/` 讲协作模式，本目录讲「全部串起来」 |

> 与 `04_multi_agent/` 的分工：04 是「多智能体协作模式」单点演示；06 是收尾，覆盖 01~05 全部知识点。

## 怎么跑

环境用 `langgraph_env`（langgraph 1.x + langchain 1.x + python-dotenv）；根 `requirements.txt` 里 `langgraph` 必须是 1.x——0.4.x 没有 `langgraph.runtime` / `Runtime` / `context=`。

当前脚本仍不可跑（客户端接入待修，见踩坑）。修复后在此补命令与实测数字，未实测一律写「待测」。

## 验收标准（能脱稿讲清）

1. 画得出图：START → `classify_intent` → 5 条分支 → 条件边 → END；审批在哪中断、怎么恢复。
2. 讲清 `checkpointer` 与 `store` 各存什么、为什么一个按 `thread_id`、一个按 `user_id`。
3. 工具集按角色隔离解决什么问题，不隔离会怎样。
4. 能说出至少 3 个失败模式：路由走空、事务冲突、配置静默失效、会话历史堆积。

## 我的改造 / 踩坑

- 待做：接入 `common/` 基建（密钥与模型名走 `common.config`，5 行锚定），去掉 `global_var`。
- 已定位（旧调试版实测，作为踩坑链留痕；填入本仓库时按修正版手敲）：
  - `SqliteStore` 连接需 `isolation_level=None`，否则写入抛 `cannot start a transaction within a transaction`。
  - `temperature` 拼成 `tempfile` 不报错，但被塞进 `model_kwargs`，采样配置静默失效。
  - 路由必须判断 `AIMessage.tool_calls`；判断 `intent` 会让 `ToolNode` 永不执行。
  - `namespace` / dict key 写读要一致（`"preferences"` / `updated_at`），否则长期记忆读不到。
  - 固定 `thread_id` + 持久化 checkpointer 会堆叠重复历史消息；新会话要换 `thread_id`。
  - 换环境后 `ModuleNotFoundError` 不一定是少装包：旧环境里 chromadb 0.3.x / fastapi 0.85 钉死 `pydantic<2`，pip 会退回 langgraph 0.4.x，缺 `langgraph.runtime`。
  - 接入 `common/` 时用错客户端：`deepseek_client()` 是原生 `openai.OpenAI`，没有 `bind_tools` / `invoke`；LangGraph 链路要用 `chat_model()`。顶层残留的 `chat.completions.create()` 还缺 `messages`，启动即抛 `TypeError`。
