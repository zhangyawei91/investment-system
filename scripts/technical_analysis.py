"""
技术指标分析模块
计算KDJ、MACD、布林线等技术指标
"""
import requests
import json
from datetime import datetime, timedelta

# 获取K线数据 - 智能选择数据源
def get_kline(code, days=30):
    """获取股票/ETF的K线数据 - 智能选择"""
    # 1. 先试东方财富
    result = _get_kline_eastmoney(code, days)
    if result:
        return result
    
    # 2. 试新浪 (适合ETF)
    result = _get_kline_sina(code, days)
    if result:
        return result
    
    # 3. 试Tushare
    result = _get_kline_tushare(code, days)
    if result:
        return result
    
    print(f"获取{code}K线失败: 所有数据源都不可用")
    return None


def _get_kline_eastmoney(code, days=30):
    """东方财富获取K线"""
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": 101,
        "fqt": 1,
        "end": "20500101",
        "lmt": days,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"]
            result = []
            for line in klines:
                parts = line.split(",")
                result.append({
                    "date": parts[0],
                    "open": float(parts[1]),
                    "close": float(parts[2]),
                    "high": float(parts[3]),
                    "low": float(parts[4]),
                    "volume": float(parts[5]),
                    "amount": float(parts[6]) if len(parts) > 6 else 0,
                })
            return result
    except:
        pass
    return None


def _get_kline_tushare(code, days=30):
    """Tushare获取K线"""
    import sys
    sys.path.insert(0, str(__file__).replace("technical_analysis.py", ""))
    from scripts.data_fetcher import TUSHARE_TOKEN, TUSHARE_API_URL
    
    ts_code = f"{code}.SZ" if code.startswith(("0", "3")) else f"{code}.SH"
    import requests as req
    data = {
        "api_name": "daily",
        "token": TUSHARE_TOKEN,
        "params": {"ts_code": ts_code, "start_date": "20260201", "end_date": "20260303"},
        "fields": "ts_code,trade_date,open,high,low,close,vol"
    }
    try:
        resp = req.post(TUSHARE_API_URL, json=data, timeout=15)
        result = resp.json()
        if result.get("code") == 0 and result.get("data", {}).get("items"):
            items = result["data"]["items"]
            klines = []
            for item in items[-days:]:
                klines.append({
                    "date": str(item[1]),
                    "open": item[2],
                    "close": item[5],
                    "high": item[3],
                    "low": item[4],
                    "volume": item[6],
                })
            return klines
    except:
        pass
    return None


def _get_kline_sina(code, days=30):
    """新浪获取ETF K线"""
    import requests as req
    # ETF代码以5开头，用sh或sz
    symbol = f"sh{code}" if code.startswith("5") else code
    url = f'https://quotes.sina.cn/cn/api_json.php/CN_MarketDataService.getKLineData?symbol={symbol}&scale=240&ma=5&datalen={days}'
    try:
        resp = req.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=10)
        import json
        data = resp.json()
        if data:
            klines = []
            for item in data:
                klines.append({
                    "date": item.get("day", ""),
                    "open": float(item.get("open", 0)),
                    "close": float(item.get("close", 0)),
                    "high": float(item.get("high", 0)),
                    "low": float(item.get("low", 0)),
                    "volume": float(item.get("volume", 0)),
                })
            return klines
    except:
        pass
    return None

def calculate_ma(prices, period):
    """计算移动平均线"""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def calculate_ema(prices, period):
    """计算指数移动平均线(EMA)"""
    if len(prices) < period:
        return None
    ema = prices[0]
    multiplier = 2 / (period + 1)
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_kdj(klines, period=9, k_period=3, d_period=3):
    """计算KDJ指标"""
    if len(klines) < period:
        return None
    
    rsv = []
    for i in range(period - 1, len(klines)):
        low_min = min(klines[i - period + 1:i + 1], key=lambda x: x["low"])["low"]
        high_max = max(klines[i - period + 1:i + 1], key=lambda x: x["high"])["high"]
        close = klines[i]["close"]
        
        if high_max == low_min:
            rsv.append(50)
        else:
            rsv.append((close - low_min) / (high_max - low_min) * 100)
    
    # 计算K、D、J值
    k_values = [50]
    d_values = [50]
    
    for i in range(1, len(rsv)):
        k = (k_values[-1] * (k_period - 1) + rsv[i]) / k_period
        d = (d_values[-1] * (d_period - 1) + k) / d_period
        j = 3 * k - 2 * d
        k_values.append(k)
        d_values.append(d)
    
    return {
        "K": k_values[-1],
        "D": d_values[-1],
        "J": 3 * k_values[-1] - 2 * d_values[-1],
        "signal": "超买" if k_values[-1] > 80 else "超卖" if k_values[-1] < 20 else "正常"
    }

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(prices) < slow:
        return None
    
    # 计算EMA
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    if ema_fast is None or ema_slow is None:
        return None
    
    dif = ema_fast - ema_slow
    
    # 计算DEA (signal线的EMA)
    # 简化计算
    dea = dif * 0.9  # 近似
    
    bar = 2 * (dif - dea)
    
    return {
        "DIF": dif,
        "DEA": dea,
        "BAR": bar,
        "signal": "金叉(买入)" if dif > dea else "死叉(卖出)"
    }

def calculate_boll(klines, period=20):
    """计算布林带"""
    if len(klines) < period:
        return None
    
    closes = [k["close"] for k in klines]
    ma = calculate_ma(closes, period)
    
    if ma is None:
        return None
    
    # 计算标准差
    variance = sum((c - ma) ** 2 for c in closes[-period:]) / period
    std = variance ** 0.5
    
    upper = ma + 2 * std
    lower = ma - 2 * std
    
    current_price = closes[-1]
    
    return {
        "MA": ma,
        "UPPER": upper,
        "LOWER": lower,
        "position": "上轨" if current_price > upper else "下轨" if current_price < lower else "中轨"
    }

def analyze_stock(code, name):
    """综合分析一只股票/ETF"""
    klines = get_kline(code, 60)  # 获取60天数据
    if not klines:
        return {"error": f"无法获取{name}的数据"}
    
    closes = [k["close"] for k in klines]
    
    result = {
        "name": name,
        "code": code,
        "current_price": closes[-1],
        "ma5": calculate_ma(closes, 5),
        "ma10": calculate_ma(closes, 10),
        "ma20": calculate_ma(closes, 20),
        "ma60": calculate_ma(closes, 60),
    }
    
    # 技术指标
    kdj = calculate_kdj(klines)
    if kdj:
        result["KDJ"] = kdj
    
    macd = calculate_macd(closes)
    if macd:
        result["MACD"] = macd
    
    boll = calculate_boll(klines)
    if boll:
        result["BOLL"] = boll
    
    return result

# 测试
if __name__ == "__main__":
    # 测试获取歌尔股份
    print("分析歌尔股份(002241)...")
    result = analyze_stock("002241", "歌尔股份")
    print(json.dumps(result, indent=2, ensure_ascii=False))
