#encoding:utf-8
import os
import sys
DIR_PATH=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(DIR_PATH)
# from prompts import *
from fin2rg.argument_gen.prompts import *
from fin2rg.log_util import init_logger
from fin2rg.utils import query_llm
from fin2rg.utils import save_to_file,read_file
from typing import Annotated


logger = init_logger(__name__)


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

def build_annual_report_key_infos(company,stock_code):
    logger.info(f'build_annual_report_key_infos started for {company} , {stock_code}')



    def order_trigger(analysis_result_content):
        # Check if the last message contains the path to the instruction text file
        return "instruction & resources saved to" in analysis_result_content


    # 设置公司名、公司股票代码、日期
    from datetime import datetime
    from dateutil.relativedelta import relativedelta


    #company = "宁德时代"
    #stock_code = "300750.sz"
    fyear = "2023" # 年度报告的发布年限 
    end_date = datetime.now().strftime('%Y-%m-%d')
    logger.info(f'end_date {end_date}')
    start_date = (datetime.now() - relativedelta(months=1)).strftime('%Y-%m-%d')



    # 获取新闻

    from fin2rg.functional.analyzer import ReportAnalysisUtils

    


    # 分析年报 
    ## business_highlights
    business_highlights_analysis_instruction_path = os.path.join(DIR_PATH,'result/business_highlights_analysis_instruction.txt')
    analyze_business_highlights_ret = ReportAnalysisUtils.analyze_business_highlights(ticker_symbol=stock_code,fyear=fyear,save_path=business_highlights_analysis_instruction_path)

    logger.info(f'analyze_business_highlights_ret: {analyze_business_highlights_ret}')

    business_highlights = analysis_post_process(analysis_result_content=analyze_business_highlights_ret)
    
    logger.info(f'business_highlights: {business_highlights}')

    ## income_summarization  
    income_stmt_analysis_instruction_path = os.path.join(DIR_PATH,'result/income_stmt_analysis_instruction.txt')
    segment_analysis_instruction_path = os.path.join(DIR_PATH,'result/segment_analysis_instruction.txt')
    income_stmt_analysis_ret = ReportAnalysisUtils.analyze_income_stmt(ticker_symbol=stock_code,fyear=fyear,save_path=income_stmt_analysis_instruction_path)
    segment_analysis_ret = ReportAnalysisUtils.analyze_segment_stmt(ticker_symbol=stock_code,fyear=fyear,save_path=segment_analysis_instruction_path)

    logger.info(f'income_stmt_analysis_ret: {income_stmt_analysis_ret}')
    logger.info(f'segment_analysis_ret: {segment_analysis_ret}')

    income_stmt_analysis = analysis_post_process(income_stmt_analysis_ret)
    segment_analysis = analysis_post_process(segment_analysis_ret)

    logger.info(f'income_stmt_analysis: {income_stmt_analysis}')
    logger.info(f'segment_analysis: {segment_analysis}')



    income_summarization_instruction_path =  os.path.join(DIR_PATH,'result/income_summarization_instruction.txt')


    income_summarization_ret = ReportAnalysisUtils.income_summarization(ticker_symbol=stock_code,fyear=fyear,income_stmt_analysis=income_stmt_analysis,
                                                                        segment_analysis=segment_analysis,save_path=income_summarization_instruction_path)

    logger.info(f'income_summarization_ret: {income_summarization_ret}')

    income_summarization = analysis_post_process(income_summarization_ret)
    logger.info(f'income_summarization: {income_summarization}')





    ## company_description
    news_factor = ReportAnalysisUtils.get_company_news(company, 30)
    logger.info('news factor: {}'.format(news_factor))

    

    ## risk_assessment
    risk_assessment_instruction_path = os.path.join(DIR_PATH,'result/risk_assessment_instruction.txt')
    risk_assessment_instruction_ret = ReportAnalysisUtils.get_risk_assessment(ticker_symbol=stock_code,fyear=fyear,save_path=risk_assessment_instruction_path)

    logger.info(f'risk_assessment_instruction_ret: {risk_assessment_instruction_ret}')

    risk_assessment =  analysis_post_process(analysis_result_content=risk_assessment_instruction_ret)

    logger.info(f'risk_assessment:{risk_assessment}.')

    

    logger.info('build_annual_report finished')

    return income_summarization,business_highlights,news_factor,risk_assessment


