import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(dir_path)
import pandas as pd
import numpy as np
import tushare as ts
from pandas import DateOffset
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from typing import Annotated, List, Tuple
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
import mplfinance as mpf  # 如果选择使用mplfinance绘制OHLC
from scipy.interpolate import make_interp_spline
import matplotlib.font_manager as fm
from fin2rg.data_source.tushare_utils import TuShareUtils
from matplotlib.font_manager import FontProperties

bright_pastel_colors = [
    '#FFB3BA',  # Pastel Red
    '#FFDFBA',  # Pastel Orange
    '#FFFFBA',  # Pastel Yellow
    '#BAFFC9',  # Pastel Green
    '#FF9AA2',  # Light Coral
    '#FFDAC1',  # Peach
    '#E2F0CB',  # Mint
    '#B5EAD7',  # Aqua
    '#C7CEEA',  # Lavender
    '#FFD1DC',  # Pink
    '#FFE5B4',  # Peach
    '#D1E8E2',  # Light Blue
    '#FADADD',  # Light Pink
]

tushare_token = "300bc174085f58253fe6b7cbffe9628ed9f40d5dea8c9cb9cdde879a"
tushare_pro = ts.pro_api(tushare_token)

my_font = FontProperties(fname=os.path.join(dir_path, "fonts/SimHei.ttf"))

result_path = "result/"

# 设置mplfinance的蜡烛颜色，up为阳线颜色，down为阴线颜色
my_color = mpf.make_marketcolors(up='r',
                                 down='g',
                                 edge='inherit',
                                 wick='inherit',
                                 volume='inherit')
# 设置图表的背景色
my_style = mpf.make_mpf_style(marketcolors=my_color,
                              figcolor='(0.82, 0.83, 0.85)',
                              gridcolor='(0.82, 0.83, 0.85)')


