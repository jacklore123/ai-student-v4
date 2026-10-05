# AI学生 · 教育预测引擎 v4 —— 代码文档

> 文件: `ai学生_v4.py`（在 v3 的「学习轨迹系统」基础上新增「物理学习修炼化」，
> 未删除原有功能，未推倒重写）。本文档说明程序架构、v3/v4 新增能力、数据仓库结构与打包/自检方式。

## 一、程序概述

这是一套单文件自包含的 Windows 桌面程序（Tkinter 深色界面），把「一个虚拟学生
从 6 岁到 18 岁（K12，4380 天）的认知成长」做成可模拟、可规划、可对话、可被
摄像头观测、并可被记录成学习轨迹的系统。

核心思想（发明专利思想）：

- 0–100 岁学习者模型 → 取 6–18 岁 K12 子集（4380 天）。
- 「空白学生体」剥离具体知识、保留认知规律。
- 「榜样模型知识库」作为成长终点（牛顿 / 高斯 / 居里）。
- S 型成长曲线 + 双时间轴（实际年龄 ↔ 榜样等效年龄）。
- MCTS + UCB 学习路径规划；时间压缩算法秒级模拟 4380 天。

## 二、运行方式

```text
python ai学生_v4.py                 # 启动图形界面
python ai学生_v4.py --selftest      # 逻辑自检（无窗口）
python ai学生_v4.py --smoke         # GUI 冒烟测试（自动开/关窗口）
python ai学生_v4.py --test-video "视频路径"   # 命令行跑完整视频分析链路
```

配置自动保存到 `%USERPROFILE%\.ai_student_config.json`；数据仓库默认在
`C:\ai_student_data`（无写权限时回退 `%USERPROFILE%\ai_student_data`）。

## 三、代码结构（模块/类）

| 模块 | 职责 |
| --- | --- |
| `GrowthCurve` | S 型理想成长曲线 `5/(1+exp(-10*(x-0.5)))` 与反函数（双时间轴核心） |
| `StudentState` | 学生整体状态：感知/规则/建模/推理/直觉 + 注意力/疲劳/保持率/思维速度 |
| `SkillState`（v3） | 学生对某个具体知识/技能的掌握状态 |
| `ErrorRecord`（v3） | 某技能上反复出现的错误/认知误区 |
| `LearningEpisode`（v3） | 一次完整学习闭环的结构化记录 |
| `MCTSNode` / `MCTSPlanner` | 教育版蒙特卡洛树搜索 + UCB 路径规划 |
| `CognitiveStatus` | 知识掌握度 / 认知发展度 / 心理匹配度 |
| `AIStudentEngine` | 调度中枢：动作执行、双时间轴、数据驱动拟合、时间压缩、学习闭环 |
| `DataVault` | 数据仓库持久化：逐日档案、轨迹 CSV、训练语料、学习轨迹 |
| `LLMClient` | 本地 Ollama / 外部 OpenAI 兼容 API（文本 + 视觉） |
| `App` / `TopInfoBar` / `ThinkZone` / `ProgressZone` / `CameraPanel` / `TrajectoryPanel` | GUI |

## 四、v3 新增：学习轨迹系统（核心升级）

目标是把原来的「学生状态模拟器」升级为真正记录
「如何学习、如何犯错、如何纠正、掌握度如何变化」的学习轨迹系统。

### 1. SkillState（技能掌握层）

与 `StudentState`（整体状态）分层，互不冲突：

```text
skill_id / skill_name / subject / chapter
mastery（掌握度 0..1）
confidence（置信度）
attempts / correct_count / error_count
last_seen / forgetting_rate（遗忘率）
misconception_count / successful_retry_count
```

`update_mastery(delta, correct, retry_correct)` 依据评估结果更新掌握度并维护计数；
`apply_forgetting(gap_days)` 近似遗忘曲线衰减。

### 2. ErrorRecord（错误/堵点层）

回答「学生为什么不会 / 最常卡在哪里」：

```text
skill / error_type / error_name / misconception
first_seen / last_seen / count / corrected
correction_method / recurrence_count
```

内置 13 类错误目录（概念错误、公式错误、计算错误、单位错误、审题错误、
推理错误、知识遗忘、注意力下降、疲劳导致、前置知识缺失、建模错误、
不理解题意、随机猜错），每种都带「认知误区描述 + 纠正方式」。

### 3. LearningEpisode（学习闭环事件）

一次完整学习过程 = 学习 → 评估 → 错误 → 纠正 → 再试 → 掌握度更新 → 记录。
每条事件记录：

```text
day / age / subject / chapter / skill
before_mastery / after_mastery
learning_action / learning_material
question / student_answer
correct / error_type / misconception / confusion
feedback / correction / retry / retry_correct
attention / fatigue / motivation / retention
timestamp / episode_id
```

由 `AIStudentEngine._assess_and_record()` 生成。该闭环已接入以下四条学习路径，
使 4380 天真正产生大量学习事件（而不仅是 Day 1..Day 4380）：