class ClaimUtils:
    def get_outline(company: Annotated[str, "company name"],
                    major_claim: Annotated[str, "major_claim content"],
                    sub_claims: Annotated[str, "sub_claims content"],
                    save_path: Annotated[str, "save outline path"]):
        """
        根据中心论点和分论点生成报告大纲,save_path为txt的文件路径
        """
        outline = StockResearchOutlinePrompt(main_argument=major_claim,sub_arguments=sub_claims).predict(model='gpt-4o')
        logger.info(f"outline:\n{outline}")
        with open(save_path, "w") as f:
             f.write(outline)
        return f"生成报告大纲并保存在{save_path}"



    def get_txt_content(file_path):
        with open(file_path, "r") as f:
            data = f.read()
        
        return data
    def get_major_claim(company: Annotated[str, "company name"],
                        income_summarization_path: Annotated[str, "income_summarization file path"],
                        business_highlights_path: Annotated[str, "business_highlights file path"],
                        news_factor_path: Annotated[str, "news factor path"],
                        risk_assessment_path: Annotated[str, "risk_assessment file path"],
                        ):
        """
        根据数据源生成中心论点和分论点
        """
        # path = os.path.join(DIR_PATH,'result/input.txt')
        print("start generation...")

        def get_txt_content(file_path):
            with open(file_path, "r") as f:
                data = f.read()
            
            return data
    
        business_highlights_ret = get_txt_content(business_highlights_path)
        income_summarization_ret = get_txt_content(income_summarization_path)
        risk_assessment_ret = get_txt_content(risk_assessment_path)
        news_factor = get_txt_content(news_factor_path)

        # business_highlights = analysis_post_process(analysis_result_content=business_highlights_ret)
        business_highlights = query_llm(business_highlights_ret, "deepseek-chat")
        income_summarization = query_llm(income_summarization_ret, "deepseek-chat")
        risk_assessment = query_llm(risk_assessment_ret, "deepseek-chat")

        # income_summarization = analysis_post_process(income_summarization_ret)

        # risk_assessment =  analysis_post_process(analysis_result_content=risk_assessment_ret)
        
        # if not os.path.exists(path):
        
        instruction_input = f"""
        ## 指令模板

        请根据以下提供的信息，形成对该公司的整体投资观点，并将其凝练成两句话内。

        ## 输入参数

        - **公司名**：{company}
        - **新闻**：{news_factor}
        - **收入总结**：{income_summarization}
        - **业务亮点**：{business_highlights}
        - **风险评估**：{risk_assessment}

        ## 输出示例

        基于以上信息，投资观点如下：
        """

            # save_to_file(input,path)
        
        # input = read_file(path)
        logger.info(f'input:\n{instruction_input}')
        major_claim_draft = MajorClaimDraftGenPrompt(input=instruction_input).predict(model="deepseek-chat")
        logger.info(f'major_claim_draft:\n{major_claim_draft}')
        # 中心论点
        branch_claims_list_str = BranchClaimsDraftGenPrompt(input= major_claim_draft,num_branches=6).predict(model="deepseek-chat")
        branch_claims_list = BranchClaimsDraftGenPrompt.parse_branch_list(branch_claims_list_str)
        
        logger.info(f'branch_claims_list:\n{branch_claims_list}')

        refined_claim_list = []
        for branch_claim in branch_claims_list:
            logger.info(f'branch_claim:{branch_claim}')
            
            rebuttals_str = ClaimRebuttalsGenPrompt(claim=branch_claim,num_branches=6).predict(model="deepseek-chat")
            logger.info(f'without input- Rebuttals:\n{rebuttals_str}\n')

            rebuttals_str = ClaimRebuttalsGenWithInputPrompt(input=input,claim=branch_claim,num_branches=6).predict(model="deepseek-chat")
            logger.info(f'with input- Rebuttals:\n{rebuttals_str}\n')

            refined_claim = ClaimRefinePrompt(claim=branch_claim,rebuttal=rebuttals_str).predict(model="deepseek-chat")

            logger.info(f'rebuttals with input for refining:\n{refined_claim}\n')
            refined_claim_list.append(refined_claim)

        # 根据refined_claim_list 重新生成中心论点
        refine_major_claim = MajorClaimGenPrompt(input=input,claims=refined_claim_list).predict(model="deepseek-chat")

        logger.info(f"refine_major_claim:\n{refine_major_claim}")
        logger.info(f'refined_claim_list:\n{refined_claim_list}')

        return refine_major_claim, refined_claim_list


