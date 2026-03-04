"""
新浪财经数据接口
免费、稳定、支持A股/港股/指数
"""
import requests
import json
from datetime import datetime

def get_index_sina(code):
    """获取指数行情 (新浪)"""
    # 沪深300: sh000300, 上证: sh000001, 创业板: sz399006
    url = f"https://hq.sinajs.cn/list=s_{code}"
    headers = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        content = resp.text
        if "hq_str" in content:
            data = content.split('="')[1].rstrip('";').split(",")
            return {
                "name": data[0],
                "price": float(data[1]),
                "change": float(data[2]),
                "change_pct": float(data[3]),
                "volume": float(data[4]) if len(data) > 4 else 0,
            }
    except:
        pass
    return None

def get_stock_sina(code):
    """获取个股/ETF行情 (新浪)"""
    # 上海: sh.600xxx, 深圳: sz.000xxx
    if code.startswith("6"):
        symbol = f"sh.{code}"
    elif code.startswith(("0", "3")):
        symbol = f"sz.{code}"
    else:
        return None
    
    url = f"https://hq.sinajs.cn/list={symbol}"
    headers = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        content = resp.text
        if "hq_str" in content:
            data = content.split('="')[1].rstrip('";').split(",")
            return {
                "name": data[0],
                "open": float(data[1]),
                "close": float(data[2]),
                "price": float(data[3]),
                "high": float(data[4]),
                "low": float(data[5]),
            }
    except:
        pass
    return None

def get_hk_stock(code):
    """获取港股行情"""
    url = f"https://hq.sinajs.cn/list=hk{code}"
    headers = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        content = resp.text
        if "hq_str" in content:
            data = content.split('="')[1].rstrip('";').split(",")
            return {
                "name": data[1],
                "price": float(data[6]),
                "change": float(data[8]) if len(data) > 8 else 0,
            }
    except:
        pass
    return None

# 测试
if __name__ == "__main__":
    print("=== 新浪财经API测试 ===")
    print("\n📈 指数:")
    for code, name in [("sh000300", "沪深300"), ("sh000001", "上证"), ("sz399006", "创业板")]:
        data = get_index_sina(code)
        if data:
            print(f"  {name}: {data['price']:.2f} ({data['change_pct']:+.2f}%)")
    
    print("\n📊 A股:")
    for code, name in [("600104", "上汽集团"), ("002241", "歌尔股份"), ("510300", "沪深300ETF")]:
        data = get_stock_sina(code)
        if data:
            change = data.get("change", 0)
            pct = (change / data["close"] * 100) if data["close"] else 0
            print(f"  {name}: {data['price']:.3f} ({pct:+.2f}%)")
    
    print("\n🌏 港股:")
    for code, name in [("00700", "腾讯"), ("09988", "阿里")]:
        data = get_hk_stock(code)
        if data:
            print(f"  {name}: ${data['price']:.2f}")
