from datetime import timedelta
from decimal import Decimal

from QuantConnect.Algorithm import QCAlgorithm


class TSMCNewsScalper(QCAlgorithm):

    def Initialize(self):

        self.SetStartDate(2021, 1, 1)  # set start date
        self.SetCash(100000)  # set cash
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.symbol = self.AddEquity("TSM", Resolution.Minute).Symbol

        self.magic_number = 101010101  # MAGIC NUMBER
        self.news_release_time = datetime(2023, 4, 3, 8, 30, 0)  # NEWS RELEASE DATE AND TIME
        self.lots = 0.01  # LOT SIZE
        self.entry_distance = 12  # ENTRY DISTANCE
        self.break_even_pips = 3  # BREAK EVEN AFTER (pips)
        self.trail_by_pips = 3  # TRAIL BY (pips)
        self.tick = Decimal(self.symbol.Properties.MinimumPriceVariation).normalize()  # minimum price variation

        self.placed_orders = False
        self.buy_order_ticket = None
        self.sell_order_ticket = None

        self.Schedule.On(self.DateRules.EveryDay(self.news_release_time.date()),
                         self.TimeRules.At(self.news_release_time.time()), self.EnterTrades)

        self.Schedule.On(self.DateRules.EveryDay(self.news_release_time.date()),
                         self.TimeRules.AfterMarketOpen(self.symbol, 1), self.CancelOrders)

        self.Schedule.On(self.DateRules.EveryDay(self.news_release_time.date()),
                         self.TimeRules.AfterMarketOpen(self.symbol, 1), self.BreakEven)

        self.Schedule.On(self.DateRules.EveryDay(self.news_release_time.date()),
                         self.TimeRules.Every(timedelta(minutes=1)), self.TrailStop)

    def EnterTrades(self):

        if not self.CheckNewsReleaseDate(self.news_release_time):
            return

        if self.placed_orders:
            return

        entry_price = None
        stop_loss = None

        if self.Securities[self.symbol].Close > self.Securities[self.symbol].Open:
            entry_price = self.Securities[self.symbol].Close + (self.entry_distance * self.tick)
            stop_loss = self.Securities[self.symbol].Close - (self.entry_distance * self.tick)
        else:
            entry_price = self.Securities[self.symbol].Close - (self.entry_distance * self.tick)
            stop_loss = self.Securities[self.symbol].Close + (self.entry_distance * self.tick)

        self.buy_order_ticket = self.LimitOrder(self.symbol, self.lots, entry_price, "Buy", self.magic_number)
        self.sell_order_ticket = self.LimitOrder(self.symbol, self.lots, entry_price, "Sell", self.magic_number)

        self.placed_orders = True

    def CancelOrders(self):

        if not self.placed_orders:
            return

        open_orders = self.Transactions.GetOpenOrders(self.symbol)
        for order in open_orders:
            self.Transactions.CancelOrder(order.Id)

    def BreakEven(self):

        if not self.placed_orders:
            return

        open_orders = self.Transactions.GetOpenOrders(self.symbol)
        if len(open_orders) == 1:
            for order in open_orders:
                if order.Symbol == self
