"""
飞书消息通知模块
用于发送每日投资报告、风险提醒到飞书
"""
import json
from datetime import datetime

# 注意：这里使用OpenClaw内置的message工具发送飞书消息
# 无需额外配置飞书API

def format_daily_report(data):
    """
    格式化每日报告
    data: 包含盘面、行业、资金等数据的字典
    """
    report = f"""
📊 威少投资每日简报
更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{'='*40}
📈 盘面概览
{'='*40}
"""
    
    if "indices" in data:
        for name, info in data["indices"].items():
            trend = "📈" if info.get("change_pct", 0) > 0 else "📉"
            report += f"{trend} {name}: {info.get('price', 0):.2f} ({info.get('change_pct', 0):+.2f}%)\n"
    
    report += f"""
{'='*40}
💰 聪明钱动向
{'='*40}
"""
    
    if "smart_money" in data:
        for name, info in data["smart_money"].items():
            signal = info.get("signal", "neutral")
            emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(signal, "⚪")
            report += f"{emoji} {name}: {info.get('detail', '')}\n"
    
    report += f"""
{'='*40}
📋 持仓提醒
{'='*40}
"""
    
    if "holdings_alert" in data:
        for alert in data["holdings_alert"]:
            report += f"⚠️ {alert}\n"
    
    report += f"""
{'='*40}
💡 今日建议
{'='*40}
{data.get('suggestion', '暂无')}
    
---
🦐 威少投资智脑
"""
    return report

def format_risk_alert(alert_type, details):
    """
    格式化风险提醒
    """
    emoji_map = {
        "止损": "🛑",
        "风险": "⚠️",
        "异动": "🔔",
    }
    
    return f"""
{emoji_map.get(alert_type, '⚠️')} 投资风险提醒

类型: {alert_type}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
详情: {details}

请及时查看并处理！
---
🦐 威少投资智脑
"""

def create_report_message(report_data):
    """
    创建飞书消息卡片格式
    """
    # 构建消息内容
    elements = []
    
    # 盘面概览
    if "indices" in report_data:
        indices_text = ""
        for name, info in report_data["indices"].items():
            trend = "↑" if info.get("change_pct", 0) > 0 else "↓"
            indices_text += f"{name}: {info.get('price', 0):.2f} {trend}{abs(info.get('change_pct', 0)):.2f}%\n"
        
        elements.append({
            "tag": "div",
            "text": f"📈 盘面概览\n{indices_text}"
        })
    
    # 资金动向
    if "smart_money" in report_data:
        money_text = ""
        for name, info in report_data["smart_money"].items():
            emoji = "🟢" if info.get("signal") == "bullish" else "🔴" if info.get("signal") == "bearish" else "⚪"
            money_text += f"{emoji} {name}: {info.get('detail', '')}\n"
        
        elements.append({
            "tag": "div",
            "text": f"💰 资金动向\n{money_text}"
        })
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "elements": elements
    }

# 测试
if __name__ == "__main__":
    # 测试报告格式
    test_data = {
        "indices": {
            "沪深300": {"price": 4100.5, "change_pct": 0.85},
            "上证指数": {"price": 3250.3, "change_pct": 0.32},
        },
        "smart_money": {
            "北向资金": {"signal": "bullish", "detail": "净买入35亿"},
            "主力资金": {"signal": "neutral", "detail": "观望"},
        },
        "holdings_alert": ["歌尔股份涨超130%，可考虑部分止盈"],
        "suggestion": "市场情绪偏多，建议持有为主",
    }
    
    print(format_daily_report(test_data))