if __name__ == "__main__":
    
    
    path = os.path.join(DIR_PATH,'result/input.txt')
    from prompts import *

    if not os.path.exists(path):
        income_summarization,business_highlights,news_factor,risk_assessment =  build_annual_report_key_infos('宁德时代',"300750.sz")
        company = '宁德时代'

        input = f"""
        ## 指令模板

        请根据以下提供的信息，形成对该公司的整体投资观点，并将其凝练成两句话内。

        ## 输入参数

        - **公司名**：{company}
        - **新闻**：{news_factor}
        - **收入总结**：{income_summarization}
        - **业务亮点**：{business_highlights}
        - **风险评估**：{risk_assessment}

        ## 输出示例

        基于以上信息，投资观点如下：
        """

        save_to_file(input,path)



    # input = read_file(path)
    # logger.info(f'input:\n{input}')
    # major_claim_draft = MajorClaimDraftGenPrompt(input=input).predict(model="deepseek-chat")
    # logger.info(f'major_claim_draft:\n{major_claim_draft}')
    # # 中心论点
    # branch_claims_list_str = BranchClaimsDraftGenPrompt(input= major_claim_draft,num_branches=6).predict(model="deepseek-chat")
    # branch_claims_list = BranchClaimsDraftGenPrompt.parse_branch_list(branch_claims_list_str)
    
    # logger.info(f'branch_claims_list:\n{branch_claims_list}')

    # refined_claim_list = []
    # for branch_claim in branch_claims_list:
    #     logger.info(f'branch_claim:{branch_claim}')
        
    #     rebuttals_str = ClaimRebuttalsGenPrompt(claim=branch_claim,num_branches=6).predict(model="deepseek-chat")
    #     logger.info(f'without input- Rebuttals:\n{rebuttals_str}\n')

    #     rebuttals_str = ClaimRebuttalsGenWithInputPrompt(input=input,claim=branch_claim,num_branches=6).predict(model="deepseek-chat")
    #     logger.info(f'with input- Rebuttals:\n{rebuttals_str}\n')

    #     refined_claim = ClaimRefinePrompt(claim=branch_claim,rebuttal=rebuttals_str).predict(model="deepseek-chat")

    #     logger.info(f'rebuttals with input for refining:\n{refined_claim}\n')
    #     refined_claim_list.append(refined_claim)

    # # 根据refined_claim_list 重新生成中心论点
    # refine_major_claim = MajorClaimGenPrompt(input=input,claims=refined_claim_list).predict(model="deepseek-chat")

    # logger.info(f"refine_major_claim:\n{refine_major_claim}")
    # logger.info(f'refined_claim_list:\n{refined_claim_list}')
    refine_major_claim = '宁德时代通过技术创新和多元化战略，巩固了全球电池市场的领先地位。'
    refined_claim_list =  ['宁德时代在动力电池和储能电池系统领域的全球市场份额持续增长，同时公司通过多元化投资和成本控制策略，为其盈利能力提供了坚实基础。', '宁德时代通过持续的技术创新和多元化的战略布局，不断提升产品性能和市场适应性，增强了综合竞争力。', '宁德时代的国际化战略成功拓展了海外市场，并通过多元化发展、产品创新、产业链整合和储能领域的领先地位，有效提升了整体盈利能力和风险分散能力。', '宁德时代通过多元化的业务布局和风险管理策略，在一定程度上缓解了宏观经济波动和原材料价格波动带来的挑战。', '宁德时代在储能电池系统领域的领先地位，结合其在动力电池系统、电池矿产资源业务及成本控制方面的综合优势，为其在新能源市场的长期增长提供了坚实基础。', '宁德时代通过与多家国际知名汽车制造商的合作，持续优化其市场拓展策略，以应对全球电池市场的挑战和机遇。']

    # outline generate
    outline = StockResearchOutlinePrompt(main_argument=refine_major_claim,sub_arguments=refined_claim_list).predict(model='gpt-4o')
    logger.info(f"outline:\n{outline}")
