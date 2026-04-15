---
name: todo-manager
description: 管理待办事项的系统化技能。支持添加、查询、更新、标记完成待办事项，并与 `todo.json`、memory 文件系统、飞书多维表格保持一致。
---

# Todo Manager - 待办管理

## 核心能力

1. **添加待办** - 创建新任务，支持分类、优先级、截止时间、重复周期。
2. **查询待办** - 按时间、状态、分类、优先级筛选，并计算紧急程度。
3. **更新待办** - 修改任务内容、优先级、截止时间、分类等字段。
4. **标记完成** - 更新完成状态，并在需要时记录执行历史。
5. **定期提醒** - 管理固定待办、周期性任务和 heartbeat 检查。
6. **记录进度** - 在 memory 文件中记录长期提醒或当日执行情况。
7. **三向同步** - 维护 `todo.json`、memory 文件和飞书多维表格的一致性。

## 存储架构

- `todo.json`
  - 主数据源，所有本地任务状态都以它为准。
  - 添加、更新、完成、删除都必须先写这里。
- `MEMORY.md`
  - 可选的长期提醒存储。
  - 仅用于用户明确要求写入的固定待办、周期性提醒、长期重要事项。
- `memory/YYYY-MM-DD.md`
  - 用于当天执行记录、临时待办、完成说明。
- 飞书多维表格
  - 用于在线协作、备份、多端访问。
  - 启用同步时，待办变更需要同步过去。

**重要原则：**

1. `todo.json` 是主数据源。
2. `MEMORY.md` 不是默认同步目标；只有用户明确要求长期记住，或该事项本来就在 `MEMORY.md` 中时，才更新它。
3. 飞书多维表格是在线协作/备份层，不反向覆盖本地主状态。
4. 所有修改遵循“本地先写，外部后同步”。
5. 已完成事项默认保留在 `todo.json` 中做备案；完成超过 3 天的事项不进入日常展示，除非用户明确要求查看历史、全部事项或已完成事项。

**配置文件：**

- `/workspace/projects/.secrets/feishu/bitable_config.json`
- `/workspace/projects/.secrets/feishu/credentials.json`

## 日期安全规则

任何涉及日期、星期、相对时间的操作都必须先做校验。

**系统时间双重检验（强制）：**

1. 先确认当前系统时间，优先使用 `scripts/date_validator.py` 的 `get_current_date()`；无法直接调用时再使用 `session_status` 或 Python `datetime.now()`。
2. 基于确认后的当前日期计算目标日期，优先使用 `calculate_target_date(description)`，不得凭记忆估算。
3. 再次核对：
   - 当前日期是否正确；
   - 目标日期是否计算正确；
   - 星期是否与日期匹配。

**日期处理要求：**

- 显式日期 + 星期：使用 `scripts/date_validator.py` 的 `validate_date_weekday()` 校验。
- 截止日期紧急程度：使用 `get_days_until()` 和 `get_urgency_level()` 计算。
- 相对日期如“这周日”“下周日”“本月”“下月”：
  - 必须基于已确认的当前系统时间，通过 `calculate_target_date()` 计算；
  - 如果语义仍有歧义，先问用户再写入。

**常用规则：**

- “这周日” = 当前日期 + `(7 - 当前星期几)` 天。
- “下周日” = 当前日期 + `(14 - 当前星期几)` 天。
- “本月” = 当前月份月末。
- “下月” = 下个月月末。

## 工作流程

### 添加待办事项

当用户说“添加一个待办”“记下来”“提醒我”时：

1. 按 `references/data_structure.md` 的结构解析任务内容、时间、优先级、分类、周期。
2. 如果涉及日期，先执行“日期安全规则”。
3. 写入 `todo.json`：
   - 使用 `scripts/todo_json.py` 的 `add_todo()`；
   - 如需补充 `due_date`、`category` 等字段，再通过 `update_todo()` 更新。
4. 同步 memory：
   - 仅当用户明确要求“记入长期记忆 / 固定提醒 / 周期提醒”时，才写入 `MEMORY.md`；
   - 仅当用户明确要求记录当天执行情况或临时事项时，才写入对应 `memory/YYYY-MM-DD.md`。
5. 如果 Bitable 同步已启用：
   - 运行 `workspace/scripts/sync_todos_to_bitable.py` 生成同步队列；
   - 基于队列执行飞书多维表格同步；
   - 不得静默跳过失败，需提示或重试。

### 查询待办事项

当用户说“有什么待办”“查看任务”“今天有什么事”时：

1. 先通过 `get_current_date()` 确认当前系统时间，作为紧急程度计算基准。
2. 默认从 `todo.json` 读取“日常展示所需事项”：
   - 使用 `get_display_todos()`；
   - 默认包含未完成事项，以及最近 3 天内完成的事项。
