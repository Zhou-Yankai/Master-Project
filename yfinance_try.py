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
# print(comp_overview)

income_statement_annual = aapl.financials.T
revenue = income_statement_annual['Total Revenue']
net_income = income_statement_annual['Net Income']
# revenue_growth_rate = revenue.pct_change() * 100
# net_income_growth_rate = net_income.pct_change() * 100
income_statement = aapl.financials

# print(income_statement)

year = '2023'
year_1 = str(int(year)-1)
year_2 = str(int(year)-2)
his_year = [year,year_1,year_2]
print(his_year)
financial_summary_3years = []

for y in his_year:
    revenue_year = float(revenue[y])
    net_income_year = float(net_income[y])
    y_1 = str(int(y)-1)
    revenue_year_1 = revenue[y_1]
    net_income_year_1 = net_income[y_1]
    revenue_year_1 = float(revenue_year_1)
    net_income_year_1 = float(net_income_year_1)
    revenue_growth_rate_year = revenue_year/revenue_year_1 * 100 - 100
    net_income_growth_rate_year = net_income_year/net_income_year_1 * 100 - 100
    # print("Income Statement (Annual):")
    # print(income_statement_annual)
    # print(f"营收（{y}）: {revenue_year}")
    # print(f"净利润（{y}）: {net_income_year}")
    # print(f"营收增长率（{y}）: {revenue_growth_rate_year}%")
    # print(f"净利润增长率（{y}）: {net_income_growth_rate_year}%")


    financial_summary = f"""
    苹果公司的{y}年财务数据如下：
    - 营收: {revenue_year}
    - 净利润: {net_income_year}
    - 营收增长率: {revenue_growth_rate_year}%
    - 净利润增长率: {net_income_growth_rate_year}%
    """
    # print(financial_summary)

    financial_summary_3years.append(financial_summary)
print(financial_summary_3years)

prompt = comp_overview + "\n" + str(financial_summary_3years) + "\n基于以上信息，请作为一个股票分析师的角色从专业的金融视角分析与总结公司概况其中包括公司的简介与近来的财务概况与变化原因,财务数据的单位是美元"

response = client.completions.create(
  model="gpt-3.5-turbo-instruct",
  prompt=prompt,
  max_tokens=1000
)

print(response)