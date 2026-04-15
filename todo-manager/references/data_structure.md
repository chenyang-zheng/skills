# 待办事项数据结构

## todo.json 格式（主数据源）

todo.json 是所有待办事项的主数据源，包含所有任务的完整状态信息。

### 基本结构

```json
{
  "todos": [
    {
      "id": 1,
      "content": "任务内容描述",
      "priority": "high",
      "created": "2026-03-02",
      "completed": false
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| id | integer | ✅ | 唯一标识符，自动递增 | 1 |
| content | string | ✅ | 任务标题或内容 | "完成信用卡记账工作流" |
| priority | string | ❌ | 优先级：high/medium/low | "high" |
| created | string | ✅ | 创建日期，YYYY-MM-DD | "2026-03-02" |
| completed | boolean | ✅ | 完成状态 | false |
| completed_at | string | ❌ | 完成时间，`YYYY-MM-DD HH:MM:SS` | "2026-03-12 10:30:00" |
| due_date | string | ❌ | 截止日期，YYYY-MM-DD | "2026-03-07" |
| category | string | ❌ | 分类标签 | "work" |

### 示例数据

```json
{
  "todos": [
    {
      "id": 1,
      "content": "3/7(周五) 前解决信用卡记账的工作流",
      "priority": "high",
      "created": "2026-03-02",
      "completed": false,
      "due_date": "2026-03-07"
    },
    {
      "id": 2,
      "content": "3/8(周六) 晚5点 何院长聚餐(定在前滩)",
      "priority": "high",
      "created": "2026-03-02",
      "completed": false,
      "due_date": "2026-03-08"
    }
  ]
}
```

### 默认展示策略

- 日常查询默认展示：
  - 所有未完成事项
  - 最近 3 天内完成的事项
- 已完成超过 3 天的事项继续保留在 `todo.json` 中做备案，但默认不展示。
- 只有用户明确要求查看“已完成 / 历史 / 全部事项”时，才读取和展示全部已完成记录。

## MEMORY.md 格式（固定待办事项）

每个待办事项包含以下核心字段：

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| title | string | ✅ | 任务标题 | "每周二下午手法" |
| category | string | ❌ | 分类标签 | "health"、"work"、"shopping" |
| priority | enum | ❌ | 优先级：high/medium/low，默认 medium | "high" |
| due_time | string | ❌ | 截止时间，ISO 8601格式或自然语言 | "2026-03-11T15:00:00+08:00" |
| status | enum | ✅ | 状态：pending/in_progress/completed | "pending" |
| recurrence | enum | ❌ | 重复周期：daily/weekly/monthly/yearly | "weekly" |
| last_updated | string | ✅ | 最后更新时间，ISO 8601 | "2026-03-06T08:30:00+08:00" |
| notes | string | ❌ | 备注信息 | "记得带按摩油" |

## MEMORY.md 格式

MEMORY.md 中的固定待办事项部分：

```markdown
## 固定待办事项

### 每周二下午3:00 - 手法
- 时间：每周二 15:00
- 优先级：medium
- 状态：pending
- 重复：weekly
- 下次提醒：2026-03-11T15:00:00+08:00
- 备注：固定安排，完成后更新当日memory

### 京东红包
- 优先级：low
- 状态：pending
- 重复：periodic_check
- 备注：需要定期提醒用户关注京东红包活动
```

## memory/YYYY-MM-DD.md 格式

当日任务执行记录：

```markdown
## 任务执行

### [15:00] 每周二手法
- 状态：completed
- 完成时间：2026-03-11T15:45:00+08:00
- 备注：完成，下次安排在 2026-03-18

### 待办
- [ ] 下午4点开会
- [ ] 整理发票
```

## heartbeat_state.json 格式

定期检查状态跟踪：

```json
{
  "lastChecks": {
    "固定待办事项": 1709731200,
    "京东红包": 1709731200
  },
  "nextReminders": {
    "每周二手法": 1710336000,
    "京东红包": null
  }
}
```

## 字段说明

### recurrence (重复周期)

- **daily** - 每天重复
- **weekly** - 每周重复（需要配合具体时间点）
- **monthly** - 每月重复
- **yearly** - 每年重复
- **periodic_check** - 周期性检查，无固定时间（如促销活动提醒）
- **null** - 不重复，一次性任务

### status (状态)

- **pending** - 待办，尚未开始
- **in_progress** - 进行中
- **completed** - 已完成
- **cancelled** - 已取消

### priority (优先级)

- **high** - 高优先级，需要重点关注
- **medium** - 中等优先级，正常处理
- **low** - 低优先级，可以延后

## 时间格式

使用 ISO 8601 标准格式：

- 完整时间：`2026-03-06T15:00:00+08:00`
- 日期：`2026-03-06`
- 自然语言：`每周二 15:00`、`2026年3月6日`

在存储时统一转换为 ISO 8601 格式便于计算和排序。
