#!/usr/bin/env python3
"""
从XMind文件导入任务到Trello
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trello_task_creator import TrelloTaskCreator

def main():
    if len(sys.argv) < 2:
        print("使用方法: python import_xmind_task.py <xmind文件路径> [分配人]")
        print("示例: python import_xmind_task.py \"D:\\Work\\XMind资料\\2026\\1月\\一月(2)(1).xmind\" 王晨阳")
        sys.exit(1)
    
    xmind_path = sys.argv[1]
    assignee = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(xmind_path):
        print(f"错误：XMind文件不存在 - {xmind_path}")
        sys.exit(1)
    
    print(f"开始解析XMind文件: {xmind_path}")
    
    try:
        creator = TrelloTaskCreator()
        # 解析XMind文件
        tasks = creator.parse_xmind(xmind_path)
        
        print(f"解析完成，共找到 {len(tasks)} 个画布（任务）")
        
        if len(tasks) == 0:
            print("错误：XMind文件中没有找到有效的画布")
            sys.exit(1)
        
        # 每个画布创建一个任务
        created_cards = []
        for i, task_data in enumerate(tasks, 1):
            if assignee:
                task_data["assignee"] = assignee
            
            print(f"\n正在创建第 {i} 个任务:")
            print(f"  标题: {task_data['title']}")
            print(f"  清单项: {len(task_data['checklist'])} 条")
            
            card = creator.create_task(task_data)
            created_cards.append(card)
            
            print(f"  创建成功! 卡片URL: {card['url']}")
        
        print(f"\n全部任务创建完成！共创建 {len(created_cards)} 个任务卡片")
        print("\n任务列表:")
        for i, card in enumerate(created_cards, 1):
            print(f"{i}. {card['name']} - {card['url']}")
            
    except Exception as e:
        print(f"错误：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
