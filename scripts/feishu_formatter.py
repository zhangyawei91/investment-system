#!/usr/bin/env python3
"""
飞书消息格式化模块 v2.0
支持富文本、颜色、表情等
"""
from datetime import datetime


def format_report_for_feishu(report_text):
    """
    将普通报告转换为飞书优化的格式
    添加表情符号和格式增强
    """
    lines = report_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # 标题增强
        if line.startswith('📊 威少投资每日简报'):
            formatted_lines.append(f"**{line}**")
        elif line.startswith('📈') and '盘面' in line:
            formatted_lines.append(f"\n**{line}**")
        elif line.startswith('📰') and '消息面' in line:
            formatted_lines.append(f"\n**{line}**")
        elif line.startswith('💰') and '资金' in line:
            formatted_lines.append(f"\n**{line}**")
        elif line.startswith('📈') and '技术分析' in line:
            formatted_lines.append(f"\n**{line}**")
        elif line.startswith('🏭') and '行业' in line:
            formatted_lines.append(f"\n**{line}**")
        elif line.startswith('📊') and '个股' in line:
            formatted_lines.append(f"\n**{line}**")
        elif line.startswith('💡') and '建议' in line:
            formatted_lines.append(f"\n**{line}**")
        # 分隔线简化
        elif line.startswith('-' * 20):
            formatted_lines.append("—" * 20)
        # 股票信息高亮
        elif '🟢' in line or '🔴' in line:
            # 已经是表情符号，保持不变
            formatted_lines.append(line)
        # 分类标签加粗
        elif line.startswith('🌍') or line.startswith('🏦') or line.startswith('🏭') or line.startswith('🛢️'):
            formatted_lines.append(f"**{line}**")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def create_interactive_card(title, sections):
    """
    创建飞书交互式卡片（如果支持）
    sections: [{"title": "", "content": ""}]
    """
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue"
        },
        "elements": []
    }
    
    for section in sections:
        card["elements"].append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**{section['title']}**"}
        })
        card["elements"].append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": section['content']}
        })
        card["elements"].append({"tag": "hr"})
    
    return card


def truncate_for_feishu(text, max_length=3000):
    """
    截断文本以适应飞书消息长度限制
    """
    if len(text) <= max_length:
        return text
    
    # 尝试在段落边界截断
    truncated = text[:max_length]
    last_newline = truncated.rfind('\n')
    if last_newline > max_length * 0.8:
        truncated = truncated[:last_newline]
    
    return truncated + "\n\n... (内容已截断，查看完整报告请访问系统)"


if __name__ == "__main__":
    # 测试
    test_report = """
📊 威少投资每日简报
更新时间: 2026-03-04 23:27

📈 盘面概览
------------------------------
📈 沪深300: 4655.90 (+1.01%)

💰 资金流向
------------------------------
🟢 北向资金: 净买入34亿
"""
    print(format_report_for_feishu(test_report))