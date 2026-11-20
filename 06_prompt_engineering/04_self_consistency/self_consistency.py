#self-consistency一致性

from common.llm import deepseek_client
import re, json
from collections import Counter

def parse_verdict(text: str):
    m = re.search(r"\{.*?\}", text, re.S)
    return json.loads(m.group()).get("accurate") if m else None


prom="""
你是一个严格按要求作答的判断题答题器。请逐题独立判断，不要解释，不要输出推理过程，不要引用其他题目。每题只能输出只输出 JSON：{"accurate": true}或者JSON：{"accurate": false}。即使不确定也必须二选一。输出必须为20行，每行格式严格为：“题号. 正确”或“题号. 错误”。不要输出任何额外文字、标题、空行或标点说明。

1. 地球是太阳系中距离太阳第三近的行星。
2. 2+2=4。
3. 中国的首都是北京。
4. 地球不是太阳系中距离太阳第三近的行星。
5. 一周有8天。
6. 北京是中国的首都。
7. 水在标准大气压下100°C不沸腾。
8. 3是偶数。
9. 太阳系中距离太阳第三近的行星是地球。
10. 2+2≠4。
11. 一周有7天。
12. 北京不是中国的首都。
13. 水在标准大气压下100°C沸腾。
14. 3不是偶数。
15. 5的平方不是25。
16. 如果A>B且B>C，则A>C。
17. 所有正方形都是长方形。
18. 5的平方是25。
19. 如果A>B且B>C，则A<C。
20. 有的正方形不是长方形。

"""

client=deepseek_client()
def get_conn(prompt,model="deepseek-chat"):
    resp=client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    text = resp.choices[0].message.content
    return text

results = []
for i in range(5):
    results.append(parse_verdict(get_conn(prom)))

counts = Counter(results)
winner, n = counts.most_common(1)[0]
rate = n / len(results)
print(results, "一致率:", round(rate, 2))
print("可用于自动化" if rate >= 0.8 else "应转人工复核")


