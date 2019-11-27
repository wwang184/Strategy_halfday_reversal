#coding:utf-8
import pandas as pd
import numpy as np
import datetime

f = lambda x: datetime.datetime.strptime(x,'%Y/%m/%d')

data = pd.read_csv('HS300DATA.csv',header=1)
data.dropna(axis=1,how='all',inplace=True)
list = ['DATE.'+str(i) for i in range(1,300)]
for label in list:
    data.drop(labels=[label],axis=1,inplace=True)

data.set_index(keys='DATE', inplace=True, drop=False)
data.rename(columns={'OPEN_PRICE': 'OPEN_PRICE.0','CLOSE_PRICE': 'CLOSE_PRICE.0'}, inplace=True)


def create_label_df(label, data):
    list = [label+'.'+str(i) for i in range(0,300)]
    list.insert(0,'DATE')
    df = data.loc[:,list]
    df = np.array(df)
    np.save(str(label)+'.npy',df)
    return df


def create_tradingday(data):
    df = data.loc[:,'DATE']
    df = np.array(df)
    np.save('TRADING_DATE.npy',df)


OPEN_PRICE = create_label_df('OPEN_PRICE',data)
# CLOSE_PRICE = create_label_df('CLOSE_PRICE',data)

create_tradingday(data)




