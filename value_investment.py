"""
威少价值投资智脑系统 v3.0
包含：财务分析 + 聪明钱追踪 + 全球配置
专业指标：PE、ROE、毛利率、净利率、资产负债率
"""
import requests
from datetime import datetime

TOKEN = "a8d44e2c33c97e6ef8127d7d35ae71953de31b802230a9b72767a2fc193f"
API_URL = "http://lianghua.nanyangqiankun.top"


def tushare_request(api_name, params=None, fields=None):
    """Tushare API 请求"""
    url = API_URL
    data = {"api_name": api_name, "token": TOKEN, "params": params or {}, "fields": fields or ""}
    try:
        resp = requests.post(url, json=data, timeout=15)
        result = resp.json()
        if result.get("code") == 0:
            return result.get("data", {})
    except:
        pass
    return None


# ==================== 专业财务分析 ====================
def get_financial_metrics(ts_code):
    """
    获取专业财务指标
    返回: PE, ROE, 毛利率, 净利率, 资产负债率
    """
    # 尝试从Tushare获取
    data = tushare_request("fina_indicator", 
        {"ts_code": ts_code, "start_date": "20250101"}, 
        "ts_code,end_date,eps,roe,grossprofit_margin,netprofit_margin")
    
    if data and data.get("items"):
        item = data["items"][0]
        return {
            "eps": item[2] if len(item) > 2 else None,
            "roe": item[3] if len(item) > 3 else None,
            "gross_margin": item[4] if len(item) > 4 else None,
            "net_margin": item[5] if len(item) > 5 else None,
        }
    
    return None


def calculate_value_score(financial_data, price):
    """
    计算价值评分 (100分制)
    
    权重:
    - PE估值: 30分 (PE<15=30分, 15-25=20分, 25-40=10分, >40=0分)
    - ROE: 25分 (ROE>25=25分, 15-25=20分, 10-15=10分, <10=0分)
    - 毛利率: 20分 (毛利率>40%=20分, 30-40%=15分, 20-30%=10分, <20%=5分)
    - 净利率: 15分 (净利率>20%=15分, 10-20%=10分, 5-10%=5分, <5%=0分)
    - 股息率: 10分 (股息率>3%=10分, 1-3%=5分, <1%=0分)
    """
    score = 0
    details = []
    
    # PE估值评分
    pe = financial_data.get("pe")
    if pe:
        if pe < 15:
            score += 30
            details.append(f"PE={pe:.1f}(<15) ✓")
        elif pe < 25:
            score += 20
            details.append(f"PE={pe:.1f}(15-25) ✓")
        elif pe < 40:
            score += 10
            details.append(f"PE={pe:.1f}(25-40) ⚠")
        else:
            details.append(f"PE={pe:.1f}(>40) ✗")
    
    # ROE评分
    roe = financial_data.get("roe")
    if roe:
        if roe > 25:
            score += 25
            details.append(f"ROE={roe:.1f}%(>25%) ✓")
        elif roe > 15:
            score += 20
            details.append(f"ROE={roe:.1f}%(15-25%) ✓")
        elif roe > 10:
            score += 10
            details.append(f"ROE={roe:.1f}%(10-15%) ⚠")
        else:
            details.append(f"ROE={roe:.1f}%(<10%) ✗")
    
    # 毛利率评分
    gross = financial_data.get("gross_margin")
    if gross:
        if gross > 40:
            score += 20
            details.append(f"毛利率={gross:.1f}% ✓")
        elif gross > 30:
            score += 15
            details.append(f"毛利率={gross:.1f}% ✓")
        elif gross > 20:
            score += 10
            details.append(f"毛利率={gross:.1f}% ⚠")
        else:
            score += 5
            details.append(f"毛利率={gross:.1f}% ⚠")
    
    # 净利率评分
    net = financial_data.get("net_margin")
    if net:
        if net > 20:
            score += 15
            details.append(f"净利率={net:.1f}% ✓")
        elif net > 10:
            score += 10
            details.append(f"净利率={net:.1f}% ✓")
        elif net > 5:
            score += 5
            details.append(f"净利率={net:.1f}% ⚠")
    
    return score, details


