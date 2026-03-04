
# ==================== 聪明钱分析模块 ====================

class SmartMoneyAnalyzer:
    """
    聪明钱分析器
    追踪北向资金、主力资金、杠杆资金、ETF资金
    """
    
    def __init__(self):
        self.data_sources = {
            "北向资金": self.get_northbound,
            "主力资金": self.get_mainforce,
            "融资融券": self.get_margin,
            "ETF资金": self.get_etf_flow,
        }
    
    def get_northbound(self):
        """
        北向资金分析
        核心指标：净买入、持仓变化、成交占比、行业偏好
        """
        # 通过Tushare获取
        # 这里模拟数据
        return {
            "daily_net_buy": 35.6,  # 亿元
            "weekly_change": 2.5,  # 周度变化%
            "monthly_change": 8.3,  # 月度变化%
            "trade_ratio": 4.2,    # 成交占比%
            "top_industry": ["新能源", "消费", "医药"],
            "signal": "买入",
            "signal_level": "🟢 积极"
        }
    
    def get_mainforce(self):
        """
        主力资金分析
        核心指标：大单净流入、散户情绪、资金脉冲
        """
        return {
            "large_order_net": -12.3,  # 亿元
            "small_order_net": 15.8,   # 亿元
            "retail_sentiment": "反向",   # 散户追涨/杀跌
            "pulse_days": 2,              # 连续流入天数
            "signal": "观望",
            "signal_level": "⚪ 中性"
        }
    
    def get_margin(self):
        """
        融资融券分析
        核心指标：融资余额、融资买入占比、融资净买入
        """
        return {
            "margin_balance": 14800,  # 亿元
            "margin_buy_ratio": 12.5,   # %
            "daily_net": 25,           # 亿元
            "signal": "乐观",
            "signal_level": "🟢 积极"
        }
    
    def get_etf_flow(self):
        """
        ETF资金分析
        核心指标：份额变化、溢价率
        """
        return {
            "etf_share_change": 3.5,  # % 月度变化
            "etf_premium": 0.2,        # % 溢价率
            "top_buy_etf": ["沪深300ETF", "中证500ETF"],
            "signal": "申购积极",
            "signal_level": "🟢 积极"
        }
    
    def generate_analysis(self):
        """生成综合分析报告"""
        results = {}
        for name, func in self.data_sources.items():
            results[name] = func()
        return results
    
    def get_trading_signal(self):
        """
        综合聪明钱信号
        """
        signals = self.generate_analysis()
        
        # 评分逻辑
        score = 0
        reasons = []
        
        # 北向资金
        if signals["北向资金"]["daily_net_buy"] > 30:
            score += 30
            reasons.append("北向资金大幅买入")
        elif signals["北向资金"]["daily_net_buy"] < -30:
            score -= 30
            reasons.append("北向资金大幅卖出")
        
        # 主力资金
        if signals["主力资金"]["large_order_net"] > 20:
            score += 20
            reasons.append("主力资金净流入")
        elif signals["主力资金"]["large_order_net"] < -20:
            score -= 20
            reasons.append("主力资金净流出")
        
        # 融资融券
        if signals["融资融券"]["margin_buy_ratio"] > 15:
            score -= 10
            reasons.append("融资买入占比过高，注意风险")
        elif signals["融资融券"]["margin_buy_ratio"] < 10:
            score += 10
            reasons.append("融资情绪健康")
        
        # ETF
        if signals["ETF资金"]["etf_share_change"] > 5:
            score += 20
            reasons.append("ETF持续申购")
        
        # 综合评级
        if score >= 60:
            grade = "🟢 强烈看多"
        elif score >= 30:
            grade = "🟢 看多"
        elif score >= -30:
            grade = "⚪ 中性"
        elif score >= -60:
            grade = "🔴 看空"
        else:
            grade = "🔴 强烈看空"
        
        return {
            "score": score,
            "grade": grade,
            "reasons": reasons
        }

# 测试
if __name__ == "__main__":
    analyzer = SmartMoneyAnalyzer()
    
    print("=== 聪明钱综合分析 ===\n")
    
    # 各资金分析
    for name, data in analyzer.generate_analysis().items():
        print(f"{name}:")
        print(f"  信号: {data['signal_level']} {data['signal']}")
        if "daily_net_buy" in data:
            print(f"  净买入: {data['daily_net_buy']}亿")
        if "large_order_net" in data:
            print(f"  大单净流入: {data['large_order_net']}亿")
        if "margin_balance" in data:
            print(f"  融资余额: {data['margin_balance']}亿")
        print()
    
    # 综合信号
    signal = analyzer.get_trading_signal()
    print(f"综合评分: {signal['score']}分")
    print(f"综合信号: {signal['grade']}")
    print(f"理由: {' | '.join(signal['reasons'])}")
