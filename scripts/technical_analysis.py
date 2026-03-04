#!/usr/bin/env python3
"""
技术分析模块 v1.0
K线数据 + 技术指标计算
"""
import requests
import json
from datetime import datetime, timedelta
import numpy as np

TUSHARE_API = "http://lianghua.nanyangqiankun.top"
TUSHARE_TOKEN = "a8d44e2c33c97e6ef8127d7d35ae71953de31b802230a9b72767a2fc193f"


class TechnicalAnalyzer:
    """技术分析器"""
    
    def __init__(self):
        self.token = TUSHARE_TOKEN
        self.api_url = TUSHARE_API
    
    def get_kline_data(self, ts_code, days=60):
        """获取K线数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = {
            "api_name": "daily",
            "token": self.token,
            "params": {
                "ts_code": ts_code,
                "start_date": start_date.strftime("%Y%m%d"),
                "end_date": end_date.strftime("%Y%m%d")
            }
        }
        
        try:
            resp = requests.post(self.api_url, json=data, timeout=15)
            result = resp.json()
            if result.get("code") == 0 and result.get("data", {}).get("items"):
                items = result["data"]["items"]
                # 转换为标准格式 [date, open, high, low, close, vol]
                klines = []
                for item in items:
                    klines.append({
                        "date": item[1],
                        "open": float(item[2]),
                        "high": float(item[3]),
                        "low": float(item[4]),
                        "close": float(item[5]),
                        "vol": float(item[9])
                    })
                return sorted(klines, key=lambda x: x["date"])
        except Exception as e:
            print(f"获取K线失败 {ts_code}: {e}")
        return []
    
    def calculate_ma(self, prices, periods=[5, 10, 20, 60]):
        """计算移动平均线"""
        mas = {}
        for period in periods:
            if len(prices) >= period:
                ma = sum(prices[-period:]) / period
                mas[f"MA{period}"] = round(ma, 2)
        return mas
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        if len(prices) < slow + signal:
            return None
        
        # 计算EMA
        ema_fast = self._ema(prices, fast)
        ema_slow = self._ema(prices, slow)
        
        # DIF = EMA(12) - EMA(26)
        dif = ema_fast - ema_slow
        
        # DEA = EMA(DIF, 9)
        dea = self._ema([dif], signal)
        
        # MACD = 2 * (DIF - DEA)
        macd = 2 * (dif - dea)
        
        return {
            "DIF": round(dif, 3),
            "DEA": round(dea, 3),
            "MACD": round(macd, 3),
            "signal": "金叉" if dif > dea and dif > 0 else "死叉" if dif < dea else "震荡"
        }
    
    def _ema(self, prices, period):
        """计算指数移动平均"""
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def calculate_rsi(self, prices, period=14):
        """计算RSI相对强弱指标"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "正常"
        return {"RSI": round(rsi, 2), "status": status}
    
    def analyze_stock(self, name, ts_code):
        """分析单只股票"""
        klines = self.get_kline_data(ts_code)
        if not klines or len(klines) < 20:
            return None
        
        closes = [k["close"] for k in klines]
        current_price = closes[-1]
        
        # 计算指标
        ma = self.calculate_ma(closes)
        macd = self.calculate_macd(closes)
        rsi = self.calculate_rsi(closes)
        
        # 趋势判断
        trend = self._judge_trend(ma, current_price)
        
        return {
            "name": name,
            "ts_code": ts_code,
            "current_price": current_price,
            "ma": ma,
            "macd": macd,
            "rsi": rsi,
            "trend": trend
        }
    
    def _judge_trend(self, ma, current_price):
        """判断趋势"""
        if not ma:
            return "未知"
        
        ma5 = ma.get("MA5", 0)
        ma10 = ma.get("MA10", 0)
        ma20 = ma.get("MA20", 0)
        
        if current_price > ma5 > ma10 > ma20:
            return "强势上涨"
        elif current_price > ma5 > ma10:
            return "上涨趋势"
        elif current_price < ma5 < ma10 < ma20:
            return "强势下跌"
        elif current_price < ma5 < ma10:
            return "下跌趋势"
        else:
            return "震荡整理"
    
    def analyze_portfolio(self, holdings_file):
        """分析整个持仓组合"""
        import os
        if not os.path.exists(holdings_file):
            return []
        
        with open(holdings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        results = []
        
        # 处理不同格式的持仓数据
        stocks = []
        if "stocks" in data:
            stocks = data["stocks"]
        elif "accounts" in data:
            for account_stocks in data["accounts"].values():
                stocks.extend(account_stocks)
        
        for stock in stocks[:10]:  # 只分析前10只，避免太慢
            name = stock.get("name", "")
            # 尝试获取股票代码
            ts_code = self._get_ts_code(name)
            if ts_code:
                analysis = self.analyze_stock(name, ts_code)
                if analysis:
                    results.append(analysis)
        
        return results
    
    def _get_ts_code(self, name):
        """根据名称获取股票代码（简化版）"""
        # 这里应该有个映射表，先用硬编码的常见股票
        mapping = {
            "紫金矿业": "601899.SH",
            "浪潮信息": "000977.SZ",
            "工业富联": "601138.SH",
            "歌尔股份": "002241.SZ",
            "四川长虹": "600839.SH",
            "上汽集团": "600104.SH",
            "TCL科技": "000100.SZ",
            "利欧股份": "002131.SZ",
            "浩物股份": "000757.SZ"
        }
        return mapping.get(name)


if __name__ == "__main__":
    analyzer = TechnicalAnalyzer()
    
    # 测试分析一只股票
    print("=== 技术分析测试 ===")
    result = analyzer.analyze_stock("紫金矿业", "601899.SH")
    if result:
        print(f"\n{result['name']} ({result['ts_code']})")
        print(f"当前价格: {result['current_price']}")
        print(f"均线: {result['ma']}")
        print(f"MACD: {result['macd']}")
        print(f"RSI: {result['rsi']}")
        print(f"趋势: {result['trend']}")