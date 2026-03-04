#!/usr/bin/env python3
"""
飞书多维表同步模块
功能：
1. 同步每日持仓行情到"持仓记录"表
2. 同步大盘指数到"资金动向"表
3. 自动运行：python3 scripts/feishu_sync.py

依赖：已集成到 OpenClaw 工具，无需额外 pip
"""
import sys
import os
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 飞书多维表配置
APP_TOKEN = "QxhTbLTqoa0xPusz3aFc2Fuanph"
TABLE_IDS = {
    "持仓记录": "tblf0WV4yNd8xtnk",
    "资金动向": "tblbmDrhAUnT879b",
}

# 威少持仓列表
HOLDINGS = [
    ("002241", "歌尔股份", "股票"),
    ("002131", "利欧股份", "股票"),
    ("600104", "上汽集团", "股票"),
    ("600839", "四川长虹", "股票"),
    ("000100", "TCL科技", "股票"),
]

INDICES = [
    ("000300", "沪深300"),
    ("000001", "上证指数"),
    ("399006", "创业板"),
]

# 工具函数 - 使用 OpenClaw 的 feishu_bitable 工具
def create_record(app_token, table_id, fields):
    """通过 OpenClaw 工具创建记录"""
    import json
    import subprocess
    
    # 构建字段 JSON
    fields_json = json.dumps(fields)
    
    # 调用 OpenClaw 工具
    cmd = [
        "openclaw", "exec", "--",
        "python3", "-c",
        f"""
import sys
sys.path.insert(0, '/root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw')
from extensions.feishu.tools.bitable import bitable_create_record
result = bitable_create_record(
    app_token="{app_token}",
    table_id="{table_id}",
    fields={fields_json}
)
print(result)
"""
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(result.stderr)


def create_record_direct(app_token, table_id, fields):
    """直接使用飞书API"""
    import requests
    import json
    import subprocess
    
    # 用 curl 调用飞书 API（更可靠）
    fields_json = json.dumps(fields).replace('"', '\\"')
    
    cmd = f'''curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records" \
      -H "Authorization: Bearer $(cat /root/.openclaw/workspace/memory/feishu_token.txt | head -1)" \
      -H "Content-Type: application/json" \
      -d '{{"fields": {json.dumps(fields)}}}' '''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    
    try:
        data = json.loads(result.stdout)
        if data.get("code") == 0:
            return data
        else:
            print(f"  API返回: {data}")
            raise Exception(f"错误: {data.get('msg')}")
    except:
        print(f"  Response: {result.stdout[:200]}")
        raise


def get_today_timestamp():
    """获取今天0点的时间戳（毫秒）"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return int(today.timestamp() * 1000)


def sync_holdings():
    """同步持仓数据"""
    if not create_record:
        print("✗ 无法同步持仓：飞书工具不可用")
        return
    
    from data_fetcher import get_stock_quote
    
    today = get_today_timestamp()
    
    for code, name, category in HOLDINGS:
        print(f"\n📊 获取 {name}...")
        quote = get_stock_quote(code)
        
        if quote:
            price = quote.get("price", 0)
            change_pct = quote.get("change_pct", 0)
            
            fields = {
                "股票名称": name,
                "日期": today,
                "现价": price,
                "盈亏比例": round(change_pct, 2),
                "建议": "持有",
                "板块": category,
            }
            
            try:
                result = create_record(
                    app_token=APP_TOKEN,
                    table_id=TABLE_IDS["持仓记录"],
                    fields=fields
                )
                print(f"  ✅ {name}: ¥{price} ({change_pct:+.2f}%)")
            except Exception as e:
                print(f"  ❌ 写入失败: {e}")
        else:
            print(f"  ❌ 数据获取失败")


def sync_indices():
    """同步大盘指数"""
    if not create_record:
        print("✗ 无法同步指数：飞书工具不可用")
        return
    
    from data_fetcher import get_index_quote
    
    today = get_today_timestamp()
    
    for code, name in INDICES:
        print(f"\n📈 获取 {name}...")
        quote = get_index_quote(code)
        
        if quote:
            price = quote.get("price", 0)
            change_pct = quote.get("change_pct", 0)
            
            fields = {
                "资金类型": name,
                "日期": today,
                "当前点位": round(price, 2),
                "涨跌幅": round(change_pct, 2),
                "状态": "观望",
            }
            
            try:
                result = create_record(
                    app_token=APP_TOKEN,
                    table_id=TABLE_IDS["资金动向"],
                    fields=fields
                )
                print(f"  ✅ {name}: {price:.2f} ({change_pct:+.2f}%)")
            except Exception as e:
                print(f"  ❌ 写入失败: {e}")
        else:
            print(f"  ❌ 数据获取失败")


def main():
    print("=" * 50)
    print("🦐 飞书多维表同步")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    print("\n📊 同步持仓数据...")
    sync_holdings()
    
    print("\n📈 同步大盘指数...")
    sync_indices()
    
    print("\n" + "=" * 50)
    print("✅ 同步完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()