class ReportChartUtils:

    def get_month_stock_data(
        ticker_symbol: Annotated[
            str, "股票的Ticker符号（例如，Apple的“AAPL”，宁波银行的“002142.ss”）"
        ],
        start_date: Annotated[
            str, "Start date of the historical data in 'YYYYMMDD' format"
        ],
        end_date: Annotated[
            str, "End date of the historical data in 'YYYYMMDD' format"
        ],
        save_path: Annotated[str, "File path where the plot should be saved"],
    ) -> str:
        """获取一段时间的股票数据，存储在.csv，并绘画一张股票数据图，输入包括：股票代码，开始时间，结束时间和保存地址"""

        stock_data = TuShareUtils.get_stock_data(ticker_symbol, start_date, end_date)
        stock_data.to_csv(result_path + save_path.split('.')[0] + '.csv', index=False)
        
        # 取出需要的列
        # stock_data.index = stock_data.trade_date
        # stock_data = stock_data.rename(index=pd.Timestamp) 
        stock_data.drop(columns=['ts_code', 'pre_close', 'change', 'pct_chg', 'amount'], inplace=True)
        stock_data.columns=['open', 'high', 'low', 'close', 'volume']
        stock_data.sort_index(inplace=True)

        ohlc = stock_data[['open', 'high', 'low', 'close']]
        volume = stock_data['volume']

        mpf.plot(stock_data, type='candle', volume=True, style=my_style, savefig=result_path + save_path)  
        # mpf.savefig(result_path + save_path, fig=fig)

        return f"数据保存到{result_path + save_path.split('.')[0] + '.csv'}，图片保存到{result_path + save_path}>"

    def get_share_performance(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock"
        ],
        filing_date: Annotated[str, "filing date in 'YYYYMMDD' format"],
        save_path: Annotated[str, "File path where the plot should be saved"],
    ) -> str:
        """Plot the stock performance of a company compared to the 沪深300 over the past year."""
        if isinstance(filing_date, str):
            filing_date = datetime.strptime(filing_date, "%Y%m%d")
        
        # def fetch_stock_data(ticker):
        start = (filing_date - timedelta(days=365)).strftime("%Y%m%d")
        end = filing_date.strftime("%Y%m%d")
        company_stock_data = TuShareUtils.get_stock_data(ticker_symbol, start, end)
        # company_stock_data['trade_date'] = pd.to_datetime(company_stock_data['trade_date'])  # 确保日期列是 datetime 类型
        # company_stock_data.set_index('trade_date', inplace=True)  # 将日期设置为索引
        target_close = company_stock_data["close"]

        hs300_stock_data = TuShareUtils.get_index_daliy("000300.sh", start, end)
        hs300_stock_data['trade_date'] = pd.to_datetime(hs300_stock_data['trade_date'])  # 确保日期列是 datetime 类型
        hs300_stock_data.set_index('trade_date', inplace=True)  # 将日期设置为索引
        hs300_close = hs300_stock_data["close"]

        info = TuShareUtils.get_stock_info(ticker_symbol)

        # 计算变化率
        company_change = (
            (target_close - target_close.iloc[0]) / target_close.iloc[0] * 100
        )
        hs300_change = (hs300_close - hs300_close.iloc[0]) / hs300_close.iloc[0] * 100

        # 计算额外的日期点
        start_date = company_change.index.min()
        four_months = start_date + DateOffset(months=4)
        eight_months = start_date + DateOffset(months=8)
        end_date = company_change.index.max()

        # 准备绘图
        plt.rcParams.update({"font.size": 30})  # 调整为更大的字体大小
        plt.figure(figsize=(14, 7))
        plt.plot(
            company_change.index,
            company_change,
            label=f'{info["name"][0]} Change %',
            color="blue",
            # fontproperties=my_font
        )
        plt.plot(
            hs300_change.index, hs300_change, label="沪深300 Change %", color="red"
            # fontproperties=my_font
        )

        # 设置标题和标签
        plt.title(f'{info["name"][0]} vs 沪深300 - Change % Over the Past Year', fontsize=20, fontproperties=my_font)
        plt.xlabel("Date")
        plt.ylabel("Change %")

        # 设置x轴刻度标签
        plt.xticks(
            [start_date, four_months, eight_months, end_date],
            [
                start_date.strftime("%Y-%m"),
                four_months.strftime("%Y-%m"),
                eight_months.strftime("%Y-%m"),
                end_date.strftime("%Y-%m"),
            ],
        )

        plt.legend(prop=my_font)
        plt.grid(True)
        plt.tight_layout()
        # plt.show()
        plot_path = (
            f"{save_path}/stock_performance.png"
            if os.path.isdir(save_path)
            else save_path
        )
        plt.savefig(plot_path)
        plt.close()
        return f"last year stock performance chart saved to <img {plot_path}>"

    def get_pe_eps_performance(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock"
        ],
        filing_date: Annotated[str | datetime, "filing date in 'YYYYMMDD' format"],
        years: Annotated[int, "number of years to search from, default to 4"] = 4,
        save_path: Annotated[str, "File path where the plot should be saved"] = None,
    ) -> str:
        """Plot the PE ratio and EPS performance of a company over the past n years."""
        if isinstance(filing_date, str):
            filing_date = datetime.strptime(filing_date, "%Y%m%d")
        
        ss = TuShareUtils.get_income_stmt(ticker_symbol, years)
        # ss['end_date'] = pd.to_datetime(ss['end_date'])  # 确保日期列是 datetime 类型
        # ss.set_index('end_date', inplace=True)  # 将日期设置为索引
        eps = ss.loc["diluted_eps", :]

        # 获取过去5年的历史数据
        # historical_data = self.stock.history(period="5y")
        days = round((years + 1) * 365.25)
        start = (filing_date - timedelta(days=days)).strftime("%Y%m%d")
        end = filing_date.strftime("%Y%m%d")
        historical_data = TuShareUtils.get_stock_data(ticker_symbol, start, end)
        # historical_data['trade_date'] = pd.to_datetime(historical_data['trade_date'])  # 确保日期列是 datetime 类型
        # historical_data.set_index('trade_date', inplace=True)  # 将日期设置为索引
        if not historical_data.index.is_monotonic_increasing:
            historical_data = historical_data.sort_index()
        
        # 指定的日期，并确保它们都是UTC时区的
        dates = pd.to_datetime(eps.index[::-1], utc=True)

        # 为了确保我们能够找到最接近的股市交易日，我们将转换日期并查找最接近的日期
        results = {}
        for date in dates:
            # 如果指定日期不是交易日，使用bfill和ffill找到最近的交易日股价
            if date not in historical_data.index:
                close_price = historical_data.asof(date.strftime("%Y-%m-%d"))
            else:
                close_price = historical_data.loc[date]

            results[date] = close_price["close"]

        pe = [p / e for p, e in zip(results.values(), eps.values[::-1])]
        dates = eps.index[::-1]
        eps = eps.values[::-1]

        info = TuShareUtils.get_stock_info(ticker_symbol)

        # 创建图形和轴对象
        fig, ax1 = plt.subplots(figsize=(14, 7))
        plt.rcParams.update({"font.size": 20})  # 调整为更大的字体大小

        # 绘制市盈率
        color = "tab:blue"
        ax1.set_xlabel("Date")
        ax1.set_ylabel("PE Ratio", color=color)
        ax1.plot(dates, pe, color=color)
        ax1.tick_params(axis="y", labelcolor=color)
        ax1.grid(True)

        # 创建与ax1共享x轴的第二个轴对象
        ax2 = ax1.twinx()
        color = "tab:red"
        ax2.set_ylabel("EPS", color=color)  # 第二个y轴的标签
        ax2.plot(dates, eps, color=color)
        ax2.tick_params(axis="y", labelcolor=color)

        # 设置标题和x轴标签角度
        plt.title(f'{info["name"][0]} PE Ratios and EPS Over the Past {years} Years',
                  fontsize=20,
                  fontproperties=my_font)
        plt.xticks(rotation=45)

        # 设置x轴刻度标签
        plt.xticks(dates, [datetime.strptime(d, "%Y%m%d").strftime("%Y-%m") for d in dates])

        plt.tight_layout()
        # plt.show()
        plot_path = (
            f"{save_path}/pe_performance.png" if os.path.isdir(save_path) else save_path
        )
        plt.savefig(plot_path)
        plt.close()
        return f"pe performance chart saved to <img {plot_path}>"
    

