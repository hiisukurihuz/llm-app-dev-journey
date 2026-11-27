# common · 全仓库公共代码

跨模块复用的东西只放这里，**不要**在每个模块里复制一份 `global_var.py`。

| 文件 | 作用 |
|---|---|
| `config.py` | 从仓库根的 `.env` 读密钥与默认配置；缺 key 立刻报错 |
| `llm.py` | `chat_model()` / `deepseek_client()` / `ark_client()` 三个工厂函数 |

## 一、准备 `.env`

```powershell
Copy-Item .env.example .env      # PowerShell
cp .env.example .env             # Git Bash
```

然后把 `.env` 里的两个占位值换成真实密钥。`.env` 已在 `.gitignore` 里，**不会进仓库**。

## 二、在任意子目录的脚本里引用（复制这 5 行到脚本开头）

```python
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
while not (_root / "common").is_dir():
    _root = _root.parent
sys.path.insert(0, str(_root))

from common.config import ds_key, volc_key
```

为什么不用 `from global_var import *`？
因为脚本散落在 `learning/05_rag/04_rerank/` 这样的多层目录里，Python 只把"脚本所在目录"加进搜索路径，
向上找根目录是唯一在任意层级都能用、又不需要配环境变量的写法。

> 另一种等价做法：在仓库根执行 `$env:PYTHONPATH="."`（PowerShell）/ `export PYTHONPATH=.`（Git Bash），
> 之后直接 `python learning/07_langchain/01_model_io/demo01.py` 也能 import。缺点是每开一个新终端都要设一次。

## 三、常用写法

```python
# 1) 只要 key
from common.config import ds_key, volc_key

# 2) LangChain 的 ChatOpenAI（默认火山方舟 + 默认模型）
from common.llm import chat_model
llm = chat_model()
print(llm.invoke("用一句话解释什么叫 RAG").content)

# 3) 原生 OpenAI SDK 直连 DeepSeek（需要原始返回结构时用）
from common.llm import deepseek_client
client = deepseek_client()
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
)

# 4) 火山方舟客户端（Embedding / 多模态）
from common.llm import ark_client
ark = ark_client()
```

> **别混用两个客户端**：`chat_model()` 返回 `ChatOpenAI`（LangChain / LangGraph 用，有 `bind_tools()` / `invoke()`）；
> `deepseek_client()` 返回原生 `openai.OpenAI`（只有 `chat.completions.create()`，没有 `bind_tools` / `invoke`）。
> 把 `deepseek_client()` 接进 `bind_tools()` 会在启动阶段直接 `AttributeError`；只有需要原始返回结构（usage、思考链）时才用它，
> 且 `create()` 必须带 `messages`，别把调试调用留在模块顶层。

## 四、自检

```powershell
cd D:\PythonProject\llm-app-dev-journey
python common\config.py
```

正常输出类似：

```
配置文件   : ...\llm-app-dev-journey\.env  (存在: True)
DEEPSEEK   : sk-1****abcd
VOLC       : ark-****wxyz
ARK 地址   : https://ark.cn-beijing.volces.com/api/v3
```
