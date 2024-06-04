import pandas as pd
import numpy as np
# from google.colab import files
import tensorflow as tf
import tensorflow_probability as tfp
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import arviz as az
from tqdm.auto import tqdm


financial_data = pd.read_csv('financial_data.csv')
technical_data = pd.read_csv('stock_data.csv')
news_data = pd.read_csv('news_data.csv')
# print(financial_data.head())
# print(technical_data.head())
# print(news_data.head())




# Cleaning news data
# transfer string of date data to data object
news_data['Published At'] = pd.to_datetime(news_data['Published At'])

# extract date as YYYY-MM-DD and generate a new column
news_data['Date'] = news_data['Published At'].dt.date
# Change the date column format datetime64
news_data['Date'] = pd.to_datetime(news_data['Date'])

# print to check
# print(news_data.head())

# Change 'No rating found' into '0', and change Rating data from string to int
news_data['Rating'] = news_data['Rating'].replace('No rating found', '0')
news_data['Rating'] = pd.to_numeric(news_data['Rating'])

# Sum up the ratings of news in same day
news_rating = news_data.groupby('Date')['Rating'].sum().reset_index()
print(news_rating.head(8))





#Cleaning technical data

# Change the date column format
technical_data['Date'] = pd.to_datetime(technical_data['Date'])

for column in technical_data.columns:
    # Skip the Date colume
    if column != 'Date':
        technical_data[column] = pd.to_numeric(technical_data[column], errors='coerce')

technical_data.sort_values('Date', inplace=True)
# Calculate close price's increased percentage
technical_data['Close_Pct_Change'] = technical_data['Close'].pct_change() * 100

# Calculate range of high to low price
technical_data['High_Low_Range'] = technical_data['High'] - technical_data['Low']

# Calculate Close to Open price increased percentage
technical_data['Open_Close_Change'] = ((technical_data['Close'] - technical_data['Open']) / technical_data['Open']) * 100

# Calculate increased percentage of open price today compared with closed price in previouse day
technical_data['Previous Close'] = technical_data['Close'].shift(-1)
technical_data['Open to Previous Close Change (%)'] = ((technical_data['Open'] - technical_data['Previous Close']) / technical_data['Previous Close']) * 100

# Define dependent variable
technical_data['Next_Day_Close_Change'] = (technical_data['Close'].shift(-1) - technical_data['Close'])/technical_data['Close']*100


# 用0填充NaN值，特别是在数据集的开始部分
# technical_data.fillna(0, inplace=True)

# Check
print(technical_data.dtypes)
print(technical_data.head(10))




# Cleaning financial data

for column in financial_data.columns[1:]:
    # Check data type
    if financial_data[column].dtype == object:
        financial_data[column] = pd.to_numeric(financial_data[column].str.replace(',', ''), errors='coerce')


# Calculate %
for column in financial_data.columns[1:]:
    if financial_data[column].dtype == float or financial_data[column].dtype == int:
        # periods=-4
        financial_data[f'{column} YoY Growth (%)'] = financial_data[column].pct_change(periods=-4) * 100

print(financial_data.head())




# Merge news rating data and stock technical data

df_merged = pd.merge(news_rating, technical_data, on='Date', how='outer')
# fillna(0)to make all NaN to zero
# df_merged.fillna(0, inplace=True)
# fillna(0)to Na of 'Rating' column
df_merged['Rating'] = df_merged['Rating'].fillna(0)

# Date range
start_date = '2024-01-01'
end_date = '2024-04-05'

# Creat a DataFrame include all date in the range
all_dates = pd.DataFrame(pd.date_range(start=start_date, end=end_date), columns=['Date'])

# Merge date frame with df_merged
df_mergedWithDate = pd.merge(all_dates, df_merged, on='Date', how='outer')

# fill NaN
df_mergedWithDate['Rating'].fillna(0, inplace=True)

# Determine it's trading day or not
df_mergedWithDate['IsTradingDay'] = df_mergedWithDate['Open'].notna().astype(int)

print(df_mergedWithDate.head(20))





# Processing data for model


df_mergedWithDate.fillna(method='ffill', inplace=True)
df_cleaned = df_mergedWithDate.dropna()
print(df_cleaned)

# train = df_cleaned.iloc[:-1]  # except last row
# test = df_cleaned.iloc[-1:]  # the last row

# print("Train size:", train.shape)
# print("Test size:", test.shape)

X = df_cleaned.drop(columns=['Next_Day_Close_Change','Date'])  # features
y = df_cleaned['Next_Day_Close_Change'] #Dependent variable
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, shuffle=False)

