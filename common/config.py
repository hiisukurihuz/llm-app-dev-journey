"""配置入口

用于调用各个大模型APIKEY

设计原则：
1.将APIKEY存入.env环境，上传GitHub时只上传.env.example，防止密钥泄露。 （踩坑点）
2.APIKEY缺失或调用异常时，抛出具体问题。    （踩坑点）
3.更换密钥只改.env

该模块心得：
1.路径用 Path(__file__) 锚定自身位置
2.fail-fast思路：检查放在 import 时机，启动即校验
    例：from common.llm import deepseek_client时与本模块联动，若密钥没配好，直接报错
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# 检验路径内是否配置.env
# 心得：Path(__file__)定到自身文件所在路径，.resolve()转为绝对路径，再跳到指定目录
REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / ".env"

#将.env写进环境变量表
load_dotenv(ENV_FILE)


def require(name: str) -> str:
    """从系统环境变量中查name，若不存在则给空串，将查不到和空串同时处理"""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"环境变量 {name} 未配置。\n"
            f"请在 {ENV_FILE} 中填写（可参考 .env.example），然后重新运行。"
        )
    return value


def optional(name: str, default: str) -> str:
    """首选读取到的环境变量，缺失时用默认值，此处为大模型默认URL。"""
    value = os.getenv(name, "").strip()
    return value or default


# ---------------------------------------------------------------- 密钥
# 心得：fail-fast思路：检查放在 import 时机，而不是用的时候。
#     例：from common.llm import deepseek_client时，若密钥没配好，直接报错

ds_key = require("DEEPSEEK_API_KEY")      # DeepSeek 开放平台
volc_key = require("VOLC_API_KEY")        # 火山方舟（Ark）

# ---------------------------------------------------------------- 默认配置
ARK_BASE_URL = optional("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
DEEPSEEK_BASE_URL = optional("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

ARK_CHAT_MODEL = optional("ARK_CHAT_MODEL", "deepseek-v4-pro-ga-260813")
ARK_EMBEDDING_MODEL = optional("ARK_EMBEDDING_MODEL", "doubao-embedding-vision-251215")


if __name__ == "__main__":
    # 自检，且在打印时隐藏key
    def mask(s: str) -> str:
        return s[:4] + "*" * 8 + s[-4:] if len(s) > 12 else "*" * len(s)

    print(f"配置文件   : {ENV_FILE}  (存在: {ENV_FILE.exists()})")
    print(f"DEEPSEEK   : {mask(ds_key)}")
    print(f"VOLC       : {mask(volc_key)}")
    print(f"ARK 地址   : {ARK_BASE_URL}")
    print(f"ARK 模型   : {ARK_CHAT_MODEL}")
    print(f"Embedding  : {ARK_EMBEDDING_MODEL}")
