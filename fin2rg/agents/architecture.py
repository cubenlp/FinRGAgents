import os 
from fin2rg.data_source.tushare_utils import TuShareUtils
from fin2rg.data_source.news_utils import News_utils
from fin2rg.functional import IPythonUtils, TextUtils, ReportAnalysisUtils
from fin2rg.functional.charting import MyReportChartUtils, ReportChartUtils
# from functional.KBUtils import KBUtils
from fin2rg.functional.report import ReportLabUtils
from fin2rg.argument_gen.argument_gen_utils import ClaimUtils
from fin2rg.functional.writing import ContentWritingUtils
from fin2rg.functional.baseline import BaselineUtils

dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
work_dir = os.path.join(dir_path, "report")

toolkits = {
    IPythonUtils.display_image,  # Display image in IPython
}


news_analysts = {
    "title": "News Analyst",
    "name": "News Analyst",
    "responsibilities": [
        "必须使用工具搜寻公司相关的新闻资料",
        "新闻资料的分析和解读，以提供丰富且有价值的信息和见解",
        "总结每一条新闻的内容，并对每条新闻进行编号"
        """总结全部的新闻信息为以下格式:
### 新闻内容
通过最新资讯收集，我们获得了几条XXX相关的重要新闻：

1. **新闻内容以及影响因子**

2. **新闻内容以及影响因子**
...
...
"""
    ],
    "toolkits": [
        ReportAnalysisUtils.get_company_news,  # Retrieve Recent Related News
    ],
}

economic_analysts = {
    "title": "Economic Trends Analyst",
    "responsibilities": [
        "分析宏观经济形势",
        "使用中文",
    ],
    "toolkits": [
    ],
}

industry_analysts = {
    "title": "Industry Development Analyst",
    "responsibilities": [
        "分析行业发展趋势",
        "使用中文",
    ],
    "toolkits": [
    ],
}

market_analysts = {
    "name": "市场分析部门",
    "responsibilities": [
        "关注宏观经济趋势、行业发展和市场情绪。",
        "提供市场趋势的报告，帮助团队了解大环境下的投资机会与风险。",
        "使用中文"
    ],
    "with_leader": {
        "leader": {
            "title": "市场分析组组长",
            "name": "市场分析组组长",
            "responsibilities": [
                "关注宏观经济趋势、行业发展和市场情绪。",
                "提供市场趋势的报告，帮助团队了解大环境下的投资机会与风险。",
                "使用中文"
            ],
        },
        "employees": [
            economic_analysts,
            industry_analysts,
            news_analysts

        ],
    },
    "without_leader": {
        "name": "市场分析部门",
        "employees": [
            economic_analysts,
            industry_analysts,
            news_analysts
        ],
    },
}

findata_analysts = {
    "title": "Financial Data Analyst",
    "name": "Financial Data Analyst",
    "responsibilities": [
        "使用tool获取研究公司的相关财务数据，每个tool调用次数不能超过一次。",
        "研究和分析公司的财务报表。",
        "运用各种财务比率，如流动比率、杠杆比率、盈利率和回报率等，来评价公司的运营效率和财务稳定性。",
        """使用中文总结全部的财务数据信息信息""",
    ],
    "toolkits": [
        ReportAnalysisUtils.get_stock_data,  # retrieve stock data dataframe
        TuShareUtils.get_index_daliy,  # retrieve stock data dataframe
        ReportAnalysisUtils.analyze_income_stmt,  # retrieve income statement dataframe
        ReportAnalysisUtils.analyze_balance_sheet,  # retrieve income statement dataframe
        ReportAnalysisUtils.analyze_cash_flow,  # retrieve cash flow dataframe
        ReportAnalysisUtils.analyze_business_highlights, # retrieve business highlights dataframe
        ReportAnalysisUtils.get_risk_assessment # retrieve risk assessment dataframe
    ],
}


vis_analysts = {
    "title": "Financial Data Visualization Specialist",
    "name": "Financial Data Visualization Specialist",
    "responsibilities": [
        "利用已有的工具进行可视化分析，每个tool只能使用一次",
        "依次绘制损益表现、主营业务分析和主要金融数据分析的可视化图表",
        f"工作目录在{work_dir}"
    ],
    "toolkits": [
        # ReportChartUtils,  # Expert Knowledge for Report Chart Plotting
        # MyReportChartUtils.cash_flow_plotting,  # Expert Knowledge for Report Chart Plotting
        # MyReportChartUtils.income_statement_plotting,  # Expert Knowledge for Report Chart Plotting
        # MyReportChartUtils.main_business_plotting,  # Expert Knowledge for Report Chart Plotting
        # MyReportChartUtils.main_financial_analysis,  # Expert Knowledge for Report Chart Plotting
        ReportChartUtils.get_pe_eps_performance,
        ReportChartUtils.get_share_performance
    ],
}

