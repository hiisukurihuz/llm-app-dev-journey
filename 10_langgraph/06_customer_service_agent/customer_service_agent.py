#一个模拟电商售后智能体的简单demo
import sqlite3  #用于本地持久化存储使用sqlite3
import uuid  #用于生成唯一标识符
from dataclasses import dataclass  #用于定义轻量级数据类（上下文对象）
from datetime import datetime  #用于记录真实时间戳
from pathlib import Path   #定位数据库文件路径
from typing import Annotated,TypedDict,Literal  #类型工具
from langchain_core.messages import AnyMessage,AIMessage  #消息类型
from langchain_core.tools import tool  # @tool装饰器：将普通函数转为 LangChain 工具
from langchain_openai import ChatOpenAI  #OpenAI兼容接口的聊天模型客户端
from langgraph.checkpoint.sqlite import SqliteSaver  ########SQLite持久化检查点   ###############################################
from langgraph.graph import StateGraph, START, END  #langgraph状态图构建器及内置起始/结束节点常量
from langgraph.graph.message import add_messages  # 消息列表 reducer：新消息追加而非覆盖
from langgraph.prebuilt import ToolNode  #工具预置节点：自动执行 LLM 返回的工具调用
from langgraph.runtime import Runtime  ############### 运行时对象，携带 context（上下文）与 store（长期记忆存储）#################
from langgraph.store.sqlite import SqliteStore  # SQLite 持久化长期记忆存储
from langgraph.types import interrupt, Command  #中断、恢复函数
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.llm import *

#初始化llm
llm=deepseek_client()
llm.chat.completions.create(
        model="deepseek-chat",
        temperature=0.9,
    )


############################# 工具函数定义 #############################
@tool
def search_knowledge_base(query:str)->str:
    """搜索根据用户问答搜索知识库"""
    kb={ # 知识库
        "退货": "7天无理由退货，需保持商品完好。",
        "保修": "电子类产品保修1年，需提供购买凭证。",
        "支付": "支持支付宝、微信、信用卡支付。",
        "营业时间": "人工客服在线时间：每天 9:00-21:00，全年无休。",
        "充电": "手机无法充电时，请先更换充电线和适配器，并清洁充电口；仍无法充电请联系售后检测。",
        "开机": "设备无法开机时，请长按电源键10秒强制重启，并确认电量充足。",
        "屏幕": "屏幕显示异常时，请先重启设备；若问题依旧，建议联系售后检测。",
        "电池": "电池耗电过快时，可降低屏幕亮度、关闭后台应用，必要时更换电池。"
    }
    if query in kb:
        return kb[query]   #关键字匹配精准搜索
    matched=[text for k,text in kb.items() if k in query]  #未命中时改用关键字包含匹配
    return "\n".join(matched) if matched else "未找到相关信息"


@tool
def query_order(order_id:str)->str:
    """查询快递数据"""
    order={
        "12345":"已发货，预计3天后到达",  #模拟订单号对应的订单情况，实际生产中可改为连接数据库
        "67890":"订单已签收"
    }
    return order.get(order_id,"未找到订单信息")


@tool
def get_bill_detail(user_id:str)->str:
    """根据用户的id查询订单消费详情"""
    return f"用户{user_id}的账单为：本月消费￥320，已出账￥150"


@tool
def new_product(user_id:str)->str:
    """向用户介绍新产品"""
    new_products=[
        {"name": "新款华为手机", "price": "4999元",
         "introduction": "全国产旗舰手机，大屏幕、折叠屏，高相机分辨率，外界相机镜头"},
        {"name": "新款超薄电脑", "price": "5999元",
         "introduction": "新款超薄电脑，轻松流畅办公，长续航，适合日常办公与学习"}
    ]
    return str(new_products)  #用于返回大模型整理,字符串即可


#大模型角色分支只绑定本领域所需函数，避免越权
product_toolset=[search_knowledge_base,new_product]  #产品专家：知识库查询 +新品查询
tech_toolset=[search_knowledge_base]  #工程专家：知识库查询 +问题解决
billing_toolset=[query_order,get_bill_detail] #订单工具：查询快递+消费详情
general_toolset=[search_knowledge_base]  #默认角色：知识库查询