- 手动打卡 `perform_action`（④成长进度区五个教学动作按钮）
- MCTS 最优路径执行
- ✈ 自动领航
- ⚡ 压缩模拟 `simulate_days`（4380 天 → 约 4380 条 LearningEpisode）

### 4. 掌握度如何变化（不再硬编码）

掌握度增量由「学习行为 + 学生状态 + 评估结果」共同决定：

```text
基础增益（按动作）× 注意力效率 × 最近发展区契合度 × (1-当前掌握度)
正确          → 全量
重试后正确    → ×0.55
仍错误        → ×0.25（获得反馈后少量掌握）
```

该接口保留为独立函数 `_skill_gain()`，未来可替换为真实轨迹数据训练的模型。

### 5. 数据仓库新增文件

在原有 `数据集/` 基础上新增（不另起炉灶）：

```text
数据集/learning_episodes.jsonl    # 逐条学习事件（增量追加）
数据集/skill_states.json          # 技能掌握状态快照
数据集/errors.jsonl               # 错误/认知误区记录
数据集/memory_records.jsonl       # 记忆/遗忘事件
```

由 `DataVault.save_learning_trajectory()` 落盘、`load_learning_trajectory()` 回读；
每次启动回读后继续「经验回放 + 数据驱动进化」。

## 五、数据仓库结构（0–100 岁目标）

```text
C:\ai_student_data\
├ 影像\D00001_0岁0天\...        # 录制的学习视频（按学习日）
├ 分析\D00001_0岁0天\...        # 抓帧与双模型分析结果
└ 数据集\
   ├ D00001.json…               # 每日片段数据
   ├ 成长轨迹_4380天.csv          # 逐日成长轨迹
   ├ 训练语料_4380天.jsonl        # 可直接喂大模型训练
   ├ learning_episodes.jsonl      # v3
   ├ skill_states.json            # v3
   ├ errors.jsonl                 # v3
   ├ memory_records.jsonl         # v3
   └ 数据规范_0-100岁.txt
```

## 六、GUI 结构（Codex 式静谧深色风格）

- 顶部工具栏：摄像头 / 录制 / API 密钥 / 上传视频 / 双模型对话 / 4380 天档案 /
  学习轨迹 / 引导。
- 主区：③思考区（AI 思维链）+ ④成长进度区（双时间轴进度条 + S 型曲线 + 教学动作）。
- 三个功能窗口：摄像头窗口、双模型对话窗口、API 设置窗口。
- v3 新增「🧭 学习轨迹窗口」：技能掌握度、最近学习事件、高频错误/堵点，可导出。

配色采用单一强调色（静谧靛蓝 `#7A8CFF`）+ 大面积中性灰、去饱和语义色，
信息层级靠灰阶/留白/字号，不再使用五颜六色。

## 七、大模型接口

- 本地 Ollama：默认 `http://127.0.0.1:11434`，默认模型 `deepseek-r1:7b`，支持视觉。
- 外部 OpenAI 兼容 API：DeepSeek / OpenAI / Kimi / 通义 / 智谱 / 阿里云百炼等，
  300s 超时 + 3 次重试 + 密钥脱敏。
- 视觉模型自动判定，不支持时自动降级为「画面统计 + 文本」。
- 任何 API 密钥都不写死在代码中，仅存于配置文件 / 环境变量。

## 八、摄像头与视频

- OpenCV 采集（DSHOW→MSMF→ANY 后端回退），支持本机/外接/RTSP 源。
- 录制先写英文临时路径再搬运（规避 OpenCV 中文路径静默失败）。
- 上传视频：采样 6 帧 → 蒙太奇 → 本地常规观察 ‖ 外部加强评分并行 →
  生成 Word/Markdown/JSON 档案。

## 九、自检与打包

`--selftest` 覆盖：成长曲线、学生状态、MCTS、4380 天压缩模拟、双时间轴、
数据驱动拟合、学习轨迹（SkillState / ErrorRecord / LearningEpisode / 持久化回读）、
知识点游标、提示词、配置往返、逐日档案、中文路径视频链路。当前 17/17 全部通过。

打包（PyInstaller onefile windowed）：

```text
python -m PyInstaller --onefile --windowed --name "ai学生_v4" ai学生_v4.py
```

> 注意：本机 Python 3.14 将 Tcl/Tk 脚本库打包为 `libtcl9.0.4.zip` /
> `libtk9.0.4.zip`，直接运行时 `_tkinter` 找不到 `init.tcl`。打包时需要先解压
> 这两个 zip，并在打包命令中设置 `TCL_LIBRARY` 与 `TK_LIBRARY` 指向解压出的
> `tcl_library` / `tk_library` 目录，PyInstaller 才能正确收集并内置 Tcl/Tk。

## 十、保留的原有功能

以下 v2 功能在 v3 中完整保留：6–18 岁/4380 天成长模拟、`StudentState` 与认知维度、
注意力/疲劳/记忆、MCTS 路径规划、榜样成长曲线、双时间轴、摄像头/录制/实时双模型
分析、上传视频分析、Ollama/DeepSeek/外部 API、JSON/CSV/JSONL 数据仓库、逐日
Word/Markdown 档案、训练语料生成、GUI 与可视化、`--selftest` / `--smoke` /
`--test-video` 命令行模式。

