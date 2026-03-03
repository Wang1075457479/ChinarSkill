---
name: daily-report-premium
description: 极简高级美学日报生成器 (Premium Daily Report)。当你收到诸如"生成今日日报"、"总结今天的工作"、"发日报"等指令时，触发此 Skill。生成包含系统数据、情绪陪伴图的高级动态视频日报，并推送到飞书。
---

# 极简高级美学日报生成器

## 触发条件

当用户说以下任何内容时触发此 Skill：
- "生成今日日报"
- "总结今天的工作"
- "发日报"
- "daily report"
- "今日总结"

## 工作流程

### Step 1: 数据聚合与图像生成

1. 分析今日系统数据：
   - 执行的任务数量
   - 创建的文件数量
   - API 调用次数
   - 会话活动情况

2. 获取狗狗情绪图片：
   - 检查 `/root/.openclaw/workspace/dog.jpg` 是否存在
   - 如存在，使用本地图片；否则使用默认图片

3. 构建 JSON 数据：
```json
{
    "date": "MARCH 02, 2026",
    "summary": "简短的一句话英文/中文总结，可以使用 <span class='text-[var(--accent)]'>高亮文字</span> 强调关键数据。",
    "quote": "以狗狗的口吻，根据今天的工作量对主人说的一句贴心的话。",
    "tags": ["高亮标签1", "高亮标签2", "高亮标签3"],
    "tasks": [
        { "title": "任务标题", "desc": "任务简短描述" }
    ],
    "metrics": {
        "m1": { "label": "FILES HANDLED", "val": 130, "max": 150 },
        "m2": { "label": "API CALLS", "val": 542, "max": 600 }
    }
}
```

- 如果今日无事，`tasks` 数组为空，`metrics` 的 `val` 设置为 0，系统会自动切换到绿色的休眠 UI 模式

### Step 2: 模板注入

1. 读取 `assets/template.html` 模板文件
2. 替换 `DOG_IMAGE_URL` 为实际图片路径
3. 替换 `todayData` JSON 对象为生成的数据
4. 保存为 `report.html`

### Step 3: 无头浏览器影视级录制

1. 使用 Playwright 启动 Chromium 浏览器
2. 设置视口大小为 1920 x 1080（16:9 比例，无黑边）
3. 打开本地生成的 `report.html`
4. 等待 2 秒让字体等资源加载
5. 录制 6 秒视频（120 帧 @ 20fps）
6. 使用 ffmpeg 合成 MP4 视频

### Step 4: 飞书推送

1. 调用飞书 API 上传媒体文件
2. 获取 file_key
3. 发送视频消息给用户

## 使用方法

直接运行脚本：

```bash
cd /root/.openclaw/workspace/ChinarSkill/skills/daily-report-premium
node scripts/generator.js
```

或通过 OpenClaw 调用：

当用户说"生成今日日报"时，自动执行上述工作流程。

## 输出文件

- 视频：`/root/.openclaw/workspace/daily-report-output/daily_report_YYYY-MM-DD.mp4`
- HTML：`/root/.openclaw/workspace/daily-report-output/report.html`

## 依赖

- Node.js >= 18
- Playwright (`npm install playwright`)
- ffmpeg (系统已安装)
- 中文字体（Noto Sans CJK）

## 配置

在 `scripts/generator.js` 中可修改：
- `width/height`: 视频分辨率
- `videoDuration`: 视频时长（毫秒）
- `fps`: 帧率
- `outputDir`: 输出目录
