"""
智能数据获取器 v2.0
自动尝试多个API源，获取可用数据
"""
import requests
import json
from datetime import datetime, timedelta

# === Tushare Pro (付费版) ===
TUShare_TOKEN = "a8d44e2c33c97e6ef8127d7d35ae71953de31b802230a9b72767a2fc193f"
TUSHARE_URL = "http://lianghua.nanyangqiankun.top"

def tushare_request(api_name, params=None, fields=None):
    url = TUSHARE_URL
    data = {
        "api_name": api_name,
        "token": TUShare_TOKEN,
        "params": params or {},
        "fields": fields or ""
    }
    try:
        resp = requests.post(url, json=data, timeout=15)
        result = resp.json()
        if result.get("code") == 0:
            return result.get("data", {})
    except:
        pass
    return None

def get_tushare_daily(ts_code):
    """获取日线行情"""
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    data = tushare_request("daily", {"ts_code": ts_code, "start_date": start, "end_date": end})
    if data and data.get("items"):
        item = data["items"][0]
        return {
            "price": item[5],  # close
            "open": item[2],
            "high": item[3],
            "low": item[4],
            "volume": item[6],
            "date": item[1]
        }
    return None

# === 新浪财经 ===
def get_sina_index(code):
    url = f"https://hq.sinajs.cn/list=s_{code}"
    headers = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        content = resp.text
        if "hq_str" in content:
            data = content.split('="')[1].rstrip('";').split(",")
            return {"price": float(data[1]), "change": float(data[2]), "change_pct": float(data[3])}
    except:
        pass
    return None

def get_sina_hk(code):
    url = f"https://hq.sinajs.cn/list=hk{code}"
    headers = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        content = resp.text
        if "hq_str" in content:
            data = content.split('="')[1].rstrip('";').split(",")
            return {"name": data[1], "price": float(data[6])}
    except:
        pass
    return None

# === 智能获取器 ===
class SmartFetcher:
    """智能数据获取器"""
    
    def __init__(self):
        pass
    
    def get_index(self, code):
        """获取指数 - 优先Tushare，备选新浪"""
        # 尝试Tushare
        if code == "000300.SH" or code == "000001.SH" or code == "399006.SZ":
            ts_code = code
            result = get_tushare_daily(ts_code)
            if result:
                result["source"] = "Tushare"
                return result
        
        # 备选新浪
        sina_code = {"000300.SH": "sh000300", "000001.SH": "sh000001", "399006.SZ": "sz399006"}.get(code)
        if sina_code:
            result = get_sina_index(sina_code)
            if result:
                result["source"] = "新浪"
                return result
        
        return {"error": "获取失败"}
    
    def get_stock(self, code):
        """获取个股/ETF - Tushare"""
        # 转换代码格式
        ts_code = code
        if not code.endswith(".SH") and not code.endswith(".SZ"):
            if code.startswith("6"):
                ts_code = f"{code}.SH"
            else:
                ts_code = f"{code}.SZ"
        
        result = get_tushare_daily(ts_code)
        if result:
            result["source"] = "Tushare"
            return result
        
        return {"error": "获取失败"}
    
    def get_hk_stock(self, code):
        """获取港股 - 新浪"""
        result = get_sina_hk(code)
        if result:
            result["source"] = "新浪港股"
            return result
        return {"error": "获取失败"}

# 测试
if __name__ == "__main__":
    f = SmartFetcher()
    
    print("=== 智能数据获取 v2.0 ===\n")
    
    print("📈 指数:")
    for code, name in [("000300.SH", "沪深300"), ("000001.SH", "上证"), ("399006.SZ", "创业板")]:
        r = f.get_index(code)
        if "error" not in r:
            print(f"  ✅ {name}: {r['price']} [{r['source']}]")
    
    print("\n📊 A股/ETF:")
    for code, name in [("002241", "歌尔股份"), ("510310", "沪深300ETF"), ("600104", "上汽集团")]:
        r = f.get_stock(code)
        if "error" not in r:
            print(f"  ✅ {name}: ¥{r['price']:.2f} [{r['source']}]")
    
    print("\n🌏 港股:")
    for code, name in [("00700", "腾讯"), ("09988", "阿里")]:
        r = f.get_hk_stock(code)
        if "error" not in r:
            print(f"  ✅ {name}: ${r['price']} [{r['source']}]")
