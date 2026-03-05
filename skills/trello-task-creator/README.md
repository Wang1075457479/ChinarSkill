# Trello任务创建Skill

## 快速开始

### 1. 配置环境变量

在使用前，需要设置以下环境变量：

```powershell
# Windows PowerShell
$env:TRELLO_API_KEY = "YOUR_TRELLO_API_KEY"
$env:TRELLO_TOKEN = "YOUR_TRELLO_TOKEN"
$env:TRELLO_BOARD_ID = "YOUR_TRELLO_BOARD_ID"
```

### 2. 使用方式

直接在对话中说：
- `创建任务：开发登录页面`
- `给"王晨阳"创建一个数据导出功能的任务`
- `帮我建个任务：重构订单系统`

## 功能特性

✅ **智能标题生成** - 自动生成【分类】-任务标题格式，不超过15字  
✅ **自动分类识别** - 智能判断任务分类（开发/优化/安全/规则/设计/测试/文档/重构）  
✅ **任务拆解** - 一句话自动拆分为带数字前缀的清单  
✅ **成员分配** - 自动匹配看板成员  
✅ **智能截止日期** - 自动设置为当月最后一个工作日  
✅ **默认列表** - 自动放入"Not Start"列表  
✅ **附件上传** - 默默上传附件，不在描述中体现  

## 任务规范

### 标题格式
- 格式：`【分类】-任务标题`
- 分类（≤5字）：开发、优化、安全、规则、设计、测试、文档、重构
- 限制：总体不超过15个汉字
- 示例：`【开发】-登录页面`、`【优化】-性能提升`

### 清单格式
```
1、第一步
2、第二步
3、第三步
```

## 示例

**输入：** `创建任务：开发登录页面`

**输出：**
- 标题：`【开发】-登录页面`
- 描述：`开发登录页面`
- 清单：
  ```
  1、设计登录页面UI
  2、实现表单验证
  3、对接后端API
  4、添加错误提示
  5、测试登录功能
  ```

**更多示例：** 见 [examples.md](references/examples.md)

## 文件结构

```
trello-task-creator/
├── SKILL.md                    # Skill核心文档
├── README.md                   # 本文件
├── scripts/
│   ├── trello_task_creator.py  # Python脚本
│   └── task_template.json      # 任务数据模板
└── references/
    ├── api.md                  # API文档
    ├── config.example.json     # 配置文件示例
    └── examples.md             # 更多示例
```
