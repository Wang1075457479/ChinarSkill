import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from datetime import datetime
import os
import sys
import time
sys.path.append("..")

class TrelloAutoOrganizer:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)['trello']
        
        self.api_key = self.config['apiKey']
        self.token = self.config['token']
        self.board_id = self.config['boardId']
        self.feishu_chat_id = "oc_e54da34b0cc94c16ec045870860f0bb8"
        self.feishu_app_id = self.config.get('feishuAppId', '')
        self.feishu_app_secret = self.config.get('feishuAppSecret', '')
        
        # 创建重试会话，自动处理网络失败和限流
        self.session = self._create_retry_session()
        
        # 本地记录文件
        self.record_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "card_modify_records.json")
        # 加载历史修改记录
        self.modify_records = self._load_records()
        
        # 分类枚举
        self.categories = ['开发', '优化', '安全', '规则', '设计', '测试', '文档', '重构', 'BUG']
        # 无意义词过滤
        self.meaningless = {'大小', '方式', '分类', '类型', '备注', '说明', '测试', '状态', '完成', '未开始'}
        
        print(f"初始化完成，看板ID：{self.board_id}")
        print(f"历史记录：{len(self.modify_records)} 个卡片已处理过")
    
    def _create_retry_session(self, retries=3, backoff_factor=1):
        """创建带自动重试的HTTP会话"""
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,  # 重试间隔：1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
            allowed_methods=["GET", "POST", "PUT"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    
    def _rate_limit(self):
        """速率控制：5请求/秒，符合Trello限流规则（100请求/10秒）"""
        time.sleep(0.2)
    
    def _load_records(self):
        """加载历史修改记录"""
        if os.path.exists(self.record_file):
            try:
                with open(self.record_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_records(self):
        """保存修改记录到本地"""
        with open(self.record_file, 'w', encoding='utf-8') as f:
            json.dump(self.modify_records, f, ensure_ascii=False, indent=2)
    
    def _get_card_hash(self, card):
        """计算卡片内容哈希，用于检测变更"""
        content = f"{card['name']}{card['desc']}{len(card.get('checklists', []))}"
        return hash(content)
    
    def get_all_cards(self):
        """获取看板下所有卡片"""
        url = f"https://api.trello.com/1/boards/{self.board_id}/cards"
        params = {
            'key': self.api_key,
            'token': self.token,
            'checklists': 'all'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            self._rate_limit()
            if response.status_code == 200:
                cards = response.json()
                print(f"获取到 {len(cards)} 个卡片")
                return cards
            else:
                print(f"获取卡片失败：{response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"获取卡片异常：{str(e)}")
            return []
    
    def normalize_title(self, title):
        """标准化标题格式：【分类】-任务名（≤30字，精炼显示）"""
        # 首先检查是否已经符合规范格式
        match = re.match(r'【(.+?)】-(.+)', title)
        if match:
            existing_category = match.group(1)
            existing_task = match.group(2)
            # 如果分类合法且长度符合要求，直接返回不修改
            if existing_category in self.categories and len(title) <= 30:
                return title, None
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
        for cat in self.categories:
            title = title.replace(cat, '').replace(cat.lower(), '').strip()
        # 移除bug相关词汇
        title = re.sub(r'bug|BUG|故障|异常|错误|崩溃', '', title, flags=re.IGNORECASE).strip()
        # 移除开头冗余词
        title = re.sub(r'^(这是一个|新的|问题|任务|关于|有关)', '', title).strip()
        # 移除末尾冗余词
        title = re.sub(r'(的问题|的bug|的任务|的功能)$', '', title).strip()
        # 清理多余的标点
        title = re.sub(r'[,，。；;！!？?\s]+$', '', title).strip()
        
        # 控制长度，≤30字（包含符号）
        # 【分类】- 占的字符数：2（括号） + len(category) + 1（横杠） = len(category) + 3
        # 注意：中文每个字占2个字符？不，Python中字符串长度是按字符数计算，不是字节
        available_length = 30 - (len(category) + 3)
        if len(title) > available_length:
            # 优先截断后半部分，保留核心信息
            task_name = title[:available_length - 1] + "…"  # 多减1，给省略号留位置
        else:
            task_name = title
        
        # 生成新标题
        new_title = f"【{category}】-{task_name}"
        
        # 检查是否需要修改
        if len(new_title) <= 30 and new_title != title:
            return new_title, f"自动识别分类为{category}，标题已标准化精炼"
        else:
            return new_title, None
    
    def generate_checklist(self, card):
        """根据卡片描述生成清单（如果没有清单）"""
        # 检查是否已有清单
        if card.get('checklists', []):
            return None, "已有清单，无需生成"
        
        desc = card.get('desc', '')
        if not desc:
            return None, "无描述内容，无法生成清单"
        
        # 提取描述中的任务点
        checklist_items = []
        
        # 按行拆分
        lines = desc.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 过滤无意义行
            if len(line) <= 2 or line in self.meaningless:
                continue
            
            # 清理符号
            line = re.sub(r'^[•\-\d、. ]+', '', line).strip()
            
            if line and len(checklist_items) < 50:
                # 生成可执行的任务描述
                if not any(keyword in line for keyword in ['完成', '实现', '开发', '优化', '完善']):
                    line = f"完成{line}相关工作"
                checklist_items.append(line)
        
        if checklist_items:
            return checklist_items, f"自动生成 {len(checklist_items)} 条清单项"
        else:
            return None, "无法提取有效清单项"
    
    def update_card(self, card_id, new_title=None, new_desc=None, keep_original_desc=True):
        """更新卡片信息，保留原有描述、附件、关联等所有信息"""
        url = f"https://api.trello.com/1/cards/{card_id}"
        params = {
            'key': self.api_key,
            'token': self.token
        }
        
        # 只更新需要修改的字段，其他字段保持不变
        if new_title:
            params['name'] = new_title
        # 描述默认不修改，仅当明确指定且不保留原描述时才更新
        if new_desc and not keep_original_desc:
            params['desc'] = new_desc
        
        try:
            response = self.session.put(url, params=params, timeout=30)
            self._rate_limit()
            return response.status_code == 200
        except Exception as e:
            print(f"更新卡片异常：{str(e)}")
            return False
    
    def add_checklist_to_card(self, card_id, items):
        """给卡片添加清单"""
        url = "https://api.trello.com/1/checklists"
        params = {
            'key': self.api_key,
            'token': self.token,
            'idCard': card_id,
            'name': '执行步骤'
        }
        
        try:
            response = self.session.post(url, params=params, timeout=30)
            self._rate_limit()
            if response.status_code == 200:
                checklist_id = response.json()['id']
                for i, item in enumerate(items, 1):
                    item_url = f"https://api.trello.com/1/checklists/{checklist_id}/checkItems"
                    item_params = {
                        'key': self.api_key,
                        'token': self.token,
                        'name': f"{i}、{item[:100]}"
                    }
                    self.session.post(item_url, params=item_params, timeout=10)
                    self._rate_limit()
                return True
            return False
        except Exception as e:
            print(f"添加清单异常：{str(e)}")
            return False
    
    def get_feishu_token(self):
        """获取飞书访问令牌"""
        if not self.feishu_app_id or not self.feishu_app_secret:
            return None
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        params = {
            "app_id": self.feishu_app_id,
            "app_secret": self.feishu_app_secret
        }
        
        try:
            response = self.session.post(url, json=params, timeout=30)
            self._rate_limit()
            if response.status_code == 200:
                return response.json().get('tenant_access_token')
            return None
        except Exception as e:
            print(f"获取飞书Token异常：{str(e)}")
            return None
    
    def send_feishu_notification(self, report):
        """发送飞书群通知"""
        token = self.get_feishu_token()
        if not token:
            print("未配置飞书AppID和AppSecret，跳过通知")
            return False
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        params = {
            "receive_id_type": "chat_id"
        }
        
        content = {
            "receive_id": self.feishu_chat_id,
            "msg_type": "interactive",
            "content": json.dumps({
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**Trello看板自动整理完成**\n\n整理时间：{now}\n\n整理结果：\n{report}"
                        }
                    }
                ],
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "Trello自动整理通知"
                    },
                    "template": "blue"
                }
            })
        }
        
        try:
            response = self.session.post(url, params=params, headers=headers, json=content, timeout=30)
            self._rate_limit()
            if response.status_code == 200:
                print("飞书通知发送成功")
                return True
            else:
                print(f"飞书通知发送失败：{response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"飞书通知发送异常：{str(e)}")
            return False
    
    def run_organize(self):
        """执行整理任务"""
        print("开始自动整理Trello看板...")
        
        cards = self.get_all_cards()
        if not cards:
            return "未获取到卡片，整理结束"
        
        report = []
        processed_count = 0
        updated_count = 0
        skipped_count = 0
        
        for card in cards:
            card_id = card['id']
            card_name = card['name']
            current_hash = self._get_card_hash(card)
            
            # 检查是否已经处理过且无变更
            if card_id in self.modify_records:
                if self.modify_records[card_id]['hash'] == current_hash:
                    skipped_count += 1
                    continue
            
            processed_count += 1
            changes = []
            
            print(f"\n处理卡片：{card_name}")
            
            # 1. 标准化标题（仅更新标题，保留原有描述、附件、关联等所有信息）
            new_title, title_change = self.normalize_title(card_name)
            if title_change:
                if self.update_card(card_id, new_title=new_title, keep_original_desc=True):
                    changes.append(f"标题标准化：{title_change}")
                    changes.append(f"   原标题：{card_name}")
                    changes.append(f"   新标题：{new_title}")
                    updated_count += 1
                else:
                    changes.append(f"标题更新失败")
            
            # 2. 生成清单（如果没有清单，添加新清单，不影响原有内容）
            checklist_items, checklist_change = self.generate_checklist(card)
            if checklist_items:
                if self.add_checklist_to_card(card_id, checklist_items):
                    changes.append(f"{checklist_change}")
                    updated_count += 1
                else:
                    changes.append(f"清单添加失败")
            
            # 记录修改
            self.modify_records[card_id] = {
                'last_modified': datetime.now().isoformat(),
                'hash': current_hash,
                'title': new_title if title_change else card_name,
                'changes': changes
            }
            
            if changes:
                report.append(f"\n### 卡片 {processed_count}")
                report.extend(changes)
        
        # 保存记录
        self._save_records()
        
        # 生成汇总报告
        summary = f"整理汇总\n- 总卡片数：{len(cards)}\n- 跳过无变更卡片：{skipped_count}\n- 处理卡片数：{processed_count}\n- 更新卡片数：{updated_count}"
        report.insert(0, summary)
        
        full_report = '\n'.join(report)
        print("\n" + "="*50)
        # 修复GBK编码问题，过滤特殊字符
        print(full_report.encode('gbk', errors='ignore').decode('gbk'))
        
        # 发送飞书通知
        if updated_count > 0:
            self.send_feishu_notification(full_report)
        
        return full_report

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "../references/config.json")
    organizer = TrelloAutoOrganizer(config_path)
    organizer.run_organize()
