# 下载最新的年报文件，调用doc2x/Textin工具获取md文件，抽取对应章节内容
import json
import logging
import os
import requests
from urllib.parse import urlparse
from fin2rg.md_utils import parse_md_file_to_section_list
from fin2rg.utils import extract_md_from_zip
from fin2rg.utils import extract_pages
from typing import Annotated

dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
report_cache_dir_path = os.path.join(os.path.dirname(dir_path),'.cache/tmp_reports')
md_cache_dir_path = os.path.join(os.path.dirname(dir_path),'annual_report_md')
report_search_url = 'https://finnews.cubenlp.com/get_curr_com_annual_reports'
# report_search_url = 'http://172.23.148.35:8091/get_curr_com_annual_reports'
os.makedirs(report_cache_dir_path,exist_ok=True)

from fin2rg.log_util import init_logger
logger = init_logger(__name__)

class SECUtils:
    

    def down_file(symbol: Annotated[str, "股票代码"]):
        """下载公司对应的最新年报，文件名称后缀为pdf，返回下载后文件路径"""
        com_code = symbol.split(".")[0]
        data = {"com_code": com_code, "top_k": 1, "report_type": "annual"}
        response = requests.post(report_search_url, json=data)
        # if re
        def download_file(url):
            # 解析URL获取文件名
            filename = urlparse(url).path.split('/')[-1]
            file_path = os.path.join(report_cache_dir_path,filename)
            if os.path.exists(file_path): # 存在缓存文件则不下载
                logger.info(f"File {file_path} has been existed.")
                return filename
            # 发送GET请求
            response = requests.get(url)

            # 检查响应状态码是否为200（成功）
            if response.status_code == 200:
                # 将内容写入文件
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"File {file_path} has been downloaded successfully.")
            else:
                logger.error(f"Failed to download file. Status code: {response.status_code}")
                return 'ERROR'
            return filename
        #
        # # 使用你的URL调用函数
        # download_url = "https://pdf.dfcfw.com/pdf/H2_AN202403151626860510_1.pdf"
        # download_file(download_url)
        print("response.content:", response.content)
        response_json = json.loads(response.content.decode('utf-8'))
        # print(response.content)
        report_info_list =  response_json['data']
        if len(report_info_list) == 0:
            logger.error('not found annual report')
            return 'ERROR'
        else:
            report_url = report_info_list[0]['pdf_url']
            filename = download_file(url=report_url)
            return os.path.join(report_cache_dir_path, filename)
        
    def get_md_file(doc_file: Annotated[str, "年报文件名称"],):
        '''
        使用Doc2x进行pdf转md
        doc2x使用说明网址：https://noedgeai.feishu.cn/wiki/Qb1SwLBi5iz6cDkVyICcVBYgnRd
        对doc2x工具的封装：https://menghuan1918.github.io/pdfdeal-docs/zh/guide/Doc2X/2.html
        安装：pip install --upgrade pdfdeal
        # 每天有限制 500页解析,200页翻译)
        '''
        pdf_dir, pdf_file_name = os.path.split(doc_file)
        file_prefix,file_type = os.path.splitext(pdf_file_name)
        md_zip_file_name = file_prefix + '_md.zip'
        md_file_name = file_prefix + '.md'
        md_file_path = os.path.join(md_cache_dir_path,md_file_name)
        pdf_file_path = os.path.join(pdf_dir,pdf_file_name)
        if os.path.exists(md_file_path):  # 存在缓存文件则不调用第三方接口转换
            logger.info(f"File {md_file_path} has been existed.")
            return md_file_name
        pdf_file_list = [pdf_file_path]
        md_name_list = [md_zip_file_name]
        from pdfdeal import Doc2X
        Client = Doc2X(apikey='CImakLSl0+KcUxCttwIaGDY2OWRmODBlNWMxOWI5YTk5YzhmOWIxOCICaDU=.6ab7364a811088f18731d84f3de28616b38f4218d47088098758ebaa5acf23d0')
        Client = Doc2X(apikey='sk-2d1n6vh2k4mzjlvgt2hgu0yhn7bf0jcl',debug=True,max_time=60*4)
        success, failed, flag = Client.pdf2file(
            pdf_file=pdf_file_list,
            output_path= report_cache_dir_path,
            output_names= md_name_list,
            output_format="md_dollar",
        )
        logger.info('Dox2x process result sucess:{},failed:{},flag:{}'.format(success,failed,flag))
        # flag=True
        # success=[]
        if flag or len(success)==0:
            #true 表示存在未成功处理
            logger.info('pdf2md failed. {}'.format(pdf_file_path))
            return 'ERROR'
        else:
            # 指定ZIP文件路径和提取路径
            zip_file_path = success[0]
            # 调用函数并打印返回的文件路径
            tmp_md_file_path = extract_md_from_zip(zip_file_path, md_cache_dir_path)
            if tmp_md_file_path:
                os.rename(tmp_md_file_path, md_file_path)
                logger.info(f"The MD file was extracted to: {md_file_path}")
                return md_file_name
            else:
                logger.info("No MD file found in the ZIP archive.")
                return 'ERROR'
    
    def get_section(
        ticker_symbol: Annotated[str, "ticker symbol"],
        section_name: Annotated[
            str | int,
            "Section of the 10-K report to extract, should be in [1, 1A, 1B, 2, 3, 4, 5, 6, 7, 7A, 8, 9, 9A, 9B, 10, 11, 12, 13, 14, 15]",
        ]
    ):
        doc_file_path = SECUtils.down_file(ticker_symbol)

        md_file_name = SECUtils.get_md_file(doc_file_path)
        md_file = os.path.join(md_cache_dir_path,md_file_name)
        
        section_list = parse_md_file_to_section_list(md_file)
        matched_section_level = -1
        matched_section_related_sections = []

        section_name = section_name.strip().strip().strip('、').strip('.')

        for section in section_list:
            if section.simple_tile == section_name:
                matched_section_level = section.level
                matched_section_related_sections.append(section)

            elif matched_section_level >= 0  and matched_section_level < section.level :
                matched_section_related_sections.append(section)
            else:
                matched_section_level = -1
        return ''.join([section.get_content() for section in matched_section_related_sections])




if __name__ == '__main__':
    doc_file_path = SECUtils.down_file('002081')
    # doc_file_name = 'H2_AN202403151626860510_1_new.pdf'
    # doc_file = os.path.join(report_cache_dir_path,doc_file_name)
    md_file_name = SECUtils.get_md_file(doc_file_path)
    md_file = os.path.join(md_cache_dir_path,md_file_name)

    # print(SECUtils.get_section(md_file,'应收款项融资'))

    # 使用你的PDF文件路径和想要提取的页面号码 -- 用于小文件测试pdf2md
    # pdf_file_path = "/home/xiefeng/homework/Fin2RG/.cache/tmp_reports/H2_AN202403151626860510_1.pdf"
    # output_file_path = "/home/xiefeng/homework/Fin2RG/.cache/tmp_reports/H2_AN202403151626860510_1_new.pdf"
    # pages_to_extract = [1,2,3,4,5,6,10]  # 你想提取的页面编号列表
    # #
    # extract_pages(pdf_file_path, output_file_path, pages_to_extract)
