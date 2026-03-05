#!/usr/bin/env python3
"""
Trello任务创建脚本
功能：
1. 智能任务拆解
2. 自动计算截止日期（当月最后一个工作日）
3. 成员匹配
4. 创建Trello卡片
"""

import requests
import json
import os
from datetime import datetime, timedelta
import calendar


class TrelloTaskCreator:
    def __init__(self, config_path=None):
        """
        初始化Trello任务创建器
        
        Args:
            config_path: 配置文件路径，默认从环境变量读取
        """
        self.base_url = "https://api.trello.com/1"
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.token = os.getenv("TRELLO_TOKEN")
        self.board_id = os.getenv("TRELLO_BOARD_ID")
        self.default_list = "Not Start"
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
        if not all([self.api_key, self.token, self.board_id]):
            raise ValueError("请配置TRELLO_API_KEY、TRELLO_TOKEN、TRELLO_BOARD_ID")
    
    def _load_config(self, config_path):
        """从配置文件加载配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            trello_config = config.get("trello", {})
            self.api_key = trello_config.get("apiKey", self.api_key)
            self.token = trello_config.get("token", self.token)
            self.board_id = trello_config.get("boardId", self.board_id)
            self.default_list = trello_config.get("defaultList", self.default_list)
    
    def get_board_data(self):
        """获取看板数据（列表、成员等）"""
        url = f"{self.base_url}/boards/{self.board_id}"
        params = {
            "key": self.api_key,
            "token": self.token,
            "lists": "open",
            "members": "all"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def find_list_id(self, lists, list_name):
        """通过名称查找列表ID"""
        for lst in lists:
            if lst.get("name") == list_name:
                return lst.get("id")
        return None
    
    def find_member_id(self, members, full_name):
        """通过姓名查找成员ID"""
        for member in members:
            if member.get("fullName") == full_name:
                return member.get("id")
        return None
    
    def get_last_workday(self):
        """获取当月最后一个工作日"""
        now = datetime.now()
        year = now.year
        month = now.month
        
        # 获取当月最后一天
        last_day = calendar.monthrange(year, month)[1]
        date = datetime(year, month, last_day)
        
        # 如果是周六（5）或周日（6），向前调整
        while date.weekday() >= 5:
            date -= timedelta(days=1)
        
        return date.strftime("%Y-%m-%d")
    
    def create_card(self, name, desc, id_list, id_members=None, due=None):
        """
        创建Trello卡片
        
        Args:
            name: 卡片标题
            desc: 卡片描述
            id_list: 列表ID
            id_members: 成员ID列表
            due: 截止日期（ISO格式）
        
        Returns:
            创建的卡片数据
        """
        url = f"{self.base_url}/cards"
        params = {
            "key": self.api_key,
            "token": self.token
        }
        data = {
            "name": name,
            "desc": desc,
            "idList": id_list
        }
        if id_members:
            data["idMembers"] = id_members
        if due:
            data["due"] = due
        
        response = requests.post(url, params=params, json=data)
        response.raise_for_status()
        return response.json()
    
    def add_checklist(self, card_id, name, items):
        """
        添加清单到卡片
        
        Args:
            card_id: 卡片ID
            name: 清单名称
            items: 清单项列表
        
        Returns:
            创建的清单数据
        """
        # 创建清单
        url = f"{self.base_url}/cards/{card_id}/checklists"
        params = {
            "key": self.api_key,
            "token": self.token
        }
        data = {
            "name": name
        }
        response = requests.post(url, params=params, json=data)
        response.raise_for_status()
        checklist = response.json()
        
        # 添加清单项
        checklist_id = checklist.get("id")
        for item in items:
            item_url = f"{self.base_url}/checklists/{checklist_id}/checkItems"
            item_data = {
                "name": item
            }
            requests.post(item_url, params=params, json=item_data)
        
        return checklist
    
    def create_task(self, task_data):
        """
        完整的任务创建流程
        
        Args:
            task_data: 任务数据字典，包含：
                - title: 任务标题
                - description: 任务描述
                - checklist: 清单项列表
                - assignee: 被分配人姓名（可选）
                - attachments: 附件列表（可选）
        
        Returns:
            创建的卡片数据
        """
        # 获取看板数据
        board_data = self.get_board_data()
        lists = board_data.get("lists", [])
        members = board_data.get("members", [])
        
        # 查找默认列表
        list_id = self.find_list_id(lists, self.default_list)
        if not list_id:
            raise ValueError(f"找不到列表: {self.default_list}")
        
        # 匹配成员
        member_id = None
        if task_data.get("assignee"):
            member_id = self.find_member_id(members, task_data["assignee"])
        
        # 计算截止日期
        due_date = self.get_last_workday()
        
        # 创建卡片
        card = self.create_card(
            name=task_data["title"],
            desc=task_data["description"],
            id_list=list_id,
            id_members=[member_id] if member_id else None,
            due=due_date
        )
        
        # 添加清单
        if task_data.get("checklist"):
            self.add_checklist(card["id"], "任务清单", task_data["checklist"])
        
        return card


def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python trello_task_creator.py <task_json_file>")
        sys.exit(1)
    
    # 读取任务数据
    task_file = sys.argv[1]
    with open(task_file, 'r', encoding='utf-8') as f:
        task_data = json.load(f)
    
    # 创建任务
    creator = TrelloTaskCreator()
    card = creator.create_task(task_data)
    
    print(f"任务创建成功!")
    print(f"卡片URL: {card.get('url')}")
    print(f"卡片ID: {card.get('id')}")


if __name__ == "__main__":
    main()