llm_product=llm.bind_tools(product_toolset)  #大模型绑定工具，伪智能体
llm_tech=llm.bind_tools(tech_toolset)
llm_bill=llm.bind_tools(billing_toolset)
llm_general=llm.bind_tools(general_toolset)


############################# 自定义状态类型 #############################
class AgentState(TypedDict):  #自定义状态类
    """定义状态，用来再节点间传递数据"""
    messages:Annotated[list[AnyMessage],add_messages]
    intent:str  #记录意图
    current_agent:str #当前处理节点
    needs_approval:bool  #是否需人工审批
    approved:bool  #审批结果状态：只有通过/拒绝
    final_response:str #节点最终回复内容

#@dataclass首次使用，装饰器：自动给类添加样本代码，__repr__,__eq__等   #######################################
@dataclass
class CustomerContext:
    """运行时上下文：标识当前用户与会话id，做长期记忆时的隔离"""
    user_id:str  #用户id
    session_id:str  #唯一会话id


############################# 持久化存储（SQLite） #############################
BASE_DIR=Path(__file__).parent   #路径定位到当前脚本目录
CHECKPOINT_DB= BASE_DIR / "customer_agent_checkpoints.db"  #checkpoint存储db
MEMORY_DB= BASE_DIR / "customer_agent_memory.db"  #mem存储db


#checkpointer:持久化会话状态，保证进程重启后仍可继续会话、恢复审批中断
checkpointer=SqliteSaver(
    sqlite3.connect(str(CHECKPOINT_DB),  #连接db
    check_same_thread=False,  #允许跨线程复用连接
    timeout=30)
)
checkpointer.setup() #首次运行自动建表

#store：持久化用户会话记忆  同理checkpointer
#isolation_level=None开启自动提交，SqliteStore内部会自行BEGIN/COMMIT
store=SqliteStore(
    sqlite3.connect(str(MEMORY_DB), check_same_thread=False, timeout=30, isolation_level=None
))
store.setup()


def build_memory_text(memories)->str:
    """将长期记忆转化为提示词文本"""
    lines=[]
    for m in memories:
        intent=m.value.get("last_intent")   #memories格式{1:{"last_intent":"......."}}
        if intent:
            lines.append(f" 最近意图：{intent} （{m.value.get('updated_at','')}）")  #同时返回mem记录时间
    return "\n".join(lines) if lines else "--暂无最近意图"


############################# 意图识别函数 #############################
def classify_intent(state:AgentState,runtime:Runtime[CustomerContext]):
    """意图分类函数，根据用户输入识别用户意图"""
    user_msg=state["messages"][-1].content   #提取用户问题
    # 通过关键字匹配方式识别意图(生产中可改成用LLM识别)
    # 投诉优先判断：投诉内容里常同时出现“产品/退款”等词，后置会被误分流到其它专家
    if any(kw in user_msg for kw in ["投诉", "差评", "不满", "生气"]):
        intent = "complaint"  # 投诉
    elif any(kw in user_msg for kw in ["账单", "付款", "退款", "钱"]):
        intent = "billing"  # 账单相关
    elif any(kw in user_msg for kw in
             ["技术", "故障", "使用", "错误", "无法", "保修", "维修", "充电", "开机", "屏幕", "电池"]):
        intent = "tech"  # 技术相关咨询
    elif any(kw in user_msg for kw in ["产品", "功能", "价格", "推荐"]):
        intent = "product"  # 产品相关咨询
    else:
        intent = "general"  # 一般咨询

    #意图识别完成后，保存用户意图到长期记忆
    namespace=(runtime.context.user_id,"preferences")  #runtime.context都为固定写法，后接user_id命名
    runtime.store.put(namespace,f"intent:{intent}",
                      {
                          "last_intent": intent,
                          "updated_at": datetime.now().isoformat(timespec="seconds") #记录传入的最新意图并记录时间
                      }
                      )
    return {"intent":intent,"current_agent":intent}


