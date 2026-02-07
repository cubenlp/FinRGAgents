import json
from typing import Annotated


class TextUtils:

    def check_text_length(
            json_str: Annotated[str, "generated json string"],
            min_length: Annotated[int, "minimum length of the text, default to 0"] = 0,
            max_length: Annotated[int, "maximum length of the text, default to 100000"] = 100000,
    ) -> str:
        """
        Check the generated report, check the length of the text.
        """
        data = json.loads(json_str)
        lost = []
        cs = ["company_name", "stock_code", "level", "text", "source", "img"]
        for c in cs:
            if c not in data:
                lost.append(c)
        if lost:
            return f"缺少字段：{lost}，不允许保存，需要重新生成JSON，生成后重新进行验证。"
        if "<1>" not in data['text']:
            return f"text中缺少数据引用，不允许保存，需要重新生成JSON，生成后重新进行验证。"
        if "<img src" in data['text']:
            return f"text中使用了<img>标签，不允许保存，需要重新生成JSON，移除相应的<img>标签，生成后重新进行验证。"
        length = len(data['text'])
        if length > max_length:
            return f"当前字符数量：{length}，超过最大长度限制，不允许保存。请将内容重写为{min_length}字符。不允许删除数据源引用，生成后重新进行验证。"
        elif length < min_length:
            return f"当前字符数量：{length}，小于最小长度限制，不允许保存。请将内容重写为{max_length}字符。不允许删除数据源引用，生成后重新进行验证。"
        else:
            return f"当前长度符合标准，允许保存。"
