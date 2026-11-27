# 12 · 服务化（FastAPI）

> 状态：🚧 进行中 ｜ 前置：05_rag、09_agent
> 已落地：`01_basic`（手写订单 CRUD）、`05_Comprehensive_demo`（电商商品管理，MySQL + 原生前端 CRUD，已实跑）；`02`/`03`/`04` 仍为规划骨架。

## 这个模块解决什么问题

把 `05_rag` 和 `09_agent` 从"命令行脚本"变成"能给别人调用的服务"：
HTTP 接口、参数校验、流式输出、异常处理、日志、容器化。
**这是把"做过 demo"变成"能交付"的最后一步，也是简历上最容易被问到工程细节的地方。**

## 知识点

- [x] FastAPI 基本用法：路由、路径/查询/请求体参数、响应模型
- [x] Pydantic 做参数校验与文档自动生成
- [x] 依赖注入（`Depends` + `yield` 请求级资源）
- [x] `response_model` 与 `response_class` 的分工（数据契约 vs 响应载体）
- [ ] SSE 流式输出：为什么 LLM 应用必须流式
- [ ] 异常处理与统一错误结构
- [ ] 日志与请求追踪
- [ ] 把 RAG 封装成 `/chat`，把 Agent 封装成 `/agent`
- [ ] Dockerfile 与 `docker-compose`（应用 + Chroma + MySQL）
- [ ] 简单压测：QPS、P95 延迟

## 目录

| 子目录 | 内容 | 状态 |
|---|---|---|
| `01_basic/` | 路由、参数校验、依赖注入（手写订单 CRUD + 17 条踩坑注释） | ✅ |
| `05_Comprehensive_demo/` | 电商商品管理：SQLAlchemy + MySQL + Pydantic + 原生前端 CRUD | ✅ 已实跑 |
| `02_rag_service/` | 把 05 的 RAG 包成 `/chat`（含 SSE 流式） | 规划 |
| `03_agent_service/` | 把 09 的 Agent 包成 `/agent` | 规划 |
| `04_deploy/` | Dockerfile、docker-compose、启动脚本 | 规划 |

## 怎么跑

`05_Comprehensive_demo` 需要本地 MySQL（库 `ecommerce_db`）：

```powershell
# 1) 按 sql/ 下两个脚本建库建表、灌入示例数据
#    01_create_datebase.sql -> 02_insert_data.sql

# 2) 进到案例目录再启动（首页与静态资源都按 __file__ 锚定，不依赖启动目录）
cd learning\12_fastapi_service\05_Comprehensive_demo
python main.py
# 打开 http://127.0.0.1:8000/        管理页面
# 打开 http://127.0.0.1:8000/docs    接口文档
```

> 依赖：`fastapi`、`uvicorn[standard]`、`sqlalchemy`、`pymysql`、`pydantic`。
> 数字开头的目录名不是合法 Python 包名，所以用「cd 进目录 + `python main.py`」启动，不要写成 `learning.12_...:app` 的模块路径。

## 验收标准（能脱稿讲清）

1. 一次请求进来，从路由到模型到返回，中间经过哪些层。
2. 流式输出怎么实现？SSE 和 WebSocket 怎么选。
3. 并发上来后哪里会先崩？你怎么测的。
4. 接口出错了，客户端收到什么？日志里留下什么。
5. Docker 里怎么管理密钥和模型文件（不能打进镜像）。
6. 你的服务 QPS 多少、P95 延迟多少、单次成本多少。（**待测**）

## 我的改造 / 踩坑

- **静态资源按 `__file__` 锚定，且只挂 `static/` 子目录**：不依赖 uvicorn 启动目录；首页读取复用同一个 `path`，两处口径一致。挂载范围收窄后，`main.py` / `sql/` 不会被 `/static` 直接下载，暴露面最小。
- **「按 ID 查询」和「查看详情」复用同一条 `GET /api/products/{id}`**：不新增接口，前端三条入口共用一个 `openViewModal(id)`，后端面与维护成本都不增加；查无此 ID 时直接透传后端的 404 `detail`。
- **列表模型与详情模型分层**：`response_model=ProductOut` 天然过滤掉 `supplier_id`；详情要展示更多字段时用独立的 `ProductDetailOut` 继承，而不是给列表模型加列（会连列表响应一起变）。
- **查看窗体回显用 `textContent`**：商品名是用户输入，不做 HTML 解析，避免把内容带进 DOM 执行。
- **ORM 对象直接喂给 `response_model`** 靠 `from_attributes=True`（Pydantic v2 用 `model_config = ConfigDict(from_attributes=True)`）；响应校验失败是 500（出参），不是 422（入参）。
