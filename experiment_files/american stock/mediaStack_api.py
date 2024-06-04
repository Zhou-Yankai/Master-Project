import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from openai import OpenAI
import re
from datetime import datetime, timedelta
import pandas as pd

def requests_retry_session(retries=3, backoff_factor=0.5, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
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

def fetch_news_content(news_url):
    """尝试从新闻页面抓取更详细的内容"""
    try:
        response = requests_retry_session().get(news_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        full_text = ' '.join(paragraph.text for paragraph in paragraphs)
        return full_text[:3000] + '...' if len(full_text) > 3000 else full_text
    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"解析错误: {e}")
    return "无法获取内容"

def fetch_news(api_key, keywords, languages='en', limit=5, start_date_str='2024-03-24', end_date_str='2024-03-27'):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    current_date = start_date
    all_news = []
    # 每两周获取100条新闻
    while current_date < end_date:
        period_end_date = current_date + timedelta(days=0)
        if period_end_date > end_date:
            period_end_date = end_date

        current_date_str = current_date.strftime('%Y-%m-%d')
        period_end_date_str = period_end_date.strftime('%Y-%m-%d')
        base_url = "http://api.mediastack.com/v1/news"
        date_range = f"{current_date_str},{period_end_date_str}"
        params = {
            'access_key': api_key,
            'keywords': keywords,
            'languages': languages,
            'limit': limit,
            'date': date_range,
        }
        try:
            response = requests_retry_session().get(base_url, params=params)
            if response.status_code == 200:
                news_data = response.json().get('data', [])
                all_news.extend(news_data)
            else:
                print("Failed to fetch news:", response.status_code)
                return None
            current_date = period_end_date + timedelta(days=1)
        
        except Exception as e:
            print(f"Failed to fetch news with error: {e}")
            return None
    
    return all_news
    
def analyze_news_with_openai(news_content, company_name):
    content = "\nAnalyze the impact of the following news article on stock of"+ company_name +" and provide a clear rating based on the criteria provided below, Please give me a clear result about rating directly without any further elaboration:\n\n"+ news_content +"\n\nRating Criteria:\n- Bullish: If the news is positive for the company's stock, rate as Slightly Bullish (1 point), Moderately Bullish (2 points), or Highly Bullish (3 points).\n- Bearish: If the news is negative for the company's stock, rate as Slightly Bearish (-1 point), Moderately Bearish (-2 points), or Highly Bearish (-3 points).\n- Not Relevant: If the news content is not directly related to the stock, rate as Low Relevance (0 point), Moderate Relevance (0 point), or High Relevance (0 point).\n\nPlease provide your analysis and a final rating based on these guidelines."
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages = [
            { "role": "system",
            "content": "You will play the role of a professional stock analyst, judging the news provided by the subsequent given rating criteria."
            },
            { "role": "user",
            "content": content
            }
        ],
        max_tokens=3000
    )
    rating_content = response.choices[0].message.content
    return rating_content





# 定义OpenAI API key
api_key = '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'
client = OpenAI()


# 替换YOUR_API_KEY为你的MediaStack API密钥
api_key = '85790e7d0fcc44c25d432cbe2806eca1'

# 定义起始和结束日期
start_date = '2024-04-01'
end_date = '2024-04-12'
company_name = 'Apple'

news_data = fetch_news(api_key, company_name, start_date_str=start_date, end_date_str=end_date)
print(news_data)
news_output = []
if news_data:
    ratings = []
    for article in news_data:
        full_text_summary = fetch_news_content(article['url'])
        rating_response = analyze_news_with_openai(full_text_summary, company_name)
        # pattern = r"(Slightly Bullish \(1 point\)|Moderately Bullish \(2 points\)|Highly Bullish \(3 points\)|Slightly Bearish \(-1 point\)|Moderately Bearish \(-2 points\)|Highly Bearish \(-3 points\)|Low Relevance \(0 point\)|Moderate Relevance \(0 point\)|High Relevance \(0 point\))"
        pattern = r"(1|2|3|-1|-2|-3|0)"
        rating_match = re.search(pattern, rating_response)
        if rating_match:
            final_rating = rating_match.group(1)
        else:
            final_rating = "No rating found"
        
        ratings.append(final_rating)

        print(f"Title: {article['title']}")
        print(f"Published At: {article['published_at']}")
        print(f"URL: {article['url']}")
        print(f"Content: {full_text_summary}")
        print(f"Rating: {final_rating}")
        print('---------------------------------')

        news_details = {
            'Title': article['title'],
            'Published At': article['published_at'],
            'URL': article['url'],
            'Content': full_text_summary,
            'Rating': final_rating
        }
        news_output.append(news_details)

    print("All Ratings:", ratings)
    news_df = pd.DataFrame(news_output)
    file_name = f'news_data_{company_name}.csv'
    news_df.to_csv(file_name, index=False)