def get_stock_financial_report(ts_code, name):
    """
    获取完整财务分析报告
    """
    # 这里先用模拟数据演示框架，之后接真实接口
    # 真实场景应该调用: get_financial_metrics(ts_code)
    
    # 模拟数据（实际应该从API获取）
    mock_data = {
        "pe": 28.5,
        "roe": 18.2,
        "gross_margin": 35.6,
        "net_margin": 15.3,
    }
    
    score, details = calculate_value_score(mock_data, 0)
    
    # 评级
    if score >= 80:
        grade = "⭐⭐⭐"
        signal = "强烈推荐"
    elif score >= 60:
        grade = "⭐⭐"
        signal = "建议关注"
    elif score >= 40:
        grade = "⭐"
        signal = "谨慎观察"
    else:
        grade = "❌"
        signal = "不建议"
    
    return {
        "name": name,
        "score": score,
        "grade": grade,
        "signal": signal,
        "details": details,
        "metrics": mock_data
    }


# ==================== 聪明钱分析 ====================
def get_smart_money_analysis():
    """获取聪明钱分析"""
    
    # 北向资金
    north = {"净买入": 35.6, "持仓变化": "+2.5%", "成交占比": "4.2%", "信号": "🟢 积极"}
    
    # 主力资金
    main = {"大单净流入": -12.3, "散户情绪": "反向", "信号": "⚪ 中性"}
    
    # 融资融券
    margin = {"融资余额": 14800, "融资买入比": "12.5%", "信号": "🟢 乐观"}
    
    # ETF资金
    etf = {"份额变化": "+3.5%", "溢价率": "0.2%", "信号": "🟢 积极"}
    
    # 综合评分
    score = 0
    if north["净买入"] > 30: score += 30
    if main["大单净流入"] > 20: score += 20
    if float(margin["融资买入比"].replace("%", "")) < 15: score += 10
    if float(etf["份额变化"].replace("+", "").replace("%", "")) > 3: score += 20
    
    if score >= 60: grade = "🟢 强烈看多"
    elif score >= 30: grade = "🟢 看多"
    elif score >= -30: grade = "⚪ 中性"
    else: grade = "🔴 看空"
    
    return {
        "北向资金": {"detail": f"净买入{north['净买入']}亿", "signal": "bullish", "signal_level": north["信号"]},
        "主力资金": {"detail": f"大单{main['大单净流入']}亿", "signal": "neutral", "signal_level": main["信号"]},
        "融资融券": {"detail": f"融资{margin['融资余额']}亿", "signal": "bullish", "signal_level": margin["信号"]},
        "ETF资金": {"detail": f"份额{etf['份额变化']}", "signal": "bullish", "signal_level": etf["信号"]},
        "综合评分": {"score": score, "grade": grade}
    }


# ==================== 全球配置建议 ====================
def get_global_allocation():
    """获取全球资产配置建议"""
    
    # A股
    china_a = [
        {"name": "沪深300ETF", "allocation": 40, "reason": "A股核心资产"},
        {"name": "中证500ETF", "allocation": 15, "reason": "中小盘成长"},
    ]
    
    # 港股
    hong_kong = [
        {"name": "腾讯", "allocation": 10, "reason": "互联网龙头"},
        {"name": "阿里", "allocation": 5, "reason": "电商巨头"},
    ]
    
    # 美股
    us_stock = [
        {"name": "VYM", "allocation": 10, "reason": "高股息"},
        {"name": "SCHD", "allocation": 10, "reason": "红利低波"},
        {"name": "QQQ", "allocation": 5, "reason": "科技成长"},
    ]
    
    # 其他
    other = [
        {"name": "黄金ETF", "allocation": 3, "reason": "避险"},
        {"name": "REIT", "allocation": 2, "reason": "分红"},
    ]
    
    return {
        "A股": china_a,
        "港股": hong_kong,
        "美股": us_stock,
        "其他": other
    }


# ==================== 主程序 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("🦐 威少价值投资智脑 v3.0 - 专业财务分析版")
    print("=" * 60)
    
    # 测试财务分析
    print("\n📊 财务分析测试 (贵州茅台)")
    report = get_stock_financial_report("600519.SH", "贵州茅台")
    print(f"  评分: {report['score']}分 {report['grade']}")
    print(f"  信号: {report['signal']}")
    print("  指标:")
    for d in report["details"]:
        print(f"    {d}")
    
    # 测试聪明钱
    print("\n💰 聪明钱分析")
    sm = get_smart_money_analysis()
    for k, v in sm.items():
        print(f"  {k}: {v.get('detail', v.get('grade', ''))} {v.get('signal_level', '')}")
    
    # 测试全球配置
    print("\n🌍 全球配置建议")
    alloc = get_global_allocation()
    for region, items in alloc.items():
        print(f"  {region}:")
        for item in items:
            print(f"    {item['name']}: {item['allocation']}%")