-- ============================================================
-- 电商商品管理系统 - 建库建表脚本
-- 数据库：MySQL 8.0+
-- ============================================================

-- 1. 创建数据库
-- DROP DATABASE IF EXISTS ecommerce_db;
CREATE DATABASE ecommerce_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE ecommerce_db;


-- 2. 创建供应商表（用于演示supplier_id 外键，且该字段不返回给前端）
CREATE TABLE supplier(
    id    INT PRIMARY KEY AUTO_INCREMENT COMMENT'供应商ID',
    name  VARCHAR(100) NOT NULL COMMENT'供应商名称',
    contact VARCHAR(50) COMMENT'联系人',
    phone  VARCHAR(20) COMMENT'联系电话',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET =utf8mb4 COMMENT ='供应商表';


-- 3. 创建商品分类表
CREATE TABLE category(
    id  INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '分类名称',
    sort_order  INT DEFAULT 0 COMMENT '排序',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 4.创建商品表（核心表）
CREATE TABLE product(
    id          INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID',
    name        VARCHAR(50) NOT NULL COMMENT '商品名称（2-50字符）',
    price       DECIMAL(10, 2) NOT NULL COMMENT '商品价格（必须大于0）',
    stock       INT NOT NULL DEFAULT 0 COMMENT '库存数量（不能为负）',
    category    VARCHAR(50) NOT NULL DEFAULT '未分类' COMMENT '商品分类',
    supplier_id INT COMMENT '供应商ID（敏感字段，不对外返回）',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 约束
    CONSTRAINT chk_price CHECK(price>0),
    CONSTRAINT chk_stock CHECK (stock >= 0),
    CONSTRAINT chk_name_length CHECK (CHAR_LENGTH(name) BETWEEN 2 AND 50),

    -- 索引
    INDEX idx_category (category),
    INDEX idx_name (name),
    INDEX idx_supplier (supplier_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 查看表
SHOW  tables






















