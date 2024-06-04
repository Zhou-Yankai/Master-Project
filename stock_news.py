import os
import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re

# 初始化OpenAI客户端
openai_api_key = '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'
client = OpenAI(api_key=openai_api_key)

folder_path = 'stock_news'
company_name = "山西汾酒"  # 指定分析的公司名称
output_file = f'news_analysis_results_{company_name}.csv'

def requests_retry_session(retries=3, backoff_factor=0.5, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def fetch_news_content(url):
    try:
        response = requests_retry_session().get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join(p.get_text() for p in paragraphs)
        return article_text[:3000] + '...' if len(article_text) > 3000 else article_text
    except Exception as e:
        print(f"Failed to fetch or parse article content for URL: {url} with error: {e}")
        return None

def analyze_news_with_openai(news_content, company_name):
    content = "\nAnalyze the impact of the following news article on stock of "+ company_name +" and provide a clear rating based on the criteria provided below, Please give me a clear result about rating directly without any further elaboration:\n\n"+ news_content +"\n\nRating Criteria:\n- Bullish: If the news is positive for the company's stock, rate as Slightly Bullish (1 point), Moderately Bullish (2 points), Highly Bullish (3 points), or Extremely Bullish (4 points).\n- Bearish: If the news is negative for the company's stock, rate as Slightly Bearish (-1 point), Moderately Bearish (-2 points), Highly Bearish (-3 points), Extremely Bearish (-4 points).\n- Not Relevant: If the news content is not directly related to the stock, rate as Low Relevance (0 point), Moderate Relevance (0.25 point), or High Relevance (0.5 point).\n\nPlease provide your analysis and a final rating based on these guidelines."
    response = client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        messages=[
            {"role": "system", "content": "You will play the role of a professional stock analyst, judging the news provided by the subsequent given rating criteria."},
            {"role": "user", "content": content}
        ],
        max_tokens=3000
    )
    rating_content = response.choices[0].message.content
    return rating_content

def append_to_csv(news_data, filename):
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
        fieldnames = ['发布时间', '新闻标题', 'URL', '影响评分']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(news_data)

# 检查文件是否存在，若不存在则创建并添加标题行
if not os.path.exists(output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=['发布时间', '新闻标题', 'URL', '影响评分'])
        writer.writeheader()

# 主循环处理每个Excel文件
for filename in os.listdir(folder_path):
    if filename.endswith(".xls") or filename.endswith(".xlsx"):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            url = row['网址']
            if pd.isna(url) or not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                print(f"Invalid URL for news item in row {index}: {url}")
                continue
            news_content = fetch_news_content(url)
            if news_content:
                news_content = row['标题'] + "  " + news_content
                rating_response = analyze_news_with_openai(news_content, company_name)
                pattern = r"(1|2|3|4|-1|-2|-3|-4|0|0.25|0.5)"
                rating_match = re.search(pattern, rating_response)
                final_rating = rating_match.group(0) if rating_match else "No rating found"
            else:
                final_rating = "No content available"
                
            # 创建包含新闻数据的字典
            news_data = {
                '发布时间': row['时间'],
                '新闻标题': row['标题'],
                'URL': url,
                '影响评分': final_rating
            }
            
            # 立即将新闻数据追加到CSV文件
            append_to_csv(news_data, output_file)
            
            print(f"新闻标题: {row['标题']}")
            print(f"发布时间: {row['时间']}")
            print(f"URL: {url}")
            print(f"新闻内容: {news_content[:1000]}")
            print(f"影响评分: {final_rating}")
            print('-' * 100)