# 定义一个函数来绘制光滑的折线图
def plot_smooth_line(x, y, label):
    x_smooth = np.linspace(x.min(), x.max(), 300)
    spl = make_interp_spline(x, y, k=3)
    y_smooth = spl(x_smooth)
    plt.plot(x_smooth, y_smooth, label=label)



def create_path_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Path '{path}' created.")
    else:
        print(f"Path '{path}' already exists.")



def fetch_and_merge_data(stock_code, start_date, end_date):
    # 获取资产负债表数据
    df_BS = tushare_pro.balancesheet(ts_code=stock_code, start_date=start_date, end_date=end_date,
                             fields='ts_code,ann_date,f_ann_date,end_date,total_cur_assets,total_nca,total_assets,total_liab,minority_int')

    # 获取利润表数据
    df_IS = tushare_pro.income(ts_code=stock_code, start_date=start_date, end_date=end_date,
                       fields='ts_code,end_date,revenue,n_income,total_cogs')

    # 获取现金流量表数据
    df_CF = tushare_pro.cashflow(ts_code=stock_code, start_date=start_date, end_date=end_date,
                         fields='ts_code,ann_date,f_ann_date,end_date,n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act')

    # 合并数据
    df_merged = pd.merge(df_BS, df_IS, on=['ts_code', 'end_date'], how='outer')
    df_merged = pd.merge(df_merged, df_CF, on=['ts_code', 'end_date'], how='outer')

    # 确保 end_date 列是日期时间类型
    df_merged['end_date'] = pd.to_datetime(df_merged['end_date'], errors='coerce')

    # 过滤掉无效的日期时间值
    df_merged = df_merged.dropna(subset=['end_date'])

    # 按照 end_date 的时间递增排序
    df_merged = df_merged.sort_values(by='end_date')

    # 提取年份
    df_merged['year'] = df_merged['end_date'].dt.year

    # 检查并处理重复的年份
    df_merged = df_merged.drop_duplicates(subset=['year'], keep='first')

    # 确保年份是严格递增的
    if not df_merged['year'].is_monotonic_increasing:
        raise ValueError("Year column is not strictly increasing.")

    df_merged = df_merged.drop(
        columns=['ann_date_x', 'f_ann_date_x', 'f_ann_date_y', 'end_date', 'ann_date_y', 'ts_code'])
    # 确保year列是整数类型
    df_merged['year'] = df_merged['year'].astype(int)
    # 重命名列名为中文
    column_mapping = {
        'total_cur_assets': '流动资产',
        'total_nca': '非流动资产',
        'total_assets': '资产',
        'total_liab': '负债',
        'minority_int': '少数股东权益',
        'revenue': '营业收入',
        'n_income': '净利润',
        'total_cogs': '营业成本',
        'n_cashflow_act': '经营现金流',
        'n_cashflow_inv_act': '投资现金流',
        'n_cash_flows_fnc_act': '筹资现金流',
        'year': '年份'
    }
    df_merged = df_merged.rename(columns=column_mapping)

    # 保留小数点后两位
    numeric_columns = [
        '流动资产', '非流动资产', '资产', '负债', '少数股东权益',
        '营业收入', '净利润', '营业成本', '经营现金流',
        '投资现金流', '筹资现金流'
    ]
    df_merged[numeric_columns] = df_merged[numeric_columns] / 1e8

    df_merged[numeric_columns] = df_merged[numeric_columns].round(2)

    df_merged = df_merged[['年份'] + [col for col in df_merged.columns if col != '年份']]

    print(df_merged)

    return df_merged



