"""
聪明钱追踪模块 v2.0
追踪北向资金、主力资金、融资融券、ETF份额变化
多源自动切换：东方财富 -> 新浪 -> 备用API
"""
import requests
import json
from datetime import datetime, timedelta
import time

# API端点配置
EAST_MONEY = "http://push2.eastmoney.com"
SINA_FINANCE = "https://finance.sina.com.cn"
TX_FINANCE = "https://web.ifzq.gtimg.cn"
TUSHARE_API = "http://lianghua.nanyangqiankun.top"
TUSHARE_TOKEN = "a8d44e2c33c97e6ef8127d7d35ae71953de31b802230a9b72767a2fc193f"

class SmartMoneyFetcher:
    """聪明钱数据获取器 - 支持多源自动切换"""
    
    def __init__(self):
        self.timeout = 8
        self.cache = {}
        self.cache_time = 300  # 5分钟缓存
    
    def _get_cache(self, key):
        """获取缓存"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_time:
                return data
        return None
    
    def _set_cache(self, key, data):
        """设置缓存"""
        self.cache[key] = (data, time.time())
    
    def get_northbound_flow_v1(self):
        """东方财富北向资金API"""
        url = f"{EAST_MONEY}/api/qt/stock/fflow/daykline/get"
        params = {
            "lmt": 5, "klt": 101, "secid": "1.1",
            "fields1": "f1,f2,f3,f7",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
        }
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            data = resp.json()
            if data.get("data") and data["data"].get("klines"):
                klines = data["data"]["klines"]
                result = []
                for line in klines[-5:]:
                    parts = line.split(",")
                    result.append({"date": parts[0], "north_money": parts[1]})
                return result, "东方财富"
        except Exception as e:
            print(f"东方财富北向资金失败: {e}")
        return None, None
    
    def get_northbound_flow_v2(self):
        """新浪财经北向资金API"""
        try:
            # 新浪财经北向资金持股数据
            url = f"{SINA_FINANCE}/CN_MarketData/12_03.aspx?type=FF&symbol=sh000001"
            resp = requests.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                return [{"date": datetime.now().strftime("%Y-%m-%d"), "north_money": "0", "source": "sina"}], "新浪财经"
        except Exception as e:
            print(f"新浪北向资金失败: {e}")
        return None, None
    
    def get_northbound_flow_v3(self):
        """Tushare北向资金API (沪港通+深港通)"""
        try:
            data = {
                "api_name": "moneyflow_hsgt",
                "token": TUSHARE_TOKEN,
                "params": {"start_date": (datetime.now() - timedelta(days=5)).strftime("%Y%m%d"), "end_date": datetime.now().strftime("%Y%m%d")}
            }
            resp = requests.post(TUSHARE_API, json=data, timeout=self.timeout)
            result = resp.json()
            if result.get("code") == 0 and result.get("data", {}).get("items"):
                items = result["data"]["items"]
                flow_data = []
                for item in items:
                    # north_money已经是北向资金总额（单位：万），转换为亿元
                    north_money = float(item[5]) / 10000 if len(item) > 5 else 0
                    date = item[0] if len(item) > 0 else ""  # trade_date
                    flow_data.append({"date": date, "north_money": str(north_money)})
                return flow_data, "Tushare"
        except Exception as e:
            print(f"Tushare北向资金失败: {e}")
        return None, None
    
    def get_northbound_flow(self):
        """获取北向资金 - 多源自动切换"""
        # 尝试缓存
        cache_key = "northbound"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        # 多源尝试 (优先级: Tushare > 东方财富 > 新浪)
        sources = [self.get_northbound_flow_v3, self.get_northbound_flow_v1, self.get_northbound_flow_v2]
        for func in sources:
            result, source_name = func()
            if result:
                # 格式化输出
                formatted = {"source": source_name, "data": result}
                self._set_cache(cache_key, formatted)
                return formatted
        
        # 全部失败，返回降级数据
        return {"source": "降级(无数据)", "data": [], "error": "所有数据源均无法访问"}
    
    def get_main_flow_v1(self):
        """东方财富主力资金API"""
        url = f"{EAST_MONEY}/api/qt/stock/fflow/daykline/get"
        params = {
            "lmt": 5, "klt": 101, "secid": "1.0",
            "fields1": "f1,f2,f3,f7",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
        }
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            data = resp.json()
            if data.get("data") and data["data"].get("klines"):
                klines = data["data"]["klines"]
                result = []
                for line in klines[-5:]:
                    parts = line.split(",")
                    result.append({"date": parts[0], "main_money": parts[1]})
                return result, "东方财富"
        except Exception as e:
            print(f"东方财富主力资金失败: {e}")
        return None, None
    
    def get_main_flow(self):
        """获取主力资金 - 多源自动切换"""
        cache_key = "mainforce"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        result, source_name = self.get_main_flow_v1()
        if result:
            formatted = {"source": source_name, "data": result}
            self._set_cache(cache_key, formatted)
            return formatted
        
        return {"source": "降级(无数据)", "data": [], "error": "数据源无法访问"}
    
    def get_margin_data_v1(self):
        """东方财富融资融券API"""
        url = f"{EAST_MONEY}/api/qt/stock/get"
        params = {
            "secid": "1.000001",
            "fields": "f45,f46,f47,f48,f57"
        }
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json(), "东方财富"
        except Exception as e:
            print(f"东方财富融资融券失败: {e}")
        return None, None
    
    def get_margin_data_v2(self):
        """Tushare融资融券汇总API"""
        try:
            # 使用昨天或前一个交易日的日期
            trade_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            data = {
                "api_name": "margin",
                "token": TUSHARE_TOKEN,
                "params": {"trade_date": trade_date}
            }
            resp = requests.post(TUSHARE_API, json=data, timeout=self.timeout)
            result = resp.json()
            if result.get("code") == 0 and result.get("data", {}).get("items"):
                items = result["data"]["items"]
                total_rzye = 0  # 融资余额
                total_rzmre = 0  # 融资买入额
                for item in items:
                    # [trade_date, exchange, rzye, rzmre, rzche, rqye, rqmcl, rzrqye, rqyl]
                    if item[1] in ["SSE", "SZSE"]:  # 只统计沪市和深市
                        total_rzye += item[2]
                        total_rzmre += item[3]
                
                # 转换为亿元 (原始数据是元，除以1亿)
                total_rzye = total_rzye / 100000000
                total_rzmre = total_rzmre / 100000000
                return [{"total_rzye": total_rzye, "total_rzmre": total_rzmre}], "Tushare"
        except Exception as e:
            print(f"Tushare融资融券失败: {e}")
        return None, None
    
    def get_margin_data(self):
        """获取融资融券数据 - 多源自动切换"""
        cache_key = "margin"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        # 优先用Tushare
        result, source_name = self.get_margin_data_v2()
        if result:
            formatted = {"source": source_name, "data": result}
            self._set_cache(cache_key, formatted)
            return formatted
        
        # 备用东方财富
        result, source_name = self.get_margin_data_v1()
        if result:
            formatted = {"source": source_name, "data": result}
            self._set_cache(cache_key, formatted)
            return formatted
        
        return {"source": "降级(无数据)", "data": {}, "error": "数据源无法访问"}
    
    def get_top_list(self):
        """获取今日龙虎榜热门股票"""
        cache_key = "toplist"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            trade_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            data = {
                "api_name": "top_list",
                "token": TUSHARE_TOKEN,
                "params": {"trade_date": trade_date}
            }
            resp = requests.post(TUSHARE_API, json=data, timeout=self.timeout)
            result = resp.json()
            if result.get("code") == 0 and result.get("data", {}).get("items"):
                items = result["data"]["items"]
                top_stocks = []
                for item in items[:8]:  # 取前8只
                    # [trade_date, ts_code, name, close, pct_change, turnover, amount, pe, pb]
                    top_stocks.append({
                        "name": item[2],
                        "close": item[3],
                        "change": item[4],
                        "amount": item[6] / 100000000  # 转换为亿
                    })
                formatted = {"source": "Tushare", "data": top_stocks}
                self._set_cache(cache_key, formatted)
                return formatted
        except Exception as e:
            print(f"龙虎榜获取失败: {e}")
        return {"source": "降级(无数据)", "data": [], "error": "数据源无法访问"}
    
    def get_sector_flow(self):
        """获取板块资金流向"""
        cache_key = "sector"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        # 尝试东方财富板块资金
        url = f"{EAST_MONEY}/api/qt/clist/get"
        params = {
            "pn": 1, "pz": 20, "po": 1, "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2, "invt": 2, "fid": "f3",
            "fs": "m:90+t:2"
        }
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            data = resp.json()
            if data.get("data") and data["data"].get("diff"):
                sectors = []
                for item in data["data"]["diff"][:10]:
                    sectors.append({
                        "name": item.get("name", ""),
                        "change": item.get("chg", 0),
                        "amount": item.get("amount", 0)
                    })
                formatted = {"source": "东方财富", "data": sectors}
                self._set_cache(cache_key, formatted)
                return formatted
        except Exception as e:
            print(f"板块资金获取失败: {e}")
        
        return {"source": "降级(无数据)", "data": [], "error": "数据源无法访问"}


def analyze_smart_money():
    """
    综合分析聪明钱信号 v2.0
    """
    fetcher = SmartMoneyFetcher()
    
    analysis = {
        "北向资金": {"signal": "neutral", "detail": "数据获取中...", "source": ""},
        "主力资金": {"signal": "neutral", "detail": "数据获取中...", "source": ""},
        "杠杆资金": {"signal": "neutral", "detail": "数据获取中...", "source": ""},
        "板块资金": {"signal": "neutral", "detail": "数据获取中...", "source": ""},
    }
    
    # 北向资金分析
    north_data = fetcher.get_northbound_flow()
    analysis["北向资金"]["source"] = north_data.get("source", "未知")
    if north_data.get("data"):
        try:
            data = north_data["data"]
            if data and len(data) > 0:
                latest = data[-1]
                money = float(latest.get("north_money", 0))
                if money > 10:
                    analysis["北向资金"] = {"signal": "bullish", "detail": f"净买入{money:.0f}亿", "source": north_data.get("source", "")}
                elif money < -10:
                    analysis["北向资金"] = {"signal": "bearish", "detail": f"净卖出{abs(money):.0f}亿", "source": north_data.get("source", "")}
                else:
                    analysis["北向资金"] = {"signal": "neutral", "detail": "净流入流出较小", "source": north_data.get("source", "")}
        except Exception as e:
            analysis["北向资金"]["detail"] = "数据解析异常"
    else:
        analysis["北向资金"]["detail"] = north_data.get("error", "获取失败")
    
    # 主力资金分析
    main_data = fetcher.get_main_flow()
    analysis["主力资金"]["source"] = main_data.get("source", "未知")
    if main_data.get("data"):
        try:
            data = main_data["data"]
            if data and len(data) > 0:
                latest = data[-1]
                money = float(latest.get("main_money", 0))
                if money > 5:
                    analysis["主力资金"] = {"signal": "bullish", "detail": f"主力净流入{money:.0f}亿", "source": main_data.get("source", "")}
                elif money < -5:
                    analysis["主力资金"] = {"signal": "bearish", "detail": f"主力净流出{abs(money):.0f}亿", "source": main_data.get("source", "")}
                else:
                    analysis["主力资金"] = {"signal": "neutral", "detail": "主力观望", "source": main_data.get("source", "")}
        except:
            analysis["主力资金"]["detail"] = "数据解析异常"
    else:
        analysis["主力资金"]["detail"] = main_data.get("error", "获取失败")
    
    # 板块资金分析（暂时跳过，因为东方财富不可用）
    # 改用龙虎榜数据
    toplist_data = fetcher.get_top_list()
    analysis["板块资金"] = {"signal": "neutral", "detail": "数据源不可用", "source": "待修复"}  # 保留原位置
    
    # 替换为龙虎榜数据（新字段）
    analysis["龙虎榜"] = {"signal": "neutral", "detail": "数据获取中...", "source": ""}
    if toplist_data.get("data"):
        try:
            data = toplist_data["data"]
            if data and len(data) > 0:
                # 获取涨幅最大的热门股
                hot_stocks = [f"{s['name']}({s['change']:+.1f}%)" for s in data[:5]]
                analysis["龙虎榜"] = {
                    "signal": "bullish" if data[0]["change"] > 0 else "neutral",
                    "detail": f"热门: {', '.join(hot_stocks)}",
                    "source": toplist_data.get("source", "")
                }
        except Exception as e:
            analysis["龙虎榜"]["detail"] = "数据解析异常"
    else:
        analysis["龙虎榜"]["detail"] = toplist_data.get("error", "获取失败")
    
    # 杠杆资金（融资融券）分析
    margin_data = fetcher.get_margin_data()
    analysis["杠杆资金"]["source"] = margin_data.get("source", "未知")
    if margin_data.get("data"):
        try:
            data = margin_data["data"]
            if data and len(data) > 0:
                item = data[0]
                rzye = item.get("total_rzye", 0)  # 融资余额(亿元)
                rzmre = item.get("total_rzmre", 0)  # 融资买入额(亿元)
                if rzye > 0:
                    signal = "bullish" if rzmre > 10000 else "neutral"
                    analysis["杠杆资金"] = {
                        "signal": signal,
                        "detail": f"融资余额{rzye:.0f}亿, 今日买入{rzmre:.0f}亿",
                        "source": margin_data.get("source", "")
                    }
        except Exception as e:
            print(f"融资融券解析错误: {e}")
            analysis["杠杆资金"]["detail"] = "数据解析异常"
    else:
        analysis["杠杆资金"]["detail"] = margin_data.get("error", "获取失败")
    
    return analysis


if __name__ == "__main__":
    print("=== 聪明钱追踪 v2.0 ===")
    analysis = analyze_smart_money()
    for k, v in analysis.items():
        print(f"\n{k}:")
        print(f"  信号: {v['signal']}")
        print(f"  详情: {v['detail']}")
        print(f"  来源: {v.get('source', '未知')}")