3. 对包含日期的任务：
   - 校验日期/星期是否冲突；
   - 计算剩余天数和紧急程度。
4. 仅在以下情况补读 memory：
   - 用户明确要求查看长期固定提醒时，读取 `MEMORY.md`；
   - 用户明确要求查看当天执行记录或临时事项时，读取当天 `memory/YYYY-MM-DD.md`。
5. 合并去重并返回结果：
   - 同一任务优先采用 `todo.json` 的状态；
   - 标注紧急程度、日期异常、周期性信息；
   - 按条件筛选后排序呈现。
6. 如果用户明确要求“查看全部 / 查看已完成 / 查看历史”，再读取 `get_completed_todos()` 或相关备案数据。

### 标记任务完成

当用户说“完成了”“搞定了”“这个任务完成了”时：

1. 用 ID 或关键词定位任务。
2. 在 `todo.json` 中执行 `complete_todo()`。
3. 仅当用户明确要求记录完成过程时，在当天 `memory/YYYY-MM-DD.md` 记录完成时间和备注。
4. 仅当该事项已在 `MEMORY.md` 中维护，或用户明确要求长期记住时，才在 `MEMORY.md` 更新下次提醒或状态。
5. 如果 Bitable 同步已启用，同步线上状态。

### 更新待办事项

当用户说“修改待办”“更新任务”“改成...”时：

1. 在 `todo.json` 中定位任务。
2. 如果更新涉及日期，先执行“日期安全规则”。
3. 使用 `update_todo()` 更新字段。
4. 仅当用户明确要求，或该事项本来就在对应 memory 文件中时，才同步更新 memory 文件。
5. 如果 Bitable 同步已启用，同步线上记录。

### 数据迁移

当用户需要从旧数据迁移时：

1. 读取 `todo.json`。
2. 区分一次性任务、周期性任务、已完成任务。
3. 仅在用户明确要求长期保存时，才把长期/周期性内容整理进 `MEMORY.md`。
4. 把执行历史按需整理进对应的 `memory/YYYY-MM-DD.md`。
5. 如果启用了 Bitable，同步生成新的线上队列。

## 同步规则

- 添加 / 更新 / 完成：
  - `todo.json` 先更新；
  - `MEMORY.md` 仅在用户明确要求或该事项已在其中维护时同步；
  - `memory/YYYY-MM-DD.md` 仅在用户明确要求记录执行过程时同步；
  - Bitable 在启用时同步。
- 删除：
  - 从 `todo.json` 删除；
  - 若该事项明确同步过 memory，再决定是否清理对应记录；
  - Bitable 记录同步删除或标记失效。
- 冲突处理：
  - 以本地 `todo.json` 为准；
  - 飞书多维表格不反向覆盖本地主状态。

## Bitable 同步说明

- 当前脚本 `workspace/scripts/sync_todos_to_bitable.py` 负责：
  - 读取本地待办和配置；
  - 将待办转换为 Bitable 记录格式；
  - 生成 `workspace/bitable_sync_queue.json` 队列文件。
- 队列中当前会生成这些字段：
  - `任务名称`
  - `优先级`
  - `状态`
  - `分类`
  - `创建时间`
  - `截止日期`
  - `剩余天数`
  - `紧迫度`
  - `标签`
  - `进度`
  - `备注`
  - `ID`
- 当前同步策略是本地优先；如果线上与本地冲突，以本地数据为准。

## 工具

- `scripts/todo_json.py`
  - `read_todos()`
  - `add_todo(content, priority)`
  - `update_todo(todo_id, **kwargs)`
  - `complete_todo(todo_id)`
  - `delete_todo(todo_id)`
  - `get_pending_todos()`
  - `get_completed_todos()`
  - `get_recently_completed_todos(days=3)`
  - `get_display_todos(completed_within_days=3)`
  - `find_todo_by_content(keyword)`
  - `get_todos_by_priority(priority)`
- `scripts/date_validator.py`
  - `parse_date_with_weekday(text)`
  - `validate_date_weekday(text)`
  - `get_days_until(date_str)`
  - `get_urgency_level(date_str)`
  - `get_current_date()`
  - `calculate_target_date(description)`
- `workspace/scripts/sync_todos_to_bitable.py`
  - `todo_to_bitable_record(todo, config)`
  - `sync_todos_to_bitable(todos, config)`
  - `extract_tags(todo)`
  - `extract_notes(todo)`

## 参考资料

- `references/data_structure.md`
- `references/categories.md`
- `references/memory_workflow.md`