def plot_dataframe(df, stock_code, save_path, company=''):
    # 创建一个新的图形
    fig, ax = plt.subplots(figsize=(15, 10), dpi=280)

    # 隐藏坐标轴
    ax.axis('off')

    # 使用 table 方法绘制表格
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    # 设置表格标题
    ax.set_title(f'{company}主要财务数据表（单位：亿元）', fontsize=14, fontweight='bold', fontproperties=my_font)
    # 隐藏坐标轴
    ax.axis('off')

    # 格式化数值列，保留小数点后两位
    formatted_values = df.values.tolist()
    for i in range(len(formatted_values)):
        for j in range(len(df.columns)):
            if df.columns[j] in [
                '流动资产', '非流动资产', '资产', '负债', '少数股东权益',
                '营业收入', '净利润', '营业成本', '经营现金流',
                '投资现金流', '筹资现金流'
            ]:
                formatted_values[i][j] = f'{formatted_values[i][j]:.2f}'
    # 设置表格的字体大小
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    # 设置列标签的字体属性
    for i, col_name in enumerate(df.columns):
        cell = table[0, i]
        cell.set_text_props(fontproperties=my_font)

        # 设置表格的边框和背景颜色
    for key, cell in table.get_celld().items():
        cell.set_edgecolor('black')
        if key[0] == 0:
            cell.set_facecolor('#f2f2f2')
            cell.set_text_props(fontproperties=my_font, fontweight='bold')
        else:
            cell.set_facecolor('white')

    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

