"""
Tushare Pro 付费版数据接口
"""
import requests
import json
from datetime import datetime, timedelta

TOKEN = "a8d44e2c33c97e6ef8127d7d35ae71953de31b802230a9b72767a2fc193f"
API_URL = "http://lianghua.nanyangqiankun.top"

def tushare_request(api_name, params=None, fields=None):
    """发送请求到Tushare"""
    url = API_URL
    data = {
        "api_name": api_name,
        "token": TOKEN,
        "params": params or {},
        "fields": fields or ""
    }
    try:
        resp = requests.post(url, json=data, timeout=15)
        result = resp.json()
        if result.get("code") == 0:
            return result.get("data", {})
        else:
            print(f"API错误: {result.get('msg')}")
    except Exception as e:
        print(f"请求错误: {e}")
    return None

# === 数据获取函数 ===

def get_daily_quote(ts_code, days=5):
    """获取日线行情"""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days+10)).strftime("%Y%m%d")
    
    data = tushare_request("daily", {
        "ts_code": ts_code,
        "start_date": start_date,
        "end_date": end_date
    }, "ts_code,trade_date,open,high,low,close,vol")
    
    if data and data.get("items"):
        return data["items"][0]  # 最新一天
    return None

def get_index_quotes():
    """获取主要指数行情"""
    indices = [
        ("000001.SH", "上证指数"),
        ("000300.SH", "沪深300"),
        ("399006.SZ", "创业板"),
    ]
    
    results = []
    for code, name in indices:
        item = get_daily_quote(code)
        if item:
            results.append({
                "name": name,
                "code": code,
                "close": item[6],  # close
                "date": item[1]
            })
    return results

def get_stock_quote(ts_code):
    """获取个股/ETF行情"""
    item = get_daily_quote(ts_code)
    if item:
        return {
            "ts_code": item[0],
            "date": item[1],
            "open": item[2],
            "high": item[3],
            "low": item[4],
            "close": item[5],
            "volume": item[6]
        }
    return None

# 测试
if __name__ == "__main__":
    print("=== Tushare Pro 数据测试 ===\n")
    
    print("📈 指数:")
    for idx in get_index_quotes():
        print(f"  {idx['name']}: {idx['close']}")
    
    print("\n📊 个股/ETF:")
    for code, name in [("002241.SZ", "歌尔股份"), ("510310.SH", "沪深300ETF"), ("600104.SH", "上汽集团")]:
        quote = get_stock_quote(code)
        if quote:
            print(f"  {name}: ¥{quote['close']:.2f}")
