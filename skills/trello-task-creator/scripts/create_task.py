#!/usr/bin/env python3
"""
快速创建Trello任务的脚本
使用方法: python create_task.py <分配人> <任务标题> [附件链接]
示例: python create_task.py 王晨阳 "UI显示重叠的bug" "https://example.com/screenshot.png"
"""

import sys
import json
import os
from trello_task_creator import TrelloTaskCreator

def main():
    if len(sys.argv) < 3:
        print("使用方法: python create_task.py <分配人> <任务标题> [附件链接]")
        print("示例: python create_task.py 王晨阳 \"UI显示重叠的bug\" \"https://example.com/screenshot.png\"")
        sys.exit(1)
    
    assignee = sys.argv[1]
    title = sys.argv[2]
    attachment = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 识别分类
    categories = ['开发', '优化', '安全', '规则', '设计', '测试', '文档', '重构', 'BUG']
    category = '设计'
    
    lower_title = title.lower()
    if 'bug' in lower_title or '故障' in lower_title or '异常' in lower_title or '错误' in lower_title:
        category = 'BUG'
    elif '开发' in lower_title or '实现' in lower_title or '功能' in lower_title or '新增' in lower_title:
        category = '开发'
    elif '优化' in lower_title or '性能' in lower_title or '提升' in lower_title or '改进' in lower_title:
        category = '优化'
    elif '测试' in lower_title or '验证' in lower_title or '联调' in lower_title:
        category = '测试'
    elif '文档' in lower_title or '编写' in lower_title or '总结' in lower_title:
        category = '文档'
    elif '设计' in lower_title or 'ui' in lower_title or '原型' in lower_title:
        category = '设计'
    
    # 清理标题
    clean_title = title
    for cat in categories:
        clean_title = clean_title.replace(cat, '').replace(cat.lower(), '')
    clean_title = clean_title.replace('bug', '').replace('BUG', '').replace('任务', '').strip()
    clean_title = clean_title.rstrip('的').strip()
    
    # 生成标准化标题
    full_title = f"【{category}】-{clean_title}"
    if len(full_title) > 30:
        full_title = full_title[:27] + "…"
    
    # 生成描述
    description = f"任务内容：{title}"
    if attachment:
        description += f"\n附件：{attachment}"
    
    # 生成清单
    if category == 'BUG':
        checklist = [
            "1、复现问题并定位根因",
            "2、修复代码并验证",
            "3、提交代码并部署测试",
            "4、回归测试确认问题解决"
        ]
    elif category == '开发':
        checklist = [
            "1、需求分析和方案设计",
            "2、代码开发和单元测试",
            "3、联调测试和功能验证",
            "4、代码评审和合并上线"
        ]
    elif category == '优化':
        checklist = [
            "1、现状分析和瓶颈定位",
            "2、优化方案设计和评审",
            "3、优化实现和效果验证",
            "4、性能对比和上线发布"
        ]
    else:
        checklist = [
            "1、需求分析和确认",
            "2、方案设计和评审",
            "3、开发实现和测试",
            "4、上线交付和验收"
        ]
    
    # 准备任务数据
    task_data = {
        "title": full_title,
        "description": description,
        "checklist": checklist,
        "assignee": assignee if assignee != '未指定' else None
    }
    
    # 创建任务
    creator = TrelloTaskCreator()
    card = creator.create_task(task_data)
    
    print("任务创建成功！")
    print(f"标题: {card['name']}")
    print(f"链接: {card['url']}")
    print(f"分配: {assignee}")
    print("清单:")
    for item in checklist:
        print(f"   {item}")

if __name__ == "__main__":
    main()
