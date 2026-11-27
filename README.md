# LLM 应用工程实践 · 从 Python 到 RAG / Agent

## 两类内容

| 目录 | 定位 | 什么时候看 |
|---|---|---|
| [`projects/`](projects/) | **项目**：端到端作品，对外主入口 | 先看这里 |
| [`learning/`](learning/) | **学习过程**：12 个按知识点编号的模块，记录从跑通到改造的留痕 | 想看基础、或某个知识点怎么练的，再展开 |

`common/`（公共代码）、`docs/`（路线图与笔记）、`requirements.txt`、`.env.example` 是两类共用的支撑层，留在根目录，不属于内容分类。

## 项目（先看这里）

见 [`projects/README.md`](projects/README.md)：综合项目与旗舰项目的规划，以及一个项目 README 该写什么。当前为规划阶段，逐个落地后补实测数字与演示链接。

## 学习过程（按需展开）

见 [`learning/README.md`](learning/README.md)：12 个模块按学习顺序编号（01 Python 基础 → 12 服务化），每个模块有目标 / 知识点 / 怎么跑 / 我的改造 / 踩过的坑。编号即学习顺序，模块内 `01_`、`02_` 同理。

> 为什么收进一个子目录：第一屏只留两类内容，避免 12 个练习目录把项目淹掉；学习过程不删、不合并，想看细节随时展开。

## 目录

```
README.md            本文件（门面）
projects/            一类：项目
learning/            一类：学习过程（01~12 模块）
common/              支撑：密钥加载、模型客户端
docs/                支撑：学习路线、复盘笔记
requirements.txt
.env.example
LICENSE
```

## 快速开始

```powershell
git clone <本仓库地址> llm-app-dev-journey
cd llm-app-dev-journey

python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Git Bash: source .venv/Scripts/activate

pip install -r requirements.txt
Copy-Item .env.example .env           # 填入自己的 DEEPSEEK_API_KEY / VOLC_API_KEY

python common\config.py               # 自检配置（密钥、路径锚定）

# 已跑通的最小 RAG（学习过程示例）：
python learning\05_rag\01_naive_rag\native_rag.py   # 全量上下文 vs RAG 检索对照，需 .env 配好密钥
```

脚本里需要引用 `common/` 时，在开头加 5 行「向上找仓库根」的引导，见 [common/README.md](common/README.md)。

## 约定

- **目录**：`projects/` 放项目，`learning/01_`~`learning/12_` 放学习模块；模块内 `01_`、`02_` 是学习顺序；文件名用英文小写下划线。
- **密钥**：只放 `.env`，代码里一律 `from common.config import ...`。
- **提交**：`<type>(<module>): <做了什么>`，例如 `feat(05_rag): 手写句子级分块 + 前向重叠`。
- **注释**：写"为什么"，不写"是什么"。
- **数据**：未实测的数字写「待测」，不填估算值。
