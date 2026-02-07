import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json
import re
from textwrap import dedent
from typing import Annotated
from datetime import timedelta, datetime
from fin2rg.utils import query_llm
from fin2rg.log_util import init_logger
from charting import MyReportChartUtils

logger = init_logger(__name__)

# 递归地在嵌套字典中查找包含目标键的字典。
def find_dict_with_key(nested_dict, target_key):
    if isinstance(nested_dict, dict):
        for key, value in nested_dict.items():
            if key == target_key:
                return nested_dict
            elif isinstance(value, dict):
                result = find_dict_with_key(value, target_key)
                if result is not None:
                    return result
            elif isinstance(value, list):
                for item in value:
                    result = find_dict_with_key(item, target_key)
                    if result is not None:
                        return result
    return None
def order_message(analysis_result_content):
        # Extract the path to the instruction text file from the last message
        full_order = analysis_result_content
        txt_path = full_order.replace("instruction & resources saved to ", "").strip()
        with open(txt_path, "r") as f:
            instruction = f.read() #+ "\n\nReply TERMINATE at the end of your response."
        return instruction


def analysis_post_process(analysis_result_content):
        instruction = order_message(analysis_result_content=analysis_result_content)
        return query_llm(instruction, "deepseek-chat")

class ContentWritingUtils:

    """```json
{
  "title": "宁德时代股票研究报告",
  "1. 公司概况": [
    "1.1 公司简介",
    "1.2 业务范围"
  ],
  "2. 技术创新与多元化战略": [
    "2.1 技术创新的核心竞争力",
    "2.2 多元化战略的实施与成效"
  ],
  "3. 全球市场地位": [
    "3.1 动力电池市场份额",
    "3.2 储能电池系统市场份额",
    "3.3 国际化战略与海外市场拓展"
  ]
}
```
    """
    def ReportWriting(
        company: Annotated[str, "公司名称"],
        outline_path: Annotated[str, "文章大纲json地址"],
        income_summarization_path: Annotated[str, "income_summarization file path"],
        business_highlights_path: Annotated[str, "business_highlights file path"],
        news_factor_path: Annotated[str, "news factor file path"],
        risk_assessment_path: Annotated[str, "risk_assessment file path"],
        md_save_path: Annotated[str, "report md save path"]
    ) -> str:
        """
        根据公司名称，大纲，返回对应的报告内容，将章节题目和年报、新闻一起输入给LLM生成对应的章节内容，并将内容保存到save_path的md文件
        """
        def get_txt_content(file_path):
            with open(file_path, "r") as f:
                data = f.read()
            
            return data
      
        outline = get_txt_content(outline_path)

        business_highlights_ret = get_txt_content(business_highlights_path)
        business_highlights_ret = business_highlights_ret.split("Instruction")[0]
        income_summarization_ret = get_txt_content(income_summarization_path)
        income_summarization_ret = income_summarization_ret.split("Instruction")[0]
        risk_assessment_ret = get_txt_content(risk_assessment_path)
        risk_assessment_ret = risk_assessment_ret.split("Instruction")[0]
        news_factor = get_txt_content(news_factor_path)

        # business_highlights = query_llm(business_highlights_ret, "deepseek-chat")
        # income_summarization = query_llm(income_summarization_ret, "deepseek-chat")
        # risk_assessment = query_llm(risk_assessment_ret, "deepseek-chat")

        # business_highlights = analysis_post_process(analysis_result_content=business_highlights_ret)

        # income_summarization = analysis_post_process(income_summarization_ret)

        # risk_assessment =  analysis_post_process(analysis_result_content=risk_assessment_ret)

        outline = outline.replace("```JOSN", "").replace("```json", "").replace("```", "")
        outline = json.loads(outline)

        report_list = []
        chapter_num = 0
        for chapter, sec_chapter in outline.items():
            if chapter == "title":
                chapter_num += 1 
                report_list.append("# "+sec_chapter)
                continue
            # 根据 sec_chapter章节 寻找对应的数据源并决定是否要确定绘图和绘图的类型
            report_list.append("## "+chapter)
            for sec_idx, sec in enumerate(sec_chapter):
                # 将 sec 转为可查询的语句，增加上下文内容，增强检索的效果。
                # 如：公司简介 -》LLM -》 宁德时代的公司发展
                report_list.append("### "+sec)
                logger.info(sec)
                # sec 转为可查询的语句
                # 增加图表可视化
                vis_prompt = dedent("""**目标**: 从背景知识和当前章节中提取关键信息和数据点，首先判断该章节是否适合增加可视化，以便于创建条形图、折线图或饼图进行可视化。
                                    
                1. **背景知识总结**：
                  请总结出本章节相关的背景知识。这应包括该领域的基本概念、重要数据来源、以及任何与当前章节内容有关的已知信息。这部分信息将有助于识别章节中的重要数据点。

                2. **章节标题解析**：
                  根据章节标题，推测可能涉及的主题和内容。这有助于预判章节中将重点讨论的内容和数据类型。

                3. **关键信息识别**：
                  列出该章节中最重要的3-5个信息点。这些信息应该与章节标题和背景知识有直接联系，并且能够支撑后续的数据可视化。

                4. **数据点提取**：
                  在章节内容中，找出与上述关键信息相关的具体数据点。这可以包括：
                  - 具体数值和统计数据（适用条形图和折线图）。
                  - 时间序列数据（适用折线图）。
                  - 类别和比例数据（适用饼图）。

                5. **可视化建议**：
                  针对提取出的数据点，建议一种最合适的图表类型，并简单解释选择理由。如果该章节不适合增加图表，说明原因。例如：
                  - "章节数据不适合可视化，因为缺乏具体数据点或数据类型不支持上述图表。"
                  - "适用条形图(bar)，因为数据涉及多个类别的比较。"
                  - "适用折线图(line)，因为数据是随时间变化的趋势。"
                  - "适用饼图(pie)，因数据反映部分和整体的比例关系。"

                6. **可视化图表类型和X轴Y轴数据**
                  根据背景知识，仅需要给出一个最合适可视化图表类型和对应X轴Y轴的数据以及图表的题目，输出结果以JSON格式输出。例如：
                  ```json
                  {
                    "Chart_Type": "bar",
                    "X": ["内容 1", "内容 2"],
                    "Y": [10, 20],
                    "Chart_Title": "chart title content"
                  }```               
                  请严格遵循JSON格式，不要改变JSON字段名称和格式，保证X轴(字符串类型)和Y轴(数值类型)为list的数据类型。
                """)
                
                vis_instruction = vis_prompt+"\n\nChapter Title: "+sec+"Background Knowledge:" +business_highlights_ret+income_summarization_ret+risk_assessment_ret+news_factor
                vis_result = query_llm(vis_instruction, "gpt-4o")
                logger.info(vis_result)
                # json_pattern = r'```json.*?\}'
                # matches = re.findall(json_pattern, vis_result, re.DOTALL)
                json_pattern = r'```json(.*?)```'
                matches = re.search(json_pattern, vis_result, re.DOTALL)
                vis_data = None
                dir_path, _ = os.path.split(md_save_path)
                if not os.path.exists(os.path.join(dir_path, company)):
                     os.makedirs(os.path.join(dir_path, company))
                vis_save_path = os.path.join(dir_path, company, str(chapter_num)+"_"+str(sec_idx)+".png")
                # if matches:
                if matches and matches is not None:
                    # vis_data = matches[0].replace("```json", "").replace("\n", "").replace(" ", "")
                    
                    vis_data = matches.group(1).replace("\n", "").replace(" ", "")
                    vis_data = json.loads(vis_data)
                    vis_data = find_dict_with_key(vis_data, "Chart_Type")
                    
                    chart_type = vis_data["Chart_Type"]
                    if "X" in vis_data:
                        x_data = vis_data["X"]
                    elif "Labels" in vis_data:
                        x_data = vis_data["Labels"]
                    if "Y" in vis_data:
                        y_data = vis_data["Y"]
                    else:
                        y_data = vis_data["Values"]
                    MyReportChartUtils.plot_charts(chart_type=chart_type, x_data=x_data, y_data=y_data, title=vis_data["Chart_Title"], save_path=vis_save_path)

                writing_prompt = f"请根据三级章节名称和背景知识生成段落内容,背景知识仅供参考,仅在需要的时候进行查询。字数不能超过300字。仅输出段落内容即可。也需要参考{vis_result}\n二级章节名称：{chapter}\n三级章节名称：{sec}+\n背景知识：\n"+business_highlights_ret+income_summarization_ret+risk_assessment_ret+news_factor
                # writing_prompt = "请根据章节名称和背景知识生成段落内容,字数不能超过300字。只输出段落内容即可。\n章节名称："+sec+"\n背景知识：\n"+business_highlights+income_summarization+risk_assessment+news_factor
                writing_content = query_llm(writing_prompt, "gpt-4o")
                logger.info(writing_content)
                writing_content += "\n" + f"![]({vis_save_path})\n"
                report_list.append(writing_content)
            chapter_num += 1
        report_content = "\n".join(report_list)
        with open(md_save_path, "w") as f:
             f.write(report_content)
        return f"报告内容保存到本地文件中:{md_save_path}"

    def generate_report(report_content: Annotated[str, "生成的报告内容"],
                    save_path: Annotated[str, "报告保存路径"]):
        """
        将报告内容保存到本地文件中
        """
        with open(save_path, "w") as f:
             f.write(report_content)


