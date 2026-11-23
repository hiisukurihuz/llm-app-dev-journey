#最小的大模型运行示例
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


#连接火山方舟模型（embedding模型）
embedding_client=ark_client()
# 获取单个文本的嵌入向量
def get_embedding(text):
    """获取单个文本的嵌入向量"""
    resp = embedding_client.multimodal_embeddings.create(
        model="doubao-embedding-vision-251215",
        input=[{"type": "text", "text": text}]
    )
    # 返回embedding向量
    return resp.data.embedding


#将知识库中的所有句子转换成向量
kb_emds=[]
for i,kb_text in enumerate(knowledge_base):
    emb=get_embedding(kb_text)  #转换向量
    kb_emds.append(emb)  #添加到列表保存

client=deepseek_client()
#改造：增加计算tokens和时间成本
def get_conn(prompt):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return resp.choices[0].message.content


user_query = "人工智能技术的作用"

query_embedding = get_embedding(user_query)

prompt=build_prompt(prompt_template,
                    info=kb_emds,
                    query=query_embedding)

result=get_conn(prompt)


if __name__=="__main__":
    print(result)








