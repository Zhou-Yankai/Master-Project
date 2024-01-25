import yfinance as yf
from openai import OpenAI
import openai
import os
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import matplotlib.pyplot as plt
import requests
import json

# $env:OPENAI_API_KEY = "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"


api_key = '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'
client = OpenAI()


aapl = yf.Ticker("AAPL")

# 获取历史市场数据
comp_overview = aapl.info['longBusinessSummary']
print(comp_overview)

income_statement_annual = aapl.financials.T
revenue = income_statement_annual['Total Revenue']
net_income = income_statement_annual['Net Income']
# revenue_growth_rate = revenue.pct_change() * 100
# net_income_growth_rate = net_income.pct_change() * 100

year = '2022'
year_1 = '2021'
revenue_year = float(revenue[year])
net_income_year = float(net_income[year])
revenue_growth_rate_year = float(revenue[year])/float(revenue[year_1]) * 100 - 100
net_income_growth_rate_year = float(net_income[year])/float(net_income[year_1]) * 100 - 100
print("Income Statement (Annual):")
# print(income_statement_annual)
print(f"营收（{year}）: {revenue_year}")
print(f"净利润（{year}）: {net_income_year}")
print(f"营收增长率（{year}）: {revenue_growth_rate_year}%")
print(f"净利润增长率（{year}）: {net_income_growth_rate_year}%")

rate = revenue.pct_change() * 100
print(f"同比增速为{rate}")

financial_summary = f"""
苹果公司的2022年财务数据如下：
- 营收: {revenue_year}
- 净利润: {net_income_year}
- 营收增长率: {revenue_growth_rate_year}%
- 净利润增长率: {net_income_growth_rate_year}%
"""

# prompt = comp_overview + "\n" + financial_summary + "\n基于以上信息，请作为一个股票分析师的角色从专业的金融视角分析与总结公司概况其中包括公司的简介与近来的财务概况,财务数据的单位是美元"

# response = client.completions.create(
#   model="gpt-3.5-turbo-instruct",
#   prompt=prompt,
#   max_tokens=600
# )

# print(response)