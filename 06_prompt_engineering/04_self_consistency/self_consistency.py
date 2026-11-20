#self-consistency一致性

#sys.path锚定程序所在的路径，保证clone代码时不会因为路径不一致而无法调用common.llm
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.llm import deepseek_client
from collections import Counter
import re, json

def parse_verdict(text: str):
    m = re.search(r'\{\s*"accurate"\s*:\s*(?:true|false)\s*\}', text, re.S)
    if not m:
        return None
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
def get_conn(prompt):
    resp=client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    text = resp.choices[0].message.content
    return text

results = []
for i in range(5):
    text = get_conn(prom)
    print(f"--- 第 {i} 次 ---\n{text}")
    results.append(parse_verdict(text))

valid = [r for r in results if isinstance(r, bool)]
coverage = len(valid) / len(results)

if len(valid) < 3:
    print(f"有效票不足（{len(valid)}/5），数据不足，转人工复核")
else:
    winner, n = Counter(valid).most_common(1)[0]
    rate = n / len(valid)
    print(results, "有效票:", valid)
    print("有效率:", round(coverage, 2), "一致率:", round(rate, 2))
    print("可用于自动化" if rate >= 0.8 and coverage >= 0.8 else "应转人工复核")


