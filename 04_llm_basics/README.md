# 04 · 大模型基础与工具调用

> 状态：🏗 重写中 ｜ 前置：01_python_core

## 这个模块解决什么问题

从"能在网页上用大模型"到"能在代码里稳定地驱动大模型"：
把调用封装成函数、让模型输出结构化 JSON、再把函数交给模型去调用（Function Calling）。

## 知识点

- [x] 大模型是什么、能做什么、不能做什么（幻觉、上下文长度、知识截止）
- [x] 主流模型与平台：DeepSeek、火山方舟（Ark）、OpenAI 兼容接口
- [x] `messages` 三种角色（system / user / assistant）与多轮上下文
- [x] `temperature`、`max_tokens`、流式输出
- [x] 用 system prompt 约束输出格式（JSON Output）
- [x] Function Calling 原理：模型不执行函数，只返回"要调用谁、参数是什么"
- [x] 单工具 / 多工具 / 多参数场景
- [x] 接入真实外部 API 作为工具（天气）
- [x] 把 SQL 查询封装成工具（自然语言 → SQL → 执行 → 归纳）
- [x] Attention 的数学直觉：`Q @ K.T` 得到的是什么矩阵

## 目录

| 子目录 | 内容 |
|---|---|
| `00_attention_intuition/` | 相似度 / 注意力分数的小实验 |
| `01_hello_llm/` | 三种调用方式、JSON 输出、多轮对话 |
| `02_function_calling/` | 单工具 → 多工具 → 真实 API → SQL 工具 |

> `math.py` 原来混在"网络编程"目录里，其实它算的是 `Q·Kᵀ`（注意力分数矩阵），属于大模型原理，故挪到这里。

## 怎么跑

```powershell
cd D:\PythonProject\llm-app-dev-journey
python 04_llm_basics\01_hello_llm\demo01_quick_start.py
```

脚本开头需要引用 `common/` 时，加 5 行"向上找仓库根"的引导（见 [common/README.md](../common/README.md)）。

## 验收标准（能脱稿讲清）

1. `messages` 里 system / user / assistant 各承担什么职责；多轮对话靠什么维持。
2. Function Calling 的完整闭环有几步？模型返回的 `tool_calls` 里是什么？
3. 为什么工具调用要比"让模型直接回答"更可靠？它的失败模式有哪些？
4. 工具描述（description / 参数 schema）写不好会导致什么问题？
5. 怎么让模型输出稳定可解析的 JSON？`temperature=0` 就能保证吗？
6. `Q @ K.T` 的物理含义：为什么除以 `sqrt(d_k)`，Softmax 之后是什么。

## 我的改造 / 踩坑

- `demo05_multi_function_calling.py` 该文件是补全练习：先留空，自己实现多工具调度。
- 天气工具加了 `days` 参数限幅、超时和城市查不到的兜底。
- SQL 工具重敲时加白名单（只允许 SELECT）。
- （继续补）