def route_by_intent(state:AgentState) ->Literal["product", "tech", "billing", "complaint", "general"]:
    """路由函数：根据意图识别结果，路由到后续专家节点"""
    return state["intent"]


def route_after_expert_agent(state:AgentState) ->Literal["tools","final_response"]:
    """分发函数：判断专家节点后是否继续执行tools"""
    last_messages=state["messages"][-1]
    if getattr(last_messages,"tool_calls",None):
        return "tools"
    return "final_response"


def route_after_complaint(state: AgentState) -> Literal["human_approval", "end"]:
    """投诉专家之后：判断是否需要人工审批"""
    if state.get("needs_approval", False):
        return "human_approval"  # 需要审批则进入人工审批节点
    return "end"  # 否则直接结束


def route_after_approval(state: AgentState) -> Literal["process_complaint", "end"]:
    """审批后路由：通过则处理投诉，否则结束"""
    if state.get("approved", False):
        return "process_complaint"  # 审批通过，进入投诉处理节点
    return "end"  # 审批拒绝，结束流程


def generate_final_response(state: AgentState, runtime: Runtime[CustomerContext]):
    """工具执行后生成最终回复节点：把工具返回结果交给LLM，让其组织自然语言回答"""
    print("generate_final_response()被调用...")
    response = llm.invoke(state["messages"])
    return {"messages": [response], "final_response": response.content}


############################# 专家功能函数 #############################
def product_agent(state:AgentState,runtime:Runtime[CustomerContext]):
    """产品专家节点：处理跟产品相关任务，例如功能、价格、推荐等"""
    print("product_agent()被调用...")
    namespace=(runtime.context.user_id,"preferences")
    memories=runtime.store.search(namespace,limit=3)  #根据ID号查用户最新3笔长期记忆数据
    memory_text=build_memory_text(memories)  #调用函数将数据转化为提示词文本

    #开始构建提示词，调用llm
    messages=state["messages"]
    system_prompt = f"""你是电商平台的产品专家。当前用户ID：{runtime.context.user_id}
    用户历史偏好：{memory_text}
    请回答用户的产品相关问题，包括产品功能、价格、推荐等。
    工具使用规则：
    1. 当用户询问有哪些产品、新产品或要求推荐产品时，如果对话中还没有 new_product 的查询结果，必须先调用 new_product 工具，user_id 参数使用当前用户ID。
    2. 收到 new_product 的工具结果后，不要重复调用，直接根据返回内容推荐一款产品并说明理由，不要虚构价格或产品参数。
    3. search_knowledge_base 仅用于查询退货、保修、支付等规则，不要用它搜索产品清单或产品推荐。"""

    # 组合完整提示词
    full_messages = [("system", system_prompt)] + messages

    # 调用LLM
    print("开始调用LLM...")
    response = llm_product.invoke(full_messages)
    print("调用LLM结束.")

    return {"messages": [response]}


def tech_agent(state: AgentState, runtime: Runtime[CustomerContext]):
    """技术专家节点：处理故障排查、使用方法类问题，需要时调用工具查询技术资料"""
    print("tech_agent()被调用...")
    namespace = (runtime.context.user_id, "preferences")
    memories = runtime.store.search(namespace, limit=3)  # 根据ID号查用户最新的3笔长期记忆数据
    memory_text = build_memory_text(memories)  # 格式化为提示词文本

    messages = state["messages"]
    system_prompt = f"""你是电商平台的技术支持专家。当前用户ID：{runtime.context.user_id}
    用户历史偏好：{memory_text}
    请回答用户的技术问题，包括故障排查、错误处理、使用方法等。
    工具使用规则：
    1. 问题涉及退货、保修、支付、充电、开机、屏幕、电池等技术资料或平台规则时，必须先调用 search_knowledge_base 工具查询。
    2. 如果对话中已经有 search_knowledge_base 的查询结果，直接依据结果回答，不要重复调用。
    3. 工具没有返回结果时，基于通用排查经验给出建议，并提醒用户可联系官方售后，不要虚构产品参数和政策。"""

    print("开始调用LLM...")
    response = llm_tech.invoke([("system", system_prompt)] + messages)
    print("调用LLM结束.")

    return {"messages": [response]}


