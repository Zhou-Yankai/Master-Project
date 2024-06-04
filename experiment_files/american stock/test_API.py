from openai import OpenAI
import os
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import matplotlib.pyplot as plt
import requests
import json

# print(os.environ.get('OPENAI_API_KEY'))
api_key = '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'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}



# API Key
api_key = 'CG4VJP9GSRM0IMWR'

ts = TimeSeries(key=api_key, output_format='pandas')
fd = FundamentalData(key=api_key)

# Accesss data
data, meta_data = ts.get_daily(symbol='AAPL', outputsize='full')
data_overview, meta_data = fd.get_company_overview(symbol='AAPL')
data_Sanyi, meta_data = ts.get_daily(symbol='600031.SS', outputsize='full')
print(data_Sanyi.head())
income_statement_annual, meta_data = fd.get_income_statement_annual(symbol='AAPL')
#income_statement_annual_Sanyi, meta_data = fd.get_income_statement_annual(symbol='600031.SS')
comp_descr = data_overview['Description']
print(income_statement_annual.head())
print(comp_descr)

# plt graph
data['1. open'].plot()
plt.title('Intraday Times Series for the MSFT stock (1 min)')
plt.show()




data = {
    "prompt": f"根据以下信息优化苹果公司的公司简介,可以增加你对苹果公司的理解，如果出现数据请确保是目前最新的数据：{comp_descr}",
    "max_tokens": 150,
    "model": "text-davinci-003"
}

response = requests.post('https://api.openai.com/v1/engines/davinci-codex/completions', headers=headers, json=data)
print(response.json())



# {
#   "prompt": "Analyze the impact of the following news article on Apple Inc.'s stock and provide a clear rating based on the criteria provided below:\n\n[Insert news content here]\n\nRating Criteria:\n- Bullish: If the news is positive for Apple's stock, rate as Slightly Bullish (1 point), Moderately Bullish (2 points), or Highly Bullish (3 points).\n- Bearish: If the news is negative for Apple's stock, rate as Slightly Bearish (1 point), Moderately Bearish (2 points), or Highly Bearish (3 points).\n- Not Relevant: If the news content is not directly related to Apple's stock, rate as Low Relevance (1 point), Moderate Relevance (2 points), or High Relevance (3 points).\n\nPlease provide your analysis and a final rating based on these guidelines."
# }
