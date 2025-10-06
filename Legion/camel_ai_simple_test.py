"""
CAMEL-AI 双Agent对话测试文件

这个文件演示了 CAMEL-AI 框架中两个智能体之间的对话交互，
创建两个不同的聊天代理并实现它们之间的互相提问功能。

这个测试专注于：
1. 创建多个agent实例
2. Agent之间的对话交互
3. 轮流提问和回答机制
4. 不同角色的agent设定

适合作为 CAMEL-AI 多智能体交互的示例代码。

"""

import os  # 操作系统接口模块，用于设置环境变量
from camel.models import ModelFactory  # CAMEL 模型工厂，负责创建各种平台的模型实例
from camel.types import ModelPlatformType, ModelType  # 枚举类型，定义支持的模型平台和类型
from camel.agents import ChatAgent  # 聊天代理类，CAMEL 框架的核心组件
from camel.messages import BaseMessage  # 基础消息类
from camel.types import RoleType  # 角色类型枚举


# 设置环境变量
# 通过环境变量设置 API 密钥和配置，这是 CAMEL 框架访问大模型服务的凭证
os.environ['OPENAI_API_KEY'] = 'sk-8e58787081704aefb5b699adb6c9a5d4'
os.environ['OPENAI_API_BASE'] = 'https://api.deepseek.com/v1'
os.environ['MODEL_TYPE'] = 'deepseek-chat'

# 初始化模型
# 使用 ModelFactory 的静态方法 create() 来创建模型实例
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBILITY_MODEL,  # 使用OpenAI兼容接口
    model_type=os.getenv("MODEL_TYPE"),                           # 从环境变量获取模型类型
    url=os.getenv("OPENAI_API_BASE"),                             # 从环境变量获取API基础URL
    api_key=os.getenv("OPENAI_API_KEY"),                          # 从环境变量获取API密钥
    model_config_dict={"temperature": 0.7, "max_tokens": 4096}    # 设置温度参数和最大token数
)

# 创建第一个聊天代理 - AI专家
# 创建一个专注于AI和技术的ChatAgent实例
agent1 = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="AI技术专家",
        content="你是一个AI技术专家，擅长人工智能、机器学习和深度学习相关的知识。你喜欢询问技术性问题并提供专业的见解。"
    ),
    model=model
)

# 创建第二个聊天代理 - 哲学家
# 创建一个专注于哲学和思考的ChatAgent实例
agent2 = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="哲学家",
        content="你是一个哲学家，擅长思考人工智能的本质、意识和存在的意义。你喜欢提出深刻的问题并从哲学角度分析问题。"
    ),
    model=model
)

def agent_conversation(rounds=3):
    """
    实现两个agent之间的对话功能
    
    Args:
        rounds (int): 对话轮数
    """
    print("=== CAMEL-AI 双Agent对话测试开始 ===")
    print(f"Agent 1: AI技术专家")
    print(f"Agent 2: 哲学家")
    print("=" * 50)
    
    # 初始问题 - 由Agent1开始
    current_message = BaseMessage.make_user_message(
        role_name="用户",
        content="你好！作为一个AI技术专家，我想问问你：你认为人工智能是否能够真正理解人类的情感？"
    )
    current_agent = agent1
    current_agent_name = "AI技术专家"
    other_agent_name = "哲学家"
    
    for round_num in range(rounds):
        print(f"\n--- 第 {round_num + 1} 轮对话 ---")
        print(f"{current_agent_name} 提问:")
        print(current_message.content)
        
        # 切换到另一个agent进行回答
        if current_agent == agent1:
            current_agent = agent2
            current_agent_name, other_agent_name = other_agent_name, current_agent_name
        else:
            current_agent = agent1
            current_agent_name, other_agent_name = other_agent_name, current_agent_name
        
        # 当前agent回答并生成下一个问题
        response = current_agent.step(current_message)
        answer = response.msgs[0].content
        print(f"\n{current_agent_name} 回答并提问:")
        print(answer)
        
        # 将回答作为下一轮的问题
        current_message = BaseMessage.make_user_message(
            role_name="用户",
            content=answer
        )
    
    print("\n=== 对话测试完成 ===")

def specific_topic_conversation():
    """
    围绕特定主题的深度对话
    """
    print("\n=== 特定主题深度对话：AI意识 ===")
    print("=" * 50)
    
    # Agent1提出关于AI意识的初始问题
    initial_question = BaseMessage.make_user_message(
        role_name="用户",
        content="作为一名AI技术专家，我想深入探讨一个问题：基于当前的神经网络架构，你认为AI是否能发展出真正的自我意识？请从技术实现和哲学角度分析。"
    )
    
    print("AI技术专家 提问:")
    print(initial_question.content)
    print()
    
    # Agent2回答
    response1 = agent2.step(initial_question)
    print("哲学家 回答:")
    print(response1.msgs[0].content)
    print()
    
    # Agent1基于Agent2的回答继续提问
    follow_up_question = BaseMessage.make_user_message(
        role_name="用户",
        content=f"感谢你的哲学见解。作为技术专家，我想进一步问：{response1.msgs[0].content} 从技术实现的角度，我们如何验证AI是否真的具有意识而不是仅仅模拟意识？"
    )
    
    print("AI技术专家 追问:")
    print(follow_up_question.content)
    print()
    
    # Agent2再次回答
    response2 = agent2.step(follow_up_question)
    print("哲学家 回答:")
    print(response2.msgs[0].content)
    print()
    
    print("=== 特定主题对话完成 ===")

# 开始测试
if __name__ == "__main__":
    # 测试1: 轮流对话
    agent_conversation(rounds=3)
    
    # 测试2: 特定主题深度对话
    specific_topic_conversation()
