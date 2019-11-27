import numpy as np
import csv


class strategy():
    def __init__(self):
        self.value = 100000  # capital
        self.dataname = 'HS300DATA.csv'  # data set
        self.flag = {}  # flag of holding
        self.hold = {}  # holding number, (/lot = *100/share)
        self.poor_size = 0  # number of stocks in the pool
        self.pool = {}
        self.net_value = 0
        self.net_value_record = []
        self.first_day = 1
        self.open_price = {}
        self.close_price = {}
        self.tradingday = []

    def get_pool(self):
        """
        get stock codes from the CSV file
        :return: dict{'n':code}
        """
        with open(self.dataname) as f:
            reader = csv.reader(f)
            pool = list(reader)[0]
            while '' in pool:
                pool.remove('')
        self.poor_size = len(pool)
        code = [i for i in range(self.poor_size)]
        self.pool = dict(zip(code, pool))

    def set_flag(self):
        # index = [i for i in range(self.poor_size)]
        self.flag = [0 for i in range(self.poor_size)]

    def set_hand(self):
        # index = [i for i in range(self.poor_size)]
        self.hold = [0 for i in range(self.poor_size)]

    def set_traingday(self):
        self.tradingday = np.load('TRADING_DATE.npy').tolist()

    def get_bar(self, label, date): # TODO:date?
        """
        :return: dict{'n':'value'}
        """
        data = np.load(label+'.npy')
        if date in data.T[0]:
            dataT = data.T.tolist()
            location = dataT[0].index(date)
            data = np.array(data)
            value = data[location].tolist()
            del value[0]
            index = [i for i in range(len(value))]
            bar = dict(zip(index, value))
            return bar

    def halfday_reversal(self, date):
        """
        The investment universe consists of all stocks from the S&P 500 index.
        The strategy buys the N worst performing shares from the open-to close period (decision period).
        These shares are bought when the market closes and they are held until the next day’s market open.
        They are subsequently sold for the opening price. Shares are equally weighted in the portfolio.
        -----OPEN-----
        1.get the opening price of each stock, get_bar
        2.value = sum(hold*price)
        3.hold =0, flag =0.
        -----CLOSE-----
        1.sort by closing prices, flag the least N ones as 1, get_bar
        2.hold = value/price
        :return:
        """

        n = 10
        index_nonan = []  # index of stocks that have open prices
        index_nan = []  # index of stocks that have nan for open prices
        rest_value = 0

        if self.first_day == 0:
            self.open_price = self.get_bar('OPEN_PRICE', date)
            for key in self.open_price.keys():
                if np.isnan(self.open_price[key]):
                    index_nan.append(key)
                else:
                    index_nonan.append(key)    # index of tradeable stocks
            self.value = sum([self.open_price[key] * self.hold[key] for key in index_nonan])
            for key in index_nonan:
                self.flag[key] = 0
                self.hold[key] = 0  # sold
            # If a stock is untradeable: flag = 1, hold keeps the same, rest value = close price* hold
            for key in index_nan:
                if not np.isnan(self.close_price[key]):
                    rest_value = rest_value + self.close_price[key]*self.hold[key]
            self.net_value = self.value + rest_value
            self.net_value_record.append((date,self.net_value))

        self.close_price = self.get_bar('CLOSE_PRICE', date)
        # We do not consider the nan stocks at that day
        nan_number = 0
        for key in self.open_price.keys():
            if np.isnan(self.open_price[key]):
                self.close_price[key] = 0
                nan_number = nan_number+1
        self.close_price = sorted(self.close_price.items(), key=lambda x: x[1], reverse=False)
        least_close_price = dict(self.close_price[nan_number:(n+nan_number)])
        self.close_price = dict(self.close_price)
        for key in least_close_price.keys():
            # if key not in index_nan:
                self.flag[key] = 1
                self.hold[key] = self.value*1.0/(n*self.close_price[key])  # Equal money for each stock
            # TODO:hold should be integers



if __name__ == '__main__':
    strategy = strategy()
    strategy.get_pool()
    strategy.set_flag()
    strategy.set_hand()
    strategy.set_traingday()
    for date in strategy.tradingday:
        strategy.halfday_reversal(date)
        strategy.first_day = 0
        print(date, strategy.net_value)

    print(strategy.net_value_record)

    # output date and net value to txt
    f = open('BackTest.txt','w')
    for i in strategy.net_value_record:
        for j in i:
            f.write(str(j)+" ")
        f.write("\n")
    f.close()

