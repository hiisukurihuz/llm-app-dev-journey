#self-consistency自洽性
#改造：新增计算处理自洽性后的成本变化

#sys.path锚定程序所在的路径，保证clone代码时不会因为路径不一致而无法调用common.llm
#后续可改进
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.llm import deepseek_client
from collections import Counter
import re, json
import time

# 踩坑点：约束模型不可靠，加固程序才正解
# 原函数：将大模型输出结果由自然语言转为{"accurate": false}格式方便后续统计，但更换prompt后约束不住
# def parse_verdict(text: str):
#     # .search 找第一个 {...}；r"" 关闭 Python 层转义；.*? 非贪婪；re.S 让 . 匹配换行
#     m = re.search(r"\{.*?\}", text, re.S)  #search返回一个match对象
#     # .group() 将match片段从原文切出；json.loads将对象解析成dict；.get找到"accurate"的布尔字段，布尔值用于后续统计
#     return json.loads(m.group()).get("accurate") if m else None

# 添加补丁为新函数
def parse_verdict(text: str):
    m = re.search(r'\{\s*"accurate"\s*:\s*(?:true|false)\s*\}', text, re.S)
    if not m:
        return None     #解析失败返回none
    try:
        return json.loads(m.group()).get("accurate")
    except json.JSONDecodeError:
        return None

prom="""
你是一个严谨的判断题答题器。先写 1-2 句推理，最后一行只输出
JSON：{"accurate": true} 或 {"accurate": false}，不要输出其他内容。

问题：袋中有 3 个红球、2 个蓝球，不放回地连续抽出 2 个。
"至少抽到 1 个红球"的概率大于 0.8，这个说法正确吗？

"""

client=deepseek_client()
#改造：增加计算tokens和时间成本
def get_conn(prompt):
    t0 = time.perf_counter() #单调时钟
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    elapsed = time.perf_counter() - t0
    return resp, elapsed

N=5  #重复次数，用于计算tokens成本
results = []
temp=[]
usages=[] #tokens统计
latencies=[] #延时统计
for i in range(N):
    temp = get_conn(prom)
    text = temp[0].choices[0].message.content
    print(f"--- 第 {i} 次 ---\n{text}")
    results.append(parse_verdict(text))  #得到一个布尔列表
    #resp.usage内存有token数据
    u = temp[0].usage
    usages.append({
        "prompt": getattr(u, "prompt_tokens", 0),    #getattr安全取值，找不到符合变量名的对象时不奔溃
        "completion": getattr(u, "completion_tokens", 0),
        "hit": getattr(u, "prompt_cache_hit_tokens", 0),
        "miss": getattr(u, "prompt_cache_miss_tokens", 0),
    })
    latencies.append(temp[1])

#改造：计算成本
print("token 输入/输出:", sum(x["prompt"] for x in usages),
                        sum(x["completion"] for x in usages))
hit  = sum(x["hit"]  for x in usages)
miss = sum(x["miss"] for x in usages)
print("缓存命中率:", round(hit / (hit + miss), 2) if hit + miss else "无数据")
print("每次延迟(s):", [round(x, 2) for x in latencies])
print("总耗时(s):", round(sum(latencies), 2))
#结论：tokens消耗≈N倍，成本随次数等比例涨；时间成本随网络环境波动不可预测性上涨


#统计自洽性投票前进行过滤，valid获取有效票数（判断r为bool时才统计）
valid = [r for r in results if isinstance(r, bool)]
coverage = len(valid) / len(results)   #有效票占比

if len(valid) < 3:   #有效样本过少,2/2的情况下一致率100%，但无实际意义   为什么取3？ ->3/5是本次示例能形成多数的最小样本
    print(f"有效票不足（{len(valid)}/5），数据不足，转人工复核")
else:
    winner, n = Counter(valid).most_common(1)[0]
    rate = n / len(valid)
    print(results, "有效票:", valid)
    #有效率取两位有效小数
    print("有效率:", round(coverage, 2), "一致率:", round(rate, 2))
    #0.8为本示例特供，实际生产中应以错误代价和成本为考量
    print("可用于自动化" if rate >= 0.8 and coverage >= 0.8 else "应转人工复核")
