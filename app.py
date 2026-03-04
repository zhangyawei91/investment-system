"""
威少投资智脑系统 - Streamlit可视化界面
"""
import streamlit as st
import sys
import os
from datetime import datetime

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# 页面配置
st.set_page_config(
    page_title="威少投资智脑",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题
st.title("📊 威少投资智脑系统")
st.markdown(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 侧边栏 - 功能导航
st.sidebar.title("导航")
page = st.sidebar.radio(
    "选择功能",
    ["📈 盘面概览", "🏭 行业追踪", "💰 聪明钱", "📋 持仓诊断", "🌏 跨境投资"]
)

# 导入数据模块
try:
    from scripts.data_fetcher import get_index_quote, get_etf_quote, get_stock_quote, ETF_CODES, STOCK_CODES
    from scripts.smart_money import analyze_smart_money
    DATA_AVAILABLE = True
except Exception as e:
    st.error(f"数据模块加载失败: {e}")
    DATA_AVAILABLE = False

# ============ 盘面概览 ============
if page == "📈 盘面概览":
    st.header("📈 A股盘面概览")
    
    if not DATA_AVAILABLE:
        st.warning("数据模块不可用，请检查配置")
    else:
        # 主要指数
        col1, col2, col3 = st.columns(3)
        
        indices = [
            ("000300", "沪深300"),
            ("000001", "上证指数"),
            ("399006", "创业板"),
        ]
        
        for i, (code, name) in enumerate(indices):
            with [col1, col2, col3][i]:
                data = get_index_quote(code)
                if data:
                    color = "green" if data["change_pct"] > 0 else "red"
                    st.metric(
                        name,
                        f"{data['price']:.2f}",
                        f"{data['change_pct']:+.2f}%"
                    )
        
        st.divider()
        
        # 行业ETF
        st.subheader("📊 持仓相关ETF")
        
        etf_cols = st.columns(4)
        for i, (name, code) in enumerate(ETF_CODES.items()):
            with etf_cols[i % 4]:
                data = get_etf_quote(code)
                if data:
                    color = "green" if data["change_pct"] > 0 else "red"
                    st.metric(
                        name,
                        f"{data['price']:.3f}",
                        f"{data['change_pct']:+.2f}%"
                    )

# ============ 行业追踪 ============
elif page == "🏭 行业追踪":
    st.header("🏭 行业追踪")
    
    st.info("📌 行业追踪功能 - 监控持仓相关行业动态")
    
    # 行业配置
    industries = {
        "医药": {"etf": "医药ETF", "concern": "集采政策、估值分位"},
        "房地产": {"etf": "房地产ETF", "concern": "政策松紧、销售数据"},
        "半导体": {"etf": "芯片ETF", "concern": "周期指标、国产替代"},
        "消费": {"etf": "消费50ETF", "concern": "消费数据、居民意愿"},
    }
    
    for ind, info in industries.items():
        with st.expander(f"🏭 {ind}行业 ({info['concern']})"):
            st.write(f"**关注指标**: {info['concern']}")
            st.write(f"**相关ETF**: {info['etf']}")
            st.write("**近期动态**: 请查看盘面概览中的ETF行情")

# ============ 聪明钱 ============
elif page == "💰 聪明钱":
    st.header("💰 聪明钱追踪")
    st.markdown("追踪北向资金、主力资金、杠杆资金动向")
    
    if DATA_AVAILABLE:
        with st.spinner("加载资金数据..."):
            analysis = analyze_smart_money()
        
        # 显示分析结果
        for name, info in analysis.items():
            signal = info["signal"]
            detail = info["detail"]
            
            if signal == "bullish":
                emoji = "🟢"
                color = "green"
            elif signal == "bearish":
                emoji = "🔴"
                color = "red"
            else:
                emoji = "⚪"
                color = "gray"
            
            st.markdown(f"### {emoji} {name}")
            st.markdown(f"**信号**: {detail}")
            st.divider()
        
        st.info("💡 信号说明: 🟢看涨 🔴看跌 ⚪中性")
    else:
        st.warning("数据模块不可用")

# ============ 持仓诊断 ============
elif page == "📋 持仓诊断":
    st.header("📋 持仓诊断")
    
    # 威少当前持仓
    holdings = {
        "歌尔股份": {"shares": 400, "cost": -86.262, "price": 26.238, "pnl": 45559.75, "pct": 130.27},
        "沪深300ETF": {"shares": 1500, "cost": 2.288, "price": 4.702, "pnl": 3758.24, "pct": 113.27},
        "利欧股份": {"shares": 200, "cost": 5.746, "price": 9.680, "pnl": 786.88, "pct": 68.47},
        "恒生指数ETF": {"shares": 1200, "cost": 2.386, "price": 2.952, "pnl": 679.60, "pct": 23.72},
        "和邦转债": {"shares": 10, "cost": 99.700, "price": 161.820, "pnl": 621.20, "pct": 62.31},
        "红利低波100ETF": {"shares": 6500, "cost": 1.425, "price": 1.462, "pnl": 237.45, "pct": 2.60},
        "顺利3": {"shares": 9900, "cost": 1.000, "price": 0.150, "pnl": -8415.00, "pct": -85.00},
        "芯片ETF": {"shares": 1900, "cost": -2.634, "price": 1.955, "pnl": -8718.90, "pct": -174.22},
    }
    
    # 统计
    total_value = sum(h["shares"] * h["price"] for h in holdings.values())
    total_pnl = sum(h["pnl"] for h in holdings.values())
    
    st.metric("总市值", f"¥{total_value:,.0f}", f"总盈亏: {total_pnl:+,.0f}")
    
    # 分类
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ 盈利标的")
        profit = {k: v for k, v in holdings.items() if v["pnl"] > 0}
        for name, data in sorted(profit.items(), key=lambda x: x[1]["pnl"], reverse=True):
            st.write(f"**{name}**: +{data['pnl']:,.0f} ({data['pct']:+.1f}%)")
    
    with col2:
        st.subheader("❌ 亏损标的")
        loss = {k: v for k, v in holdings.items() if v["pnl"] < 0}
        for name, data in sorted(loss.items(), key=lambda x: x[1]["pnl"]):
            st.write(f"**{name}**: {data['pnl']:,.0f} ({data['pct']:.1f}%)")
    
    # 建议
    st.divider()
    st.subheader("💡 操作建议")
    
    suggestions = [
        ("顺利3", "立即清仓", "退市风险"),
        ("芯片ETF", "建议减仓/止损", "周期下行"),
        ("歌尔股份", "可部分止盈", "130%收益可观"),
    ]
    
    for name, action, reason in suggestions:
        st.write(f"• **{name}**: {action} - {reason}")

# ============ 跨境投资 ============
elif page == "🌏 跨境投资":
    st.header("🌏 跨境投资建议")
    
    st.markdown("""
    ## 价值投资体系下的跨境配置建议
    """)
    
    # 配置建议
    st.subheader("📊 建议配置比例")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("A股ETF", "50-60%")
    with col2:
        st.metric("港股", "10-15%")
    with col3:
        st.metric("美股ETF", "10-15%")
    with col4:
        st.metric("其他", "10-15%")
    
    # 标的推荐
    st.divider()
    st.subheader("📈 推荐标的")
    
    recommendations = {
        "港股": [
            ("腾讯控股", "00700", "社交+游戏+云"),
            ("阿里巴巴", "09988", "电商+云计算"),
            ("美团", "03690", "本地生活"),
            ("恒生ETF", "513100", "一网打尽"),
        ],
        "美股": [
            ("纳指ETF", "QQQ", "科技巨头"),
            ("标普500ETF", "SPY", "美国核心资产"),
            ("Vanguard全球ETF", "VT", "全球分散"),
        ],
        "其他": [
            ("黄金ETF", "518880", "避险"),
            ("REITs", "鹏华前海", "收息"),
        ]
    }
    
    for region, stocks in recommendations.items():
        with st.expander(f"🌍 {region}"):
            for name, code, reason in stocks:
                st.write(f"**{name}** ({code}): {reason}")

# 页脚
st.divider()
st.caption("🦐 威少投资智脑系统 | 投资有风险，入市需谨慎")
