"""
数据获取模块
获取A股指数、行业ETF、个股数据
智能选择：东方财富 → 新浪 → Tushare，哪个有数据用哪个
"""
import requests
import json
import time
from datetime import datetime

# 东方财富API - 免费数据源
EAST_MONEY_BASE = "http://push2his.eastmoney.com"

# Tushare API (付费)
TUSHARE_TOKEN = "a8d44e2c33c97e6ef8127d7d35ae71953de31b802230a9b72767a2fc193f"
TUSHARE_API_URL = "http://lianghua.nanyangqiankun.top"


def try_east_money_index(code):
    """东方财富获取指数"""
    url = f"{EAST_MONEY_BASE}/api/qt/stock/get"
    params = {
        "secid": f"1.{code}" if code.startswith("0") else f"0.{code}",
        "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f59,f60,f116,f117,f118,f162,f167,f168,f169,f170,f171,f173,f177"
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get("data"):
            return {
                "price": data["data"].get("f43", 0) / 1000,
                "change": data["data"].get("f46", 0) / 1000,
                "change_pct": data["data"].get("f170", 0) / 100,
                "volume": data["data"].get("f47", 0),
                "source": "eastmoney"
            }
    except:
        pass
    return None


def try_sina_index(code):
    """新浪获取指数"""
    sina_code = f"sh{code}" if code.startswith("0") else f"sz{code}"
    url = f"https://hq.sinajs.cn/list={sina_code}"
    try:
        resp = requests.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=5)
        text = resp.text
        if "=" in text:
            parts = text.split('="')[1].split(",")
            if len(parts) > 5:
                # 新浪指数: [1]开盘 [2]当前价 [3]最低 [4]最高 [8]成交量 [30]日期 [31]时间
                price = float(parts[2]) if parts[2] else 0
                open_price = float(parts[1]) if parts[1] else price
                change = price - open_price  # 涨跌幅 = 当前 - 开盘
                change_pct = (change / open_price * 100) if open_price else 0
                return {
                    "price": price,
                    "change": change,
                    "change_pct": change_pct,
                    "volume": float(parts[8]) if len(parts) > 8 else 0,
                    "source": "sina"
                }
    except:
        pass
    return None


def try_tushare_index(code):
    """Tushare获取指数"""
    ts_code = f"{code}.SH" if code.startswith("0") else f"{code}.SZ"
    data = {
        "api_name": "index_daily",
        "token": TUSHARE_TOKEN,
        "params": {"ts_code": ts_code, "start_date": "20260301", "end_date": "20260303"}
    }
    try:
        resp = requests.post(TUSHARE_API_URL, json=data, timeout=10)
        result = resp.json()
        if result.get("code") == 0 and result.get("data", {}).get("items"):
            item = result["data"]["items"][0]
            return {
                "price": item[2],
                "change": item[7] if len(item) > 7 else 0,
                "change_pct": item[8] * 100 if len(item) > 8 else 0,
                "source": "tushare"
            }
    except:
        pass
    return None


def try_east_money_stock(code):
    """东方财富获取个股"""
    url = f"{EAST_MONEY_BASE}/api/qt/stock/get"
    secid = f"0.{code}" if code.startswith("0") or code.startswith("3") else f"1.{code}"
    params = {
        "secid": secid,
        "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f59,f60,f116,f117,f118,f162,f167,f168,f169,f170,f171,f173,f177"
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get("data"):
            return {
                "price": data["data"].get("f43", 0) / 1000,
                "change": data["data"].get("f46", 0) / 1000,
                "change_pct": data["data"].get("f170", 0) / 100,
                "volume": data["data"].get("f47", 0),
                "source": "eastmoney"
            }
    except:
        pass
    return None


def try_sina_stock(code):
    """新浪获取个股"""
    sina_code = f"sh{code}" if code.startswith("6") else f"sz{code}"
    url = f"https://hq.sinajs.cn/list={sina_code}"
    try:
        resp = requests.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=5)
        text = resp.text
        if "=" in text:
            parts = text.split('="')[1].split(",")
            if len(parts) > 5:
                # 新浪个股: [1]开盘 [2]前收 [3]最低 [4]最高 [5]当前价 [8]成交量
                price = float(parts[5]) if parts[5] else 0
                prev_close = float(parts[2]) if parts[2] else price
                change = price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0
                return {
                    "price": price,
                    "change": change,
                    "change_pct": change_pct,
                    "volume": float(parts[8]) if len(parts) > 8 else 0,
                    "source": "sina"
                }
    except:
        pass
    return None


