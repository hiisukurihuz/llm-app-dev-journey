#自定义fastapi后端服务器，实现订单的增删改查
#
# ============================================================================
# 今日踩坑记录（2026-11-25，全手写 demo）
# 格式：[坑 N] 主题 → 之前怎么错 / 现象 → 怎么修正
# 正文中 # [坑N] 是对应代码位置的锚点；本次只加注释，未改动任何业务逻辑
# ============================================================================
#
# --- 一、csv 基础（前置练习 create_csv.py）---
# [坑 1] 文件名与标准库同名
#   之前：脚本叫 csv.py，第 1 行 import csv
#   现象：模块搜索路径先命中脚本自己，自己还没执行完，
#         AttributeError: module 'csv' has no attribute 'DictWriter'
#   修正：改名 create_csv.py，清掉 __pycache__/csv.*.pyc；别拿标准库名当文件名
# [坑 2] fieldnames 与数据字典 key 不一致
#   之前：fieldnames = ["姓名", "成绩"]，data 里却是 order_id / product_id / ...
#   现象：ValueError: dict contains fields not in fieldnames
#   修正：fieldnames 必须和数据字典的 key 完全对齐（见下方 FIELDS）
# [坑 3] 读回值的类型
#   之前：以为 row["order_id"] 取出来是数字 123
#   现象：CSV 是纯文本，取到的是字符串 '123'；price 123.45 → '123.45'
#   修正：按列名取要用 DictReader（普通 reader 只能按下标）；计算前显式 int() / float()
# [坑 4] 写文件漏了 newline=""
#   之前：open(..., "w", encoding="utf-8")
#   现象：Windows 下每行变成 \r\r\n，Excel 打开多出空行
#   修正：读写都带 newline=""
# [坑 5] 以为有独立的「改 / 删」指令
#   之前：想找类似 UPDATE / DELETE 的 csv 方法
#   现象：csv 只有读(reader / DictReader)和写(writer / DictWriter)两组能力
#   修正：增 = "a" 追加；改 / 删 = 读出全部 → 内存里改或过滤 → "w" 整体重写
#
# --- 二、Pydantic 模型 ---
# [坑 6] 两个只有类名不同的类
#   之前：OrderIn / OrderOut 把同样的 5 个字段复制了两遍
#   现象：冗余；OrderOut = OrderIn 只是别名，不是两个类
#         （__name__ 仍是 OrderIn，OpenAPI 也不会多出一个 schema）
#   修正：class OrderOut(OrderIn): pass，字段和校验规则全部继承  ← 第 23 行
# [坑 7] 字段全带 default
#   之前：五个字段都写 Field(default="商品名") 之类
#   现象：POST 传 {} 不报缺失，直接插入一行默认值
#         "商品名,A000,0,...,0,True"，接口还回「商品增加成功」
#   修正：改成 Field(..., ...) 必填，传 {} 会 422  ← 第 10-21 行
# [坑 8] 请求体没「平铺」+ /docs 示例是占位值
#   之前：body 写成 {"orders": {...}}；或直接在 /docs 点 Execute
#   现象：多余字段被 extra='ignore' 静默丢掉，字段全落回默认值；
#         /docs 里 "string" / 0 / true 是 Swagger 按 type 生成的示意值，
#         直接执行会把 "string" 当成订单号写进 CSV
#   修正：body 顶层直接放字段 {"order_id":"125", ...}（参数名 orders 不进 JSON）；
#         在 /docs 编辑框里改成真实值再 Execute；
#         想让示例显示真实值可加 json_schema_extra={"example": "125"}
#
# --- 三、路由与 response_model ---
# [坑 9] open 模式写成 "ra"
#   之前：open("test.csv", "ra", ...)，想同时读和追加
#   现象：ValueError: must have exactly one of create/read/write/append mode
#   修正：r / w / a / x 恰好选一个；追加用 "a"  ← 第 34 行
# [坑 10] 追加模式里还写表头
#   之前："a" 打开后仍调用 writeheader()
#   现象：每 POST 一次多一行表头，DictReader 之后会把表头当数据读出来
#   修正：追加时只 writerow；只有 "w" 整体重写时才 writeheader()  ← 第 42 / 80 行
# [坑 11] POST 参数没有类型注解
#   之前：create_order(order_id, product_id, amt, price, status)
#   现象：五个参数全被当查询参数，body 传 JSON 得 422 loc:["query","order_id"]
#   修正：用请求体模型 orders: OrderIn  ← 第 68 行
# [坑 12] response_model 与返回值形状不符
#   之前：GET /orders 声明 response_model=OrderOut，却 return 一整个列表
#   现象：ResponseValidationError: Input should be a valid dictionary or object
#   修正：列表接口要声明 list[OrderOut]  ← 第 46 行
# [坑 13] 出参模型字段不全
#   之前：CSV 里有 create_time，OrderOut 只有继承来的 5 个字段
#   现象：response_model 校验时多余字段被 extra='ignore' 静默过滤，create_time 消失
#   修正：需要就给 OrderOut 补 create_time 字段，或去掉 response_model
# [坑 14] 花括号单元素不是字典
#   之前：return {f"未找到{order_id}商品"}
#   现象：这是 set 字面量，被转成数组 ["未找到999商品"]，返回类型与预期不符
#   修正：return {"msg": f"未找到{order_id}商品"}（本文件第 64 行仍是 set，待改）
#
# --- 四、Depends / yield 依赖 ---
# [坑 15] 普通 return 的依赖活不到视图执行完
#   之前：update_csv() 里 with open(...) 然后 return (row, writer)，POST 用 Depends 接
#   现象：三个错叠在一起，实测先撞上 io.UnsupportedOperation: not readable
#         a) "a" 模式不可读，csv.DictReader(csvfile) 一迭代就炸
#         b) with 退出后文件已关闭，writer 再写 → ValueError: I/O operation on closed file
#         c) Depends 把整个 (row, writer) 元组塞给 writer 参数
#            → AttributeError: 'tuple' object has no attribute 'writerow'
#   修正：改成 yield 依赖 —— FastAPI 在视图执行完才走 yield 后面的收尾，
#         文件这期间一直开着  ← 第 33-43 行
# [坑 16] 增和删不能共用一个依赖
#   之前：一个 update_csv() 同时想服务「增」和「删」
#   现象：增要 "a" 追加；删必须 "w" 整体重写，追加模式删不掉任何行
#   修正：拆成 update_csv(追加, yield writer) 与 rewrite_csv(读旧 + "w" 重写, yield rows, w)
# [坑 17] 删接口的三处笔误
#   之前：r["order_id"] != "order_id"（字面量）/ writer.writerow(row)（传 list）
#         / writer=Depends(...), row=Depends(...)（同一依赖跑两次，都拿到元组）
#   现象：比对永远不成立；DictWriter 要 dict 不是 list；依赖重复执行
#   修正：!= order_id；writerows([...])；一次 ctx=Depends(rewrite_csv) 再 rows, w = ctx
#         ← 第 84-88 行
#
# --- 仍可优化（不影响当前运行，留作后续练习）---
# * 第 64 行仍是 set 返回；第 84 行删除仍挂 @app.post（REST 惯例用 @app.delete）
# * product_id 仍带 default="A000"；若要全必填，改成 Field(...)
# * GET /orders/{order_id} 未加 response_model，返回原始 dict
# * status: bool 写进 CSV 是 True/False，与老数据行的 1 格式不一致（可写 int(orders.status)）
# * test.csv 用相对路径，取决于 uvicorn 的启动目录
# ============================================================================
import csv
from fastapi import FastAPI,Depends
from pydantic import BaseModel,Field
import datetime

