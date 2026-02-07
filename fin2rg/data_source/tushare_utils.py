import pandas as pd
import tushare as ts
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Annotated, Callable, Any, Optional
from pandas import DataFrame

# tushare_token = "300bc174085f58253fe6b7cbffe9628ed9f40d5dea8c9cb9cdde879a"
tushare_token = "55c2880ecdf2037bc549835334aba080d5ff929fda6749cf19ee1682" # xf points-2100 
tushare_pro = ts.pro_api(tushare_token)

class TuShareUtils:
        
    def get_stock_data(
        symbol: Annotated[str, "股票代码"],
        start_date: Annotated[
            str, "检索股价开始时间, YYYYmmdd"
        ],
        end_date: Annotated[
            str, "检索股价结束时间, YYYYmmdd"
        ],
    ):
        """
        获取symbol的start_date到end_date之间的股价数据
        """
        stock_df = tushare_pro.daily(**{
                "ts_code": symbol,
                "trade_date": "",
                "start_date": start_date,
                "end_date": end_date,
            }, fields=[
                "ts_code",
                "trade_date",
                "open",
                "high",
                "low",
                "close",
                "pre_close",
                "change",
                "pct_chg",
                "vol",
                "amount"
            ])
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'])  # 确保日期列是 datetime 类型
        stock_df.set_index('trade_date', inplace=True)  # 将日期设置为索引
        return stock_df
    def get_index_daliy(symbol: Annotated[str, "股票代码"],
        start_date: Annotated[
            str, "检索股价开始时间, YYYYmmdd"
        ],
        end_date: Annotated[
            str, "检索股价结束时间, YYYYmmdd"
        ],):
        """
        获取沪深300指数的start_date到end_date之间的股价数据
        """
        daily_df = tushare_pro.index_daily(**{
            "ts_code": "000300.sh",
            "start_date": start_date,
            "end_date": end_date,
        }, fields=[
            "ts_code",
            "trade_date",
            "close",
            "open",
            "high",
            "low",
            "pre_close",
            "change",
            "pct_chg",
            "vol",
            "amount"
        ])
        return daily_df
    def get_income_stmt(symbol: Annotated[str, "ticker symbol"],
                        years: Annotated[int, "number of years to search from, default to 4"] = 4
                        ) -> DataFrame:
        """Fetches and returns the latest income statement of the company as a DataFrame."""
        start_time = datetime.now()
        period_time = datetime.now().strftime("%Y")+"1231"
        now_date = datetime.now().strftime("%Y%m%d")
        if now_date < period_time: 
            start_time = datetime.now() - relativedelta(years=1)
            period_time = (datetime.now()- relativedelta(years=1)).strftime("%Y")+"1231"
        def get_tushare_income_data(symbol, period_time):
            income_stmt = tushare_pro.income(**{
                "ts_code": symbol,
                "period": period_time,
            }, fields=[
                "end_date",
                "basic_eps",
                "diluted_eps",
                "total_revenue",
                "revenue",
                "int_income",
                "prem_earned",
                "comm_income",
                "n_commis_income",
                "n_oth_income",
                "n_oth_b_income",
                "prem_income",
                "out_prem",
                "une_prem_reser",
                "reins_income",
                "n_sec_tb_income",
                "n_sec_uw_income",
                "n_asset_mg_income",
                "oth_b_income",
                "fv_value_chg_gain",
                "invest_income",
                "ass_invest_income",
                "forex_gain",
                "total_cogs",
                "oper_cost",
                "int_exp",
                "comm_exp",
                "biz_tax_surchg",
                "sell_exp",
                "admin_exp",
                "fin_exp",
                "assets_impair_loss",
                "prem_refund",
                "compens_payout",
                "reser_insur_liab",
                "div_payt",
                "reins_exp",
                "oper_exp",
                "compens_payout_refu",
                "insur_reser_refu",
                "reins_cost_refund",
                "other_bus_cost",
                "operate_profit",
                "non_oper_income",
                "non_oper_exp",
                "nca_disploss",
                "total_profit",
                "income_tax",
                "n_income",
                "n_income_attr_p",
                "minority_gain",
                "oth_compr_income",
                "t_compr_income",
                "compr_inc_attr_p",
                "compr_inc_attr_m_s",
                "ebit",
                "ebitda",
                "insurance_exp",
                "undist_profit",
                "distable_profit",
                "rd_exp",
                "fin_exp_int_exp",
                "fin_exp_int_inc",
                "transfer_surplus_rese",
                "transfer_housing_imprest",
                "transfer_oth",
                "adj_lossgain",
                "withdra_legal_surplus",
                "withdra_legal_pubfund",
                "withdra_biz_devfund",
                "withdra_rese_fund",
                "withdra_oth_ersu",
                "workers_welfare",
                "distr_profit_shrhder",
                "prfshare_payable_dvd",
                "comshare_payable_dvd",
                "capit_comstock_div",
                "continued_net_profit"
            ])
            return income_stmt
        
        all_income_stmt = pd.DataFrame()
        for year_offset in range(years):
            period_time = (start_time - relativedelta(years=year_offset)).strftime("%Y")+"1231"
            income_stmt = get_tushare_income_data(symbol, period_time)
            if income_stmt.shape[0] == 2:
                income_stmt = income_stmt.drop_duplicates() # 删除重复行
            if all_income_stmt.empty:
                all_income_stmt = income_stmt.set_index("end_date").T
            else:
                all_income_stmt = pd.concat([all_income_stmt, income_stmt.set_index("end_date").T], axis=1)
        
        return all_income_stmt
    def get_balance_sheet(symbol: Annotated[str, "ticker symbol"],
                          years: Annotated[int, "number of years to search from, default to 4"] = 4
                          ) -> DataFrame:
        """Fetches and returns the latest balance sheet of the company as a DataFrame."""

        start_time = datetime.now()
        period_time = datetime.now().strftime("%Y")+"1231"
        now_date = datetime.now().strftime("%Y%m%d")
        if now_date < period_time: 
            start_time = datetime.now() - relativedelta(years=1)
            period_time = (datetime.now()- relativedelta(years=1)).strftime("%Y")+"1231"
        def get_tushare_balance_data(symbol, period_time):
            balance_sheet = tushare_pro.balancesheet(**{
                    "ts_code": symbol,
                    "period": period_time,
                }, fields=[
                    "end_date",
                    "total_share",
                    "cap_rese",
                    "undistr_porfit",
                    "surplus_rese",
                    "special_rese",
                    "money_cap",
                    "trad_asset",
                    "notes_receiv",
                    "accounts_receiv",
                    "oth_receiv",
                    "prepayment",
                    "div_receiv",
                    "int_receiv",
                    "inventories",
                    "amor_exp",
                    "nca_within_1y",
                    "sett_rsrv",
                    "loanto_oth_bank_fi",
                    "premium_receiv",
                    "reinsur_receiv",
                    "reinsur_res_receiv",
                    "pur_resale_fa",
                    "oth_cur_assets",
                    "total_cur_assets",
                    "fa_avail_for_sale",
                    "htm_invest",
                    "lt_eqt_invest",
                    "invest_real_estate",
                    "time_deposits",
                    "oth_assets",
                    "lt_rec",
                    "fix_assets",
                    "cip",
                    "const_materials",
                    "fixed_assets_disp",
                    "produc_bio_assets",
                    "oil_and_gas_assets",
                    "intan_assets",
                    "r_and_d",
                    "goodwill",
                    "lt_amor_exp",
                    "defer_tax_assets",
                    "decr_in_disbur",
                    "oth_nca",
                    "total_nca",
                    "cash_reser_cb",
                    "depos_in_oth_bfi",
                    "prec_metals",
                    "deriv_assets",
                    "rr_reins_une_prem",
                    "rr_reins_outstd_cla",
                    "rr_reins_lins_liab",
                    "rr_reins_lthins_liab",
                    "refund_depos",
                    "ph_pledge_loans",
                    "refund_cap_depos",
                    "indep_acct_assets",
                    "client_depos",
                    "client_prov",
                    "transac_seat_fee",
                    "invest_as_receiv",
                    "total_assets",
                    "lt_borr",
                    "st_borr",
                    "cb_borr",
                    "depos_ib_deposits",
                    "loan_oth_bank",
                    "trading_fl",
                    "notes_payable",
                    "acct_payable",
                    "adv_receipts",
                    "sold_for_repur_fa",
                    "comm_payable",
                    "payroll_payable",
                    "taxes_payable",
                    "int_payable",
                    "div_payable",
                    "oth_payable",
                    "acc_exp",
                    "deferred_inc",
                    "st_bonds_payable",
                    "payable_to_reinsurer",
                    "rsrv_insur_cont",
                    "acting_trading_sec",
                    "acting_uw_sec",
                    "non_cur_liab_due_1y",
                    "oth_cur_liab",
                    "total_cur_liab",
                    "bond_payable",
                    "lt_payable",
                    "specific_payables",
                    "estimated_liab",
                    "defer_tax_liab",
                    "defer_inc_non_cur_liab",
                    "oth_ncl",
                    "total_ncl",
                    "depos_oth_bfi",
                    "deriv_liab",
                    "depos",
                    "agency_bus_liab",
                    "oth_liab",
                    "prem_receiv_adva",
                    "depos_received",
                    "ph_invest",
                    "reser_une_prem",
                    "reser_outstd_claims",
                    "reser_lins_liab",
                    "reser_lthins_liab",
                    "indept_acc_liab",
                    "pledge_borr",
                    "indem_payable",
                    "policy_div_payable",
                    "total_liab",
                    "treasury_share",
                    "ordin_risk_reser",
                    "forex_differ",
                    "invest_loss_unconf",
                    "minority_int",
                    "total_hldr_eqy_exc_min_int",
                    "total_hldr_eqy_inc_min_int",
                    "total_liab_hldr_eqy",
                    "lt_payroll_payable",
                    "oth_comp_income",
                    "oth_eqt_tools",
                    "oth_eqt_tools_p_shr",
                    "lending_funds",
                    "acc_receivable",
                    "st_fin_payable",
                    "payables",
                    "hfs_assets",
                    "hfs_sales",
                    "cost_fin_assets",
                    "fair_value_fin_assets",
                    "contract_assets",
                    "contract_liab",
                    "accounts_receiv_bill",
                    "accounts_pay",
                    "oth_rcv_total",
                    "fix_assets_total",
                    "cip_total",
                    "oth_pay_total",
                    "long_pay_total",
                    "debt_invest",
                    "oth_debt_invest",
                    "update_flag"
                ])
            return balance_sheet

        all_balance_sheet = pd.DataFrame()
        for year_offset in range(years):
            period_time = (start_time - relativedelta(years=year_offset)).strftime("%Y")+"1231"
            balance_sheet = get_tushare_balance_data(symbol, period_time)
            if balance_sheet.shape[0] == 2:
                balance_sheet = balance_sheet.drop_duplicates() # 删除重复行
            if all_balance_sheet.empty:
                all_balance_sheet = balance_sheet.set_index("end_date").T
            else:
                all_balance_sheet = pd.concat([all_balance_sheet, balance_sheet.set_index("end_date").T], axis=1)
        
        return all_balance_sheet
    def get_cash_flow(symbol: Annotated[str, "ticker symbol"],
                      years: Annotated[int, "number of years to search from, default to 4"] = 4
                      ) -> DataFrame:
        """Fetches and returns the latest cash flow statement of the company as a DataFrame."""
        start_time = datetime.now()
        period_time = datetime.now().strftime("%Y")+"1231"
        now_date = datetime.now().strftime("%Y%m%d")
        if now_date < period_time: 
            start_time = datetime.now() - relativedelta(years=1)
            period_time = (datetime.now()- relativedelta(years=1)).strftime("%Y")+"1231"
        def get_tushare_cash_flow(symbol, period_time):
            cash_flow = tushare_pro.cashflow(**{
                    "ts_code": symbol,
                    "period": period_time,
                }, fields=[
                    "end_date",
                    "finan_exp",
                    "c_fr_sale_sg",
                    "recp_tax_rends",
                    "n_depos_incr_fi",
                    "n_incr_loans_cb",
                    "n_inc_borr_oth_fi",
                    "prem_fr_orig_contr",
                    "n_incr_insured_dep",
                    "n_reinsur_prem",
                    "n_incr_disp_tfa",
                    "ifc_cash_incr",
                    "n_incr_disp_faas",
                    "n_incr_loans_oth_bank",
                    "n_cap_incr_repur",
                    "c_fr_oth_operate_a",
                    "c_inf_fr_operate_a",
                    "c_paid_goods_s",
                    "c_paid_to_for_empl",
                    "c_paid_for_taxes",
                    "n_incr_clt_loan_adv",
                    "n_incr_dep_cbob",
                    "c_pay_claims_orig_inco",
                    "pay_handling_chrg",
                    "pay_comm_insur_plcy",
                    "oth_cash_pay_oper_act",
                    "st_cash_out_act",
                    "n_cashflow_act",
                    "oth_recp_ral_inv_act",
                    "c_disp_withdrwl_invest",
                    "c_recp_return_invest",
                    "n_recp_disp_fiolta",
                    "n_recp_disp_sobu",
                    "stot_inflows_inv_act",
                    "c_pay_acq_const_fiolta",
                    "c_paid_invest",
                    "n_disp_subs_oth_biz",
                    "oth_pay_ral_inv_act",
                    "n_incr_pledge_loan",
                    "stot_out_inv_act",
                    "n_cashflow_inv_act",
                    "c_recp_borrow",
                    "proc_issue_bonds",
                    "oth_cash_recp_ral_fnc_act",
                    "stot_cash_in_fnc_act",
                    "free_cashflow",
                    "c_prepay_amt_borr",
                    "c_pay_dist_dpcp_int_exp",
                    "incl_dvd_profit_paid_sc_ms",
                    "oth_cashpay_ral_fnc_act",
                    "stot_cashout_fnc_act",
                    "n_cash_flows_fnc_act",
                    "eff_fx_flu_cash",
                    "n_incr_cash_cash_equ",
                    "c_cash_equ_beg_period",
                    "c_cash_equ_end_period",
                    "c_recp_cap_contrib",
                    "incl_cash_rec_saims",
                    "uncon_invest_loss",
                    "prov_depr_assets",
                    "depr_fa_coga_dpba",
                    "amort_intang_assets",
                    "lt_amort_deferred_exp",
                    "decr_deferred_exp",
                    "incr_acc_exp",
                    "loss_disp_fiolta",
                    "loss_scr_fa",
                    "loss_fv_chg",
                    "invest_loss",
                    "decr_def_inc_tax_assets",
                    "incr_def_inc_tax_liab",
                    "decr_inventories",
                    "decr_oper_payable",
                    "incr_oper_payable",
                    "others",
                    "im_net_cashflow_oper_act",
                    "conv_debt_into_cap",
                    "conv_copbonds_due_within_1y",
                    "fa_fnc_leases",
                    "im_n_incr_cash_equ",
                    "net_dism_capital_add",
                    "net_cash_rece_sec",
                    "credit_impa_loss",
                    "use_right_asset_dep",
                    "oth_loss_asset",
                    "end_bal_cash",
                    "beg_bal_cash",
                    "end_bal_cash_equ",
                    "beg_bal_cash_equ",
                    "update_flag",
                    "net_profit"
                ])
            return cash_flow
        
        all_cash_flow = pd.DataFrame()
        for year_offset in range(years):
            period_time = (start_time - relativedelta(years=year_offset)).strftime("%Y")+"1231"
            cash_flow = get_tushare_cash_flow(symbol, period_time)
            if cash_flow.shape[0] == 2:
                cash_flow = cash_flow.drop_duplicates() # 删除重复行
            if all_cash_flow.empty:
                all_cash_flow = cash_flow.set_index("end_date").T
            else:
                all_cash_flow = pd.concat([all_cash_flow, cash_flow.set_index("end_date").T], axis=1)
        
        return all_cash_flow
    
    
    def get_stock_info(symbol: Annotated[str, "股票代码"]):
        """获取股票代码的基本信息"""
        stock_info_df = tushare_pro.stock_basic(**{
                "ts_code": symbol,
                "name": "",
                "exchange": "",
                "market": "",
                "is_hs": "",
                "list_status": "",
                "limit": "",
                "offset": ""
            }, fields=[
                "ts_code",
                "symbol",
                "name",
                "area",
                "industry",
                "cnspell",
                "market",
                "list_date",
                "act_name",
                "act_ent_type"
            ])

        return stock_info_df   
    def get_financial_metrics(
        ticker_symbol: Annotated[str, "ticker symbol"],
        years: Annotated[int, "number of the years to search from, default to 4"] = 4,
    ) -> pd.DataFrame:
        """Get the financial metrics for a given stock for the last 'years' years"""
        # Base URL setup for FMP API
        # base_url = "https://financialmodelingprep.com/api/v3"
        # Create DataFrame
        df = pd.DataFrame()

        period_time = datetime.now().strftime("%Y")+"1231"
        start_year = datetime.now()
        now_date = datetime.now().strftime("%Y%m%d")
        if now_date < period_time: 
            start_year = (datetime.now()- relativedelta(years=1))
            # period_time = (datetime.now()- relativedelta(years=1)).strftime("%Y")+"1231"

        # Iterate over the last 'years' years of data
        for year_offset in range(years):
            period_time = (start_year - relativedelta(years=year_offset)).strftime("%Y")+"1231"
            
            income_data = tushare_pro.income(**{ "ts_code": ticker_symbol,
                                    "period": period_time,},
                                    fields=['revenue', 'int_income', 'basic_eps', 
                                            'n_income', 'income_tax', 'fin_exp_int_inc'])
            # key_metrics_data = requests.get(key_metrics_url).json()
            # EBIT=净利润+所得税+利息
            # EBIT Margin = EBIT / 营业收入
            # if income_data['int_income'][0] is None:
            #     income_data['int_income'][0] = 0.0
            try:
                ebitPerRevenue = (income_data['n_income'][0]+income_data['income_tax'][0]+income_data['fin_exp_int_inc'][0])/income_data['n_income'][0]
            except Exception as e:
                print(str(e))
                ebitPerRevenue = "N/A"
            key_metrics_data = tushare_pro.fina_indicator(**{"ts_code": ticker_symbol,
                                    "period": period_time,},
                                    fields=['roe'])
            
            pe_pb_data = tushare_pro.index_dailybasic(**{"ts_code": ticker_symbol,
                                    "trade_date": period_time,},
                                    fields=['pe', 'pb'])
            # Extracting needed metrics for each year
            # if income_data and key_metrics_data and ratios_data:
            metrics = {
                "Operating Revenue": income_data["revenue"][0] / 1e6,   # 营业收入 Revenue in millions
                "Adjusted Net Profit": income_data["fin_exp_int_inc"][0] / 1e6, # 	利息收入
                "Adjusted EPS": income_data["basic_eps"][0], # 基本每股收益
                "EBIT Margin": ebitPerRevenue, # 
                "ROE": key_metrics_data["roe"][0], # 	净资产收益率
                # "PE Ratio": pe_pb_data['pe'][0],  # 	市盈率
                # "EV/EBITDA": key_metrics_data[year_offset][
                #     "enterpriseValueOverEBITDA" 
                # ], # 
                # "PB Ratio": pe_pb_data['pb'][0], # 市净率
            } 
            # Append the year and metrics to the DataFrame
            # Extracting the year from the date
            year = (start_year - relativedelta(years=year_offset)).strftime("%Y")
            df[year] = pd.Series(metrics)

        df = df.sort_index(axis=1)
        df = df.round(2)

        return df

    def get_historical_market_cap(ticker_symbol: Annotated[str, "ticker symbol"],
        date: Annotated[int, "date of the target price, should be 'yyyymmdd"]):
        """Get the historical market capitalization for a given stock on a given date"""
        
        df = tushare_pro.daily_basic(**{
                "ts_code": ticker_symbol,
                "trade_date": date,
            }, fields=[
                "ts_code",
                "trade_date",
                "close",
                "turnover_rate",
                "turnover_rate_f",
                "volume_ratio",
                "pe",
                "pe_ttm",
                "pb",
                "ps",
                "ps_ttm",
                "dv_ratio",
                "dv_ttm",
                "total_share",
                "float_share",
                "free_share",
                "total_mv", # 单位为万元
                "circ_mv"
            ])
        print("df:", df["total_mv"])
        # print("total_mv:", df["total_mv"][0])
        try:
            mkt_cap = df["total_mv"][0]*1e4
        except:
            mkt_cap = 0

        return mkt_cap
    
    # def get_target_price(
    #     ticker_symbol: Annotated[str, "ticker symbol"],
    #     date: Annotated[str, "date of the target price, should be 'yyyy-mm-dd'"],
    # ) -> str:
    #     """Get the target price for a given stock on a given date"""
    #     # API URL
    #     url = f"https://financialmodelingprep.com/api/v4/price-target?symbol={ticker_symbol}&apikey={fmp_api_key}"
        
    #     # 发送GET请求
    #     price_target = "Not Given"
    #     response = requests.get(url)

    #     # 确保请求成功
    #     if response.status_code == 200:
    #         # 解析JSON数据
    #         data = response.json()
    #         est = []

    #         date = datetime.strptime(date, "%Y-%m-%d")
    #         for tprice in data:
    #             tdate = tprice["publishedDate"].split("T")[0]
    #             tdate = datetime.strptime(tdate, "%Y-%m-%d")
    #             if abs((tdate - date).days) <= 1:
    #                 est.append(tprice["priceTarget"])

    #         if est:
    #             price_target = f"{np.min(est)} - {np.max(est)} (md. {np.median(est)})"
    #         else:
    #             price_target = "N/A"
    #     else:
    #         return f"Failed to retrieve data: {response.status_code}"

    #     return price_target