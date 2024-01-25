import csv
import json
import requests
from lxml import etree
import pandas as pd


class DataScraper:
    def __init__(self):
        self.pagename_type = {
            "业绩报表": "RPT_LICO_FN_CPD",
            "业绩快报": "RPT_FCI_PERFORMANCEE",
            "业绩预告": "RPT_PUBLIC_OP_NEWPREDICT",
            "预约披露时间": "RPT_PUBLIC_BS_APPOIN",
            "资产负债表": "RPT_DMSK_FN_BALANCE",
            "利润表": "RPT_DMSK_FN_INCOME",
            "现金流量表": "RPT_DMSK_FN_CASHFLOW"
        }

        self.pagename_en = {
            "业绩报表": "yjbb",
            "业绩快报": "yjkb",
            "业绩预告": "yjyg",
            "预约披露时间": "yysj",
            "资产负债表": "zcfz",
            "利润表": "lrb",
            "现金流量表": "xjll"
        }

        self.en_list = []

        self.url = 'https://datacenter-web.eastmoney.com/api/data/v1/get?'
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'closed',
            'Referer': 'https://data.eastmoney.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def get_table(self, page):
        params = {
            'sortTypes': '-1,-1',
            'reportName': self.table_type,
            'columns': 'ALL',
            'filter': f'(REPORT_DATE=\'{self.timePoint}\')'
        }

        if self.table_type in ['RPT_LICO_FN_CPD']:
            params['filter'] = f'(REPORTDATE=\'{self.timePoint}\')'
        params['pageNumber'] = str(page)
        response = requests.get(url=self.url, params=params, headers=self.headers)
        data = json.loads(response.text)
        if data['result']:
            return data['result']['data']
        else:
            return

    def get_header(self, all_en_list):
        ch_list = []
        url = f'https://data.eastmoney.com/bbsj/{self.pagename_en[self.pagename]}.html'
        response = requests.get(url)
        res = etree.HTML(response.text)
        for en in all_en_list:
            ch = ''.join(
                [i.strip() for i in res.xpath(f'//div[@class="dataview"]//table[1]//th[@data-field="{en}"]//text()')])
            if ch:
                ch_list.append(ch)
                self.en_list.append(en)
        return ch_list
    

    def write_header(self, table_data):
        with open(self.filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if table_data:  # 检查 table_data 是否为 None
                headers = self.get_header(list(table_data[0].keys()))
                writer.writerow(headers)
            else:
                print("无法获取表格数据/该年份无数据")

    def write_table(self, table_data):
        with open(self.filename, 'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for item in table_data:
                row = []
                for key in item.keys():
                    if key in self.en_list:
                        row.append(str(item[key]))
                print(row)
                writer.writerow(row)

    def print_table(self, table_data):
        if table_data:
            # 使用 Pandas DataFrame 打印表格数据
            df = pd.DataFrame(table_data)
            return df
        else:
            print("无法获取表格数据/该年份无数据")
            return pd.DataFrame()


    def get_timeList(self):
        headers = {
            'Referer': 'https://data.eastmoney.com/bbsj/202206.html',
        }
        response = requests.get('https://data.eastmoney.com/bbsj/202206.html', headers=headers)
        res = etree.HTML(response.text)
        return res.xpath('//*[@id="filter_date"]//option/text()')

    def run(self):
        self.timeList = self.get_timeList()
        for index, value in enumerate(self.timeList):
            if (index + 1) % 5 == 0:
                print(value)
            else:
                print(value, end=' ; ')

        self.timePoint = str(input('\n请选择时间（可选项如上）:'))
        self.pagename = str(
            input('请输入报表类型（业绩报表;业绩快报;业绩预告;预约披露时间;资产负债表;利润表；现金流量表）:'))
        assert self.timePoint in self.timeList, '时间输入错误'
        assert self.pagename in list(self.pagename_type.keys()), '报表类型输入错误'
        self.table_type = self.pagename_type[self.pagename]
        self.filename = f'{self.pagename}_{self.timePoint}.csv'
        self.write_header(self.get_table(1))

        all_data = []
        page = 1
        while True:
            table = self.get_table(page)
            if table:
                # self.write_table(table)
                df = self.print_table(table)  # 获取DataFrame
                all_data.append(df)  # 将DataFrame添加到列表中
            else:
                break
            page += 1
        print(df)
        # table_data = self.get_table(1)
        # if table_data:
        #     page = 1
        #     while True:
        #         table = self.get_table(page)
        #         if table:
        #             self.print_table(table)
        #         else:
        #             break
        #         page += 1


if __name__ == '__main__':
    scraper = DataScraper()
    scraper.run()