app=FastAPI()

class OrderIn(BaseModel):
    # [坑7] 用 ... 表示必填；写 default 会让空 body 静默插入一行默认值
    order_id: str=Field(...,
                        description="商品名称")
    product_id:str=Field(default="A000",
                         description="商品编号")
    amt:int=Field(...,
                  ge=0,
                  description="商品数量")
    price:float=Field(...,
                    ge=0,
                    description="商品价格")
    status:bool=Field(...,
                      description="商品状态")

class OrderOut(OrderIn):        # [坑6] 继承；不要写 OrderOut = OrderIn（只是别名）
    pass   #出参格式直接继承

def open_csv():                 # [坑4][坑5] 读：newline="" + DictReader 按列名取
    with open("test.csv", newline="", encoding="utf-8") as csvfile:
        row = list(csv.DictReader(csvfile))
    return row

FIELDS = ["order_id", "product_id", "amt", "create_time", "price", "status"]   # [坑2] 与 data 的 key 对齐

def update_csv():                       # [坑15][坑16] yield 依赖，专供「增」
    with open("test.csv", "a", newline="", encoding="utf-8") as f:   # [坑4][坑9] "a" + newline=""
        yield csv.DictWriter(f, fieldnames=FIELDS)                     # [坑15] yield，不是 return

def rewrite_csv():                      # [坑16] 「删」专用：读旧数据 + "w" 整体重写
    with open("test.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open("test.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()                 # [坑10] 只有整体重写时才写表头
        yield rows, w                   # [坑15] 文件在视图执行期间保持打开

#查全部
@app.get("/orders",response_model=list[OrderOut])   # [坑12] 返回 list 就要声明 list[...]
async def order(row=Depends(open_csv)):
    """读取csv数据并返回"""
    result=row
    return  result

#根据id查
@app.get("/orders/{order_id}")
async def get_order(order_id,row=Depends(open_csv)):
    """读取特定编号的csv数据并返回"""
    temp=row
    result=[]
    for i in temp:
        if i["order_id"] == order_id:
            result=i
    if result:
        return result
    else:
        return {f"未找到{order_id}商品"}   # [坑14] 这是 set，建议改成 {"msg": ...}


@app.post("/orders")
async def create_order(orders: OrderIn,writer=Depends(update_csv)):   # [坑8][坑11][坑15]
    """增加商品"""
    data = [
        {"order_id": orders.order_id,
         "product_id": orders.product_id,
         "amt": orders.amt,
         "create_time": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
         "price": orders.price,
         "status": orders.status
         }
    ]
    for row in data:
        writer.writerow(row)            # [坑10] 追加不写表头；[坑15] writer 是 DictWriter 本体
    return "商品增加成功"


@app.post("/orders/{order_id}")        # [坑17] 建议改成 @app.delete
async def delete_order(order_id, ctx=Depends(rewrite_csv)):   # [坑17] 一次依赖，解包一次
    """删除商品"""
    rows, w = ctx
    w.writerows([r for r in rows if r["order_id"] != order_id])   # [坑17] 用路径参数，不是字面量
    return f"商品{order_id}删除成功"


