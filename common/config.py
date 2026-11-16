"""全仓库统一的配置入口。

踩坑点：
缺 key 时立刻抛错并告诉你怎么办，而不是跑到一半返回空字符串。
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# 本文件在 <仓库根>/common/config.py，所以 parents[1] 就是仓库根
REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / ".env"

load_dotenv(ENV_FILE)


def require(name: str) -> str:
    """读取一个必需的环境变量；缺失时给出可操作的报错。"""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"环境变量 {name} 未配置。\n"
            f"请在 {ENV_FILE} 中填写（可参考 .env.example），然后重新运行。"
        )
    return value


def optional(name: str, default: str) -> str:
    """读取一个可选的环境变量，缺失时用默认值。"""
    value = os.getenv(name, "").strip()
    return value or default


# ---------------------------------------------------------------- 密钥
ds_key = require("DEEPSEEK_API_KEY")      # DeepSeek 开放平台
volc_key = require("VOLC_API_KEY")        # 火山方舟（Ark）

# ---------------------------------------------------------------- 默认配置
ARK_BASE_URL = optional("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
DEEPSEEK_BASE_URL = optional("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

ARK_CHAT_MODEL = optional("ARK_CHAT_MODEL", "deepseek-v4-pro-ga-260813")
ARK_EMBEDDING_MODEL = optional("ARK_EMBEDDING_MODEL", "doubao-embedding-vision-251215")


if __name__ == "__main__":
    # 自检：只打印"有没有配好"，不打印密钥本身
    def mask(s: str) -> str:
        return s[:4] + "*" * 8 + s[-4:] if len(s) > 12 else "*" * len(s)

    print(f"配置文件   : {ENV_FILE}  (存在: {ENV_FILE.exists()})")
    print(f"DEEPSEEK   : {mask(ds_key)}")
    print(f"VOLC       : {mask(volc_key)}")
    print(f"ARK 地址   : {ARK_BASE_URL}")
    print(f"ARK 模型   : {ARK_CHAT_MODEL}")
    print(f"Embedding  : {ARK_EMBEDDING_MODEL}")
