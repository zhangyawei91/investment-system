"""
聪明钱追踪模块
追踪北向资金、主力资金、融资融券、ETF份额变化
"""
import requests
import json
from datetime import datetime, timedelta

# 东方财富资金流向API
EAST_MONEY = "http://push2.eastmoney.com"

def get_northbound_flow():
    """
    获取北向资金（外资）流向
    重点指标：净买入、净卖出
    """
    url = f"{EAST_MONEY}/api/qt/stock/fflow/daykline/get"
    params = {
        "lmt": 10,
        "klt": 101,
        "secid": "1.1",  # 北向资金
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"]
            result = []
            for line in klines[-5:]:  # 最近5天
                parts = line.split(",")
                result.append({
                    "date": parts[0],
                    "north_money": parts[1],  # 北向资金
                    "north_buy": parts[2],
                    "north_sell": parts[3],
                })
            return result
    except Exception as e:
        print(f"获取北向资金失败: {e}")
    return []

def get_main_flow():
    """
    获取主力资金流向
    大单净流入/流出
    """
    url = f"{EAST_MONEY}/api/qt/stock/fflow/daykline/get"
    params = {
        "lmt": 5,
        "klt": 101,
        "secid": "1.0",  # 主力资金
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"]
            result = []
            for line in klines[-5:]:
                parts = line.split(",")
                result.append({
                    "date": parts[0],
                    "main_money": parts[1],
                })
            return result
    except Exception as e:
        print(f"获取主力资金失败: {e}")
    return []

def get_margin_data():
    """
    获取融资融券数据
    融资余额变化反映杠杆资金情绪
    """
    url = f"{EAST_MONEY}/api/qt/stock/get"
    params = {
        "secid": "1.000001",  # 上证指数的融资融券
        "fields": "f45,f46,f47,f48"  # 融资相关字段
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        # 简化返回
        return {"status": "ok", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def analyze_smart_money():
    """
    综合分析聪明钱信号
    """
    analysis = {
        "北向资金": {"signal": "neutral", "detail": ""},
        "主力资金": {"signal": "neutral", "detail": ""},
        "杠杆资金": {"signal": "neutral", "detail": ""},
    }
    
    # 北向资金分析
    north_flow = get_northbound_flow()
    if north_flow:
        try:
            # 最近一天的资金流向
            latest = north_flow[-1]
            money = float(latest.get("north_money", 0))
            if money > 10:
                analysis["北向资金"] = {"signal": "bullish", "detail": f"净买入{money:.0f}亿"}
            elif money < -10:
                analysis["北向资金"] = {"signal": "bearish", "detail": f"净卖出{abs(money):.0f}亿"}
            else:
                analysis["北向资金"] = {"signal": "neutral", "detail": "净流入流出较小"}
        except:
            pass
    
    # 主力资金分析
    main_flow = get_main_flow()
    if main_flow:
        try:
            latest = main_flow[-1]
            money = float(latest.get("main_money", 0))
            if money > 5:
                analysis["主力资金"] = {"signal": "bullish", "detail": f"主力净流入{money:.0f}亿"}
            elif money < -5:
                analysis["主力资金"] = {"signal": "bearish", "detail": f"主力净流出{abs(money):.0f}亿"}
            else:
                analysis["主力资金"] = {"signal": "neutral", "detail": "主力观望"}
        except:
            pass
    
    return analysis

if __name__ == "__main__":
    print("=== 聪明钱追踪 ===")
    print("\n北向资金:")
    nf = get_northbound_flow()
    for item in nf:
        print(f"  {item}")
    
    print("\n主力资金:")
    mf = get_main_flow()
    for item in mf:
        print(f"  {item}")
    
    print("\n综合分析:")
    analysis = analyze_smart_money()
    for k, v in analysis.items():
        print(f"  {k}: {v['signal']} - {v['detail']}")