def billing_agent(state: AgentState, runtime: Runtime[CustomerContext]):
    """账单专家节点：处理付款、退款、发票、账单查询类问题"""
    print("billing_agent()被调用...")
    namespace = (runtime.context.user_id, "preferences")
    memories = runtime.store.search(namespace, limit=3)  # 根据ID号查用户最新的3笔长期记忆数据
    memory_text = build_memory_text(memories)  # 格式化为提示词文本

    # 构建提示词，调用LLM
    messages = state["messages"]
    system_prompt = f"""你是电商平台的账单专家。当前用户ID：{runtime.context.user_id}
    用户历史偏好：{memory_text}
    请回答用户的账单相关问题，包括付款、退款、发票等。
    工具使用规则：
    1. 查询订单状态时调用 query_order 工具，订单号从用户消息中提取。
    2. 查询账单金额时调用 get_bill_detail 工具，user_id 参数使用当前用户ID。
    3. 收到工具结果后直接回答用户，不要重复调用同一个工具，不要虚构账单金额。"""

    print("开始调用LLM...")
    response = llm_bill.invoke([("system", system_prompt)] + messages)
    print("调用LLM结束.")

    return {"messages": [response]}


def general_agent(state: AgentState, runtime: Runtime[CustomerContext]):
    """综合客服节点：处理无法归入其他类别的一般咨询"""
    print("general_agent()被调用...")
    namespace = (runtime.context.user_id, "preferences")
    memories = runtime.store.search(namespace, limit=3)  # 根据ID号查用户最新的3笔长期记忆数据
    memory_text = build_memory_text(memories)  # 格式化为提示词文本

    # 构建提示词，调用LLM
    messages = state["messages"]
    system_prompt = f"""你是电商平台的综合客服专家。当前用户ID：{runtime.context.user_id}
    用户历史偏好：{memory_text}
    请回答用户的一般咨询问题。如果问题涉及产品、技术、账单或投诉，
    请引导用户说明具体意图，不要虚构平台没有的服务和价格。
    工具使用规则：
    1. 涉及退货、保修、支付、营业时间等平台规则时，必须先调用 search_knowledge_base 查询，再依据查询结果回答，不要凭记忆编造。
    2. 只调用与用户问题直接相关的工具；工具没有返回结果时，直接回答或引导用户说明需求，不要反复换关键词重复调用。"""

    print("开始调用LLM...")
    response = llm_general.invoke([("system", system_prompt)] + messages)
    print("调用LLM结束.")

    return {"messages": [response]}


def complaint_agent(state: AgentState, runtime: Runtime[CustomerContext]):
    """投诉专家节点：记录投诉并标记需要人工审批"""
    print("complaint_agent()被调用...")
    # 记录投诉信息到长期记忆
    complaint_record = {
        "complaint": state["messages"][-1].content,  # 投诉原文
        "session_id": runtime.context.session_id,  # 所属会话
        "timestamp": datetime.now().isoformat(timespec="seconds"),  # 真实投诉时间
    }
    # 存入独立命名空间 (user_id, "complaints")，便于后续审计/查询
    complaint_namespace = (runtime.context.user_id, "complaints")
    runtime.store.put(complaint_namespace, str(uuid.uuid4()), complaint_record)

    # 标记需要人工审批，并先回复用户一条提示消息
    return {
        "messages": [AIMessage(content="您的投诉已收到，需要经理审批处理，请稍候...")],
        "needs_approval": True,
    }


