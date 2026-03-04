#!/usr/bin/env python3
"""
财经新闻获取模块 v2.0
从东方财富获取实时财经新闻
"""
import requests
import json
from datetime import datetime


# 东方财富新闻接口
NEWS_URL = "http://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html"


def get_financial_news(count=8):
    """
    获取财经新闻
    
    Args:
        count: 获取新闻数量，默认8条
        
    Returns:
        list: 新闻列表 [{title, digest, time}]
    """
    try:
        resp = requests.get(NEWS_URL, timeout=10)
        text = resp.text
        
        # 解析 JSONP 响应
        if "ajaxResult" in text:
            json_str = text.replace("var ajaxResult=", "").strip()
            data = json.loads(json_str)
            
            if data.get("rc") == 1:  # 东方财富 RC=1 表示成功
                news_list = data.get("LivesList", [])
                result = []
                
                for item in news_list[:count]:
                    result.append({
                        "title": item.get("title", ""),
                        "digest": item.get("digest", "")[:50] + "..." if len(item.get("digest", "")) > 50 else item.get("digest", ""),
                        "time": item.get("showtime", ""),
                    })
                
                return result
    except Exception as e:
        print(f"获取新闻失败: {e}")
    
    return []


def format_news_for_report(news_list):
    """
    格式化新闻为简报格式
    """
    if not news_list:
        return "  暂无新闻"
    
    lines = []
    for i, news in enumerate(news_list, 1):
        # 过滤过于简短或无关的新闻
        title = news.get("title", "")
        if len(title) < 8:
            continue
            
        # 简化标题
        title = title[:35] + "..." if len(title) > 35 else title
        lines.append(f"  {i}. {title}")
    
    if not lines:
        return "  暂无重要新闻"
    
    return "\n".join(lines)


def get_market_summary():
    """
    获取市场整体情况（涨跌停、涨跌家数）
    """
    result = {}
    
    # 涨停家数
    try:
        url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("data", {}).get("total"):
            result["涨停"] = data["data"]["total"]
    except:
        pass
    
    # 跌停家数
    try:
        url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=0&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:7,m:0+t:81,m:1+t:3,m:1+t:24"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("data", {}).get("total"):
            result["跌停"] = data["data"]["total"]
    except:
        pass
    
    return result


if __name__ == "__main__":
    print("=" * 50)
    print("测试财经新闻获取")
    print("=" * 50)
    
    # 获取新闻
    news = get_financial_news(5)
    print("\n📰 财经要闻:")
    print(format_news_for_report(news))
    
    # 获取涨跌停
    print("\n📊 涨跌停:")
    summary = get_market_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}家")