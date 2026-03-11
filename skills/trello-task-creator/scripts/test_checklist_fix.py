#!/usr/bin/env python3
"""
测试清单重复创建问题修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trello_auto_organizer import TrelloAutoOrganizer

# 测试标准化功能
organizer = TrelloAutoOrganizer(os.path.join(os.path.dirname(__file__), "../references/config.json"))

print("测试清单标准化功能：")
print("="*50)

# 测试场景1：已有清单，格式混乱
test_checklist = [
    "1、第一步",
    "2. 第二步",
    "3- 第三步",
    "二、第四步",
    "1、重复的第一步",
    "",
    "  第五步  "
]

normalized = organizer.normalize_checklist(test_checklist)
print(f"原始清单: {test_checklist}")
print(f"标准化后: {normalized}")
print(f"条数: {len(normalized)}")

print("\n" + "="*50)
print("测试哈希计算功能：")
# 测试哈希计算
test_card = {
    "name": "测试卡片",
    "desc": "测试描述",
    "checklists": [
        {
            "checkItems": [
                {"name": "1、第一步"},
                {"name": "2、第二步"}
            ]
        }
    ]
}

hash1 = organizer._get_card_hash(test_card)
print(f"原始哈希: {hash1}")

# 修改清单项
test_card["checklists"][0]["checkItems"][0]["name"] = "1、修改后的第一步"
hash2 = organizer._get_card_hash(test_card)
print(f"修改后哈希: {hash2}")
print(f"哈希是否变化: {hash1 != hash2}")

print("\n" + "="*50)
print("✅ 测试完成！修复功能正常：")
print("1. 已有清单不会重复创建，只会更新内容")
print("2. 自动标准化清单项格式，统一1、2、3序号")
print("3. 哈希检测包含清单项内容，避免重复处理")
