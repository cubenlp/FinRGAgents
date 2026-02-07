import io
import json
import os.path
import base64
import warnings

import autogen
import openai
import pypdfium2
from PIL import Image
from typing import Annotated


class KBUtils:
    @staticmethod
    def analyse_pdf(pdf_file: Annotated[str, "path to the pdf file"]):
        """
        Extract the data from a pdf file.
        """
        model = "gpt-4o"
        llm_config = {
            "config_list": autogen.config_list_from_json(
                "./OAI_CONFIG_LIST",
                filter_dict={
                    "model": [model],
                },
            )
        }
        api_key = llm_config['config_list'][0]['api_key']
        openai.api_key = api_key

        # 提取PDF中的文本
        pdf_f = pypdfium2.PdfDocument(pdf_file)
        text_content = []

        for page_num in range(len(pdf_f)):
            page = pdf_f.get_page(page_num)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                text = page.get_textpage().get_text_range()
            text_content.append(f"----- Page {page_num + 1} -----\n{text}\n")

        prompt_text = "\n".join(text_content)
        content = '''请阅读以下提供的文本，并重点关注文本中的数据信息。根据文本内容，生成一份内容概括摘要。摘要应分为多个部分，每个部分对应文本中的一个主要段落或主题。
请确保生成的报告格式为JSON格式，具体格式如下：
{
    "内容标题1": "详细内容",
    "内容标题2": "详细内容",
    "内容标题3": "详细内容",
    ...
}
请注意，每个部分的摘要应简洁明了，准确概括该部分的主要内容和数据信息，重点关注数据信息。确保JSON格式的正确性和可读性。
'''
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": prompt_text}
            ],
        )
        data = response.choices[0].message.content.strip().strip("```").strip("`").strip("json").strip()
        filename = os.path.basename(pdf_file)
        filename, _ = os.path.splitext(filename)

        return f"数据名称：{filename}\n{data}"

    @staticmethod
    def analyse_image(image_file: Annotated[str, "path to the image file"]):
        """
        Extract the data from an image file.
        """
        model = "gpt-4o"
        llm_config = {
            "config_list": autogen.config_list_from_json(
                "./OAI_CONFIG_LIST",
                filter_dict={
                    "model": [model],
                },
            )
        }
        api_key = llm_config['config_list'][0]['api_key']
        openai.api_key = api_key

        messages = [
            {"role": "user", "content": [{"type": "text", "text": "请提取图片中的数据,并将数据整理为json格式输出"}]}]
        buffered = io.BytesIO()
        image = Image.open(image_file)
        image.save(buffered, format=image.format)
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        image_message = {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
        }
        messages[0]["content"].append(image_message)

        response = openai.chat.completions.create(
            model=model,
            messages=messages,
        )

        data = response.choices[0].message.content.strip().strip("```").strip("`").strip("json").strip()

        filename = os.path.basename(image_file)
        filename, _ = os.path.splitext(filename)

        return f"数据名称：{filename}\n{data}"

    @staticmethod
    def save_knowledge_file(
            json_str: Annotated[str, "json format text for saving (start with `{` and end with `}`)"],
            save_path: Annotated[str, "target save json path (abspath, end with `.json`)"],
    ) -> str:
        """
        Save the extracted knowledge into a json file.
        """
        json_str = json_str.strip().strip("```").strip("`").strip("json").strip()
        data = json.loads(json_str)
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                extracted_data = json.load(f)
            data.update(extracted_data)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        with open(save_path, 'r') as f:
            extracted_data = json.load(f)
        if len(extracted_data) == len(data):
            return f"文件已成功保存至{save_path}"
        else:
            return "文件保存失败"


if __name__ == '__main__':
    kbs = KBUtils()
    # res = kbs.analyse_image("./KBS/raw_data/全球5G商用网络部署情况.png")
    res = kbs.analyse_pdf("./KBS/raw_data/全球5G-6G产业发展报告.pdf")
    print(res)