def human_approval_node(state: AgentState):
    """人工审批节点：通过 interrupt 暂停图执行，等待经理审批后恢复"""
    print("human_approval_node()被调用，等待审批...")
    # 取最近一条用户消息作为待审批的投诉原文（当前位置的最后一条消息是 AI 的受理提示）
    complaint_text = next(
        (m.content for m in reversed(state["messages"]) if m.type == "human"), ""
    )
    # interrupt() 暂停执行，向外部抛出审批请求；恢复时返回外部传入的输入
    user_input = interrupt({
        "type": "complaint_approval",  # 中断类型标识
        "complaint": complaint_text,  # 待审批的投诉内容
        "message": "请经理审批此投诉请求：是否批准处理？",  # 提示文案
    })

    # 从恢复输入中读取审批结果，默认不通过
    if user_input.get("approved", False):
        return {
            "approved": True,
            "messages": [AIMessage(content="投诉已审批通过，正在为您处理...")],
        }
    return {
        "approved": False,
        "messages": [AIMessage(content="投诉已拒绝，如有疑问请联系人工客服。")],
    }


def process_complaint_node(state: AgentState):
    """处理投诉节点（审批通过后执行）：调用 LLM 生成专业解决方案"""
    print("process_complaint_node()被调用...")
    # 取最近一条用户消息作为投诉原文，避免把 AI 的受理提示当成用户诉求
    complaint_text = next(
        (m.content for m in reversed(state["messages"]) if m.type == "human"), ""
    )
    response = llm.invoke([
        ("system", "你是投诉处理专家，请为用户提供专业的投诉解决方案，并安抚用户情绪。"),
        ("user", f"用户投诉内容：{complaint_text}"),
    ])
    return {
        "messages": [AIMessage(content=f"投诉处理完成：{response.content}")],
        "final_response": response.content,
    }


# 创建图
builder = StateGraph(AgentState)

# 添加节点：5 个专家各自独立成一条并列分支，互不交叉
builder.add_node("classify_intent", classify_intent)  # 意图分类节点
builder.add_node("product_agent", product_agent)  # 产品专家节点
builder.add_node("product_tools", ToolNode(product_toolset))  # 产品分支专属工具节点
builder.add_node("product_final", generate_final_response)  # 产品分支最终回复
builder.add_node("tech_agent", tech_agent)  # 技术专家节点
builder.add_node("tech_tools", ToolNode(tech_toolset))  # 技术分支专属工具节点
builder.add_node("tech_final", generate_final_response)  # 技术分支最终回复
builder.add_node("billing_agent", billing_agent)  # 账单专家节点
builder.add_node("billing_tools", ToolNode(billing_toolset))  # 账单分支专属工具节点
builder.add_node("billing_final", generate_final_response)  # 账单分支最终回复
builder.add_node("complaint_agent", complaint_agent)  # 投诉专家节点
builder.add_node("human_approval", human_approval_node)  # 人工审批节点（中断点）
builder.add_node("process_complaint", process_complaint_node)  # 投诉处理节点
builder.add_node("general_agent", general_agent)  # 综合客服节点
builder.add_node("general_tools", ToolNode(general_toolset))  # 综合分支专属工具节点
builder.add_node("general_final", generate_final_response)  # 综合分支最终回复


# 添加边
builder.add_edge(START, "classify_intent")  # START -> 意图识别节点
builder.add_conditional_edges(
    "classify_intent",  # 上一个节点
    route_by_intent,  # 路由函数
    {
        "product": "product_agent",
        "tech": "tech_agent",
        "billing": "billing_agent",
        "complaint": "complaint_agent",
        "general": "general_agent",
    }
)


# 产品专家分支：产品专家 -> 产品工具，产品工具 -> 产品专家 ->决定是否再调用工具，还是直接返回最终回复
builder.add_conditional_edges(
    "product_agent",
    route_after_expert_agent,
    {"tools": "product_tools", "final_response": "product_final"},
)
builder.add_edge("product_tools", "product_agent")
builder.add_edge("product_final", END)


# 技术专家分支
builder.add_conditional_edges(
    "tech_agent",
    route_after_expert_agent,
    {"tools": "tech_tools", "final_response": "tech_final"},
)
builder.add_edge("tech_tools", "tech_agent")
builder.add_edge("tech_final", END)


# 账单专家分支
builder.add_conditional_edges(
    "billing_agent",
    route_after_expert_agent,
    {"tools": "billing_tools", "final_response": "billing_final"},
)
builder.add_edge("billing_tools", "billing_agent")
builder.add_edge("billing_final", END)


