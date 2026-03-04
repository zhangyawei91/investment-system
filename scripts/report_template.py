#!/usr/bin/env python3
"""
投资报告格式化模板
统一每日简报格式
"""
from datetime import datetime

# 统一的简报格式 v2.0 - 包含聪明钱分析
REPORT_TEMPLATE = """
📊 威少投资每日简报 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {date} {time}

📈 【大盘行情】
{indices}

💰 【聪明钱分析】⭐
{smart_money}

🔍 【持仓分析】
{holdings}

💡 【操作建议】
{suggestion}

⚠️ 【风险提示】
{risk}

━━━━━━━━━━━━━━━━━━━━━━━━━━
🦐 威少投资智脑 v3.0
"""


def format_report(indices_data, holdings_data, suggestions, smart_money_data=None):
    """
    格式化统一报告
    
    indices_data: dict - 指数数据 {name: {price, change_pct}}
    holdings_data: list - 持仓数据 [{name, price, change_pct, advice}]
    suggestions: dict - 建议 {action: items}
    smart_money_data: dict - 聪明钱数据
    """
    # 格式化指数
    indices_str = ""
    for name, info in indices_data.items():
        trend = "📈" if info.get("change_pct", 0) >= 0 else "📉"
        indices_str += f"  {trend} {name}: {info.get('price', 0):.2f} ({info.get('change_pct', 0):+.2f}%)\n"
    
    if not indices_str:
        indices_str = "  数据获取中...\n"
    
    # 格式化聪明钱
    if smart_money_data:
        sm = smart_money_data
        
        # 北向资金
        nb = sm.get("北向资金", {})
        northbound = f"  📈 北向资金: {nb.get('daily_net_buy', 'N/A')}亿 {nb.get('signal_level', '')}"
        
        # 主力资金
        mf = sm.get("主力资金", {})
        mainforce = f"  🏦 主力资金: {mf.get('large_order_net', 'N/A')}亿 {mf.get('signal_level', '')}"
        
        # 融资融券
        mg = sm.get("融资融券", {})
        margin = f"  💳 融资融券: {mg.get('margin_balance', 'N/A')}亿 {mg.get('signal_level', '')}"
        
        # ETF资金
        etf = sm.get("ETF资金", {})
        etf_flow = f"  📊 ETF资金: {etf.get('etf_share_change', 'N/A')}% {etf.get('signal_level', '')}"
        
        smart_money_str = f"{northbound}\n{mainforce}\n{margin}\n{etf_flow}"
    else:
        smart_money_str = "  数据获取中...\n"
    
    # 格式化持仓
    holdings_str = ""
    for h in holdings_data:
        trend = "📈" if h.get("change_pct", 0) >= 0 else "📉"
        holdings_str += f"  • {h.get('name', '')} ¥{h.get('price', 0):.2f} ({h.get('change_pct', 0):+.2f}%)\n"
    
    if not holdings_str:
        holdings_str = "  数据获取中...\n"
    
    # 格式化建议
    suggestions_str = ""
    if suggestions.get("清仓"):
        suggestions_str += f"  🛑 清仓: {', '.join(suggestions['清仓'])}\n"
    if suggestions.get("减仓"):
        suggestions_str += f"  📉 减仓: {', '.join(suggestions['减仓'])}\n"
    if suggestions.get("持有"):
        suggestions_str += f"  ✅ 持有: {', '.join(suggestions['持有'])}\n"
    
    if not suggestions_str:
        suggestions_str = "  暂无\n"
    
    # 格式化风险
    risk_str = "  • 亏损超20%需重点关注\n  • 保持ETF仓位70%+\n  • 主力资金流出时谨慎加仓\n"
    
    # 渲染模板
    report = REPORT_TEMPLATE.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        time=datetime.now().strftime("%H:%M"),
        indices=indices_str,
        smart_money=smart_money_str,
        holdings=holdings_str,
        suggestion=suggestions_str,
        risk=risk_str
    )
    
    return report


def get_sample_data():
    """测试数据"""
    return {
        "indices": {
            "沪深300": {"price": 4728.67, "change_pct": -0.18},
            "上证指数": {"price": 4182.59, "change_pct": -0.16},
            "创业板": {"price": 3294.16, "change_pct": -0.68},
        },
        "holdings": [
            {"name": "歌尔股份", "price": 25.71, "change_pct": -2.76},
            {"name": "利欧股份", "price": 8.30, "change_pct": -8.89},
            {"name": "上汽集团", "price": 14.16, "change_pct": -0.84},
            {"name": "四川长虹", "price": 9.90, "change_pct": -2.37},
            {"name": "TCL科技", "price": 4.80, "change_pct": -3.03},
        ],
        "suggestions": {
            "清仓": ["顺利3(退市风险)"],
            "减仓": ["芯片ETF"],
            "持有": ["歌尔股份", "沪深300ETF"],
        }
    }


if __name__ == "__main__":
    # 测试
    data = get_sample_data()
    print(format_report(
        indices_data=data["indices"],
        holdings_data=data["holdings"],
        suggestions=data["suggestions"]
    ))