# Initialize standardizer
scaler = StandardScaler()

# standardized data
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Initialize normalizer
scaler = MinMaxScaler()

# Train the normalizer
scaler.fit(X_train)

# Normalize data
X_train_normalized = scaler.transform(X_train)
X_test_normalized = scaler.transform(X_test)

# X = df_mergedWithDate.drop(columns=['Next_Day_Close_Change']).copy()
# y = df_mergedWithDate['Next_Day_Close_Change'].values



print("Run model")
tfd = tfp.distributions
tfb = tfp.bijectors

class BayesianLinearRegression(tf.Module):
    def __init__(self, num_features):
        super(BayesianLinearRegression, self).__init__()
        self.num_features = num_features

    def model(self, X, weights, biases):
        y_pred = tf.add_n([X[:, i:i+1] * weights[i] + biases[i] for i in range(len(weights))])
        return tf.reduce_sum(y_pred, axis=1)

    def define_prior(self):
        weight_priors = [tfd.Normal(loc=0., scale=1.) for _ in range(self.num_features)]
        bias_priors = [tfd.Normal(loc=0., scale=1.) for _ in range(self.num_features)]
        return weight_priors, bias_priors

    def joint_log_prob(self, X, y, weights, biases):
        weight_priors, bias_priors = self.define_prior()
        prior_log_prob = tf.add_n([weight_priors[i].log_prob(weights[i]) + bias_priors[i].log_prob(biases[i]) for i in range(len(weights))])
        y_pred = self.model(X, weights, biases)
        likelihood = tfd.Normal(loc=y_pred, scale=1.)
        return prior_log_prob + tf.reduce_sum(likelihood.log_prob(y))

def run_mcmc(model, X_train, y_train, num_features, num_results=1000, num_burnin_steps=500, num_chains=4, num_iterations=5):
    # 初始化权重和偏置
    initial_weights = [tf.zeros([], name=f"init_weight_{i}") for i in range(num_features)]
    initial_biases = [tf.zeros([], name=f"init_bias_{i}") for i in range(num_features)]

    # 定义目标对数概率函数
    def target_log_prob_fn(*params):
        return model.joint_log_prob(X_train, y_train, params[:num_features], params[num_features:])

    # 设置HMC采样器
    adaptive_hmc = tfp.mcmc.SimpleStepSizeAdaptation(
        tfp.mcmc.HamiltonianMonteCarlo(
            target_log_prob_fn=target_log_prob_fn,
            step_size=0.01,
            num_leapfrog_steps=3),
        num_adaptation_steps=int(num_burnin_steps * 0.8))

    # 使用tqdm显示进度
    trace_fn = lambda _, pkr: pkr.inner_results.is_accepted
    samples = []
    for i in tqdm(range(num_iterations), desc='MCMC Sampling'):
        states, kernel_results = tfp.mcmc.sample_chain(
            num_results=num_results,
            num_burnin_steps=num_burnin_steps,
            current_state=initial_weights + initial_biases,
            kernel=adaptive_hmc,
            num_steps_between_results=0,  # Updated to 0 for demonstration purposes
            parallel_iterations=num_chains,
            trace_fn=trace_fn)
        samples.append(states)
    return samples

# 假设 X_train_normalized 和 y_train 已经被正确定义
num_features = X_train_normalized.shape[1]
model = BayesianLinearRegression(num_features=num_features)

# 执行MCMC采样
states = run_mcmc(model, X_train_normalized, y_train, num_features)

# 解包权重和偏置样本
weight_samples = states[:num_features]
bias_samples = states[num_features:]





# 将权重和偏置样本转换为 NumPy 数组
weight_samples = np.array(states[:num_features])
bias_samples = np.array(states[num_features:])

# 计算平均权重和偏置
mean_weights = np.mean(weight_samples, axis=1)
mean_biases = np.mean(bias_samples, axis=1)

# 打印形状
print("Mean weights shape:", mean_weights.shape)
print("Mean biases shape:", mean_biases.shape)


# # 使用 arviz 将采样结果转换为 InferenceData
# idata = az.from_dict(posterior={"weights": weight_samples_np, "biases": bias_samples_np})

# # 计算 R hat
# r_hat = az.rhat(idata)
# print("R hat values:", r_hat)


# 使用平均参数进行预测
y_predict = model.model(X_test_normalized, mean_weights, mean_biases)

# 打印预测结果
print("Predicted values:")
print(y_predict)
print("True values:")
