import os
import openai
import json
import time
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Annotated
import chinese_calendar
# Define custom annotated types
# VerboseType = Annotated[bool, "Whether to print data to console. Default to True."]
SavePathType = Annotated[str, "File path to save data. If None, data is not saved."]

RetryCount = 3

# def process_output(data: pd.DataFrame, tag: str, verbose: VerboseType = True, save_path: SavePathType = None) -> None:
#     if verbose:
#         print(data.to_string())
#     if save_path:
#         data.to_csv(save_path)
#         print(f"{tag} saved to {save_path}")


def save_output(data: pd.DataFrame, tag: str, save_path: SavePathType = None) -> None:
    if save_path:
        data.to_csv(save_path)
        print(f"{tag} saved to {save_path}")


def get_current_date():
    return date.today().strftime("%Y-%m-%d")


def register_keys_from_json(file_path):
    with open(file_path, "r") as f:
        keys = json.load(f)
    for key, value in keys.items():
        os.environ[key] = value


def decorate_all_methods(decorator):
    def class_decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                setattr(cls, attr_name, decorator(attr_value))
        return cls

    return class_decorator


def get_next_weekday(date):

    if not isinstance(date, datetime):
        date = datetime.strptime(date, "%Y-%m-%d")

    if date.weekday() >= 5:
        days_to_add = 7 - date.weekday()
        next_weekday = date + timedelta(days=days_to_add)
        return next_weekday
    else:
        return date


def query_llm(question, model):
    history_message = []

    if model in ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo']:
        openai.api_key = "sk-fad0tLlqZp0HyxWT6c6cDa8dD9754c71A8329dEa51D1C2Ec"
        openai.base_url = "https://openai.wokaai.com/v1/"
    elif model in ["deepseek-chat"]:
        # openai.api_key = "sk-pIZqFR8dIXaps8jbA78179660c1c4965950eD41f7f41B959"
        # openai.base_url = "https://one-api.cubenlp.cn/v1/"
        history_message.append({"role": "system", "content": "You are a helpful assistant"})
        openai.api_key = "sk-5ad0e8ebbf584fafb1dc73cb65082598"
        openai.base_url = "https://api.deepseek.com/v1/"
    else:
        openai.api_key = "sk-gZU5wBewg2d8XfFM75463966E8Bb4fCcAfAd5612DdBd8bF9"
        openai.base_url = "https://one-api-new.cubenlp.cn/v1/"
    # openai.api_key = "sk-74bba9f46c5c443d9911656569685065"
    # openai.base_url = "https://api.deepseek.com/v1/"
    # model = 'deepseek-chat'
    # openai.api_key = "sb-a45a71e916e40960da3b79971994d07c3a2a272e3ad75b5e"
    # openai.base_url = "https://api.openai-sb.com/v1/"
    history_message.append({"role": "user", "content": question})
    cnt = 0
    err_msg = ""
    while cnt < RetryCount:
        cnt += 1
        try:
            response = openai.chat.completions.create(
                        model=model,
                    messages=history_message,
            )
            return response.choices[0].message.content
        except Exception as e:
            # return str(e)
            err_msg = str(e)
            print("cnr:", cnt, "query err_msg:", err_msg)
        time.sleep(1)
    return err_msg


import zipfile
import os


def extract_md_from_zip(zip_path, extract_path='.'):
    # 创建一个ZipFile对象
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 获取压缩文件中的所有文件名
        files_in_zip = zip_ref.namelist()

        # 遍历所有文件名
        for file_name in files_in_zip:
            # 如果文件名以.md结尾，则是Markdown文件
            if file_name.endswith('.md'):
                # 提取文件到指定路径
                zip_ref.extract(file_name, extract_path)
                # 返回提取后的文件的完整路径
                return os.path.join(extract_path, file_name)
    return None




import fitz  # PyMuPDF

def extract_pages(pdf_path, output_path, page_numbers):
    doc = fitz.open(pdf_path)
    output_pdf = fitz.open()

    for page_num in page_numbers:
        output_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)

    output_pdf.save(output_path)
    output_pdf.close()
    print("Selected pages have been extracted and saved to:", output_path)



def register_keys_from_json(file_path):
    with open(file_path, "r") as f:
        keys = json.load(f)
    for key, value in keys.items():
        os.environ[key] = value

def save_to_file(data: str, file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(data)
def read_file(file_path:str):
    with open(file_path, "r") as f:
        return f.read()


# def create_inner_assistant(
#         name, system_message, llm_config, max_round=10,
#         code_execution_config=None
#     ):

#     inner_assistant = autogen.AssistantAgent(
#         name=name,
#         system_message=system_message + "Reply TERMINATE when the task is done.",
#         llm_config=llm_config,
#         is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
#     )
#     executor = autogen.UserProxyAgent(
#         name=f"{name}-executor",
#         human_input_mode="NEVER",
#         code_execution_config=code_execution_config,
#         default_auto_reply="",
#         is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
#     )
#     assistant.register_nested_chats(
#         [{"recipient": assistant, "message": reflection_message, "summary_method": "last_msg", "max_turns": 1}],
#         trigger=ConversableAgent
#         )
#     return manager
