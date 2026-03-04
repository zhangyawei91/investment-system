"""
威少投资智脑系统 - 主程序
每日定时运行，生成报告并通过飞书推送
"""
import sys
import os
import json
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def run_daily_check():
    """
    每日检查任务
    """
    print(f"\n{'='*50}")
    print(f"🕐 威少投资智脑 - 每日检查")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    # 1. 获取盘面数据
    print("📈 获取盘面数据...")
    from data_fetcher import get_index_quote, get_etf_quote
    
    indices_data = {}
    indices = [("000300", "沪深300"), ("000001", "上证指数"), ("399006", "创业板")]
    for code, name in indices:
        data = get_index_quote(code)
        if data:
            indices_data[name] = {
                "price": data.get("price", 0),
                "change_pct": data.get("change_pct", 0),
                "change": data.get("change", 0)
            }
            print(f"  {name}: {data.get('price', 0):.2f} ({data.get('change_pct', 0):+.2f}%)")
    
    # 2. 获取聪明钱数据
    print("\n💰 获取资金动向...")
    from smart_money import analyze_smart_money
    smart_money = analyze_smart_money()
    for name, info in smart_money.items():
        print(f"  {name}: {info['detail']}")
    
    # 3. 构建报告数据
    report_data = {
        "indices": indices_data,
        "smart_money": smart_money,
        "suggestion": generate_suggestion(indices_data, smart_money)
    }
    
    # 4. 发送飞书通知
    print("\n📤 生成报告...")
    from feishu_notify import format_daily_report
    report_text = format_daily_report(report_data)
    print(report_text)
    
    # 5. 保存报告
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"daily_{datetime.now().strftime('%Y%m%d')}.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\n✅ 报告已保存: {report_file}")
    
    return report_data

def generate_suggestion(indices_data, smart_money):
    """
    根据数据生成投资建议
    """
    # 简单逻辑
    signals = []
    
    # 北向资金信号
    if "北向资金" in smart_money:
        if smart_money["北向资金"]["signal"] == "bullish":
            signals.append("北向资金买入，关注")
        elif smart_money["北向资金"]["signal"] == "bearish":
            signals.append("北向资金卖出，谨慎")
    
    # 主力资金信号
    if "主力资金" in smart_money:
        if smart_money["主力资金"]["signal"] == "bullish":
            signals.append("主力资金流入")
        elif smart_money["主力资金"]["signal"] == "bearish":
            signals.append("主力资金流出")
    
    if not signals:
        return "市场情绪中性，建议持有为主"
    
    return " | ".join(signals)

if __name__ == "__main__":
    run_daily_check()
