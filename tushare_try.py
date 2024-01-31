# import tushare as ts
# import pandas as pd


# # 设置tushare pro的token并初始化接口
# pro = ts.pro_api()
# ts_token = ts.set_token('0a14e93298e2c6f043629fe5488be9aebbaf106ad85a3d2d19d19a82')
# pro = ts.pro_api(ts_token)

# # 获取数据
# df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001', fields='exchange,cal_date,is_open,pretrade_date', is_open='0')

# # 查看数据
# print(df.head())

x = '2021'
y = '2020'
z = str(int(x) + int (y))
print(z)