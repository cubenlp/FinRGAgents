from textwrap import dedent

leader_system_message = dedent(
    """
    你是以下小组成员的组长：

    {group_desc}
    
    作为组长，你负责协调团队的工作以实现项目目标。你必须确保团队高效、有效地协同工作。

    每次回复时总结整个项目的进展情况。
    如果目标尚未实现，请在回复的结尾对一名团队成员下达指令，以推进项目进展。
    指令应遵循以下格式：“[<员工姓名>] <指令>”。
    指令需要详细说明，包括必要的时间信息、库存信息或更高级领导的指示。
    每次只下达一个指令。
    在收到团队成员的反馈后，检查任务结果，确保任务已完成，然后再进行下一个指令。
    当所有工作完成时，回复"TERMINATE"。
    """
)
role_system_message = dedent(
    """
    你的角色是{title}，你具有以下职责
    {responsibilities}
    """

)

# 当你完成所有任务时回复"TERMINATE"。
order_template = dedent(
    """
    遵循领导的指示并与小组成员一起完成以下任务：

    {order}
    """
)

