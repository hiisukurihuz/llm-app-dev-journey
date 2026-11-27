# ============================================================
# 电商商品管理系统 —— FastAPI + MySQL + Pydantic 综合示例
# ============================================================
# 本文件演示了一个典型的「分层」后端服务：
#   1) 数据库连接层：SQLAlchemy Engine + Session
#   2) ORM 模型层：把 MySQL 表映射为 Python 类
#   3) FastAPI 应用层：路由 + Pydantic 校验 + 依赖注入
#
# 数据流（以查询商品列表为例）：
#   浏览器请求 /api/products?page=1
#     → FastAPI 解析 Query 参数并做类型/范围校验
#     → Depends(get_db) 注入一个数据库 Session
#     → 路由函数用 ORM 查询 MySQL
#     → 返回值经 response_model(ProductListOut) 序列化/过滤后返回 JSON
#
# 运行前准备：
#   - 已安装依赖：fastapi uvicorn sqlalchemy pymysql pydantic
#   - MySQL 中已存在数据库 ecommerce_db 及相应表结构
#   - 项目根目录存在 static/index.html（首页模板）
# ============================================================

from fastapi import FastAPI, Path, Query, HTTPException, Depends
# HTMLResponse : 让路由直接返回 HTML 文本（用于首页）
from fastapi.responses import HTMLResponse
# StaticFiles  : 把本地目录挂载为静态资源服务（CSS/JS/图片等）
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import pathlib


#数据库配置
DB_USER="root"
DB_PASSWORD="root"
DB_HOST="localhost"
DB_PORT="3306"
DB_NAME="ecommerce_db"


#拼接SQLAlchemy连接串
DATABASE_URL=f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"


engine=create_engine(
    DATABASE_URL,
    echo=False, #True可打印sql语句，用于调试
    pool_pre_ping=True, #连接前先ping
    pool_recycle=3600 #1小时回收连接
)

#sessionmaker是session工厂，绑定连接串，设置不自动提交事务，不自动flush（提交更改但不提交事务）
#实例化sessionmaker对象
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)

#declarative_base返回一个基类，所有的ORM模型都继承该基类
#SQLAlchemy通过它手机所有表定义并维护元数据
Base = declarative_base()


#获取数据库会话的依赖
#FastApi的依赖注入会在每个请求进入时调用，请求结束后执行finally关闭会话
#使用生成器依赖yield
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#创建ORM模型
#每一个类对应db中一个表；类属性对应列
class Supplier(Base):
    """供应商表"""
    __tablename__ = "supplier"
    id=Column(Integer,primary_key=True,autoincrement=True)  #id列，主键自增
    name=Column(String(100),nullable=False)  #name列，必填
    contact=Column(String(50))  #联系人，可空
    phone=Column(String(20))  #联系电话
    created_at=Column(DateTime,server_default=func.now())    #func自带计时函数


class Category(Base):
    """商品分类表"""
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)  # 分类名唯一，避免重复
    sort_order = Column(Integer, default=0)  # 排序权重，越小越靠前
    created_at = Column(DateTime, server_default=func.now())


class Product(Base):
    """商品表"""
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)  # 金额用 DECIMAL，避免浮点误差
    stock = Column(Integer, nullable=False, default=0)  # 库存，默认 0
    category = Column(String(50), nullable=False, default="未分类")
    # 外键指向 supplier.id；未定义 relationship，
    # 因此查询商品时不会自动带出供应商对象，需手动 join。
    supplier_id = Column(Integer, ForeignKey("supplier.id"))
    created_at = Column(DateTime, server_default=func.now())
    # onupdate=func.now()：每次 UPDATE 时由数据库自动刷新该字段
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


#FastAPI应用
#元信息展示在/docs和/redoc中
app = FastAPI(
    title="电商商品管理系统",
    description="FastAPI + MySQL + Pydantic 综合案例",
    version="2.0.0"
)

#锚定main所在文件路径，将本地static目录挂载到app_path路径，用于提供前端静态资源
path=pathlib.Path(__file__).resolve().parent
app.mount("/static",StaticFiles(directory=path / "static"),name="static")


#Pydantic模型
class ProductIn(BaseModel):
    """商品请求模型 创建/更新 用入参"""
    name: str = Field(default="未命名商品",
                      min_length=2,
                      max_length=50,
                      description="商品名称，2-50 个字符")
    price: float = Field(gt=0,
                         description="商品价格，必须大于 0")  # gt=0：必须 > 0
    stock: int = Field(default=0,
                       ge=0,
                       description="库存数量，不能为负数")  # ge=0：>= 0
    category: str = Field(default="未分类",
                          description="商品分类")
    supplier_id: Optional[int] = Field(default=None,
                                       description="供应商ID")

class ProductOut(BaseModel):  # 返回使用该类型
    """商品响应模型（不含 supplier_id -> 敏感信息不返回前端）"""
    id: int
    name: str
    price: float
    stock: int
    category: str
    created_at: datetime

    class Config:
        from_attributes=True #允许ORM对象转换（Pydantic v2 写法；v1 为 orm_mode=True）


class ProductListOut(BaseModel):
    """分页列表响应：总数 + 当前页信息 + 数据项"""
    total: int
    page: int
    page_size: int
    items: List[ProductOut]  # 每一项都会按 ProductOut 过滤字段


