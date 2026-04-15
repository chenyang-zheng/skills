# Memory 文件集成工作流

## 文件分工

### todo.json（主数据源）
**用途：** 所有待办事项的持久化存储和状态管理

**适用场景：**
- 所有待办任务的增删改查
- 快速筛选和排序
- 任务状态跟踪
- 数据同步的主数据源

**文件位置：** `/workspace/projects/workspace/todo.json`

**操作方式：** 通过 `scripts/todo_json.py` 脚本进行读写

### MEMORY.md
**用途：** 长期、固定的待办事项和重要提醒

**适用场景：**
- 固定周期性任务（每周、每月）
- 长期跟踪的重要事项
- 不需要频繁变动的信息

**示例：**
```markdown
## 固定待办事项

### 每周二下午3:00 - 手法
- 时间：每周二 15:00
- 优先级：medium
- 状态：pending
- 重复：weekly
- 下次提醒：2026-03-11T15:00:00+08:00
```

### memory/YYYY-MM-DD.md
**用途：** 当天的任务执行记录、临时待办、日常事件

**适用场景：**
- 一次性任务
- 当天临时安排
- 任务完成记录
- 日常流水日志

**示例：**
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

## 工作流程

### 1. 添加待办事项

**判断存储位置：**
- 固定周期性任务 → MEMORY.md 的"固定待办事项"部分
- 一次性任务或当天临时安排 → memory/YYYY-MM-DD.md 的"待办"部分

**步骤：**
1. 读取目标文件
2. 解析任务信息（标题、时间、优先级、周期等）
3. 按照数据结构格式添加条目
4. 如果是周期性任务，计算并设置下次提醒时间

### 2. 查询待办事项

**合并查询：**
1. 读取 MEMORY.md 中的固定待办
2. 读取当天的 memory/YYYY-MM-DD.md
3. 合并去重
4. 按条件筛选（时间、状态、分类）
5. 排序后呈现

**示例查询逻辑：**
```
查询"今天的待办"：
1. 从 MEMORY.md 筛选出 recurrence=daily/weekly/periodic 且下次提醒在今天的任务
2. 从 memory/YYYY-MM-DD.md 读取"待办"部分
3. 合并并按优先级排序
```

### 3. 标记任务完成

**一次性任务：**
1. 在 memory/YYYY-MM-DD.md 中标记为 completed
2. 添加完成时间戳
3. 从 MEMORY.md 中删除（如果在固定待办中）

**周期性任务：**
1. 在当天的 memory/YYYY-MM-DD.md 中记录完成
2. 在 MEMORY.md 中更新状态为 completed（临时）
3. 计算下一次到期时间
4. 更新 MEMORY.md 中的"下次提醒"字段

**示例：**
```markdown
# 当天 memory 记录
### [15:00] 每周二手法
- 状态：completed
- 完成时间：2026-03-11T15:45:00+08:00
- 备注：完成，下次安排在 2026-03-18

# MEMORY.md 更新
- 下次提醒：2026-03-18T15:00:00+08:00
```

### 4. 定期检查（Heartbeat）

**检查频率：** 建议 2-4 次/天（根据 HEARTBEAT.md 配置）

**检查步骤：**
1. 读取 heartbeat_state.json 获取上次检查时间
2. 读取 MEMORY.md 中的固定待办
3. 计算当前时间与下次提醒时间的差距
4. 如果即将到期（< 2小时）或已过期，主动提醒用户
5. 更新 heartbeat_state.json 记录检查时间

**提醒判断逻辑：**
```python
current_time = now()
for task in MEMORY.md.固定待办事项:
    next_remind = parse_iso(task.下次提醒)
    if next_remind <= current_time + 2小时:
        send_remind(task)
    elif next_remind <= current_time and task.status != "completed":
        send_remind(task, type="overdue")
```

### 5. 维护和清理

**定期清理：**
- 已完成的当天临时待办（可在次日归档或删除）
- 过期的周期性任务（询问用户是否保留）

**归档策略：**
- 当月完成的任务 → memory/YYYY-MM-archive.md
- 重要任务记录 → MEMORY.md 的"已完成历史"部分

## 文件读取顺序

1. **优先级1：** MEMORY.md（固定待办、长期信息）
2. **优先级2：** memory/YYYY-MM-DD.md（当天任务）
3. **优先级3：** references/heartbeat_state.json（状态跟踪）

## 错误处理

**文件不存在：**
- memory/YYYY-MM-DD.md 不存在时自动创建
- heartbeat_state.json 不存在时使用默认值初始化

**格式错误：**
- 解析失败时提示用户并尝试修复
- 保留原始内容，添加格式修正标记

**冲突处理：**
- 同一任务在多个文件中存在 → 以 MEMORY.md 为准
- 时间戳冲突 → 使用最新时间戳
