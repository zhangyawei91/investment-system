"""
飞书多维表同步模块
每日自动同步数据到飞书
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# 飞书多维表配置
APP_TOKEN = "QxhTbLTqoa0xPusz3aFc2Fuanph"
TABLE_IDS = {
    "持仓记录": "tblf0WV4yNd8xtnk",
    "每日行情": "tblBaGcC3HidGSXY",
    "资金动向": "tblbmDrhAUnT879b",
    "财务分析": "tblx2S0cmOlxTTvl",
    "ETF配置建议": "tblJvb3tzKvFjg5u",
}

# 字段ID映射
FIELDS = {
    "持仓记录": {
        "股票名称": "fldvL3UxQD",
        "日期": "fldMh3tGKB",
        "持仓数": "fldjmLyjI2",
        "成本价": "fldVsyfbRF",
        "现价": "fld4BqzK7w",
        "盈亏金额": "fldiqdeYD0",
        "盈亏比例": "fldNMt34Bx",
        "板块": "fldhqyoAQu",
        "建议": "fldSI9hAmd",
    },
    "资金动向": {
        "资金类型": "fldJNZYJyH",
        "日期": "fldtee61tp",
        "当前点位": "fldErktNfb",
        "涨跌幅": "fldu3az6AV",
        "净流入": "fldcjaEPvQ",
        "状态": "fldTkvvA1c",
    },
    "每日行情": {
        "股票名称": "fldXXXXX",
        "日期": "fldXXXXX",
        "开盘价": "fldXXXXX",
        "收盘价": "fldXXXXX",
        "涨跌幅": "fldXXXXX",
    },
}


def update_holdings(symbols_data):
    """更新持仓记录"""
    from feishu_bitable_list_records
    table_id = TABLE_IDS["持仓记录"]
    
    for stock in symbols_data:
        fields = {
            "股票名称": stock["name"],
            "日期": int(datetime.now().timestamp() * 1000),
            "现价": stock.get("price", 0),
            "盈亏金额": stock.get("pnl", 0),
            "盈亏比例": stock.get("pnl_pct", 0),
            "建议": stock.get("suggestion", "持有"),
        }
        if "holdings" in stock:
            fields["持仓数"] = stock["holdings"]
        if "cost" in stock:
            fields["成本价"] = stock["cost"]
        
        # 检查是否存在
        print(f"更新 {stock['name']}: {fields}")
    
    return True


def update_market_index(indices_data):
    """更新资金动向/大盘数据"""
    table_id = TABLE_IDS["资金动向"]
    
    for idx in indices_data:
        fields = {
            "资金类型": idx["name"],
            "日期": int(datetime.now().timestamp() * 1000),
            "当前点位": idx.get("price", 0),
            "涨跌幅": idx.get("change_pct", 0),
            "净流入": idx.get("net_inflow", 0),
            "状态": "观望",
        }
        print(f"更新 {idx['name']}: {fields}")
    
    return True


if __name__ == "__main__":
    # 测试
    print("飞书多维表同步测试")
    print(f"APP: {APP_TOKEN}")
    print(f"表: {TABLE_IDS}")