#!/usr/bin/env python3
"""
投资报告构建器 v3.0
分模块生成报告，最后合并发送
"""
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.data_fetcher import get_index_quote, get_etf_quote
from scripts.smart_money import analyze_smart_money
from scripts.news_fetcher import get_financial_news
from scripts.technical_analysis import TechnicalAnalyzer


class ReportBuilder:
    """报告构建器 - 分模块生成"""
    
    def __init__(self):
        self.modules = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def build_all(self) -> str:
        """构建完整报告"""
        report = f"📊 威少投资每日简报\n"
        report += f"更新时间: {self.timestamp}\n"
        report += "=" * 50 + "\n\n"
        
        # 按顺序生成各模块
        report += self.build_market_overview()
        report += self.build_news_section()
        report += self.build_fund_flow()
        report += self.build_technical_analysis()
        report += self.build_sector_analysis()
        report += self.build_stock_analysis()
        report += self.build_advice()
        
        report += "\n" + "=" * 50 + "\n"
        report += "🦐 威少投资智脑\n"
        
        return report
    
    def build_market_overview(self) -> str:
        """模块1: 盘面总览"""
        report = "📈 盘面总览\n"
        report += "-" * 30 + "\n"
        
        indices = [("000300", "沪深300"), ("000001", "上证指数"), ("399006", "创业板")]
        
        for code, name in indices:
            data = get_index_quote(code)
            if data:
                price = data.get("price", 0)
                change_pct = data.get("change_pct", 0)
                emoji = "📈" if change_pct > 0 else "📉"
                report += f"{emoji} {name}: {price:.2f} ({change_pct:+.2f}%)\n"
            else:
                report += f"⚪ {name}: 数据获取失败\n"
        
        report += "\n"
        self.modules["盘面总览"] = "✅"
        return report
    
    def build_news_section(self) -> str:
        """模块2: 消息面分析（带分类）"""
        report = "📰 消息面分析\n"
        report += "-" * 30 + "\n"
        
        # 分类配置
        categories = {
            '🌍 国际': ['美国', '欧洲', '英国', '日本', '韩国', '中东', '俄乌', '美联储', '关税', '伊朗', '以军'],
            '🏦 金融政策': ['央行', '降息', '加息', '存款准备金', '利率', '金融', '银行', '保险', '外汇'],
            '🏭 产业政策': ['政策', '证监会', '财政部', '国务院', '监管', '新能源', 'AI', '芯片', '汽车'],
            '🛢️ 大宗商品': ['原油', '黄金', '石油', '天然气', '期货', '铜', '铝'],
            '🏠 地产基建': ['房地产', '地产', '楼市', '建筑', '基建', '水泥'],
            '💻 科技': ['华为', '芯片', 'AI', '互联网', '软件', '5G', '6G', '激光雷达'],
            '🏥 医药': ['医药', '医疗', '疫苗', '生物', '中药', '器械'],
        }
        
        try:
            news = get_financial_news(8)
            if news:
                # 按分类整理
                categorized = {cat: [] for cat in categories.keys()}
                categorized['📋 其他'] = []
                
                for n in news:
                    title = n['title']
                    assigned = False
                    for cat, keywords in categories.items():
                        if any(k in title for k in keywords):
                            categorized[cat].append(n)
                            assigned = True
                            break
                    if not assigned:
                        categorized['📋 其他'].append(n)
                
                # 输出分类新闻
                for cat, items in categorized.items():
                    if items:
                        report += f"\n{cat}\n"
                        for n in items[:3]:  # 每类最多3条
                            report += f"  • {n['time'][5:16]} {n['title'][:40]}\n"
            else:
                report += "暂无重要新闻\n"
        except Exception as e:
            report += f"新闻获取失败: {e}\n"
        
        report += "\n"
        self.modules["消息面"] = "✅"
        return report
    
    def build_fund_flow(self) -> str:
        """模块3: 资金流向"""
        report = "💰 资金流向\n"
        report += "-" * 30 + "\n"
        
        try:
            analysis = analyze_smart_money()
            
            # 北向资金
            nb = analysis.get("北向资金", {})
            signal = "🟢" if nb.get("signal") == "bullish" else "⚪"
            report += f"{signal} 北向资金: {nb.get('detail', '无数据')}\n"
            
            # 杠杆资金
            lg = analysis.get("杠杆资金", {})
            report += f"⚪ 杠杆资金: {lg.get('detail', '无数据')}\n"
            
            # 龙虎榜
            lhb = analysis.get("龙虎榜", {})
            if lhb.get("data"):
                report += f"🟡 龙虎榜: {lhb.get('detail', '')[:50]}\n"
            
        except Exception as e:
            report += f"资金数据获取失败: {e}\n"
        
        report += "\n"
        self.modules["资金流向"] = "✅"
        return report
    
    def build_technical_analysis(self) -> str:
        """模块4: 技术分析"""
        report = "📈 技术分析\n"
        report += "-" * 30 + "\n"
        
        try:
            analyzer = TechnicalAnalyzer()
            
            # 分析几只重点股票
            stocks_to_analyze = [
                ("紫金矿业", "601899.SH"),
                ("歌尔股份", "002241.SZ"),
                ("四川长虹", "600839.SH")
            ]
            
            for name, ts_code in stocks_to_analyze:
                result = analyzer.analyze_stock(name, ts_code)
                if result:
                    trend_emoji = "🟢" if "上涨" in result['trend'] else "🔴" if "下跌" in result['trend'] else "⚪"
                    report += f"{trend_emoji} {name}: {result['current_price']:.2f}\n"
                    report += f"   趋势: {result['trend']}\n"
                    if result['ma']:
                        ma5 = result['ma'].get('MA5', 0)
                        ma20 = result['ma'].get('MA20', 0)
                        report += f"   MA5/MA20: {ma5:.2f}/{ma20:.2f}\n"
                    if result['rsi']:
                        report += f"   RSI: {result['rsi']['RSI']} ({result['rsi']['status']})\n"
                    if result['macd']:
                        report += f"   MACD: {result['macd']['signal']}\n"
                    report += "\n"
                else:
                    report += f"⚪ {name}: 数据获取失败\n\n"
                    
        except Exception as e:
            report += f"技术分析获取失败: {e}\n"
        
        self.modules["技术分析"] = "✅"
        return report
    
    def build_sector_analysis(self) -> str:
        """模块5: 行业板块"""
        report = "🏭 行业板块\n"
        report += "-" * 30 + "\n"
        report += "⚠️ 行业板块数据暂不可用（东方财富API网络不通）\n"
        report += "   替代方案: 关注持仓股所属行业表现\n"
        report += "\n"
        self.modules["行业板块"] = "⚠️"
        return report
    
    def build_stock_analysis(self) -> str:
        """模块5: 个股分析"""
        report = "📊 个股分析\n"
        report += "-" * 30 + "\n"
        
        try:
            # 读取持仓数据（支持多个账户）
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            holdings_files = [
                os.path.join(data_dir, "holdings.json"),
                os.path.join(data_dir, "holdings_zhongxin.json")
            ]
            all_stocks = []
            total_pnl = 0
            found_data = False
            
            for holdings_file in holdings_files:
                if os.path.exists(holdings_file):
                    found_data = True
                    import json
                    with open(holdings_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # 判断数据结构
                    if "broker" in data:
                        # 单账户格式（中信建投）
                        broker = data.get("broker", "未知券商")
                        report += f"\n{broker}:\n"
                        report += f"  总资产: {data.get('total_assets', 0):,.2f}元\n"
                        report += f"  总市值: {data.get('market_value', 0):,.2f}元\n"
                        report += f"  仓位: {data.get('position_ratio', 0)}%\n"
                        
                        for s in data.get("stocks", []):
                            shares = s["shares"]
                            cost = s["cost"]
                            current = s.get("current", cost)
                            pnl = s.get("pnl", (current - cost) * shares)
                            pnl_pct = s.get("pnl_pct", (current - cost) / cost * 100 if cost > 0 else 0)
                            total_pnl += pnl
                            
                            emoji = "🟢" if pnl > 0 else "🔴"
                            report += f"  {emoji} {s['name']}: {shares}股, 成本{cost:.3f}, 现价{current:.3f}, {pnl:+.0f}({pnl_pct:+.1f}%)\n"
                            all_stocks.append({"name": s["name"], "pnl_pct": pnl_pct})
                    elif "accounts" in data:
                        # 多账户格式
                        for account, stocks in data.get("accounts", {}).items():
                            report += f"\n{account}:\n"
                            for s in stocks:
                                shares = s["shares"]
                                cost = s["cost"]
                                current = s.get("current", cost)
                                pnl = (current - cost) * shares
                                pnl_pct = (current - cost) / cost * 100 if cost > 0 else 0
                                total_pnl += pnl
                                
                                emoji = "🟢" if pnl > 0 else "🔴"
                                report += f"  {emoji} {s['name']}: {shares}股, 成本{cost:.2f}, 当前{current:.2f}, {pnl:+.0f}({pnl_pct:+.1f}%)\n"
                                all_stocks.append({"name": s["name"], "pnl_pct": pnl_pct})
            
            if not found_data:
                report += "⚠️ 持仓数据文件不存在\n"
            elif all_stocks:
                # 总结
                report += f"\n  总浮动盈亏: {total_pnl:+.0f}元\n"
                
                # 涨跌幅排行
                sorted_stocks = sorted(all_stocks, key=lambda x: x["pnl_pct"], reverse=True)
                best = sorted_stocks[0]
                worst = sorted_stocks[-1]
                report += f"  最佳: {best['name']} ({best['pnl_pct']:+.1f}%)\n"
                report += f"  最差: {worst['name']} ({worst['pnl_pct']:+.1f}%)\n"
                
        except Exception as e:
            report += f"持仓数据读取失败: {e}\n"
        
        report += "\n"
        self.modules["个股分析"] = "✅"
        return report
    
    def build_advice(self) -> str:
        """模块6: 综合建议"""
        report = "💡 综合建议\n"
        report += "-" * 30 + "\n"
        
        # 根据已有数据生成建议
        try:
            analysis = analyze_smart_money()
            
            signals = []
            
            # 北向资金信号
            if analysis.get("北向资金", {}).get("signal") == "bullish":
                signals.append("北向资金买入，积极关注")
            elif analysis.get("北向资金", {}).get("signal") == "bearish":
                signals.append("北向资金卖出，谨慎操作")
            
            # 杠杆资金信号
            lg = analysis.get("杠杆资金", {}).get("detail", "")
            if "买入" in lg and "2810" in lg:
                signals.append("融资活跃，市场情绪偏多")
            
            # 龙虎榜信号
            lhb = analysis.get("龙虎榜", {}).get("detail", "")
            if "+" in lhb:
                signals.append("龙虎榜热门股表现强劲")
            
            if signals:
                report += " | ".join(signals) + "\n"
            else:
                report += "市场情绪中性，建议持有为主\n"
                
        except Exception as e:
            report += f"建议生成失败: {e}\n"
        
        report += "\n"
        self.modules["综合建议"] = "✅"
        return report
    
    def get_module_status(self) -> Dict[str, str]:
        """获取各模块状态"""
        return self.modules


def generate_report() -> str:
    """生成完整报告"""
    builder = ReportBuilder()
    report = builder.build_all()
    print(f"模块状态: {builder.get_module_status()}")
    return report


if __name__ == "__main__":
    print("=" * 50)
    print("🕐 威少投资报告 v3.0")
    print("=" * 50 + "\n")
    
    report = generate_report()
    print(report)
    
    # 保存报告
    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"daily_{datetime.now().strftime('%Y%m%d')}.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ 报告已保存: {report_file}")