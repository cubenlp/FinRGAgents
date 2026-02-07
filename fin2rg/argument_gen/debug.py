from autogen import AssistantAgent, UserProxyAgent,GroupChatManager,GroupChat, config_list_from_json

config_list = config_list_from_json(env_or_file="/sshfs/liushu/Fin2RG/OAI_CONFIG_LIST")

'''
流程：
1.先利用 assistant 生成一些与主题相关的角色
2.创建1个user_proxy与3个agent 并将其加入一个group_chat
2.让user_proxy开启对话 对话顺序为user_proxy，persona_1，persona_2，persona_3
3.对话完成后生成大纲

存在的问题：
1.没能实现直接让user_proxy生成角色并进行分配 
2.目前每个agent都有概率会生成一份大纲，并且一轮对话结束就开始生成大纲
3.有时候某个agent的角色还会自动变化 有些agent也会去进行所有人观点的总结与反驳 角色如何严格固定下来
4.主团队得到满足和评论者被说服不知道怎么实现
'''

#proposition = "所有的博物馆都应当免门票"
proposition = "我们应该允许在国家组织的选举中使用电子和互联网投票"
prompt = f"""- Role: 辩论策略规划师和评论者
- Background: 现在需要就“{proposition}”这一话题对所有人的发言进行反驳，直到你被说服，然后根据整个对话列出所有的论点。
- Profile: 你是一位专业的辩论策略规划师，擅长辩论场景，同时具备评论者的能力，能够对辩论进行深入分析和评论。
- Skills: 你具备辩论技巧、逻辑分析和批判性思维的能力，能够引导辩论，最后提供有见地的评论。
- Goals: 作为评论者对辩论进行反驳和总结。
- Constrains: 辩论内容需围绕该话题展开，评论需公正客观，论点大纲需清晰有逻辑。
- OutputFormat: 辩论对话记录、评论和论点大纲。
- Workflow:
  1. 作为评论者，对辩论进行评论和反驳。
  2. 根据辩论内容，整合出一个论点大纲。
- Examples:
  - 辩论对话记录：
    - 博物馆馆长：博物馆免费可以吸引更多游客，增加社会教育价值。
    - 经济学者：免费可能导致政府预算压力增大，影响博物馆运营质量。
    - 教育工作者：教育应该平等，免费博物馆有助于教育资源的普及。
    - 评论者：免费与否应考虑博物馆的财务状况和社会效益，不能一概而论。
  - 论点大纲：
    1. 免费博物馆的社会教育价值
    2. 免费博物馆对政府预算的影响
    3. 免费博物馆与教育平等的关系
    4. 免费博物馆的财务可持续性
"""

# 创建代理 以生成角色池
assistant = AssistantAgent(name="Assistant", llm_config={"config_list": config_list})
content = f"找出5-10个与“{proposition}”话题有利益相关的角色,回答样例格式如下,不要输出除名称之外的其他内容：1.角色1 2.角色2 3.角色3 4.角色4"
persona_pool = assistant.generate_reply(messages=[{"content": content}])
# 创建三个角色代理
persona_message = f"你是一个辩手，请先从{persona_pool}中随机选择一个与之前发言的人不同的角色，然后根据角色立场对“{proposition}”进行辩论，你无需对辩论内容进行总结，回应反驳时只需回应针对自身角色的部分即可。"
persona_1 = AssistantAgent("persona_1", llm_config={"config_list": config_list}, system_message=persona_message)
persona_2 = AssistantAgent("persona_2", llm_config={"config_list": config_list}, system_message=persona_message)
persona_3 = AssistantAgent("persona_3", llm_config={"config_list": config_list}, system_message=persona_message)

# 设定用户代理任务
user_proxy = UserProxyAgent(
    "user_proxy",
    llm_config={"config_list": config_list},
    code_execution_config={"work_dir": "chatting", "use_docker": False},
    system_message=prompt
)
#critic = AssistantAgent("critic", llm_config={"config_list": config_list}, system_message="你是一个评论家，需要对其他人的辩论进行反驳。")

# 这个图定义了哪个代理可以在哪个代理之后发言
# A:[B,C]
# BC可以在A之后发言
graph_dict = {
    user_proxy: [user_proxy,persona_1],
    persona_1: [persona_2,persona_3],
    persona_2: [persona_1,persona_3],
    persona_3: [user_proxy]
}

# 创建群聊
group_chat = GroupChat(agents=[user_proxy, persona_1, persona_2, persona_3], 
                       messages=[],
                       speaker_selection_method="round_robin"   # 顺序发言
                       #allowed_or_disallowed_speaker_transitions=graph_dict,
                       #allow_repeat_speaker=None,
                       #speaker_transitions_type="allowed"
                       )

# 创建群聊管理器
group_chat_manager = GroupChatManager(groupchat=group_chat, llm_config={"config_list": config_list})


# 通过用户代理启动对话
#user_proxy.initiate_chat(group_chat_manager, message=f"欢迎您参与这场关于博物馆是否应该免费的辩论。我将为您构建角色，请从以下角色中选择一个并根据其立场进行辩论：{persona_pool}")
message = f"欢迎您参与这场关于“{proposition}”的辩论，请根据自身角色立场发表自己的观点。"
user_proxy.initiate_chat(group_chat_manager, message=message)