rating_analysts = {
    "title": "Investment Rating Analyst",
    "name": "Investment Rating Analyst",
    "responsibilities": [
        "预测公司的未来财务表现，包括收入增长和潜在的财务风险。",
        "基于财务分析结果，评估公司的投资价值和股票的公允价值。",
        "提供买入、持有或卖出的投资建议。",
        "使用中文"
    ],
    "toolkits": [
        ReportAnalysisUtils,  # Expert Knowledge for Report Analysis
    ],
}

report_writer = {
    "title": "Report Writing Specialist",
    "name": "Report Writing Specialist",
    "responsibilities": [
        """汇总已有信息，根据字数限制总结报告内容"""
    ],
    "toolkits": [
        # ReportLabUtils.build_annual_report
        ContentWritingUtils.ReportWriting,
        # ContentWritingUtils.generate_report
    ],
}

claim_writer = {
    "title": "Chief Analyst",
    "name": "Chief Analyst",
    "responsibilities": [
        """根据已有的数据源，生成具有前瞻性的中心论点和分论点"""
    ],
    "toolkits": [
        ClaimUtils.get_major_claim
    ],
}

outline_writer = {
    "title": "Senior Analyst",
    "name": "Senior Analyst",
    "responsibilities": [
        """根据中心论点和分论点通过使用工具生成大纲。"""
    ],
    "toolkits": [
        ClaimUtils.get_outline
    ],
}

report_checker = {
    "title": "Report Verification Specialist",
    "name": "Report Verification Specialist",
    "responsibilities": [
        "确保text中包含了正确数据和新闻的引用，例如<1>这样的数据引用",
        "数据源的标注十分关键，需要在报告里以相关的标号进行标示，例如：XX股价呈现下跌趋势<1>"
        "检查报告格式是否规范，使用工具检查长度要求是否合规，如果长度不符合要求，需要对相关内容进行适当缩写或扩充以达到要求。",
        "获得当前长度符合标准的提示后，使用工具保存最终报告，确认保存成功。",
        "任务结束时输出TERMINATE"
    ],
    "toolkits": [
        TextUtils.check_text_length,  # Check text length
        ReportLabUtils.build_annual_report,  # Save json file report
    ],
}

kb_builder = {
    "title": "Knowledge Analysts",
    "name": "Knowledge Analysts",
    "responsibilities": [
        "抽取文件中（包括PDF和图片）的内容，并汇总为文本形式信息，并对汇总后的信息进行保存",
        "需要关注数据信息，这非常重要，尽量使用中文"
        """输出样例：
{
    "全球5G商用网络部署情况": {
        "2019": {
            "5G商用网络数量": "xxxx万",
            "新增数量": "xxxx万"
        },
        "2020": {
            ...
        },
        ...
    },
    ...
}
        """,
        "将JSON文件文件使用工具进行保存",
        "任务结束时输出TERMINATE"
    ],
    "toolkits": [
        # KBUtils.analyse_pdf,  # Analyse pdf
        # KBUtils.analyse_image,  # Analyse image
        # KBUtils.save_knowledge_file,  # Save json file report
    ],
}

industry_data_analysts = {
    "title": "Industry Data Analyst",
    "name": "Industry Data Analyst",
    "responsibilities": [
        "获取行业宏观数据，这些数据以JSON格式存储在相应位置，读取JSON文件以获取全部信息",
        "筛选必要的信息，为其他人的任务做准备",
        "不需要对最终报告进行生成，那是其他人的事情",
        """将筛选后的信息总结为以下的JSON格式:
{
    "数据名称": {
        "数据": {...}
        "数据来源": {...}
    },
    "数据名称": {
        "数据": {...}
        "数据来源": {...}
    },
    ...
}
"""
    ],
    "toolkits": [
        # IndustryDataUtils.get_industry_data,  # Retrieve data
    ],
}

