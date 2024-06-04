import requests
import pandas as pd 
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf

# 替换为你的API密钥
company_name = 'Q32 Bio'
api_key = 'CG4VJP9GSRM0IMWR'
start_date = '2024-01-01'  
end_date = '2024-04-12'

symbol = 'QTTB'

# 获取收入声明数据
url_income = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}'
income_response = requests.get(url_income)
income_data = income_response.json()

# 获取资产负债表数据
url_balance = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={api_key}'
balance_response = requests.get(url_balance)
balance_data = balance_response.json()

# 获取现金流量表数据
url_cash_flow = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={api_key}'
cash_flow_response = requests.get(url_cash_flow)
cash_flow_data = cash_flow_response.json()

# 提取季度报告
quarterly_income_reports = income_data.get('quarterlyReports', [])
quarterly_balance_reports = balance_data.get('quarterlyReports', [])
quarterly_cash_flow_reports = cash_flow_data.get('quarterlyReports', [])

# 初始化一个列表来保存规范化的数据
formatted_data = []

# 假设季度报告数量相等，遍历季度报告
for income_report, balance_report, cash_flow_report in zip(quarterly_income_reports, quarterly_balance_reports, quarterly_cash_flow_reports):
    fiscal_quarter_ending = income_report.get('fiscalDateEnding', 'N/A')
    total_revenue = income_report.get('totalRevenue', 'N/A')
    net_income = income_report.get('netIncome', 'N/A')
    ebitda = income_report.get('ebitda', 'N/A')
    gross_profit = income_report.get('grossProfit', 'N/A')
    r_and_d = income_report.get('researchAndDevelopment', 'N/A')
    total_assets = balance_report.get('totalAssets', 'N/A')
    total_liabilities = balance_report.get('totalLiabilities', 'N/A')
    cash_flow_from_operating_activities = cash_flow_report.get('operatingCashflow', 'N/A')
    cash_flow_from_investing_activities = cash_flow_report.get('cashflowFromInvestment', 'N/A')
    cash_flow_from_financing_activities = cash_flow_report.get('cashflowFromFinancing', 'N/A')
    dividends_paid = cash_flow_report.get('dividendPayout', 'N/A')

    # 将提取的数据添加到列表中
    formatted_data.append({
        'Fiscal Quarter Ending': fiscal_quarter_ending,
        'Total Revenue': total_revenue,
        'Gross Profit': gross_profit,
        'Net Income': net_income,
        'EBITDA': ebitda,
        'R&D Expenses': r_and_d,
        'Total Assets': total_assets,
        'Total Liabilities': total_liabilities,
        'Cash Flow from Operating Activities': cash_flow_from_operating_activities,
        'Cash Flow from Investing Activities': cash_flow_from_investing_activities,
        'Cash Flow from Financing Activities': cash_flow_from_financing_activities,
        'Dividends Paid': dividends_paid
    })

# # 打印规范化的数据
# for item in formatted_data:
#     print(f"Quarter Ending: {item['Fiscal Quarter Ending']}, Total Revenue: {item['Total Revenue']}, "
#           f"Gross Profit: {item['Gross Profit']}, Net Income: {item['Net Income']}, "
#           f"EBITDA: {item['EBITDA']}, R&D Expenses: {item['R&D Expenses']}, "
#           f"Total Assets: {item['Total Assets']}, Total Liabilities: {item['Total Liabilities']}, "
#           f"Cash Flow from Operating Activities: {item['Cash Flow from Operating Activities']}, "
#           f"Cash Flow from Investing Activities: {item['Cash Flow from Investing Activities']}, "
#           f"Cash Flow from Financing Activities: {item['Cash Flow from Financing Activities']}, "
#           f"Dividends Paid: {item['Dividends Paid']}")
    
df_financials = pd.DataFrame(formatted_data)
print (df_financials)
file_name = f'financial_data_{company_name}.csv'
df_financials.to_csv(file_name, index=False)


url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
stocktech_data = requests.get(url)
data = stocktech_data.json()

# 获取每日时间序列数据
time_series_daily = data['Time Series (Daily)']

# 打印从2019年开始的每日股票数据
formatted_stock_data = []
print("Date\t\tOpen\t\tHigh\t\tLow\t\tClose\t\tVolume")
for date, daily_data in time_series_daily.items():
    if start_date <= date <= end_date:  
        formatted_stock_data.append({
            'Date': date,
            'Open': daily_data['1. open'],
            'High': daily_data['2. high'],
            'Low': daily_data['3. low'],
            'Close': daily_data['4. close'],
            'Volume': daily_data['5. volume']
        })

df_stock = pd.DataFrame(formatted_stock_data)
print(df_stock)

file_name = f'stock_data_{company_name}.csv'
df_stock.to_csv(file_name, index=False)