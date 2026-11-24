"""大模型客户端的便捷函数。

实际项目内通过from common.llm import chat_model调用大模型。

依赖是延迟导入的：用不到哪个库，就不会因为没装它而报错。
"""

from __future__ import annotations

from . import config


def chat_model(model: str | None = None, *, base_url: str | None = None, api_key: str | None = None, **kwargs):
    """返回一个 LangChain 的 ChatOpenAI，默认走火山方舟。

    例：
        from common.llm import chat_model
        llm = chat_model()
        print(llm.invoke("用一句话解释 RAG").content)
    """
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:  # pragma: no cover
        raise ImportError("请先安装: pip install langchain-openai") from exc

    return ChatOpenAI(
        model=model or config.ARK_CHAT_MODEL,
        openai_api_key=api_key or config.volc_key,
        openai_api_base=base_url or config.ARK_BASE_URL,
        **kwargs,
    )


def deepseek_client():
    """原生 OpenAI SDK 客户端，直连 DeepSeek 官方接口。

    适合需要直接拿到 SDK 原始返回结构的场景（思考链、usage、finish_reason）；
    只做普通问答时用 chat_model()。
    """
    try:
        from openai import OpenAI
    except ImportError as exc: # pragma: no cover
        raise ImportError("请先安装: pip install openai") from exc

    return OpenAI(api_key=config.ds_key, base_url=config.DEEPSEEK_BASE_URL)


def ark_client():
    """火山方舟 SDK 客户端（Embedding / 多模态用）。"""
    try:
        from volcenginesdkarkruntime import Ark
    except ImportError as exc:  # pragma: no cover
        raise ImportError("请先安装: volcengine-ark-runtime") from exc

    return Ark(api_key=config.volc_key)