industry_news_analysts = {
    "title": "Industry News Analyst",
    "name": "Industry News Analyst",
    "responsibilities": [
        "使用工具搜寻行业相关的新闻资料，不需要再对个股信息进行查询，使用相关行业的概念进行信息搜集",
        "新闻资料的分析和解读，以提供丰富且有价值的信息和见解",
        "总结每一条新闻的内容，并对每条新闻进行编号"
        "不要生成最终的行业研究报告，那是其他人的事情，认清自己的职责",
        """总结全部的新闻信息为以下格式:
### 新闻内容
通过最新资讯收集，我们获得了几条XXX相关的重要新闻：

1. **新闻标题xxxx**
   - 来源：(http://xxxx)

2. **新闻标题xxxx**
   - 来源：(http://xxxx)
...


### 新闻总结

- 新闻总结1 <1><2>
- 新闻总结2 <3><4><5>
...
"""
    ],
    "toolkits": [
        # NewsUtils.fetch_news,  # Retrieve Recent Related News
        # ReportLabUtils.build_annual_report,  # Build annual report in designed pdf format
    ],
}

industry_stock_writer = {
    "title": "Industry Report Writing Specialist",
    "name": "Industry Report Writing Specialist",
    "responsibilities": [
        """汇总已有信息，根据字数限制总结报告内容，并记录相应的数据出处和引用""",
        """数据源的标注十分关键，需要在json格式的报告里以相关的标号进行标示，例如：XX股价呈现下跌趋势<1>...""",
        """例如:
```json
{
"company_name": "骆驼股份",
"stock_code": "601311",
"level":"1",
"text": "骆驼股份的股价在最近一年内波动较大，近期股价呈现下跌趋势<1>。公司在2024年第一季度实现净利润1.56亿元，同比下降4.86%。全年净利润为5.72亿元，同比增长21.79%<2>。资产负债率为32.80%<3>。经营活动产生的现金流量净额为6.91亿元，同比增长1.81倍<4>。近期新闻显示，公司2023年年度权益分派每股派发现金红利0.27元<5>。公司表示铅价的上涨对其影响较小<6>。公司2024年一季度净利润1.56亿元，同比下降4.86%<7>。综合以上分析，建议持有骆驼股份。"
"source":[
    {"<1>":"市场数据"},
    {"<2>":"利润表数据"},
    {"<3>":"资产负债表数据"},
    {"<4>":"现金流量表数据"},
    {"<5>":"新闻:2023年年度权益分派10派2.7元(http://yuqiqiao.machine365.com/news/3274894584.html)"},
    {"<6>":"新闻:铅价上涨影响较小(https://t.10jqka.com.cn/pid_373223455.shtml)"},
    {"<7>":"新闻:2024年一季度净利润下降4.86%(https://xueqiu.com/S/601311)"}
]
}
```
""",
        "其中，level=0对应卖出，level=1对应持有",
        "stock_code不需要包含.SZ或.SH",
        "输出最终的JSON格式",
    ],
    "toolkits": [
    ],
}

industry_viz_analysts = {
    "title": "Industry Data Visualization Specialist",
    "name": "Industry Data Visualization Specialist",
    "responsibilities": [
        "利用所有已有的工具对行业信息尽可能多地进行可视化分析，每个tool至少使用一次",
        "包括十只股票股价趋势图，十只股票均价趋势图，行业分布饼图，行业柱状图，行业折线图，这些图都是必须的",
        "使用中文",
        "针对的数据对象为行业宏观数据或者已经做过详细分析的个股，不能使用其他股票数据",
        "不需要对最终报告进行生成，那是其他人的事情",
        """以列表格式输出所有生成的数据图路径，例如：
["./imgs/XXX_ten_stock_trend.png", "./imgs/XXX_ten_stock_average_trend.png", "./imgs/XXX_distribution.png", "./imgs/XXX_barchart.png", "./imgs/XXX_linechart.png", ...]
""",
        # "依次绘制损益表现、主营业务分析和主要金融数据分析的可视化图表",
    ],
    "toolkits": [
        # ReportChartUtils,  # Expert Knowledge for Report Chart Plotting
        # MyReportChartUtils.cash_flow_plotting,  # Expert Knowledge for Report Chart Plotting
        MyReportChartUtils.plot_ten_stocks_trend,  # Expert Knowledge for Report Chart Plotting
        MyReportChartUtils.plot_ten_stocks_average_trend,  # Expert Knowledge for Report Chart Plotting
        MyReportChartUtils.plot_industry_pie,  # Expert Knowledge for Report Chart Plotting
        MyReportChartUtils.plot_two_bars_chart,  # Expert Knowledge for Report Chart Plotting
        MyReportChartUtils.plot_line_chart,  # Expert Knowledge for Report Chart Plotting
    ],
}

