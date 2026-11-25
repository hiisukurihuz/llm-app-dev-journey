#自定义fastapi后端服务器，实现订单的增删改查
import csv
from fastapi import FastAPI,Depends
from pydantic import BaseModel,Field
import datetime

app=FastAPI()

class OrderIn(BaseModel):
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

class OrderOut(OrderIn):
    pass   #出参格式直接继承

def open_csv():
    with open("test.csv", newline="", encoding="utf-8") as csvfile:
        row = list(csv.DictReader(csvfile))
    return row

FIELDS = ["order_id", "product_id", "amt", "create_time", "price", "status"]

def update_csv():                       # 增：追加写入
    with open("test.csv", "a", newline="", encoding="utf-8") as f:
        yield csv.DictWriter(f, fieldnames=FIELDS)

def rewrite_csv():                      # 删：读旧数据 + 整体重写
    with open("test.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open("test.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        yield rows, w

#查全部
@app.get("/orders",response_model=list[OrderOut])
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
        return {f"未找到{order_id}商品"}


@app.post("/orders")
async def create_order(orders: OrderIn,writer=Depends(update_csv)):
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
        writer.writerow(row)
    return "商品增加成功"


@app.post("/orders/{order_id}")
async def delete_order(order_id, ctx=Depends(rewrite_csv)):
    rows, w = ctx
    w.writerows([r for r in rows if r["order_id"] != order_id])
    return f"商品{order_id}删除成功"
