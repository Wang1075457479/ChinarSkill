# Trello API 文档

## 基础配置

API基础URL：`https://api.trello.com/1`

认证方式：所有请求都需要携带 `key` 和 `token` 参数

## 核心API端点

### 1. 获取看板信息

```
GET /boards/{boardId}?key={key}&token={token}&lists=open&cards=open&members=all
```

**参数：**
- `lists=open`：获取所有开放列表
- `cards=open`：获取所有开放卡片
- `members=all`：获取所有成员

**响应：**
包含看板信息、列表、卡片、成员的完整JSON

### 2. 创建卡片

```
POST /cards?key={key}&token={token}
```

**请求体参数：**
- `name`：卡片标题（必填）
- `desc`：卡片描述
- `idList`：列表ID（必填）
- `idMembers`：成员ID数组
- `due`：截止日期（ISO格式）
- `pos`：位置（默认底部）

### 3. 添加清单

```
POST /cards/{cardId}/checklists?key={key}&token={token}
```

**请求体参数：**
- `name`：清单名称
- `pos`：位置

### 4. 添加清单项

```
POST /checklists/{checklistId}/checkItems?key={key}&token={token}
```

**请求体参数：**
- `name`：清单项名称
- `pos`：位置
- `checked`：是否已完成（true/false）

### 5. 添加附件

```
POST /cards/{cardId}/attachments?key={key}&token={token}
```

**请求体参数：**
- `file`：文件（multipart/form-data）
- `name`：附件名称
- `url`：URL（可选，替代文件上传）

## 使用示例

### Python示例：创建卡片

```python
import requests

API_KEY = "your_api_key"
TOKEN = "your_token"
BASE_URL = "https://api.trello.com/1"

def create_card(name, desc, id_list, id_members=None, due=None):
    url = f"{BASE_URL}/cards"
    params = {
        "key": API_KEY,
        "token": TOKEN
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
    return response.json()
```

### 日期计算：当月最后一个工作日

```python
from datetime import datetime, timedelta
import calendar

def get_last_workday(year, month):
    # 获取当月最后一天
    last_day = calendar.monthrange(year, month)[1]
    date = datetime(year, month, last_day)
    
    # 如果是周六（5）或周日（6），向前调整
    while date.weekday() >= 5:
        date -= timedelta(days=1)
    
    return date.strftime("%Y-%m-%d")
```

## 成员匹配

从看板成员列表中通过姓名匹配用户ID：

```python
def find_member_id(members, full_name):
    for member in members:
        if member.get("fullName") == full_name:
            return member.get("id")
    return None
```

## 列表查找

通过列表名称查找列表ID：

```python
def find_list_id(lists, list_name):
    for lst in lists:
        if lst.get("name") == list_name:
            return lst.get("id")
    return None
```