class MyReportChartUtils:
    def cash_flow_plotting(stock_code: Annotated[
        str, "stock code"
    ], start_date: Annotated[
        str, "Start date of the cash flow in 'YYYYMMDD' format"
    ], end_date: Annotated[
        str, "End date of the cash flow in 'YYYYMMDD' format"
    ]) -> str:
        """Plot the cash flow performance of a company over the past n years."""
        df_cf = tushare_pro.cashflow(ts_code=stock_code, start_date=start_date, end_date=end_date,
                             fields='ts_code,ann_date,f_ann_date,end_date,n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act')

        # 获取年报数据
        filtered_df = df_cf[df_cf['end_date'].str.contains('1231')]
        # 将 end_date 转换为 datetime 类型
        filtered_df['end_date'] = pd.to_datetime(filtered_df['end_date'], errors='coerce')
        # 过滤掉无效的日期时间值
        filtered_df = filtered_df.dropna(subset=['end_date'])

        # 按照 end_date 的时间递增排序
        filtered_df = filtered_df.sort_values(by='end_date')
        # 提取年份
        filtered_df['year'] = filtered_df['end_date'].dt.year
        # 检查并处理重复的年份
        filtered_df = filtered_df.drop_duplicates(subset=['year'], keep='first')

        # 确保年份是严格递增的
        if not filtered_df['year'].is_monotonic_increasing:
            raise ValueError("Year column is not strictly increasing.")

        # 将现金流数值除以 10^8 以亿为单位
        filtered_df['n_cashflow_act'] /= 1e8
        filtered_df['n_cashflow_inv_act'] /= 1e8
        filtered_df['n_cash_flows_fnc_act'] /= 1e8
        # 绘制折线图
        plt.figure(figsize=(10, 6), dpi=280)

        # 绘制光滑的折线图并标注具体值
        for column, label in zip(['n_cashflow_act', 'n_cashflow_inv_act', 'n_cash_flows_fnc_act'],
                                 ['Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow']):
            plot_smooth_line(filtered_df['year'], filtered_df[column], label)
            # for x, y in zip(filtered_df['year'], filtered_df[column]):
            #     if abs(y) < 0.01:  # 如果数值非常小，使用科学计数法
            #         plt.annotate(f'{y:.2e}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontproperties=my_font)
            #     else:
            #         plt.annotate(f'{y:.2f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontproperties=my_font)

        plt.xlabel('年份', fontproperties=my_font)
        plt.ylabel('现金流(亿元)', fontproperties=my_font)
        plt.title('现金流量分析', fontproperties=my_font)
        plt.legend()
        plt.grid(True)
        # plt.show()

        # 指定保存路径
        save_path = os.path.join(result_path, stock_code.split('.')[0] + '_cash_flow_analysis.png')
        # 保存图片
        plt.savefig(save_path, bbox_inches='tight')

        return f"cash flow analysis chart saved to <img {save_path}>"

    def income_statement_plotting(stock_code: Annotated[
        str, "stock code"
    ], start_date: Annotated[
        str, "Start date of the cash flow in 'YYYYMMDD' format"
    ], end_date: Annotated[
        str, "End date of the cash flow in 'YYYYMMDD' format"
    ]) -> str:
        """Plot the income statement performance of a company over the past n years."""
        df_IS = tushare_pro.income(ts_code=stock_code, start_date='20180101', end_date='20240630',
                           fields='ts_code,end_date,revenue,n_income,total_cogs')
        # 确保 end_date 列是日期时间类型
        df_IS['end_date'] = pd.to_datetime(df_IS['end_date'], errors='coerce')

        # 过滤掉无效的日期时间值
        df_IS_filtered = df_IS.dropna(subset=['end_date'])

        # 按照 end_date 的时间递增排序
        df_IS_filtered = df_IS_filtered.sort_values(by='end_date')

        # 提取年份
        df_IS_filtered['year'] = df_IS_filtered['end_date'].dt.year

        # 检查并处理重复的年份
        df_IS_filtered = df_IS_filtered.drop_duplicates(subset=['year'], keep='first')

        # 确保年份是严格递增的
        if not df_IS_filtered['year'].is_monotonic_increasing:
            raise ValueError("Year column is not strictly increasing.")

        df_IS_filtered = df_IS_filtered.query('2019 <= year <= 2023')

        # 将revenue和n_income转换为亿为单位
        df_IS_filtered['revenue_billion'] = df_IS_filtered['revenue'] / 1e8
        df_IS_filtered['n_income_billion'] = df_IS_filtered['n_income'] / 1e8
        df_IS_filtered['total_cogs_billion'] = df_IS_filtered['total_cogs'] / 1e8

        # 创建柱状图
        fig, ax = plt.subplots(figsize=(10, 6), dpi=280)

        # 设置柱状图的宽度
        bar_width = 0.35

        # 计算每个柱状图的位置
        index = df_IS_filtered['year']
        index_revenue = index - bar_width / 2
        index_n_income = index + bar_width / 2

        # # 绘制revenue的柱状图
        # ax.bar(index_revenue, df_IS_filtered['revenue_billion'], bar_width, label='revenue', alpha=0.7)

        # # 绘制n_income的柱状图
        # ax.bar(index_n_income, df_IS_filtered['n_income_billion'], bar_width, label='net income', alpha=0.7)

        # 绘制revenue的柱状图
        bars_revenue = ax.bar(index_revenue, df_IS_filtered['revenue_billion'], bar_width, label='收入（单位：亿元）',
                              color='#FF6347', alpha=0.7)

        # 绘制n_income的柱状图
        bars_n_income = ax.bar(index_n_income, df_IS_filtered['n_income_billion'], bar_width, label='净利润（单位：亿元）',
                               color='#FFA07A', alpha=0.7)

        # 绘制total_cogs的折线图
        ax.plot(index, df_IS_filtered['total_cogs_billion'], marker='o', color='#FF4500', label='总成本（单位：亿元）')

        # 标注数值
        for bar in bars_revenue:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),
                        textcoords="offset points", ha='center', va='bottom', fontproperties=my_font)

        for bar in bars_n_income:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),
                        textcoords="offset points", ha='center', va='bottom', fontproperties=my_font)

        # 计算最近一年的同比变化
        last_year_revenue = df_IS_filtered.loc[df_IS_filtered['year'] == 2023, 'revenue_billion'].values[0]
        last_year_n_income = df_IS_filtered.loc[df_IS_filtered['year'] == 2023, 'n_income_billion'].values[0]

        prev_year_revenue = df_IS_filtered.loc[df_IS_filtered['year'] == 2022, 'revenue_billion'].values[0]
        prev_year_n_income = df_IS_filtered.loc[df_IS_filtered['year'] == 2022, 'n_income_billion'].values[0]

        revenue_growth = ((last_year_revenue - prev_year_revenue) / prev_year_revenue) * 100
        n_income_growth = ((last_year_n_income - prev_year_n_income) / prev_year_n_income) * 100

        # 标注同比变化
        revenue_arrow = '↑' if revenue_growth > 0 else '↓'
        n_income_arrow = '↑' if n_income_growth > 0 else '↓'
        ax.annotate(
            f'2023收入增长百分比: {revenue_growth:.2f}% {revenue_arrow} | 2023净收入增长百分比: {n_income_growth:.2f}% {n_income_arrow}',
            xy=(0.5, 1.1), xycoords='axes fraction', ha='center', fontsize=12, color='black', fontproperties=my_font)

        # 设置图例
        ax.legend(prop=my_font)

        # 设置标题和标签
        ax.set_title('业绩情况分析', fontproperties=my_font)
        ax.set_xlabel('年份', fontproperties=my_font)
        ax.set_ylabel('亿元', fontproperties=my_font)

        # 指定保存路径
        # dir_path = os.path.join(result_path, 'result', 'task_1', 'imgs')
        dir_path = result_path
        create_path_if_not_exists(dir_path)
        file_name = stock_code.split('.')[0] + '_performance_analysis.png'
        save_path = os.path.join(dir_path, file_name)
        # 保存图片
        plt.savefig(save_path, bbox_inches='tight')
        return f"performance analysis chart saved to <img {os.path.join(dir_path, file_name)}>"

    def main_business_plotting(
            stock_code: Annotated[str, "stock code"],
            start_date: Annotated[str, "Start date of the cash flow in 'YYYYMMDD' format"],
            end_date: Annotated[str, "End date of the cash flow in 'YYYYMMDD' format"],
            type: Annotated[str, "business type, default = 'P'"]
    ) -> str:
        """Plot the main business analysis of a company over the past n years."""
        df_mainbz = tushare_pro.fina_mainbz(ts_code=stock_code, start_date=start_date, end_date=end_date,   type=type,
                                    fields='ts_code,end_date,bz_item,bz_profit')

        # 绘制饼图
        plt.figure(figsize=(10, 7), dpi=280)
        wedges, texts, autotexts = plt.pie(df_mainbz['bz_profit'], labels=df_mainbz['bz_item'], autopct='%1.1f%%',
                                           startangle=140, colors=bright_pastel_colors[:len(df_mainbz)],
                                           textprops={'fontsize': 12, 'color': 'black', 'fontproperties': my_font})

        # 添加标题
        plt.title('主营业务分析', fontproperties=my_font)

        # # 显示图例
        # plt.legend(df_mainbz['bz_item'], loc='best', prop=prop)

        # # 调整图例位置，避免覆盖饼图
        # plt.legend(wedges, df_mainbz['bz_item'], loc="center left", bbox_to_anchor=(1.2, 0.5), prop=prop)
        # 显示图形
        # plt.show()
        # dir_path = os.path.join(result_path, 'result', 'task_1', 'imgs')
        dir_path = result_path
        # 指定保存路径
        create_path_if_not_exists(dir_path)
        file_name = stock_code.split('.')[0] + '_main_business_analysis.png'
        save_path = os.path.join(dir_path, file_name)
        # 保存图片
        plt.savefig(save_path, bbox_inches='tight')

        return f"main business analysis chart saved to <img {os.path.join(dir_path, file_name)}>"

    def main_financial_analysis(
            stock_code: Annotated[str, "stock code"],
            start_date: Annotated[str, "Start date of the cash flow in 'YYYYMMDD' format"],
            end_date: Annotated[str, "End date of the cash flow in 'YYYYMMDD' format"],
            company: Annotated[str, "Company Name in Chinese"]) -> str:
        """Plot the main financial analysis of a company over the past n years."""
        # 获取并合并数据
        df_merged = fetch_and_merge_data(stock_code, start_date, end_date)

        # 指定保存路径
        # dir_path = os.path.join(result_path, 'result', 'task_1', 'imgs')
        dir_path = result_path
        create_path_if_not_exists(dir_path)
        file_name = stock_code.split('.')[0] + '_financial_analysis.png'
        save_path = os.path.join(dir_path, file_name)
        # save_path = os.path.join(result_path, 'result', "task_1", stock_code.split('.')[0] + '_financial_analysis' + '.png')
        # 绘制并保存表格
        plot_dataframe(df_merged, stock_code, save_path, company)
        return f"main financial analysis chart saved to <img {os.path.join(dir_path, file_name)}>"

    def plot_ten_stocks_trend(
            industry: Annotated[str, "industry name"],
            company_name: Annotated[List[str], "a list including company names of stocks"],
            stock_code: Annotated[List[str], "a list including stock codes of the stocks(code end with .SH or .SZ etc)"]
    ) -> str:
        """Draw a picture showing the trend of stocks' prices in one industry"""
        # 获取今天的日期
        end_date = datetime.today()

        # 计算一年前的日期
        start_date = end_date - timedelta(days=365)

        # 格式化日期为字符串
        end_date = end_date.strftime('%Y%m%d')
        start_date = start_date.strftime('%Y%m%d')

        # 存储所有股票数据的DataFrame
        all_data = pd.DataFrame()

        # 获取每只股票的数据
        for code in stock_code:
            stock_data = tushare_pro.weekly(ts_code=code, start_date=start_date, end_date=end_date,
                                    fields=['ts_code', 'trade_date', 'close'])
            all_data = pd.concat([all_data, stock_data])

        # 将数据按日期排序
        all_data = all_data.sort_values(by='trade_date')

        # 绘制图表
        plt.figure(figsize=(14, 7), dpi=280)

        for code, name in zip(stock_code, company_name):
            subset = all_data[all_data['ts_code'] == code]
            plt.plot(subset['trade_date'], subset['close'], label=name)

        # 减少x轴刻度的密度
        dates = all_data['trade_date'].unique()
        step = max(1, len(dates) // 10)  # 每10个日期显示一个刻度
        plt.xticks(dates[::step], rotation=45)

        plt.title(industry + '股票收盘价趋势图', fontproperties=my_font)
        plt.xlabel('日期', fontproperties=my_font)
        plt.ylabel('收盘价', fontproperties=my_font)
        plt.legend(prop=my_font)

        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        # dir_path = os.path.join(result_path, 'result', 'task_2', 'imgs')
        dir_path = result_path
        create_path_if_not_exists(dir_path)
        file_name = industry + '_ten_stock_trend.png'
        save_path = os.path.join(dir_path, file_name)
        # 保存图片
        plt.savefig(save_path, bbox_inches='tight')
        return f"Ten stocks trend chart saved to <img {os.path.join(dir_path, file_name)}>"

    def plot_ten_stocks_average_trend(
            industry: Annotated[str, "industry name"],
            company_name: Annotated[List[str], "a list including company names of stocks"],
            stock_code: Annotated[List[str], "a list including stock codes of the stocks(code end with .SH or .SZ)"]
    ) -> str:
        """Draw a picture showing the trend of an industry based on ten main stocks' prices"""

        # 获取今天的日期
        end_date = datetime.today()
        # 计算一年前的日期
        start_date = end_date - timedelta(days=365)

        # 格式化日期为字符串
        end_date = end_date.strftime('%Y%m%d')
        start_date = start_date.strftime('%Y%m%d')

        # 存储所有股票数据的DataFrame
        all_data = pd.DataFrame()

        # 获取每只股票的数据
        for code in stock_code:
            stock_data = tushare_pro.weekly(ts_code=code, start_date=start_date, end_date=end_date,
                                    fields=['ts_code', 'trade_date', 'close'])
            all_data = pd.concat([all_data, stock_data])

        # 将数据按日期排序
        all_data = all_data.sort_values(by='trade_date')

        # 计算加权平均值
        weights = [0.1] * len(stock_code)
        # weighted_average = all_data.groupby('trade_date')['close'].apply(lambda x: (x * weights).sum() / sum(weights))
        weighted_average = all_data.groupby('trade_date').apply(
            lambda x: (x['close'] * weights[:len(x)]).sum() / sum(weights[:len(x)]))
        # 绘制图表
        plt.figure(figsize=(14, 7), dpi=280)
        plt.plot(weighted_average.index, weighted_average.values, label='加权平均收盘价')

        # 减少x轴刻度的密度
        dates = all_data['trade_date'].unique()
        step = max(1, len(dates) // 10)  # 每10个日期显示一个刻度
        plt.xticks(dates[::step], rotation=45)

        plt.title(industry + '加权平均收盘价趋势图', fontproperties=my_font)
        plt.xlabel('日期', fontproperties=my_font)
        plt.ylabel('加权平均收盘价', fontproperties=my_font)
        plt.legend(prop=my_font)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        # save_path = "./" + industry + "_ten_stock_average_trend.png"
        # plt.savefig(save_path)
        # dir_path = os.path.join(result_path, 'result', 'task_2', 'imgs')
        dir_path = result_path
        create_path_if_not_exists(dir_path)
        file_name = industry + '_ten_stock_average_trend.png'
        save_path = os.path.join(dir_path, file_name)
        # 保存图片
        plt.savefig(save_path, bbox_inches='tight')
        return f"Ten stocks average trend chart saved to <img {os.path.join(dir_path, file_name)}>"

    def plot_industry_pie(
            industry: Annotated[str, "name of the industry"],
            labels: Annotated[List[str], "a list of labels"],
            sizes: Annotated[List[float], "a list of numbers showing how much each label covers"],
            title: Annotated[str, "title of the pie chart"],
            resource_name: Annotated[str, "names of data resource (default is None)"]
    ) -> str:
        """draw a pie chart showing industry distribution"""
        # 创建图形和轴
        fig, ax = plt.subplots(dpi=280)

        # 绘制饼图
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=bright_pastel_colors[:len(labels)],
               textprops={'fontsize': 12, 'color': 'black', 'fontproperties': my_font})

        # 添加标题
        ax.set_title(title, fontproperties=my_font)
        # 在最下方增加一行文字“资料来源：”
        plt.figtext(0.1, 0.01, '资料来源：' + resource_name, ha='left', va='bottom', fontsize=10,
                    fontproperties=my_font)

        # dir_path = os.path.join(result_path, 'result', 'task_2', 'imgs')
        dir_path = result_path
        create_path_if_not_exists(dir_path)
        file_name = industry + "_distribution.png"
        save_path = os.path.join(dir_path, file_name)
        # 保存图片
        plt.savefig(save_path, bbox_inches='tight')
        return f"Industry distribution chart saved to <img {os.path.join(dir_path, file_name)}>"

    def plot_two_bars_chart(
            x_labels: Annotated[List, "A list of labels for the x-axis"],
            data1: Annotated[List[float], "A list of values for the first dataset"],
            data2: Annotated[List[float], "A list of values for the second dataset"],
            x_label: Annotated[str, "The label for the x-axis"],
            y_label: Annotated[str, "The label for the y-axis"],
            title: Annotated[str, "The title of the bar chart"],
            data1_label: Annotated[str, "The label for the first dataset"],
            data2_label: Annotated[str, "The label for the second dataset"],
            source_text: Annotated[str, "The source text to display at the bottom of the chart (default is None)"],
            industry: Annotated[str, "The industry name"]
    ) -> str:
        """Draws a bar chart for two datasets with a common x-axis."""
        bar_width = 0.35

        # 生成x轴的位置
        index = np.arange(len(x_labels))

        # 创建图形和轴
        fig, ax = plt.subplots(dpi=280)

        # 绘制柱状图
        rects1 = ax.bar(index - bar_width / 2, data1, bar_width, label=data1_label)
        rects2 = ax.bar(index + bar_width / 2, data2, bar_width, label=data2_label)

        # 添加标签、标题和图例
        ax.set_xlabel(x_label, fontproperties=my_font)
        ax.set_ylabel(y_label, fontproperties=my_font)
        ax.set_title(title, fontproperties=my_font)
        ax.set_xticks(index)
        ax.set_xticklabels(x_labels, fontproperties=my_font)
        ax.legend(prop=my_font)

        # 在柱子上添加数值标签
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height}', xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontproperties=my_font)

        autolabel(rects1)
        autolabel(rects2)

        # 显示图形
        plt.tight_layout()

        # 在最下方增加一行文字“资料来源：”
        if source_text:
            plt.figtext(0.1, 0.01, "资料来源：" + source_text, ha='left', va='bottom', fontsize=10,
                        fontproperties=my_font)

        plt.show()
        # save_path = "./" + industry + "_barchart.png"
        # plt.savefig(save_path)
        # plt.close()
        # dir_path = os.path.join(result_path, 'result', 'task_2', 'imgs')
        dir_path = result_path
        create_path_if_not_exists(dir_path)
        file_name = industry + '_barchart.png'
        save_path = os.path.join(dir_path, file_name)
        # 保存图片
        plt.savefig(save_path, bbox_inches='tight')
        return f"Industry bar chart saved to <img {os.path.join(dir_path, file_name)}>"
    
    def plot_charts(chart_type, x_data, y_data, title, save_path):
        """
        创建并保存图表。

        :param chart_type: str, 图表类型，支持 'bar'（柱状图）, 'line'（折线图）, 'pie'（饼图）
        :param x_data: list, x轴数据
        :param y_data: list, y轴数据
        :param save_path: str, 图表保存路径
        """
        plt.figure(figsize=(10, 6))
    
        if chart_type == 'bar':
            bars = plt.bar(x_data, y_data, color='green')
            plt.xlabel('Categories', fontproperties=my_font)
            plt.ylabel('Values', fontproperties=my_font)
            plt.title(title, fontproperties=my_font)
            # 添加每个柱子上的数值标签
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval,2), ha='center', va='bottom', fontproperties=my_font)
        
        elif chart_type == 'line':
            plt.plot(x_data, y_data, marker='o', color='green')
            plt.xlabel('Categories', fontproperties=my_font)
            plt.ylabel('Values', fontproperties=my_font)
            plt.title(title, fontproperties=my_font)
        elif chart_type == 'pie':
            plt.pie(y_data, labels=x_data, autopct='%1.1f%%', startangle=140, textprops={'fontproperties': my_font})
            plt.title(title, fontproperties=my_font)
        else:
            raise ValueError("Unsupported chart type. Supported types: 'bar', 'line', 'pie'.")

        plt.xticks(rotation=45, ha='right', fontproperties=my_font)
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        print(f"Chart saved to {save_path}")
    def plot_line_chart(
            x_data: Annotated[List, "A list of x-axis data"],
            y_data: Annotated[List, "A list of y-axis data"],
            x_label: Annotated[str, "The label for the x-axis"],
            y_label: Annotated[str, "The label for the y-axis"],
            title: Annotated[str, "The title of the line chart"],
            source_text: Annotated[str, "The source text to display at the bottom of the chart (default is None)"],
            industry: Annotated[str, "the industry name"]
    ) -> str:
        """draw a line chart for the prediction data."""
        # 创建图形和轴
        plt.figure(figsize=(10, 6), dpi=280)

        # 绘制曲线
        plt.plot(x_data, y_data, marker='o', linestyle='-', color='b')

        # 添加标题和标签
        plt.title(title, fontproperties=my_font)
        plt.xlabel(x_label, fontproperties=my_font)
        plt.ylabel(y_label, fontproperties=my_font)

        # 添加图例
        # plt.legend()

        # 显示网格
        plt.grid(True)

        # 在最下方增加一行文字“资料来源：”
        if source_text:
            plt.figtext(0.1, 0.01, '资料来源：' + source_text, ha='left', va='bottom', fontsize=12,
                        fontproperties=my_font)

        # 在文字上下方画两条横线
        plt.axhline(y=0.06, color='black', linewidth=0.8)
        plt.axhline(y=0.04, color='black', linewidth=0.8)

        # 保存图形
        # dir_path = os.path.join(result_path, 'result', 'task_2', 'imgs')
        dir_path = result_path
        create_path_if_not_exists(dir_path)
        file_name = industry + '_linechart.png'
        save_path = os.path.join(dir_path, file_name)
        # 保存图片
        plt.savefig(save_path, bbox_inches='tight')
        return f"Industry line chart saved to <img {os.path.join(dir_path, file_name)}>"
    
if __name__ == "__main__":
    ReportChartUtils.get_month_stock_data(
        ticker_symbol="601311.ss",
        start_date="2023-01-01",
        end_date="2023-01-31",
        save_path="test",
    )