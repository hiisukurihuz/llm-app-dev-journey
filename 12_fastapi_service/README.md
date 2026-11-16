# 12 · 服务化（FastAPI）

> 状态：⏳ 未开始 ｜ 前置：05_rag、09_agent

## 这个模块解决什么问题

把 `05_rag` 和 `09_agent` 从"命令行脚本"变成"能给别人调用的服务"：
HTTP 接口、参数校验、流式输出、异常处理、日志、容器化。
**这是把"做过 demo"变成"能交付"的最后一步，也是简历上最容易被问到工程细节的地方。**

## 知识点（计划）

- [ ] FastAPI 基本用法：路由、路径/查询/请求体参数、响应模型
- [ ] Pydantic 做参数校验与文档自动生成
- [ ] 依赖注入（`Depends`）
- [ ] SSE 流式输出：为什么 LLM 应用必须流式
- [ ] 异常处理与统一错误结构
- [ ] 日志与请求追踪
- [ ] 把 RAG 封装成 `/chat`，把 Agent 封装成 `/agent`
- [ ] Dockerfile 与 `docker-compose`（应用 + Chroma + MySQL）
- [ ] 简单压测：QPS、P95 延迟

## 目录（计划）

| 子目录 | 内容 |
|---|---|
| `01_basic/` | 路由、参数校验、依赖注入 |
| `02_rag_service/` | 把 05 的 RAG 包成 `/chat`（含 SSE 流式） |
| `03_agent_service/` | 把 09 的 Agent 包成 `/agent` |
| `04_deploy/` | Dockerfile、docker-compose、启动脚本 |

## 怎么跑

```powershell
pip install fastapi "uvicorn[standard]"
uvicorn 12_fastapi_service.01_basic.main:app --reload
# 打开 http://127.0.0.1:8000/docs
```

> 注意：`01_basic` 这种以数字开头、带点的目录不能直接作为 Python 包导入。
> 这一节用 `cd 12_fastapi_service\01_basic; uvicorn main:app --reload` 的方式启动，
> 或者把目录名改成 `basic_service` 之类的合法标识符。

## 验收标准（能脱稿讲清）

1. 一次请求进来，从路由到模型到返回，中间经过哪些层。
2. 流式输出怎么实现？SSE 和 WebSocket 怎么选。
3. 并发上来后哪里会先崩？你怎么测的。
4. 接口出错了，客户端收到什么？日志里留下什么。
5. Docker 里怎么管理密钥和模型文件（不能打进镜像）。
6. 你的服务 QPS 多少、P95 延迟多少、单次成本多少。

## 我的改造 / 踩坑

- （做到再补）