industry_report_writer = {
    "title": "Industry Report Writing Specialist",
    "name": "Industry Report Writing Specialist",
    "responsibilities": [
        """汇总已有信息，根据字数限制总结报告内容，并记录相应的数据出处和引用""",
        """例如:
{
"industry": "新能源储能行业",
"company_name": ["派能科技", "宁德时代", "亿纬锂能", "国电南瑞", "长虹能源", "赣锋锂业", "国轩高科", "德赛电池", "上能电气", "阳光电源"],
"stock_code": ["688063", "300750", "300014", "600406", "836239", "002460", "002074", "000049", "300827", "300274"],
"level": ["1", "1", "1", "1", "0", "0", "1", "0", "1", "1"],
"text": "截至2023年底，中国新型储能项目累计装机规模达3139万千瓦，同比增长超过260%<1>。这一数据表明，新能源储能行业正处于高速增长阶段。2024年中国储能电池出货量预计将超200GWh，同比增长超25%<3>，显示出储能电池市场的强劲增长潜力。此外，《新能源汽车产业发展规划(2021—2035年)》和《“十四五”新型储能发展实施方案》为行业发展提供了明确的方向和支持<4>。\n阳光电源成功签约全球最大储能项目，容量高达7.8GWh，2025年全容量并网运行<2>，显示出其在储能市场的领先地位。国轩高科2024年一季度实现归母净利润6,913.80万元，同比下降8.56%，但扣非归母净利润扭亏为盈，2023年产品交付突破40GWh，同比增长超过40%<5>。然而，赣锋锂业和德赛电池的财报显示扣非净利润分别下降111.89%和58.73%<6,7>，而国电南瑞和上能电气的业绩则相对稳定或增长<8,9>。",
"source": [
    {"<1>": "储能装机规模数据"},
    {"<2>": "阳光电源储能项目"},
    {"<3>": "储能电池出货量预测"},
    {"<4>": "国内政策环境"},
    {"<5>": "新闻:2023年年度权益分派10派2.7元(http://yuqiqiao.machine365.com/news/3274894584.html)"},
    {"<6>": "新闻:铅价上涨影响较小(https://t.10jqka.com.cn/pid_373223455.shtml)"},
    {"<7>": "新闻:第七届数xxx大会(https://www.ceweekly.cn/company/2024/0528/2341211.html)"},
    {"<8>": "新闻:人力资源成本呈现xxx(https://mp.weixin.qq.com/s?__biz=Mzg5NzI0OTc5OQ==cd421879152d4b);"},
],
"img": ["./imgs/xxx.png", "./imgs/yyy.png"]
}
""",
        "其中，level=0对应卖出，level=1对应持有",
        "stock_code不需要包含.SZ或.SH",
        "新闻数据源需要同时包含新闻的标题和url",
        "JSON中必须包含[industry, company_name, stock_code, level, text, source, img]",
        "数据源的标注十分关键，需要在json格式的报告里以相关的标号进行标示，例如：同比增长超过xxx%<1>",
        "输出最终的JSON格式",
    ],
    "toolkits": [
    ],
}

industry_report_checker = {
    "title": "Industry Report Verification Specialist",
    "name": "Industry Report Verification Specialist",
    "responsibilities": [
        "确保text中包含了正确数据和新闻的引用，例如<1>这样的数据引用",
        "数据源的标注十分关键，需要在报告里以相关的标号进行标示，例如：XX股价呈现下跌趋势<1>"
        "检查报告格式是否规范，使用工具检查长度要求是否合规，如果长度不符合要求，需要对相关内容进行适当缩写或扩充以达到要求。",
        "必须对报告进行检查",
        "获得当前长度符合标准的提示后，使用工具保存最终报告，确认保存成功。",
        "任务结束时输出TERMINATE"
    ],
    "toolkits": [
        TextUtils.check_text_length,  # Check text length
        # ReportUtils.save_report,  # Save json file report
    ],
}

# ----baseline agent config ----
baseline_report_writer = {
    "title": "Report Writing Specialist",
    "name": "Report Writing Specialist",
    "responsibilities": [
        """汇总已有信息，根据字数限制总结报告内容"""
    ],
    "toolkits": [
        BaselineUtils.ReportWriting
    ],
}


baseline_outline_writer = {
    "title": "Senior Analyst",
    "name": "Senior Analyst",
    "responsibilities": [
        """根据新闻、年报内容生成大纲。"""
    ],
    "toolkits": [
        BaselineUtils.get_outline
    ],
}