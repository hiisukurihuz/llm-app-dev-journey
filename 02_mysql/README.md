# 02 · MySQL 与 SQL

> 状态：🏗 重写中 ｜ 前置：01_python_core

## 这个模块解决什么问题

从"会写 SELECT"到"知道为什么慢"：建表设计、关联查询、聚合、索引、约束、事务，
最后用 `pymysql` 在 Python 里安全地读写数据库。

## 知识点

- [x] 数据库/表/字段/记录的基本概念，常用数据类型
- [x] 建库建表、`ALTER TABLE`、增删改查
- [x] 条件、排序、分页、去重
- [x] 聚合函数、`GROUP BY` / `HAVING`、子查询
- [x] 多表关联（内/左/右连接）、外键约束
- [x] 索引：原理、类型、什么时候会失效
- [x] 视图、常用函数（日期、字符串、窗口函数）
- [x] 事务：ACID、`BEGIN` / `COMMIT` / `ROLLBACK`、隔离级别
- [x] 存储引擎差异（InnoDB vs MyISAM）
- [x] `pymysql`：连接、游标、参数化查询、事务提交

## 目录

| 子目录 | 内容 |
|---|---|
| `01_basic_sql/` | 建库建表、增删改查、单表练习 |
| `02_advanced_sql/` | 关联查询、聚合、索引、约束、窗口函数 |
| `03_transaction/` | 事务提交与回滚（两个会话对照） |
| `04_python_mysql/` | pymysql 增删改查（参数化 + 上下文管理） |
| `data/` | 建库脚本（ `tedu.sql`） |

## 怎么跑

```powershell
# 1) 起 MySQL（用你自己的服务或容器）
# 2) 导入示例库
mysql -u root -p < 02_mysql\data\tedu.sql

# 3) 跑 Python 侧
python 02_mysql\04_python_mysql\demo01_crud.py
```

事务演示需要两个客户端窗口，分别执行 `03_transaction/` 下的 `session1.sql` / `session2.sql`。

## 验收标准（能脱稿讲清）

1. 主键、唯一索引、普通索引的区别；为什么给 `WHERE` 后面的列建索引有效。
2. 什么情况下索引会失效（前导模糊、函数运算、隐式类型转换、`OR`）。
3. 内连接和左连接的结果集差异，用一张图讲出来。
4. 事务的四个特性分别对应什么机制（日志、锁、MVCC…）。
5. `DELETE` / `TRUNCATE` / `DROP` 的差异与能否回滚。
6. 为什么必须用参数化查询（`%s` 占位）而不是字符串拼接。

## 我的改造 / 踩坑

- 重敲时把 `P01_MySQL_PY.py` 从"字符串拼 SQL + 裸连接"改成参数化 + `with` 管理连接。
- `03_transaction/` 原有两个文件夹各一个会话，迁移后合并到同一目录用文件名区分。
- （继续补：慢查询、EXPLAIN 读法、练习里踩的坑）