if __name__ == "__main__":
    
    outline = """```json
{
  "title": "宁德时代股票研究报告",
  "1. 公司概况": [
    "1.1 公司简介",
    "1.2 业务范围"
  ],
  "2. 技术创新与多元化战略": [
    "2.1 技术创新的核心竞争力",
    "2.2 多元化战略的实施与成效"
  ],
  "3. 全球市场地位": [
    "3.1 动力电池市场份额",
    "3.2 储能电池系统市场份额",
    "3.3 国际化战略与海外市场拓展"
  ],
  "4. 盈利能力与成本控制": [
    "4.1 多元化投资与盈利能力",
    "4.2 成本控制策略与成效"
  ],
  "5. 风险管理与宏观经济应对": [
    "5.1 多元化业务布局与风险分散",
    "5.2 宏观经济波动与原材料价格波动应对策略"
  ],
  "6. 产业链整合与市场适应性": [
    "6.1 产业链整合的优势",
    "6.2 市场适应性与产品创新"
  ],
  "7. 合作伙伴与市场拓展策略": [
    "7.1 国际知名汽车制造商的合作",
    "7.2 市场拓展策略的优化"
  ],
  "8. 未来展望与增长潜力": [
    "8.1 新能源市场的长期增长潜力",
    "8.2 未来发展战略与目标"
  ]
}
```
    """
    company = "宁德时代"

    news_factor = """获取到的相关新闻数据影响因子如下：1. **新能源客车电池技术进步**：宁德时代发布的天行（B）-客车版电池将新能源客车全生命周期延长至15年150万公里，能量密度达到175Wh/kg，解决了客车动力电池长寿命与长续航的双重难题。这表明宁德时代在电池技术上的创新和进步，能够显著提升新能源客车的使用寿命和性能。

2. **商用车电池市场扩展**：宁德时代与多家整车企业合作，将在宇通客车、金龙、海格等企业品牌的80款车型上进行开发。这显示了宁德时代在商用车电池市场的扩展和合作，有助于提升其市场份额和品牌影响力。

3. **政策支持与市场需求**：中国新能源乘用车渗透率持续提升，新能源商用车领域有望成为新的增长空间。政策对新能源商用车的推广和应用支持力度不断加码，为宁德时代等企业提供了发展机遇。

4. **国际合作与市场拓展**：宁德时代与山东重工集团签署战略合作协议，与一汽解放、福田汽车、陕汽控股等企业合资合作，显示了宁德时代在国际市场上的合作和扩展，有助于提升其全球市场份额。

5. **技术创新与产品多样化**：宁德时代构建了包括麒麟电池、神行电池在内的车用动力电池产品矩阵，推出了天行电池L-超充版和天行电池L-长续航版等产品。这表明宁德时代在技术创新和产品多样化方面的努力，能够满足不同市场需求。"""
    income_summarization = """### 综合分析

2023年，公司整体收入和盈利能力显著提升，总收入达到4009.17亿元，同比增长22.01%，净利润增长39.76%至467.61亿元。毛利率从9.4%提升至11.03%，营业利润率和净利润率分别提升至13.4%和11.66%，显示出公司在成本控制和运营效率方面的显著进步。核心业务分部收入稳定增长，长期股权投资增加，存货管理优化，市场份额保持稳定。金融资产分部收入增长15.61%，应收款项融资增加，但新开具票据减少。其他业务分部收入增长15.61%，计提返利及售后服务费增加。总体来看，公司财务状况稳健，收入和盈利能力持续增长，显示出良好的市场竞争力和增长潜力。"""
    business_highlights = """1. **动力电池系统**：公司动力电池销量显著增长，市场份额连续七年位列全球第一。报告期内，公司发布了多款创新产品，如凝聚态电池和神行电池，并与多家主流车企深化合作，助力客户打造更具竞争力的产品。

2. **储能电池系统**：储能电池销量大幅提升，全球市场份额连续三年保持第一。公司在国内外多个大型储能项目中取得重要进展，发布了零辅源光储直流耦合解决方案，推动储能技术的广泛应用。

3. **电池材料及回收**：电池材料需求随动力及储能电池增长而扩大，公司通过回收利用和投资合作保障供应链安全。报告期内，公司持续优化供应链管理，确保原材料供应及成本控制。

4. **电池矿产资源**：公司在锂、镍、钴等关键电池矿产资源方面进行布局，确保上游资源供应。通过自建、参股、合资等方式，公司在多个项目中投入运营，提升资源保障能力。"""

    risk_assessment = """1. **宏观经济与市场波动风险**：全球经济不确定性可能导致市场需求下滑，影响公司业绩。
2. **市场竞争加剧风险**：新能源市场快速发展导致国内外企业产能扩张，竞争加剧。
3. **原材料价格波动及供应风险**：主要原材料价格受大宗商品影响，价格波动对成本造成较大影响。"""
    """
    company: Annotated[str, "公司名称"],
    outline_path: Annotated[str, "文章大纲json地址"],
    income_summarization_path: Annotated[str, "income_summarization file path"],
    business_highlights_path: Annotated[str, "business_highlights file path"],
    news_factor_path: Annotated[str, "news factor file path"],
    risk_assessment_path: Annotated[str, "risk_assessment file path"],
    md_save_path: Annotated[str, "report md save path"]
    """
    result = ContentWritingUtils.ReportWriting(company="宁德时代",
                                                  outline_path="/sshfs/liushu/Fin2RG/result/outline.md",
                                                  income_summarization_path="/sshfs/liushu/Fin2RG/result/risk_assessment.json",
                                                  business_highlights_path="/sshfs/liushu/Fin2RG/result/business_highlights.json",
                                                  news_factor_path="/sshfs/liushu/Fin2RG/result/news_factor.json",
                                                  risk_assessment_path="/sshfs/liushu/Fin2RG/result/risk_assessment.json",
                                                  md_save_path="/sshfs/liushu/Fin2RG/result/宁德时代.md")

    print(result)
  
        