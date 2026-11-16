"""全仓库公共模块。

提供两个东西：
    common.config  —— 从仓库根目录的 .env 读密钥与默认配置
    common.llm     —— 构造 ChatOpenAI / Ark / OpenAI 客户端的便捷函数

在子目录的脚本里这样引用（"向上找到含 common/ 的仓库根"，任意层级都能用）：

    import sys
    from pathlib import Path

    _root = Path(__file__).resolve().parent
    while not (_root / "common").is_dir():
        _root = _root.parent
    sys.path.insert(0, str(_root))

    from common.config import ds_key, volc_key
    from common.llm import chat_model

详见 common/README.md。
"""
