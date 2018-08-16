#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import pandas as pd
import matplotlib.pyplot as plt

data_code = {'CO2': 'EN.ATM.CO2E.KT', 'METH': 'EN.ATM.METH.KT.CE', 'NOX': 'EN.ATM.NOXE.KT.CE',
             'GHGO': 'EN.ATM.GHGO.KT.CE', 'GHGR': 'EN.CLC.GHGR.MT.CE'}
df_data = pd.read_excel("ClimateChange.xlsx", sheetname='Data', index_col=0, na_values=['NA'], parse_cols="A,C,G:AB")
df_temperature = pd.read_excel("GlobalTemperature.xlsx", index_col=0, parse_cols="A,B,E")


# nations = ['CHN', 'USA', 'GBR', 'FRA', 'RUS']


def year_data(data):
    '''以年為單位將資料加總,輸出df'''
    df = df_data.loc[df_data['Series code'] == data_code[data]].replace(
        {'..': pd.np.NaN}).drop('Series code', 1)  # 選擇data，並將表中的".."替換成NaN，刪除"Series code" col
    df = df.fillna(method='ffill', axis=1).fillna(method='bfill', axis=1)  # 填NaN數據
    df.dropna(how='all', inplace=True)
    df = df.sum()
    df.name = data
    # df[data + '-SUM'] = df.values.sum(1)  # 以國為單位將資料加總
    return df


def climate_data():
    '''將各年溫室氣體排放資料加總，輸出df'''
    df = pd.concat([year_data(key) for key, _ in data_code.items()], axis=1).sum(1)
    # df = pd.concat([nation_data('CO2')['CO2-SUM'], nation_data('GDP')['GDP-SUM']], axis=1)#
    return df


def normalize(df):
    '''將輸入的df歸依化後輸出'''
    df = (df - df.min()) / (df.max() - df.min())  # normalize the data
    return df


def climate_plot():
    df1 = climate_data()
    df1.name = 'Total GHG'
    df1.index = pd.to_datetime(df1.index, format='%Y')  # 將index改為年datetime object
    df1.index = df1.index.to_period('A').to_timestamp('A')  # 將datetime start of the year change to end of the year

    df_temp = df_temperature
    df_temp.index = pd.to_datetime(df_temp.index, format='%Y-%m-%d')  # 將index改為年datetime object
    df2 = df_temp
    df2 = df2.resample('A').mean()  # 重採樣為以年為頻率，方法為平均
    df_temp = df_temp.resample('Q').mean()

    df_ghg_temp = normalize(pd.concat([df2, df1], axis=1, join='inner')).loc['1990':'2010']  # 1990 年 - 2010 年

    fig, axes = plt.subplots(nrows=2, ncols=2)


    # 子图 1（线形图 kind = 'line'）：绘制 1990 年 - 2010 年间，「全球历年温室气体排放总量」与「历年陆地平均温度」及「历年陆地-海洋平均温度」三者之间的线形图。
    #plt.subplot(221)
    ax1 = df_ghg_temp.plot(kind='line', ax=axes[0, 0], figsize=(16, 9))
    ax1.set_xlabel('Years')
    ax1.set_ylabel('Values')
    #ax1.legend(loc='best')
    ax1.autoscale(axis='x', tight=True)
    ax1.grid(True)

    # 子图 2（柱状图 kind = 'bar'）：绘制 1990 年 - 2010 年间，「全球历年温室气体排放总量」与「历年陆地平均温度」及「历年陆地-海洋平均温度」三者之间的柱状图。
    #plt.subplot(222)
    ax2 = df_ghg_temp.plot(kind='bar', ax=axes[0, 1], figsize=(16, 9))
    ax2.xaxis.set_major_formatter(plt.FixedFormatter(df_ghg_temp.index.to_series().dt.strftime("%Y")))
    ax2.set_xlabel('Years')
    ax2.set_ylabel('Values')
    #ax2.legend(loc='best')
    ax2.autoscale(axis='x', tight=True)
    ax2.grid(True)


    # 子图 3（面积图 kind = 'area'）：绘制有气象数据的年份，「各季度地面平均温度」与「各季度地面-海洋平均温度」面积图。
    #plt.subplot(223)
    ax3 = df_temp.plot(kind='area', ax=axes[1, 0], figsize=(16, 9))
    ax3.set_xlabel('Years')
    ax3.set_ylabel('Values')
    #ax3.legend(loc='best')
    ax3.autoscale(axis='x', tight=True)
    ax3.grid(True)

    # 子图 4（核密度估计图 kind = 'kde'）：绘制有气象数据年份，「各季度地面平均温度」与「各季度地面-海洋平均温度」对应的核密度估计图。
    #plt.subplot(224)
    ax4 = df_temp.plot(kind='kde', ax=axes[1, 1], figsize=(16, 9)) # set figsize 避免擠在一起
    ax4.set_xlabel('Values')
    ax4.set_ylabel('Values')
    ax4.autoscale(axis='x', tight=True)
    ax4.grid(True)
    # Adjust the subplot layout, because the logit one may take more space
    # than usual, due to y-tick labels like "1 - 10^{-3}"
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                        wspace=0.35)
    plt.show()
    return fig
