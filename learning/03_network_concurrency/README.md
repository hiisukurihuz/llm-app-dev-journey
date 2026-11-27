# 03 · 网络编程与并发

>  状态：🏗 重写中 ｜ 前置：01_python_core

## 这个模块解决什么问题

写清楚"一个请求从网卡到函数"的路径：UDP/TCP 套接字 → 阻塞式 C/S → 多进程/多线程并发服务器 →
最简单的 HTTP 服务器。这块内容和大模型无关，但**面试几乎必问**。

## 知识点

- [x] 网络基础：IP/端口/协议分层、UDP vs TCP
- [x] TCP 三次握手、四次挥手，为什么需要 TIME_WAIT
- [x] 套接字编程：`socket` / `bind` / `listen` / `accept` / `recv` / `send`
- [x] UDP 与 TCP 的代码差异（有无连接、粘包问题）
- [x] 应用层小案例：文件传输、英汉词典查询、聊天机器人
- [x] 进程：`fork`/`Process`、PID/PPID、进程间不共享内存
- [x] 进程间通信：`Queue`、管道
- [x] 线程：`Thread`、共享变量、`Lock`、GIL 是什么、为什么 CPU 密集要用多进程
- [x] 线程池 / 进程池、`asyncio` 协程初探
- [x] 并发服务器：多进程 server、多线程 server、带数据库的业务 server
- [x] HTTP 协议与手写 HTTP 服务器、静态资源响应

## 目录

| 子目录 | 内容 |
|---|---|
| `01_socket_basic/` | UDP/TCP 基础 C/S、收发数据 |
| `02_socket_apps/` | 文件传输、词典、机器人三个应用 |
| `03_process_thread/` | 进程、线程、Queue、Lock、异步 |
| `04_concurrent_server/` | 多进程/多线程/带 DB 的并发服务器 |
| `05_http_server/` | 手写 HTTP server、静态页面与图片 |

> **整合说明**：``03_process_thread/` 收录进程与线程的一套完整实现。此主题我写过两版（多进程版、多线程版），两者差异的对比笔记见该目录内说明。

## 怎么跑

```powershell
# 终端 1
python learning\03_network_concurrency\01_socket_basic\tcp_server.py
# 终端 2
python learning\03_network_concurrency\01_socket_basic\tcp_client.py
```

HTTP 服务：

```powershell
python learning\03_network_concurrency\05_http_server\demo01_HTTP_server.py
# 浏览器打开 http://127.0.0.1:8000/
```

## 验收标准（能脱稿讲清）

1. 为什么 TCP 要三次握手、四次挥手；`TIME_WAIT` 的作用。
2. `accept()` 返回的是什么；为什么它能区分不同客户端。
3. 一个线程阻塞在 `recv` 时，其他线程能不能跑？GIL 到底锁的是什么？
4. 多进程和多线程各自的适用场景，进程间为什么不能直接共享变量。
5. 为什么生产环境不用"一个连接一个线程"，线程池解决了什么。
6. 手写 HTTP 服务器时，响应头里哪些字段是必须的。

## 我的改造 / 踩坑

- 两份进程/线程代码合并，删掉重复实现。
- 重写时给并发 server 加：`daemon=True`、最大并发数、`Ctrl+C` 优雅退出。
- （继续补：粘包、端口占用、僵尸进程等实际报错）
