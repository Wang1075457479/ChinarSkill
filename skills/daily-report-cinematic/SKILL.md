---
name: daily-report-cinematic
description: 影视级全景动态日报生成器 (Ultra Premium Cinematic Edition)。当收到"生成今日日报"、"发日报"、"工作总结"等指令时，汇集今日系统运行数据，生成符合当前情绪的狗狗陪伴图，注入HTML模板，录制15秒24帧1080P影视级汇报视频，并推送到飞书。
---

# 影视级全景动态日报生成器

## 触发条件

当用户说以下任何内容时触发：
- "生成今日日报"
- "发日报"
- "工作总结"
- "daily report"

## 工作流程

### Step 1: 数据聚合与图像提取

1. 统计今日系统数据：
   - 新增文件数
   - API调用次数
   - 已执行的核心任务流

2. 生成情感图：
   - 提取预设狗狗形象（`/root/.openclaw/workspace/dog.jpg`）
   - 结合系统负载（极度忙碌/平稳运行/休眠）
   - 生成16:9构图的超清宠物图

3. 构建JSON数据：
```json
{
    "date": "MARCH 02, 2026",
    "summary": "简短的一句话英文/中文总结。<br><span class='text-[var(--accent)]'>高亮文字</span>",
    "quote": "以狗狗口吻对主人说的贴心话",
    "tags": ["高亮标签1", "高亮标签2", "高亮标签3"],
    "tasks": [
        { "title": "任务主标题", "desc": "任务详细描述" }
    ],
    "metrics": {
        "m1": { "label": "FILES HANDLED", "val": 130, "max": 150 },
        "m2": { "label": "API CALLS", "val": 542, "max": 600 }
    }
}
```

- 如果今日无任务，`tasks` 为空数组 `[]`，系统自动进入休眠UI模式

### Step 2: 模板注入与渲染

1. 读取 `assets/cinematic-template.html`
2. 替换 `DOG_IMAGE_URL` 为实际图片链接
3. 替换 `todayData` JSON对象
4. 保存为 `report.html`

### Step 3: 无头浏览器录屏（CRITICAL）

**必须严格遵守以下参数：**

- **视口锁定**: `width: 1920, height: 1080, deviceScaleFactor: 1`
- **禁止裁剪**: 不要元素定位截图，直接录制整个屏幕
- **视频录制规范**:
  - FPS: 24
  - 时长: 15秒（页面内置15秒3段式轮播特效）
  - 分辨率: 1920x1080
- **降级方案**: 如不支持视频录制，等待12秒后截取全屏PNG

### Step 4: 飞书推送

1. 上传MP4视频或PNG截图到飞书
2. 获取 `file_key` 或 `image_key`
3. 推送至飞书对话框

## 使用方法

```bash
cd /root/.openclaw/workspace/ChinarSkill/skills/daily-report-cinematic
npm install
node scripts/generator.js
```

## 输出文件

- 视频：`/root/.openclaw/workspace/daily-report-output/report.mp4`
- 截图：`/root/.openclaw/workspace/daily-report-output/report.png`
- HTML：`/root/.openclaw/workspace/daily-report-output/report.html`

## 依赖

- Node.js >= 18
- Playwright
- ffmpeg
- 中文字体

## 配置

在 `scripts/generator.js` 中可修改：
- `fps`: 帧率（默认24）
- `duration`: 录制时长（默认15秒）
- `width/height`: 分辨率（默认1920x1080）
