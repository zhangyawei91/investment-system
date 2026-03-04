"""
威少投资每日报告生成器
整合多维表数据、技术分析、优化报告格式
"""
import requests
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加scripts路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from data_fetcher import get_index_quote, get_stock_quote
from technical_analysis import analyze_stock

# 威少持仓配置
HOLDINGS_CONFIG = {
    "歌尔股份": "002241",
    "利欧股份": "002131",
    "上汽集团": "600104",
    "四川长虹": "600839",
    "TCL科技": "000100",
    "沪深300ETF": "510300",
    "芯片ETF": "159995",
    "医药ETF": "512010",
    "恒生指数ETF": "513100",
}

# 多维表配置
BITABLE_CONFIG = {
    "app_token": "QxhTbLTqoa0xPusz3aFc2Fuanph",
    "holdings_table": "tblf0WV4yNd8xtnk",  # 持仓记录
    "market_table": "tblBaGcC3HidGSXY",   # 每日行情
    "fund_table": "tblbmDrhAUnT879b",      # 资金动向
}

def generate_report():
    """生成每日投资报告"""
    report = []
    report.append("=" * 50)
    report.append("📊 威少投资每日简报")
    report.append(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 50)
    
    # 1. 大盘行情
    report.append("\n📈 大盘行情")
    report.append("-" * 30)
    indices = [("000300", "沪深300"), ("000001", "上证指数"), ("399006", "创业板")]
    for code, name in indices:
        data = get_index_quote(code)
        if data:
            trend = "📈" if data["change_pct"] > 0 else "📉"
            report.append(f"{trend} {name}: {data['price']:.2f} ({data['change_pct']:+.2f}%)")
        else:
            report.append(f"  {name}: 数据获取失败")
    
    # 2. 持仓技术分析
    report.append("\n🔍 持仓技术分析")
    report.append("-" * 30)
    
    for name, code in HOLDINGS_CONFIG.items():
        result = analyze_stock(code, name)
        if "error" in result:
            report.append(f"  {name}: {result['error']}")
            continue
        
        report.append(f"\n  📊 {name} (¥{result['current_price']:.2f})")
        
        # 均线
        ma = result.get("ma", {})
        if ma:
            ma_info = f"MA5:{ma.get('ma5',0):.2f} MA10:{ma.get('ma10',0):.2f} MA20:{ma.get('ma20',0):.2f}"
            report.append(f"     均线: {ma_info}")
        
        # KDJ
        kdj = result.get("KDJ")
        if kdj:
            signal_emoji = "🔴" if kdj.get("signal") == "超买" else "🟢" if kdj.get("signal") == "超卖" else "⚪"
            report.append(f"     KDJ: K={kdj.get('K',0):.1f} D={kdj.get('D',0):.1f} J={kdj.get('J',0):.1f} {signal_emoji}{kdj.get('signal')}")
        
        # MACD
        macd = result.get("MACD")
        if macd:
            signal_emoji = "🔴" if "死叉" in macd.get("signal", "") else "🟢" if "金叉" in macd.get("signal", "") else "⚪"
            report.append(f"     MACD: DIF={macd.get('DIF',0):.3f} DEA={macd.get('DEA',0):.3f} {signal_emoji}{macd.get('signal')}")
        
        # 布林带
        boll = result.get("BOLL")
        if boll:
            report.append(f"     BOLL: {boll.get('position')} (中轨:{boll.get('MA',0):.2f})")
    
    # 3. 操作建议
    report.append("\n💡 操作建议")
    report.append("-" * 30)
    suggestions = [
        ("顺利3", "🛑 立即清仓", "退市风险"),
        ("芯片ETF", "⚠️ 建议减仓", "MACD死叉"),
        ("歌尔股份", "📊 继续持有", "KDJ正常，MACD死叉"),
        ("沪深300ETF", "✅ 持有", "趋势向好"),
    ]
    for name, action, reason in suggestions:
        report.append(f"  • {name}: {action} - {reason}")
    
    # 4. 风险提示
    report.append("\n⚠️ 风险提示")
    report.append("-" * 30)
    report.append("  • 亏损超过20%的标的需重点关注")
    report.append("  • 主力资金净流出时谨慎加仓")
    report.append("  • 保持ETF仓位在70%+")
    
    report.append("\n" + "=" * 50)
    report.append("🦐 威少投资智脑")
    
    return "\n".join(report)

if __name__ == "__main__":
    print(generate_report())
