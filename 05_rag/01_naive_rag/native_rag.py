#全量上下文与RAG检索区别
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.llm import *
import numpy as np

#设置知识库
knowledge_base = [
    "机器学习是人工智能的一部分",
    "自然语言处理处理文本数据",
    "计算机视觉识别图像内容",
    "数据仓库用来存储海量数据",
    "数据透视表用来分析数据",
    "计算机网络用来连接计算机设备",
    "伊朗和美国在巴基斯坦进行了停战谈判"
]

#设置prompt模板
prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。

已知信息:
__INFO__

用户问：
__QUERY__

请用中文回答用户问题。
"""

user_query = "人工智能技术的作用"
TOP_K = 3 # 筛选相似度（或相关程度）最高的3个句子

######################### 全量上下文检索 ###############################
#拼接提示词函数
def build_prompt(prompt_template,**kwargs):
    """
    构建动态提示词，将模板中的变量替换为实际值

    prompt_template:提示词模板字符串，包含__变量__格式的占位符
    **kwargs:关键字参数，用于替换模板中的变量
    """
    prompt=prompt_template #初始化模板

    for k,v in kwargs.items():
        if isinstance(v,str): #如果传入的关键字参数value是字符串
            val=v
        elif isinstance(v,list) and all(isinstance(tem,str) for tem in v): #如果value是列表，且所有元素是字符串
            val="\n".join(v) #用换行符连接列表所有元素
        else:
            val=str(v)

        placeholder=f"__{k.upper()}__"  #构造模板中使用的占位符，准备替换
        prompt=prompt.replace(placeholder,val) #执行替换
    return prompt



def get_conn(client, prompt):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return resp.choices[0].message.content


#关系型数据库检索
def get_query(client, prompt):
    return get_conn(client, prompt)


######################### RAG检索 ###############################

# 获取单个文本的嵌入向量
def get_embedding(embedding_client, text):
    resp = embedding_client.multimodal_embeddings.create(
        model="doubao-embedding-vision-251215",
        input=[{"type": "text", "text": text}]
    )
    return resp.data.embedding


#计算向量的余弦相似度
def cosine_sim(a,b):  #计算a,b余弦相似度
    a,b=np.array(a),np.array(b)  #将a,b转换成数组
    dot_product = np.dot(a,b)   #a和b两个数组（向量）做点乘（相似度）
    #将相似度转换到-1~1 范围
    norm_a = np.linalg.norm(a)   #向量a的模长（向量的长度）
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0
    else:
        return dot_product/(norm_a*norm_b)


#RAG检索
def embed_text(kb_emds,query_embedding,top_k=TOP_K):
    #依次计算query向量和知识库中每个向量的相似度
    result = []  # 计算结果
    for i, emb in enumerate(kb_emds):  # 遍历向量列表
        similarity = cosine_sim(query_embedding, emb)  # 计算余弦相似度
        result.append((knowledge_base[i], similarity, i))  # 原句子，相似度，序号  作为元组存入结果列表

    # 对results进行排序
    result.sort(key=lambda x: x[1], reverse=True)  # x表示列表中的元素，x[1]表示排序依据，根据第二个值（相似度）排序
    return result[:top_k]


def main():
    client = deepseek_client()
    embedding_client = ark_client()

    # 对照：全量上下文直接生成
    full_prompt = build_prompt(prompt_template, info=knowledge_base, query=user_query)
    print("全量上下文检索结果：", get_query(client, full_prompt), "\n")
    print("=" * 20)

    # Retrieval：向量化 + TopK
    query_embedding = get_embedding(embedding_client, user_query)
    kb_emds = [get_embedding(embedding_client, t) for t in knowledge_base]
    top_chunks = embed_text(kb_emds, query_embedding)
    for text, simi, index in top_chunks:
        print(f"相似度：{simi},原句子：{text}")

    # Augmentation + Generation：把 TopK 原文本拼回 prompt，再调一次模型
    context = [text for text, _, _ in top_chunks]
    rag_prompt = build_prompt(prompt_template, info=context, query=user_query)
    print("\nRAG 生成结果：", get_conn(client, rag_prompt))


if __name__=="__main__":

    main()