## 十一、v4 新增：物理学习修炼化（九字秘法 + 境界 + 榜位）

v4 在 v3 的学习轨迹系统之上，把「物理学习」本身做成一套可修炼、可记账、
可量化比较的体系。**不推倒重写**：九字秘法的每一次修炼都复用 v3 已经跑通的
「学习→评估→错误→纠正→再试→掌握度更新→记录」闭环。

### 1. 数据层（模块级常量）

| 常量 | 职责 |
| --- | --- |
| `NINE_ARTS` | 九字秘法：key / 字 / 名 / 释义 / 修炼要点 / 落地动作 / 侧重维度 / 所属境界 |
| `ART_BY_KEY` `ART_BY_CH` `ART_SEQ` | 按 key、按字、按顺序索引；`ART_SEQ` 即「删解秒分合列推创造」 |
| `REALMS` | 四重境界（启蒙 0-6 / 立榜 6-12 / 分科 12-15 / 精进 15-18），带天数区间、要务 |
| `RANK_TIERS` | 境內段位阈值 → 初窥 / 小成 / 大成 / 圆满 |
| `ROLE_TIMELINE` | 榜样 6-18 岁里程碑时间轴（周岁 / 里程碑 / 能力目标 / 侧重学科） |
| `PHYSICS_MODELS` | 高中物理模型清单（「创」式演化对象），首批准入 22 个，目标 108 |

辅助函数：`realm_of_day` / `realm_index` / `realm_of_key` / `tier_of` /
`next_realm_of` / `art_skill_id` / `art_of_skill_id`。

### 2. 引擎层（AIStudentEngine）

| 方法 | 职责 |
| --- | --- |
| `practice_art(key)` | 修炼一式：置 `_art_hint` → 走 `perform_action` 完整闭环 → 结果额外记入该式独立修为 |
| `arts_summary()` | 九式的修为 / 段位 / 修炼次数 / 对错统计 |
| `_art_skill(key)` | 取得（或创建）该式的 `SkillState`，subject=「秘法」，与知识点技能分层 |
| `level_rating()` | **统一评价标准**：修为 → 境界 / 段位 / 榜位 / 榜样等效水平 / 九字修为 / 下一目标 |
| `_check_breakthrough()` | 水平境界跨过门槛时发「突破」事件 |
| `role_timeline_note()` | 榜样时间轴：已达成的里程碑 + 下一个目标 |
| `current_model()` | 「创」式当前应演化的物理模型（按修为推进） |

`perform_action` 末尾新增 `_check_breakthrough()`；`push_traj_row` 的逐日轨迹
新增 `realm` / `rank` 两列；`persona()` 新增 `cultivate` 字段并进入系统提示词，
使大模型对话沿用「九字秘法 + 境界榜位」的口径（提示词内已写明讲题要指出
这一题练的是哪几个字）。

### 3. GUI 层

新增 `LevelPanel`（「🀄 修炼 · 境界榜位 · 九字秘法」窗口）：

- 顶部 Canvas 画榜位进度条 + 四境界刻度（当前位置高亮）；
- 九宫格秘法面板：每格显示「字 + 名 + 段位 + 修为%」，点一格即修炼一式；
- 明细区：修为/境界/榜位/等效榜样年龄/九式修为清单/榜样时间轴/当前应演化模型；
- 「导出…」把 `level_rating()` 存成 JSON。

接入点：工具栏按钮、菜单「数据 → 🀄 修炼 · 境界榜位 · 九字秘法…」、
`App.practice_art()`、`App.open_level()`；`engine_ui_refresh()` 会在窗口可见时
同步刷新；成长进度区的双时间轴行也会显示「境界·段位 榜位」。

### 4. 数据仓库新增

```text
数据集/level_rating.json     # 统一评价标准快照(境界/榜位/等效年龄/九字修为)
数据集/skill_states.json     # 九字秘法作为 subject=秘法 的技能, 与知识点技能共存
```

每次修炼、每次压缩模拟结束、每次打开修炼窗口都会更新 `level_rating.json`。

### 5. 自检

`--selftest` 由 16 项增至 **20 项**，新增：

```text
境界体系: 四境连续覆盖 6-18 岁
统一评价: 修为提升→水平境界/榜位单调不降(rank_global)
九字秘法: 九式独立修为且与知识点技能分层
修炼档案: 统一评价标准落盘(level_rating.json)
```

### 6. 可继续扩展的点

- `PHYSICS_MODELS` 从 22 个补全到设计稿所述 108 个（数据驱动，不影响引擎）；
- 境界阈值目前按年龄固定，可改为按榜样模型分别配置（不同榜样不同境界门槛）；
- `rank_global` 已留好跨境界的可比刻度，接入服务器后可做真正的全国榜位排名；
- 九字秘法的段位阈值（`RANK_TIERS`）与修为增益（`_skill_gain`）都是单一入口，
  未来可用真实轨迹数据训练替换。