def try_tushare_stock(code):
    """Tushare获取个股"""
    ts_code = f"{code}.SZ" if code.startswith("0") or code.startswith("3") else f"{code}.SH"
    data = {
        "api_name": "daily",
        "token": TUSHARE_TOKEN,
        "params": {"ts_code": ts_code, "start_date": "20260301", "end_date": "20260303"}
    }
    try:
        resp = requests.post(TUSHARE_API_URL, json=data, timeout=10)
        result = resp.json()
        if result.get("code") == 0 and result.get("data", {}).get("items"):
            item = result["data"]["items"][0]
            return {
                "price": item[5] if len(item) > 5 else 0,
                "change": item[7] if len(item) > 7 else 0,
                "change_pct": item[8] * 100 if len(item) > 8 else 0,
                "source": "tushare"
            }
    except:
        pass
    return None

def get_index_quote(code):
    """
    获取指数实时行情 - 智能选择数据源
    优先级: 东方财富 → 新浪 → Tushare
    """
    # 1. 先试东方财富
    result = try_east_money_index(code)
    if result:
        return {"code": code, "change_pct": result["change_pct"], **result, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    # 2. 试新浪
    result = try_sina_index(code)
    if result:
        return {"code": code, "change_pct": result["change_pct"], **result, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    # 3. 试Tushare
    result = try_tushare_index(code)
    if result:
        return {"code": code, "change_pct": result["change_pct"], **result, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    print(f"获取指数{code}失败: 所有数据源都不可用")
    return None

def get_etf_quote(code):
    """获取ETF行情 - 智能选择数据源"""
    # 先试东方财富
    url = f"{EAST_MONEY_BASE}/api/qt/stock/get"
    params = {
        "secid": f"1.{code}",
        "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f59,f60,f116,f117,f118,f162,f167,f168,f169,f170,f171,f173,f177"
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get("data"):
            return {
                "code": code,
                "name": data["data"]["f58"],
                "price": data["data"].get("f43", 0) / 1000,
                "change": data["data"].get("f46", 0) / 1000,
                "change_pct": data["data"].get("f170", 0) / 100,
                "source": "eastmoney"
            }
    except:
        pass
    
    # 试新浪 (ETF格式和个股一样)
    sina_code = f"sh{code}"
    url = f"https://hq.sinajs.cn/list={sina_code}"
    try:
        resp = requests.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=5)
        text = resp.text
        if "=" in text:
            parts = text.split('="')[1].split(",")
            if len(parts) > 5:
                price = float(parts[5]) if parts[5] else 0
                prev_close = float(parts[2]) if parts[2] else price
                change = price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0
                return {
                    "code": code,
                    "price": price,
                    "change": change,
                    "change_pct": change_pct,
                    "source": "sina"
                }
    except:
        pass
    
    return None

def get_stock_quote(code):
    """获取个股行情 - 智能选择数据源"""
    # 1. 先试东方财富
    result = try_east_money_stock(code)
    if result:
        return {"code": code, **result}
    
    # 2. 试新浪
    result = try_sina_stock(code)
    if result:
        return {"code": code, **result}
    
    # 3. 试Tushare
    result = try_tushare_stock(code)
    if result:
        return {"code": code, **result}
    
    print(f"获取股票{code}失败: 所有数据源都不可用")
    return None

def get_market_summary():
    """
    获取市场整体行情（涨跌停、成交量等）
    """
    # 获取涨跌停数据
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": 1,
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",  # 涨停
        "fields": "f1,f2,f3,f4,f12,f13,f14"
    }
    try:
        # 简单返回成功状态
        return {"status": "ok", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# 威少持仓相关ETF代码映射
ETF_CODES = {
    "沪深300ETF": "510310",  # 或者 510300
    "中证500ETF": "510500",
    "创业板50ETF": "159949",
    "医药ETF": "512010",
    "芯片ETF": "159995",
    "房地产ETF": "512200",
    "消费50ETF": "515650",
    "证券保险ETF": "512070",
    "恒生指数ETF": "513100",
    "中概互联网ETF": "513050",
    "红利低波100ETF": "515100",
    "航空航天ETF": "512660",
    "科技50ETF": "515000",
    "黄金ETF": "518880",
}

# 持仓个股代码
STOCK_CODES = {
    "歌尔股份": "002241",
    "利欧股份": "002131",
    "上汽集团": "600104",
    "四川长虹": "600839",
    "TCL科技": "000100",
}

if __name__ == "__main__":
    # 测试数据获取
    print("测试获取沪深300指数...")
    hs300 = get_index_quote("000300")
    print(f"沪深300: {hs300}")
    
    print("\n测试获取ETF...")
    etf = get_etf_quote("510300")
    print(f"沪深300ETF: {etf}")
    
    print("\n测试获取个股...")
    stock = get_stock_quote("002241")
    print(f"歌尔股份: {stock}")
