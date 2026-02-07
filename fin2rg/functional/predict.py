from textwrap import dedent
from typing import Annotated
from fin2rg.utils import query_llm

class PredictStock:
    def predict_stock_price(
        ticker_symbol: Annotated[str, "公司名称"],
        stock_data_str: Annotated[str, "股票数据序列数据"],
        news_str: Annotated[str, "新闻factor"],
        summary_str: Annotated[str, "总结报告"]
    ) -> str:
        """预测某一家公司下一个交易日的股价涨跌情况"""
        # 过长的输入，是否会导致模型失焦？
        # news+report+stock - 》prompt
        # -》 gpt4
        # -》 输出
        # 后处理
        Predict_Temp = "根据以下信息，请判断股票价格是上涨还是下跌,请注意只需要输出上涨或者下跌,其他内容不需要输出。"
        prompt = dedent(
            f"""
            {Predict_Temp}
            "近期股价涨跌情况："{stock_data_str}
            "最近可能影响股价的因素："{news_str}
            "汇总报告："{summary_str}
            """
        )
        response = query_llm(prompt, "glm-4")
        return response