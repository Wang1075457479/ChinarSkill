#!/usr/bin/env python3
"""
Trello任务创建脚本
功能：
1. 智能任务拆解
2. 自动计算截止日期（当月最后一个工作日）
3. 成员匹配
4. 创建Trello卡片
5. 支持XMind文件解析
"""

import requests
import json
import os
from datetime import datetime, timedelta
import calendar
import re
from xmindparser import xmind_to_dict


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
        
        # 默认加载references/config.json
        if not config_path:
            default_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../references/config.json")
            if os.path.exists(default_config):
                config_path = default_config
        
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
    
    def normalize_title(self, title):
        """标准化标题格式：【分类】-任务名（≤30字，精炼显示）"""
        # 分类枚举
        categories = ['开发', '优化', '安全', '规则', '设计', '测试', '文档', '重构', 'BUG']
        
        # 首先检查是否已经符合规范格式
        match = re.match(r'【(.+?)】-(.+)', title)
        if match:
            existing_category = match.group(1)
            existing_task = match.group(2)
            # 如果分类合法且长度符合要求，直接返回
            if existing_category in categories and len(title) <= 30:
                return title
            # 否则提取任务内容，重新处理
            title = existing_task.strip()
        
        # 自动识别分类（优先级顺序）
        category = '设计'  # 默认分类
        lower_title = title.lower()
        
        # BUG类优先级最高
        if 'bug' in lower_title or '故障' in lower_title or '异常' in lower_title or '错误' in lower_title or '崩溃' in lower_title:
            category = 'BUG'
        # 开发类
        elif '开发' in lower_title or '实现' in lower_title or '功能' in lower_title or '新增' in lower_title or '搭建' in lower_title:
            category = '开发'
        # 优化类
        elif '优化' in lower_title or '性能' in lower_title or '提升' in lower_title or '改进' in lower_title or '修复' in lower_title:
            category = '优化'
        # 测试类
        elif '测试' in lower_title or '验证' in lower_title or '联调' in lower_title or '回归' in lower_title:
            category = '测试'
        # 文档类
        elif '文档' in lower_title or '编写' in lower_title or '总结' in lower_title or '说明' in lower_title:
            category = '文档'
        # 设计类
        elif '设计' in lower_title or 'ui' in lower_title or '原型' in lower_title or '效果图' in lower_title:
            category = '设计'
        # 安全类
        elif '安全' in lower_title or '权限' in lower_title or '漏洞' in lower_title:
            category = '安全'
        # 规则类
        elif '规则' in lower_title or '规范' in lower_title or '标准' in lower_title:
            category = '规则'
        # 重构类
        elif '重构' in lower_title or '重写' in lower_title or '架构' in lower_title:
            category = '重构'
        
        # 清理标题中的冗余内容
        # 移除分类词
        for cat in categories:
            title = title.replace(cat, '').replace(cat.lower(), '').strip()
        # 移除bug相关词汇
        title = re.sub(r'bug|BUG|故障|异常|错误|崩溃', '', title, flags=re.IGNORECASE).strip()
        # 移除开头冗余词
        title = re.sub(r'^(这是一个|新的|问题|任务|关于|有关)', '', title).strip()
        # 移除末尾冗余词
        title = re.sub(r'(的问题|的bug|的任务|的功能)$', '', title).strip()
        # 清理多余的标点和数字前缀
        title = re.sub(r'^[0-9一二三四五六七八九十、. \-]+', '', title).strip()
        title = re.sub(r'[,，。；;！!？?\s]+$', '', title).strip()
        # 清理多余的中括号和短横线
        title = re.sub(r'[【】\[\]-]+', '', title).strip()
        
        # 控制长度，≤30字（包含符号）
        available_length = 30 - (len(category) + 3)
        if len(title) > available_length:
            # 优先截断后半部分，保留核心信息
            task_name = title[:available_length - 1] + "…"  # 多减1，给省略号留位置
        else:
            task_name = title
        
        # 生成新标题
        new_title = f"【{category}】-{task_name}"
        
        return new_title
    
    def normalize_checklist(self, checklist_items):
        """标准化清单格式：统一使用 1、2、3 前缀，避免重复，过滤无效项"""
        normalized = []
        seen = set()
        
        for item in checklist_items:
            if not item or len(item.strip()) < 2:
                continue
            
            # 清理原有的序号前缀
            clean_item = re.sub(r'^[0-9一二三四五六七八九十、. \-]+', '', item.strip())
            clean_item = re.sub(r'^第[0-9一二三四五六七八九十]+[步骤条项]', '', clean_item).strip()
            
            if not clean_item or clean_item in seen:
                continue
            
            seen.add(clean_item)
            normalized.append(clean_item)
            
            # 最多50条
            if len(normalized) >= 50:
                break
        
        # 如果不足3条，自动补充
        while len(normalized) < 3:
            normalized.append(f"完成相关工作第{len(normalized)+1}步")
        
        # 添加标准序号前缀
        result = [f"{i+1}、{item}" for i, item in enumerate(normalized)]
        
        return result
    
    def parse_xmind(self, xmind_path):
        """解析XMind文件，返回任务数据列表（每个画布一个任务）"""
        if not os.path.exists(xmind_path):
            raise FileNotFoundError(f"XMind文件不存在: {xmind_path}")
        
        # 解析XMind
        xmind_data = xmind_to_dict(xmind_path)
        tasks = []
        
        # 每个画布对应一个任务
        for sheet in xmind_data:
            sheet_title = sheet.get('title', '未命名任务')
            
            # 提取根节点的子节点作为清单项
            root_topic = sheet.get('topic', {})
            checklist_items = []
            all_nodes = []
            
            # 递归解析子节点
            def parse_topic(topic, depth=0):
                title = topic.get('title', '').strip()
                if title and depth > 0:  # 根节点是画布标题，不加入清单
                    all_nodes.append(title)
                    # 只提取一级和二级节点作为清单项，避免太多
                    if depth <= 2:
                        checklist_items.append(title)
                
                # 处理子节点
                for child in topic.get('topics', []):
                    parse_topic(child, depth + 1)
            
            parse_topic(root_topic)
            
            # 生成精炼描述（≤300字）
            description = f"【{sheet_title}】\n"
            description += f"核心功能：{len(all_nodes)}个功能点，包含"
            # 提取前5个核心节点作为描述
            core_features = [node for node in all_nodes[:5] if len(node) > 2]
            description += "、".join(core_features)
            if len(all_nodes) > 5:
                description += f"等{len(all_nodes)}项内容\n"
            else:
                description += "\n"
            description += "主要目标：完成系统设计、开发和落地实施"
            
            # 限制描述长度≤300字
            if len(description) > 300:
                description = description[:297] + "…"
            
            # 生成任务数据
            task_data = {
                "title": self.normalize_title(sheet_title),
                "description": description,
                "checklist": self.normalize_checklist(checklist_items),
                "assignee": None
            }
            
            tasks.append(task_data)
        
        return tasks
    
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
        
        # 标准化标题
        normalized_title = self.normalize_title(task_data["title"])
        
        # 标准化清单
        normalized_checklist = self.normalize_checklist(task_data.get("checklist", []))
        
        # 匹配成员
        member_id = None
        if task_data.get("assignee"):
            member_id = self.find_member_id(members, task_data["assignee"])
        
        # 计算截止日期
        due_date = self.get_last_workday()
        
        # 创建卡片
        card = self.create_card(
            name=normalized_title,
            desc=task_data["description"],
            id_list=list_id,
            id_members=[member_id] if member_id else None,
            due=due_date
        )
        
        # 添加清单
        if normalized_checklist:
            self.add_checklist(card["id"], "任务清单", normalized_checklist)
        
        return card
    
    def create_task_from_xmind(self, xmind_path, assignee=None):
        """从XMind文件创建任务（每个画布一个任务卡片）"""
        tasks = self.parse_xmind(xmind_path)
        created_cards = []
        
        for task_data in tasks:
            if assignee:
                task_data["assignee"] = assignee
            card = self.create_task(task_data)
            created_cards.append(card)
        
        return created_cards


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
