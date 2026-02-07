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
import os
import json
from fin2rg.data_source.news_utils import News_utils
from fin2rg.functional.analyzer import ReportAnalysisUtils
from fin2rg.data_source.sec_utils import SECUtils
from fin2rg.utils import query_llm

from typing import Annotated
logger = init_logger(__name__)

report_cache_dir_path = os.path.join(DIR_PATH,'annual_report_md')
print(report_cache_dir_path)



class BaselineUtils:
    def get_outline(company_name: Annotated[str, "company name"],
                    ticker_symbol: Annotated[str, "股票代码"],
                    save_path: Annotated[str, "save outline path"])-> str:
        """
        报告大纲生成,save_path为outline的txt文件路径
        """

        # 新闻
        print('company_name',company_name)
        response = News_utils.get_company_news(company_name, 50)
        news_dic = response.json()['data']
        news_list = []
        for idx, news in enumerate(news_dic):
            date = news["date"]
            title = news["title"]
            content = news["content"]
            news_list.append(f"第{idx+1}条新闻,新闻发生时间:{date},新闻标题:{title},新闻内容:{content}")

        # 年报
        doc_file_path = SECUtils.down_file(ticker_symbol.split(".")[0])
        # doc_file_name = 'H2_AN202403151626860510_1_new.pdf'
        # doc_file = os.path.join(report_cache_dir_path,doc_file_name)
        md_file_name = SECUtils.get_md_file(doc_file_path)
        # print(md_file_name)
        if md_file_name == 'ERROR':
            print('error',company_name)
            return 'ERROR'
        md_file = os.path.join(report_cache_dir_path,md_file_name)
        # print(md_file)
        with open(md_file, "r") as f:
            md_content = f.read()

        news_str = '\n'.join(news_list)[:3000]
        WritingPrompt = f"""
        新闻：{news_str}
        年报：{md_content[:10000]}
        任务：您是一位专业的研报撰写分析师，请根据提供的新闻和年报资料，为{company_name}撰写一份公司研报大纲。研报大纲，包括报告标题和各个章节的名称。
        输出JSON格式：
        {{
            "report_outline": "研报大纲(markdown表示)",
        }}
        注意：生成大纲(markdown表示)时，输出的时候保证JSON格式的合法性，不要输出其他任何东西。
        """
        print(json.dumps({
            'news_list':news_list[:1],
            'report_md':md_content[:100],
            'company_name':company_name,
        },ensure_ascii=False))
    
        financial_report = query_llm(WritingPrompt, "gpt-4o")
        print('output josn start:{}:end'.format(financial_report))
        financial_report = financial_report.replace("```json", "").replace("```", "")
        print(financial_report)
        report_outline = json.loads(financial_report)["report_outline"]
        logger.info(f"outline:\n{report_outline}")
        with open(save_path, "w") as f:
            json.dump({
                'news_list': news_list,
                'annual_report_md': md_content[:10000],
                'report_outline': report_outline
            }, f, ensure_ascii=False)
        logger.info('done')
        return f"生成报告大纲并保存在{save_path}"
    
    def ReportWriting(
        company_name: Annotated[str, "公司名称"],
        outline_path: Annotated[str, "文章大纲json地址"],
        md_save_path: Annotated[str, "report md save path"]
    ) -> str:
        """
        基于大纲，根据新闻和年报内容，生成报告内容，并将内容保存到save_path的md文件
        """
        def get_outline_info(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
            return data
      
        outline_info = get_outline_info(outline_path)
        outline = outline_info['report_outline']
        news_list = outline_info['news_list']
        annual_report_md = outline_info['annual_report_md']

        WritingPrompt =f"""
        新闻：{news_list[:1000]}
        年报：{annual_report_md[:10000]}
        任务：您是一位专业的研报撰写分析师，请基于下面提供的研报大纲，结合提供的新闻和年报资料，根据大纲撰写完整的公司研报为{company_name}撰写一份公司研报。
        研报大纲：{outline}

        输出JSON格式：
        {{
            "report_content": "研报内容(markdown表示)"
        }}
        注意：输出的时候保证JSON格式的合法性，不要输出其他任何东西。
        """
    
        financial_report = query_llm(WritingPrompt, "gpt-4o")
        print('output josn start:{}:end'.format(financial_report))
        financial_report = financial_report.replace("```json", "").replace("```", "")
        print(financial_report)
        report_content = json.loads(financial_report)["report_content"]
        logger.info(f"report_content:\n{report_content}")
        with open(md_save_path, "w") as f:
            f.write(report_content)


        return f"生成报告大纲并保存在{md_save_path}"
if __name__ == "__main__":
    company_name = '东方财富'
    code = '300059.SZ'
    result_dir = '/home/dev/workspace/mafin2rg/result/baseline/tmp/'
    os.makedirs(result_dir,exist_ok=True)
    outline_save_path = os.path.join(result_dir,f'{company_name}_outline.txt')
    md_save_path = os.path.join(result_dir,f'{company_name}.md')

    ret = BaselineUtils.get_outline(company_name,ticker_symbol=code,save_path=outline_save_path)
    print(ret)
    ret = BaselineUtils.ReportWriting(company_name,outline_path=outline_save_path,md_save_path=md_save_path)
    print(ret)

