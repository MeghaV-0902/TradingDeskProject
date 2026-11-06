GROUP_CODE = "G15-MRPW"
# Group: Vasu Megha, Ambre Rugved Suresh Puri Harshita,
# Shaikh Mohammed Arsalan, Kakade Subodh Sunil
# Reference: Vasu Megha

import numpy as np
import pandas as pd
import math
import random


class TradingAgent:

    def __init__(self):
        self.price_history = [] # stores history of clsing prices
        self.buy_history = [] #stores prices at which agent decides to buy
        self.sell_history = [] #stores prices at which agent decides to sell

        self.previous_action = "HOLD" # lastest action adviced by agent
        self.days_since_trade = 999

        self.entry_price = None
        self.highest_price_since_buy = None
        self.stop_price = None

        # News-only regime state
        self.news_days_held = 0
        self.mood_history = []
        self.max_hold_news = 6

        self.positive_words = {
            "surge", "rally", "gain", "breakout", "inflow", "boom",
            "growth", "profit", "rise", "bullish", "strong", "beat",
            "upgrade", "positive", "record"
        }

        self.negative_words = {
            "crash", "plunge", "loss", "selloff", "outflow", "fear",
            "decline", "drop", "bearish", "weak", "fall", "miss",
            "downgrade", "negative", "warning"
        }

    # ==================== PRICE INDICATORS ====================

    def moving_average(self, period, offset=0):

        end = len(self.price_history) - offset
        start = end - period

        if start < 0:
            return None

        return sum(self.price_history[start:end]) / period

    def volatility_range(self, period=14):

        if len(self.price_history) < period + 1:
            return None

        prices = self.price_history[-period-1:]
        ranges = []

        for i in range(1, len(prices)):
            ranges.append(abs(prices[i] - prices[i-1]))

        if not ranges:
            return None

        return sum(ranges) / len(ranges)

    def momentum(self, period=6):

        if len(self.price_history) <= period:
            return None

        old_price = self.price_history[-period-1]
        current = self.price_history[-1]

        if old_price <= 0:
            return None

        return (current - old_price) / old_price

    def market_trend(self):

        ma10 = self.moving_average(10)
        ma20 = self.moving_average(20)
        ma50 = self.moving_average(50)

        if ma10 is None or ma20 is None or ma50 is None:
            return "UNKNOWN"

        if ma10 > ma20 > ma50:
            return "BULLISH"

        if ma10 < ma20 < ma50:
            return "BEARISH"

        return "NEUTRAL"

    def market_falling(self, period=5):

        if len(self.price_history) < period:
            return False

        recent = self.price_history[-period:]

        return recent[-1] < recent[0]

    # ==================== NEWS ====================

    def calculate_news_sentiment(self, headlines):

        if headlines is None:
            return 0

        sentiment = 0

        for headline in headlines:

            words = headline.lower().split()

            for word in words:

                word = word.strip(".,!?;:()[]{}\"'")

                if word in self.positive_words:
                    sentiment += 1

                elif word in self.negative_words:
                    sentiment -= 1

        return sentiment

    # ==================== ENTRY STRATEGY ====================

    def buy_signal(self, cash, shares, headlines):

        if shares > 0 or cash <= 0:
            return False

        if len(self.price_history) < 51:
            return False

        current = self.price_history[-1]

        ma10 = self.moving_average(10)
        ma20 = self.moving_average(20)
        ma50 = self.moving_average(50)

        previous_ma20 = self.moving_average(20, offset=1)

        # Strong trend confirmation
        if not (ma10 > ma20 > ma50):
            return False

        # Rising medium-term trend
        if previous_ma20 is None or ma20 <= previous_ma20:
            return False

        # Stronger momentum
        momentum = self.momentum(6)

        if momentum is None or momentum < 0.01 or momentum > 0.045:
            return False

        # Breakout above previous 10-day high
        previous_prices = self.price_history[-11:-1]

        if len(previous_prices) < 10:
            return False

        if current <= max(previous_prices):
            return False

        # Avoid excessively extended prices
        if current > ma20 * 1.05:
            return False

        # Avoid sudden spikes
        if current > max(previous_prices) * 1.015:
            return False

        if self.market_falling(5):
            return False

        # News confirmation
        sentiment = self.calculate_news_sentiment(headlines)

        if headlines is not None and sentiment < 0:
            return False

        return True

    # ==================== POSITION TRACKING ====================

    def update_position(self, close_price, shares, bar, last_response):

        if shares <= 0:

            self.entry_price = None
            self.highest_price_since_buy = None
            self.stop_price = None

            return

        # Approximate execution price
        if self.entry_price is None:

            if (
                self.previous_action == "BUY"
                and last_response == "ACCEPT"
            ):

                self.entry_price = bar["open"]

            else:

                self.entry_price = close_price

            self.highest_price_since_buy = max(
                self.entry_price,
                close_price
            )

        self.highest_price_since_buy = max(
            self.highest_price_since_buy,
            close_price
        )

        entry = self.entry_price
        peak = self.highest_price_since_buy

        atr = self.volatility_range(14)

        # Initial volatility-adjusted stop
        if atr is None:

            initial_distance = entry * 0.025

        else:

            initial_distance = min(
                max(atr * 2.0, entry * 0.015),
                entry * 0.035
            )

        hard_stop = entry - initial_distance

        peak_gain = (peak / entry) - 1

        # Profit protection
        if peak_gain >= 0.10:

            trailing_stop = peak * 0.985

        elif peak_gain >= 0.07:

            trailing_stop = peak * 0.975

        elif peak_gain >= 0.04:

            trailing_stop = peak * 0.97

        elif peak_gain >= 0.02:

            trailing_stop = peak * 0.96

        else:

            trailing_stop = hard_stop

        self.stop_price = max(
            hard_stop,
            trailing_stop
        )

    # ==================== EXIT STRATEGY ====================

    def should_sell(self, headlines):

        if self.entry_price is None or not self.price_history:
            return False

        current = self.price_history[-1]

        # Stop-loss or trailing stop
        if current <= self.stop_price:
            return True

        # Trend reversal
        ma5 = self.moving_average(5)
        ma10 = self.moving_average(10)
        ma20 = self.moving_average(20)

        # Earlier trend-reversal exit: short-term weakness confirmed by
        # either a deteriorating MA10 or a close below the medium trend.
        if ma5 is not None and ma10 is not None and ma20 is not None:
            if ma5 < ma10 and (ma10 < ma20 or current < ma20):
                return True

        # Strong negative news
        sentiment = self.calculate_news_sentiment(headlines)

        if sentiment <= -2:
            return True

        return False

    # ==================== POSITION SIZING ====================

    def calculate_buy_quantity(self, cash, close_price):

        if cash <= 0 or close_price <= 0:
            return 0

        atr = self.volatility_range(14)

        if atr is None or atr <= 0:
            return 0

        # Increased risk budget: 1.25% of cash
        risk_budget = cash * 0.0125

        stop_distance = max(
            atr * 2.0,
            close_price * 0.015
        )

        stop_distance = min(
            stop_distance,
            close_price * 0.035
        )

        quantity_by_risk = risk_budget / stop_distance

        # Increased allocation: maximum 50% cash
        quantity_by_cash = (
            cash * 0.50
        ) / (close_price * 1.001)

        quantity = min(
            quantity_by_risk,
            quantity_by_cash
        )

        return max(0, quantity)

    # ==================== TRADE SUMMARY ====================

    def trade_summary(self):

        print("Total BUY decisions:", len(self.buy_history))
        print("Total SELL decisions:", len(self.sell_history))

        if self.buy_history:

            print(
                "Average BUY price:",
                round(sum(self.buy_history) / len(self.buy_history), 2)
            )

        if self.sell_history:

            print(
                "Average SELL price:",
                round(sum(self.sell_history) / len(self.sell_history), 2)
            )

    # ==================== MAIN DECISION ENGINE ====================

    def decide(self, bar, headlines, cash, shares, last_response):

        sentiment = self.calculate_news_sentiment(headlines)
        mood_today = sentiment if headlines is not None else 0

        self.mood_history.append(mood_today)

        if len(self.mood_history) > 5:
            self.mood_history.pop(0)

        recent_mood = sum(self.mood_history)

        # Reset counters after rejected orders
        if last_response == "REJECT":
            self.days_since_trade = 0
            self.news_days_held = 0

        # ==========================================================
        # NEWS-ONLY REGIME: no OHLCV bar is supplied
        # ==========================================================
        if bar is None:
            self.days_since_trade += 1

            if shares > 0:
                self.news_days_held += 1

                # Exit as soon as sentiment is no longer positive,
                # or after 4 days to limit stale-news exposure.
                # Exit on negative sentiment or stale news
                if recent_mood <= -2 or sentiment < 0 or self.news_days_held >= self.max_hold_news:
                    self.previous_action = "SELL"
                    self.days_since_trade = 0
                    self.news_days_held = 0
                    self.sell_history.append(float("nan"))
                    return ("SELL", -1)

                self.previous_action = "HOLD"
                return ("HOLD", 0)

            # Require stronger positive news and a longer cooldown
            # to avoid repeatedly entering on weak headlines.
            # Require sustained positive news sentiment
            if cash > 0 and self.days_since_trade >= 5 and recent_mood >= 2:
                self.previous_action = "BUY"
                self.days_since_trade = 0
                self.news_days_held = 0
                self.buy_history.append(float("nan"))
                # -1 tells the engine to buy the maximum affordable quantity
                return ("BUY", -1)

            self.previous_action = "HOLD"
            return ("HOLD", 0)

        # ==========================================================
        # OHLCV / COMBINED REGIME: original price-based logic
        # ==========================================================
        close_price = bar["close"]

        self.price_history.append(close_price)
        if len(self.price_history) > 100:
            self.price_history.pop(0)

        self.update_position(
            close_price,
            shares,
            bar,
            last_response
        )

        self.days_since_trade += 1

        # SELL
        if shares > 0:
            if self.should_sell(headlines):
                self.previous_action = "SELL"
                self.days_since_trade = 0
                self.sell_history.append(close_price)
                return ("SELL", -1)

        # BUY
        if shares <= 0 and self.days_since_trade >= 7:
            if self.buy_signal(cash, shares, headlines):
                quantity = self.calculate_buy_quantity(cash, close_price)

                if quantity > 0:
                    self.previous_action = "BUY"
                    self.days_since_trade = 0
                    self.buy_history.append(close_price)
                    return ("BUY", quantity)

        self.previous_action = "HOLD"
        return ("HOLD", 0)