# 投诉专家分支：记录投诉 -> 人工审批中断 -> 审批通过后处理投诉
builder.add_conditional_edges(
    "complaint_agent",
    route_after_complaint,
    {
        "human_approval": "human_approval",
        "end": END,
    }
)
builder.add_conditional_edges(
    "human_approval",
    route_after_approval,
    {
        "process_complaint": "process_complaint",
        "end": END,
    }
)
builder.add_edge("process_complaint", END)


# 综合客服分支
builder.add_conditional_edges(
    "general_agent",
    route_after_expert_agent,
    {"tools": "general_tools", "final_response": "general_final"},
)
builder.add_edge("general_tools", "general_agent")
builder.add_edge("general_final", END)

# 编译图
graph = builder.compile(checkpointer=checkpointer, store=store)


def run_customer_service(user_id:str,session_id:str,user_message:str):
    """执行智能体"""
    config={"configurable":{"thread_id":session_id}}
    context=CustomerContext(user_id=user_id,session_id=session_id)  #存入用户id会话id
    result=graph.invoke(
        {
            "messages": [("user", user_message)],  # 用户问题提示词
        },
        config=config,
        context=context
    )

    # 投诉场景会在human_approval节点中断：打印审批请求，模拟经理审批通过后恢复执行
    if "__interrupt__" in result:
        print(f"审批请求: {result['__interrupt__'][0].value}")
        result = graph.invoke(Command(resume={"approved": True}), config=config, context=context)

    # 打印对话消息
    for msg in result["messages"]:
        print(f"{msg.type}: {msg.content}")
    print("=" * 50)

    return result

def check_persistent_data():
    """查看SQlite中持久化的长期记忆与会话检查点数据"""
    print("=" * 50)
    print(f"长期记忆库：{MEMORY_DB}")

    memory_conn=sqlite3.connect(str(MEMORY_DB))
    print("memory tables:",[t[0] for t in memory_conn.execute(
        "select name from sqlite_master where type='table'"
    )])
    for row in memory_conn.execute("select prefix, key, value from store"):
        print("memory row:", row)
    memory_conn.close()

    print(f"检查点库：{CHECKPOINT_DB}")
    checkpoint_conn = sqlite3.connect(str(CHECKPOINT_DB))
    print("checkpoint tables:", [r[0] for r in checkpoint_conn.execute(
        "select name from sqlite_master where type='table'")])
    print("threads:", [r[0] for r in checkpoint_conn.execute(
        "select distinct thread_id from checkpoints")])
    checkpoint_conn.close()


#主程序执行
if __name__ == "__main__":
    #每次运行使用新的session_id：同一用户开新会话,长期记忆仍可跨会话复用；
    #若固定session_id，持久化检查点会把历史消息不断堆叠到同一会话中
    session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"


    # 1. 产品咨询：应路由到 product_agent
    # run_customer_service(
    #     user_id="alice_001",
    #     session_id="session_001",
    #     user_message="我想了解一下你们有什么电子产品？推荐一款性价比高的。"
    # )

    # 2. 技术问题：应路由到 tech_agent
    run_customer_service(
        user_id="bob_002",
        session_id=session_id,
        user_message="购买你们的产品，保修期是多久？"
    )

    # 3. 账单查询：应路由到 billing_agent，触发 query_order / get_bill_detail 工具
    # run_customer_service(
    #     user_id="carol_003",
    #     session_id="session_003",
    #     user_message="帮我查一下本月账单和订单12345的状态"
    # )

    # 4. 投诉建议：应路由到 complaint_agent，随后在 human_approval 处中断等待审批
    # run_customer_service(
    #     user_id="dave_004",
    #     session_id="session_004",
    #     user_message="我非常不满，服务太差了，我要投诉！"
    # )

    # 5. 一般咨询：应路由到 general_agent
    # run_customer_service(
    #     user_id="eve_005",
    #     session_id="session_005",
    #     user_message="你们营业时间是什么时候？"
    # )

    # 查看持久化结果：长期记忆表数据 + 已保存的会话 thread
    check_persistent_data()








