class MessageOut(BaseModel):
    """通用消息响应（如删除成功）"""
    message: str
    product_id: Optional[int] = None  #为什么单独置为None


#路由定义
#summary参数：生成文档使用
@app.get("/",response_class=HTMLResponse,summary="首页")
async def home():
    """生成前端主页"""
    with open(path /"static/index.html","r",encoding="utf-8") as f:
        return f.read()


#response_class和response_model区别：
#response_class：响应的外层载体，返回Response 类，决定用什么容器装
#response_model：响应数据的结构，返回Pydantic 模型，决定数据的格式规范


#summary、tags参数：文档组织分组使用，不影响功能
@app.get("/api/products",response_model=ProductListOut,   #model -- class区别
         summary="商品列表（分页 + 筛选 + 搜索）", tags=["商品管理"])
async def list_products(

        # Query 第一个参数是默认值；ge/le 为范围校验，description 写入文档
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
        category: Optional[str] = Query(None, description="分类筛选"),
        keyword: Optional[str] = Query(None, description="名称关键词搜索"),
        # 依赖注入：每个请求一个 Session
        db: Session = Depends(get_db)
):
    """从sql查询商品列表

        流程：
      1) 构造基础 query
      2) 按 category / keyword 追加过滤条件（可选）
      3) 先 count 得到总数（用于分页）
      4) 再 offset+limit 取当前页数据
    注意：total 必须在分页前统计，否则会得到当前页条数。

    """
    print("list_products函数被调用")
    query=db.query(Product)

    if category:
        query=query.filter(Product.category==category)

    if keyword:
        #like使用%通配；参数由SQLAlchemy参数化，避免SQL注入
        query=query.filter(Product.name.like(f"%{keyword}%"))  ##通配？

    total=query.count() #过滤后的总条数
    items=(query.order_by(Product.id)  #固定排序顺序
           .offset((page-1)*page_size)  #跳过前面页数的数据
           .limit(page_size)   #本页条数
            .all()
           )

    # 返回 dict 即可，FastAPI 会按 response_model 做字段过滤与类型转换
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@app.get("/api/products/{product_id}",response_model=ProductOut,
         summary="商品详情",tags=["商品管理"])
async def get_product(
        product_id:int = Path(...,gt=0),   #Path
        db: Session = Depends(get_db)
):
    """按ID查询单个商品，不存在则返回404"""
    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        #不存在
        raise HTTPException(status_code=404,detail=f"商品{product_id}不存在")
    return product


@app.post("/api/products",response_model=ProductOut,status_code=201,
          summary="创建商品",tags=["商品管理"])
async def create_product(product:ProductIn,db: Session = Depends(get_db)):
    """创建商品

    - 请求体由 ProductIn 校验（类型、范围、长度）
    - 校验通过后构造 ORM 对象，add → commit → refresh
    - refresh 用于从数据库回读自增 id、created_at 等字段
    - 响应经 ProductOut 过滤，不返回 supplier_id
    """
    new_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
        category=product.category,
        supplier_id=product.supplier_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)   #数据库刷新对象，拿到自增主键与默认时间
    return new_product


@app.put("/api/products/{product_id}",response_model=ProductOut,
         summary="更新商品",tags=["商品管理"])
async def update_product(
        product_id: int = Path(..., gt=0),  #Path()得到"/api/products/{product_id}"内的{product_id}
        product: ProductIn = None,  # 请求体；这里给 None 是为了让参数顺序合法，
        # 实际请求必须提供 body，否则会 422
        db: Session = Depends(get_db)
        ):
    """
    按 ID 全量更新商品。
    注意：
      - 这是「整体覆盖」式更新：name/price/stock/category 都会被请求体覆盖。
      - supplier_id 只在请求体显式提供时才更新，避免误清空外键。
      - 未做并发控制（如乐观锁），高并发下可能覆盖他人修改。
    """
    db_product=db.query(Product).filter(Product.id==product_id).first()
    if not db_product:
        raise HTTPException(status_code=404,detail=f"商品{product_id}不存在")

    db_product.name=product.name
    db_product.price=product.price
    db_product.stock=product.stock
    db_product.category=product.category
    if product.supplier_id is not None:
        db_product.supplier_id=product.supplier_id

    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/products/{product_id}",response_model=MessageOut,
            summary="删除商品",tags=["商品管理"])
async def delete_product(
        product_id: int = Path(..., gt=0),
        db:Session = Depends(get_db)
):
    """按ID删除商品，不存在则404
    此处为物理删除；
    生产环境中更推荐软删除（增加is_delete字段），以便审计与恢复；
    同时要注意外键约束（若其他表引用该商品则会删除失败）
    """
    db_product=db.query(Product).filter(Product.id==product_id).first()
    if not db_product:
        raise HTTPException(status_code=404,detail=f"商品{product_id}不存在")
    db.delete(db_product)
    db.commit()
    return {"message":f"商品{product_id}已删除","product_id":product_id}


@app.get("/api/categories",summary="获取所有分类",tags=["辅助接口"])
async def get_categories(db: Session = Depends(get_db)):
    """
    返回按sort_order升序排列的分类名列表

    只select了name列，减少数据传输；
    .call()返回Row元组列表，因此用r[0]取第一列
    """
    rows=db.query(Category.name).order_by(Category.sort_order).all()
    return {"categories": [r[0] for r in rows]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app,host="127.0.0.1",port=8000)




































