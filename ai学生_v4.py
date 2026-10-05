# -*- coding: utf-8 -*-
r"""
================================================================================
 AI学生 · 教育预测引擎  (AI STUDENT · Educational Prediction Engine)
================================================================================
 设计依据(发明专利思想):
   一种基于ai学生的教育预测模型的建构方法
   · 0-100岁学习者模型 -> 6-18岁 K12 子集(4380天) -> 标准学生模型
   · 空白学生体(剥离知识、保留认知规律) + 榜样模型知识库(终点)
   · 蒙特卡洛树搜索(MCTS) + UCB 路径规划, 起点=学生学情, 终点=榜样知识库
   · S型成长曲线(参考"高斯模型/4380天核心代码"的生长曲线)
   · 双时间轴进度条: 实际年龄 <-> 榜样等效年龄, 动态纠偏
   · 时间压缩算法: 把4380天学习过程压缩到秒级模拟验证
   · 摄像头视觉感知模块(学习状态观测, 预留外接摄像头源)

 程序四大分区(图形界面):
   [1] 本地大模型区   —— 启动时自动探测并调用本地 Ollama 大模型(默认 deepseek-r1:7b)
   [2] 外部大模型API区 —— 接入 OpenAI 兼容外部 API(DeepSeek/OpenAI/Kimi 等)
   [3] 思考区         —— AI学生的实时"思维链"日志(感知/比对/规划/决策/生长)
   [4] 成长进度区     —— 榜样模型进度条 + 当下学生进度条 + S型成长曲线
   顶栏: 学生信息(姓名/年级/学习状态) | 右上角: 摄像头模块(笔记本/外接)

 运行:  python ai学生.py            (图形界面)
        python ai学生.py --selftest (逻辑自检, 无窗口)
        python ai学生.py --smoke    (GUI 冒烟测试, 无窗口闪现)
        python ai学生.py --test-video "C:\videos\test.mp4"
                                    (命令行跑完整视频分析链路并生成档案)

 v2 修复要点:
   ① 数据仓库统一英文路径 C:\ai_student_data(中文路径会让 OpenCV 静默失败);
   ② 上传视频先复制到英文临时路径, 图片一律 imencode+tofile / fromfile+imdecode;
   ③ 外部 API: 300s 超时 + 3 次重试 + 密钥脱敏 + "测试连接";
   ④ 视觉模型自动判定, 不支持视觉时自动降级为"画面统计+文本"(不报错);
   ⑤ 本地与外部双通道并行分析, 进度实时回写思考区与状态栏;
    ⑥ Word 档案优先 python-docx(A4/2cm 页边距/可嵌采样帧), 缺失自动回退内置 OOXML;
    ⑦ 新增 --test-video 命令行自检; 保留 --selftest / --smoke。

 v3 核心升级(学习轨迹系统):
    ① 新增 LearningEpisode 学习事件闭环: 学习→评估→错误→纠正→再试→掌握度更新→记录;
    ② 新增 SkillState(具体技能掌握度) 与 ErrorRecord(错误/认知误区), 与 StudentState 分层;
    ③ 4380天压缩模拟 / 手动打卡 / MCTS / 自动领航 均产生结构化学习事件;
    ④ 数据仓库新增 learning_episodes.jsonl / skill_states.json / errors.jsonl /
       memory_records.jsonl, 支持启动回读与数据驱动进化;
    ⑤ GUI 新增「学习轨迹」窗口(技能掌握度 + 最近学习事件 + 高频错误堵点);
    ⑥ 界面改为 Codex 式静谧深色风格(单一强调色, 去饱和, 不花哨)。

 v4 核心升级(物理学习修炼化):
    ① 九字秘法: 删/解/秒/分/合/列/推/创/造 九式各有独立修为与段位
       (初窥/小成/大成/圆满), 点一格即"修炼一式", 复用完整学习闭环并单独记账;
    ② 榜样模型的境界体系: 启蒙境→立榜境→分科境→精进境
       (对应 0-6/6-12/12-15/15-18 岁), 修为跨过门槛时触发「突破」事件;
    ③ 统一评价标准: 把学情量化为「相当于榜样几岁的水平 + 境界 + 榜位/100」,
       可导出为数据(数据集/level_rating.json) —— 不以分数计量, 以水平计量;
    ④ 榜样 6-18 岁里程碑时间轴(ROLE_TIMELINE): 给出"已达成的节点"与"下一个目标";
    ⑤ GUI 新增「🀄 修炼 · 境界榜位 · 九字秘法」窗口(境界阶梯 + 九宫格秘法面板);
    ⑥ 高中物理模型清单(「创」式演化对象): 首批准入 22 个, 目标 108 个。

 v4.1 核心升级(教材投喂, 课本与练习驱动):
    ① 教材投喂: 把课本/练习(.pdf/.docx/.txt/.md/图片)扫成「章→节→知识点→习题」
       的知识地图(自动过滤页眉、目录、断号, 处理中文硬换行), 落盘 material_map.json;
    ② 自动学习: 空白学生体按真实课本顺序逐日学习 —— 有题就做题, 没题就精读知识点,
       全部复用 v3 的学习闭环与 v4 的九字秘法/境界榜位;
    ③ 学生视角的思考过程: 读题→划关键词→删→解/分/合/列→路线→复盘(错因/纠正/掌握度),
       实时写进思考区, 并把真实题干写进 LearningEpisode;
    ④ 视觉模型接口(预留并已可用): 图片/扫描页 → 视觉模型"看课本"转写 → 同一套流程;
       本地 Ollama 视觉或外部 OpenAI 兼容视觉接口均可, 缺失时自动降级跳过;
    ⑤ 命令行: python ai学生_v4.py --ingest "课本.pdf或文件夹" [--study 10] [--out 目录]。

 本文件为单文件自包含程序: 不依赖任何外部数据文件, 配置自动保存在
 %USERPROFILE%\.ai_student_config.json (可随时删除, 不影响运行)。
================================================================================
"""

import os
import sys
import json
import math
import time
import random
import threading
import queue
import datetime
import subprocess
import urllib.request
import urllib.error
import urllib.parse
import base64
import hashlib
import re
import shutil
import uuid
import zipfile

# ----------------------------------------------------------------- tkinter ---
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from tkinter import font as tkfont
from collections import deque

# 打包成 exe(windowed) 时 stdout 可能仍是 GBK, 打印 emoji/中文会 UnicodeEncodeError
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 摄像头视觉模块依赖(缺失时自动降级为占位画面, 不影响主程序)
try:
    import cv2                      # noqa: E402  OpenCV(打包 exe 时内置)
    HAVE_CV2 = True
except Exception:
    cv2 = None
    HAVE_CV2 = False
try:
    from PIL import Image, ImageTk  # noqa: E402  Pillow(打包 exe 时内置)
    HAVE_PIL = True
except Exception:
    Image = ImageTk = None
    HAVE_PIL = False

try:
    import docx as _docx_pkg        # noqa: E402  python-docx(生成 Word 档案)
    HAVE_DOCX = True
except Exception:
    _docx_pkg = None
    HAVE_DOCX = False

try:                                     # 高DPI 清晰显示(Win)
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

APP_NAME = "AI学生 · 教育预测引擎"
APP_VER = "4.1.0"
CFG_PATH = os.path.join(os.path.expanduser("~"), ".ai_student_config.json")

# =============================================================== 基础工具 =====

def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else (hi if x > hi else x)

def now_ms():
    return time.time() * 1000.0

def now_str():
    return datetime.datetime.now().strftime("%H:%M:%S")

def est_tokens(text):
    """中文为主文本的 Token 粗估。"""
    if not text:
        return 0
    return max(1, int(len(text) * 0.55) + int(sum(1 for c in text if ord(c) > 127) * 0.35))

# ======================================================= 榜样模型知识库 ========
# 对应权利要求4: 榜样模型知识库(终点), 精确到天/阶段的成长轨迹数据化建模

ROLE_MODELS = {
    "newton": {
        "key": "newton", "label": "ai牛顿 · 物理学", "emoji": "🍎",
        "subjects": ("数学", "物理"),
        "desc": "艾萨克·牛顿(Isaac Newton) 0-24岁成长模型：感知观察 -> 规则实验 -> 模型建立 -> 公理体系推理",
        "milestones": [
            (6,  "童年大量动手制作机械模型, 积累感性经验"),
            (12, "沉迷读书与实验, 建立规则化思考习惯"),
            (19, "进入剑桥, 系统学习欧氏几何与自然哲学"),
            (22, "发明流数术(微积分)雏形, 建立力学模型雏形"),
            (24, "完成光学实验与万有引力思想萌芽, 形成公理推理能力"),
        ],
    },
    "gauss": {
        "key": "gauss", "label": "ai高斯 · 数学", "emoji": "📐",
        "subjects": ("数学", "物理"),
        "desc": "卡尔·弗里德里希·高斯(Carl F. Gauss) 0-24岁成长模型：以数感与规律发现为核心的成长轨迹",
        "milestones": [
            (3,  "幼年展现惊人计算敏感度, 感知数字规律"),
            (10, "课堂上秒解1+2+...+100, 掌握等差规律建模"),
            (17, "证明二次互反律, 建立数论模型体系"),
            (20, "完成正十七边形尺规作图, 推理能力成熟"),
            (24, "系统整理数论著作《算术研究》, 形成公理化数学体系"),
        ],
    },
    "curie": {
        "key": "curie", "label": "ai居里 · 科学", "emoji": "🧪",
        "subjects": ("化学", "物理", "生物"),
        "desc": "玛丽·居里(Marie Curie) 0-24岁成长模型：实验观察与跨学科融合的成长轨迹",
        "milestones": [
            (6,  "童年博览群书, 培养敏锐观察力"),
            (16, "以金质奖章毕业, 规则学习能力突出"),
            (19, "自学物理化学, 进入实验科学领域"),
            (24, "系统研究放射现象, 建立实验-理论双驱动模型"),
        ],
    },
}

# ------------------------------------------------------- 境界体系(v4) --------
# 对应 PPT「榜样模型的境界划分」: 0-6岁想象力与专注力 → 6-12岁引入榜样模型 →
# 12-15岁选择学科、学习学科规则 → 15-18岁发展学科并比对历史科学家的进度条。
# 本引擎模拟 6-18 岁(4380天), 故「启蒙境」位于模拟区间之前, 作为起点前史保留,
# 使"实际境界"与"水平境界"可以在同一把尺子上比较。

REALMS = [
    {"key": "meng", "name": "启蒙境", "emoji": "🌱", "age": (0, 6),
     "day": (-6 * 365, 0),
     "desc": "培养想象力与专注力",
     "focus": "感知 · 专注 · 动手",
     "task": "以观察、动手、语言积累建立学习兴趣"},
    {"key": "libang", "name": "立榜境", "emoji": "🌿", "age": (6, 12),
     "day": (0, 6 * 365),
     "desc": "引入学习榜样模型(ai牛顿 / ai高斯)",
     "focus": "榜样模仿 · 规则内化",
     "task": "用榜样模型锚定目标, 把焦虑换成超越前人的动力"},
    {"key": "fenke", "name": "分科境", "emoji": "🌳", "age": (12, 15),
     "day": (6 * 365, 9 * 365),
     "desc": "选择学科方向, 学习该学科的规则",
     "focus": "学科规则 · 模型建立",
     "task": "按学科规则建立模型, 打通前置知识链条"},
    {"key": "jingjin", "name": "精进境", "emoji": "🏛", "age": (15, 18),
     "day": (9 * 365, 12 * 365),
     "desc": "发展学科专长, 与历史科学家的进度条实时比对",
     "focus": "专长发展 · 超越前人",
     "task": "对标榜样同期的记录, 用更短的时间突破"},
]

# 境內修为段位(修炼语汇: 对应 PPT「进度条/成就感体系」)
RANK_TIERS = [(0.00, "初窥"), (0.30, "小成"), (0.60, "大成"), (0.85, "圆满")]


def realm_of_day(day):
    """按学习天数取境界; 超出模拟区间时钳位到首境/末境。"""
    for r in REALMS:
        if r["day"][0] <= day < r["day"][1]:
            return r
    return REALMS[0] if day < REALMS[0]["day"][0] else REALMS[-1]


def realm_index(day):
    return REALMS.index(realm_of_day(day))


def realm_of_key(key):
    for r in REALMS:
        if r["key"] == key:
            return r
    return REALMS[0]


def tier_of(frac):
    """境界内进度(0..1) → 段位名(入门/初通/熟练/贯通)。"""
    name = RANK_TIERS[0][1]
    for lo, nm in RANK_TIERS:
        if frac >= lo:
            name = nm
    return name


def next_realm_of(day):
    idx = realm_index(day)
    return REALMS[idx + 1] if idx + 1 < len(REALMS) else None


# ------------------------------------------- 榜样 6-18 岁里程碑时间轴 --------
# 把 ROLE_MODELS 的粗里程碑细化为"可对齐到天"的时间轴, 供双时间轴比对与
# 「下一个目标」提示使用。条目: (周岁, 里程碑, 能力目标, 侧重学科)。
# 说明: 这是教学用简化里程碑, 年龄按史料近似, 只保留与学习建模相关的节点,
# 不追求传记细节的完整与精确。

ROLE_TIMELINE = {
    "newton": [
        (6,  "童年动手制作风车、水钟、日晷", "以机械模型积累感性经验", "物理"),
        (12, "沉迷读书与实验, 建立规则化思考习惯", "把观察变成可重复的规则", "物理"),
        (15, "在文法学校系统学习拉丁语与数学", "掌握语言与数学两套符号规则", "数学"),
        (17, "离开学校回家务农, 仍坚持自学与观察实验", "自学习惯稳定: 观察→记录→验证", "物理"),
        (19, "进入剑桥, 系统学习欧氏几何与自然哲学", "把规则升格为可证明的体系", "数学"),
        (22, "发明流数术(微积分)雏形, 建立力学模型雏形", "用变化率描述运动", "数学"),
        (24, "完成光学实验与万有引力思想萌芽", "形成公理推理能力", "物理"),
    ],
    "gauss": [
        (7,  "进入小学, 心算与规律发现能力远超同龄", "以数感直接发现规律", "数学"),
        (10, "课堂上秒解 1+2+…+100, 掌握等差规律建模", "把规律写成通式", "数学"),
        (12, "自学代数与几何, 开始追问公理是否可靠", "从运用规则转向质疑规则", "数学"),
        (15, "独立推导级数与数论结论", "用分析工具处理整数问题", "数学"),
        (17, "证明二次互反律, 建立数论模型体系", "把零散结论连成体系", "数学"),
        (18, "掌握高等分析与数论工具, 系统构造证明", "形成公理化数学体系雏形", "数学"),
        (20, "完成正十七边形尺规作图", "推理能力成熟, 直达构造", "数学"),
        (24, "系统整理数论著作《算术研究》", "形成完整的公理化体系", "数学"),
    ],
    "curie": [
        (6,  "童年博览群书, 培养敏锐观察力", "以阅读扩展感知范围", "综合"),
        (10, "进入寄宿学校, 成绩常年第一", "以自律维持稳定学习节奏", "综合"),
        (13, "对物理与化学实验产生浓厚兴趣", "从书本走向动手实验", "化学"),
        (16, "以金质奖章毕业, 规则学习能力突出", "把学科规则学到可迁移", "综合"),
        (18, "在受限环境里仍坚持自学实验方法", "在缺少条件时自己创造条件", "物理"),
        (19, "自学物理化学, 进入实验科学领域", "实验与理论双线并进", "化学"),
        (24, "系统研究放射现象, 建立实验-理论双驱动模型", "以实验反推理论模型", "物理"),
    ],
}

# ======================================================= 九字秘法(v4核心) =====
# 「物理学习 = 修炼」: 九个字是物理学习的九式秘法, 每式各有独立的修为(掌握度)。
# 释义取自设计原稿(PPT第30页), 未作改写; engine 动作是每式在当前引擎里的
# 落地动作(用于复用已跑通的认知生长与学习闭环机制)。
# 条目: key / 字 / 名 / 释义 / 修炼要点 / 落地动作 / 侧重维度 / 所属境界

NINE_ARTS = [
    {"key": "shan", "ch": "删", "name": "图像化拆解",
     "tip": "文字转图像, 转完一句删一句",
     "key_point": "读一句→画一笔→删一句, 只留图和数, 把题干从文字负担变成图形余量",
     "action": "jiangjie", "dims": ("PER", "MOD"), "realm": "libang"},
    {"key": "jie", "ch": "解", "name": "方程求解",
     "tip": "方程解的思维, 例如必修一的知三求二",
     "key_point": "把已知量/未知量/方程一一对应; 运动学五个量, 知三求二",
     "action": "liti", "dims": ("RUL", "REA"), "realm": "libang"},
    {"key": "miao", "ch": "秒", "name": "二级结论速判",
     "tip": "结合常见的二级结论, 秒杀适合的题",
     "key_point": "先把结论推导过一遍再记; 用时必须能说清适用条件, 否则不许秒",
     "action": "liti", "dims": ("REA", "INT"), "realm": "fenke"},
    {"key": "fen", "ch": "分", "name": "隔离受力",
     "tip": "受力分析 + 正交分解 + 隔离法(分析有几个接触点, 每一点都可能有力)",
     "key_point": "数接触点→逐点找力→画受力图→正交分解, 一步不许跳",
     "action": "liti", "dims": ("MOD", "REA"), "realm": "fenke"},
    {"key": "he", "ch": "合", "name": "整体简力",
     "tip": "整体法, 简化受力",
     "key_point": "系统内力的成对性先想清, 再决定整体还是隔离, 把受力项减到最少",
     "action": "fansi", "dims": ("MOD", "RUL"), "realm": "fenke"},
    {"key": "lie", "ch": "列", "name": "坐标列式",
     "tip": "按照坐标系列出平衡状态方程",
     "key_point": "建系→投影→逐轴列方程, 未知数与方程个数对齐后才动笔算",
     "action": "liti", "dims": ("RUL", "MOD"), "realm": "fenke"},
    {"key": "tui", "ch": "推", "name": "公式体系推导",
     "tip": "对课本的公式进行记忆编程, 以图像化的去推导出所有的公式体系",
     "key_point": "不背结论背来路: 从一个母公式推出一整片公式, 形成可自我恢复的公式体系",
     "action": "fansi", "dims": ("RUL", "REA", "INT"), "realm": "jingjin"},
    {"key": "chuang", "ch": "创", "name": "模型演化",
     "tip": "高中108个物理模型, 在脑海里演化这些模型, 进行理想化模拟",
     "key_point": "把题目归到模型上, 在脑中跑一遍理想化过程, 再回到题目条件",
     "action": "hudong", "dims": ("MOD", "INT"), "realm": "jingjin"},
    {"key": "zao", "ch": "造", "name": "动手造物",
     "tip": "动手做物理实体, 去改变世界",
     "key_point": "把模型做出来: 斜面、轨道、杠杆、电路, 用真实误差修正头脑里的理想化",
     "action": "hudong", "dims": ("PER", "INT"), "realm": "jingjin"},
]
ART_BY_KEY = {a["key"]: a for a in NINE_ARTS}
ART_BY_CH = {a["ch"]: a for a in NINE_ARTS}
ART_SEQ = [a["ch"] for a in NINE_ARTS]           # 删解秒分合列推创造
ART_SKILL_PREFIX = "秘法::"


def art_skill_id(key):
    return ART_SKILL_PREFIX + key


def art_of_skill_id(skill_id):
    """由技能ID反查九字秘法条目(非秘法则返回 None)。"""
    if not skill_id:
        return None
    key = skill_id.split(ART_SKILL_PREFIX, 1)[-1] if ART_SKILL_PREFIX in skill_id else ""
    return ART_BY_KEY.get(key)


# --------------------------------------------- 高中物理模型清单(九字「创」) ---
# 首批准入模型, 供「创」式演化练习使用; 逐步补全至设计稿所述的 108 个模型。

PHYSICS_MODELS = [
    "斜面模型", "传送带模型", "连接体模型", "板块模型", "弹簧模型",
    "轻绳轻杆模型", "平抛运动", "圆周运动临界", "竖直圆轨道", "万有引力与卫星",
    "功与能综合", "机车启动", "碰撞模型", "子弹打木块", "绳球与杆球",
    "电容器动态分析", "带电粒子电场偏转", "带电粒子磁场圆周", "电磁感应单杆",
    "电磁感应双杆", "变压器模型", "安培力平衡",
]
PHYSICS_MODEL_TARGET = 108      # 设计目标: 高中108个物理模型

# ==================================================== 教材投喂(课本与练习) =====
# 把"真正的课本与练习"喂给引擎: 扫描 → 切章/节/知识点/习题 → 空白学生体按真实
# 内容顺序逐日自动学习, 并把学习时的思考过程完整写出来。
# 支持 .txt/.md(零依赖) · .docx(解压读取, 零依赖) · .pdf(可选 pypdf)。
# 教材属于外部数据, 不写死在程序里; 解析结果落到 数据集/material_map.json。

# 图片/扫描页走视觉模型(像真人一样"看"课本); 其余格式直接读文字
MATERIAL_IMAGE_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff")
MATERIAL_EXT = (".txt", ".md", ".markdown", ".docx", ".pdf") + MATERIAL_IMAGE_EXT

# 章 / 节 / 栏目 / 题号 的识别规则(人教版教材与常见讲义通用)
RE_CHAPTER = re.compile(r"^\s*第\s*([一二三四五六七八九十百]+)\s*章[\s、.：:]*(.{0,34})")
RE_SECTION = re.compile(
    r"^\s*(?:第\s*([一二三四五六七八九十]+)\s*节|(\d{1,2})\s*[.．]\s*(\d{1,2}))"
    r"[\s、.：:]+([^\d]{2,26})$")          # 标题里不允许再出现数字(排除 0.02 s 这类量值)
# 只有"真正的课后练习"栏目才切题; 思考与讨论/做一做/科学漫步属于正文
RE_BLOCK = re.compile(r"^\s*(练习与应用|复习与提高|问题与练习|课后练习)\s*[（(]?\s*$")
RE_QUESTION = re.compile(r"^\s*(\d{1,2})\s*[.．、]\s*(.{8,})")
RE_PAGE_NOISE = re.compile(r"^\s*(?:\d{1,3}\s*[|｜]\s*)?高中物理[^\n]{0,14}$")
RE_FIG_ONLY = re.compile(r"^\s*图\s*\d+[-－.]\d+[^\n]{0,24}$")
# 目录行(带页码)与短标题: 目录/页眉会大量干扰, 需要专门识别
RE_TOC_LINE = re.compile(r"(?:[.．·…]{3,}|\s{3,})\s*\d{1,3}\s*$")
RE_HEAD_TAIL_NO = re.compile(r"\s*\d{1,3}\s*$")

# 物理关键词(用于审题时"划关键词"与判断题型)
PHY_KEYWORDS = (
    "速度", "加速度", "位移", "路程", "时间", "平均速度", "瞬时速度", "自由落体",
    "重力", "弹力", "摩擦力", "受力", "合力", "分力", "平衡", "牛顿", "质量", "密度",
    "压强", "浮力", "功", "功率", "机械能", "动能", "势能", "动量", "冲量",
    "圆周运动", "平抛", "斜面", "弹簧", "绳", "杆", "滑轮", "传送带", "板块",
    "电场", "电荷", "电压", "电流", "电阻", "电容", "电路", "欧姆", "磁场",
    "磁通量", "安培", "洛伦兹", "电磁感应", "感应电动势", "变压器",
    "折射", "反射", "透镜", "波长", "频率", "光子", "光电效应", "原子核", "半衰期",
    "温度", "内能", "热量", "比热容",
)
QUESTION_KINDS = (
    ("实验", ("实验", "测量", "器材", "步骤", "记录", "作图", "图像")),
    ("说明", ("说明", "解释", "为什么", "原因", "判断", "分析")),
    ("证明", ("证明", "推导", "验证")),
    ("计算", ("求", "计算", "多少", "多大", "等于", "比值")),
)


def read_text_auto(path):
    """按常见中文编码依次尝试读取文本文件。"""
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb18030"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    return ""


def read_docx_text(path):
    """零依赖读取 .docx: docx 即 zip, 直接取 word/document.xml 的文本。"""
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
    except Exception:
        return ""
    xml = (xml.replace("</w:p>", "\n").replace("<w:br/>", "\n")
              .replace("<w:tab/>", " "))
    return re.sub(r"<[^>]+>", "", xml)


def read_pdf_text(path, max_pages=0):
    """可选: 提取 PDF 文字(pypdf); 未安装时返回空并给出原因。"""
    try:
        from pypdf import PdfReader
    except Exception:
        return "", "缺少 pypdf(可 pip install pypdf 后重试)"
    try:
        rd = PdfReader(path)
        out = []
        for i, pg in enumerate(rd.pages):
            if max_pages and i >= max_pages:
                break
            out.append(pg.extract_text() or "")
        return "\n".join(out), ""
    except Exception as e:
        return "", str(e)


# ------------------------------------------- 视觉模型"看课本"(v4.1 接口) -----
# 设计目标: 让 ai学生 像真人一样, 直接"看"课本页面与练习照片去学习。
# 链路: 页面图片/扫描页 → 视觉模型转写(保持题号与设问) → 进入同一套切分与学习流程。
# 本地 Ollama 视觉(如 llava / qwen2.5-vl)或外部 OpenAI 兼容视觉接口均可, 缺失时自动降级为跳过。

VISION_READ_PROMPT = (
    "你在扮演一个正在读书的学生。请把这一页教材/练习的内容转写出来:\n"
    "1) 逐字转写页面上的可见文字, 公式用纯文本表示(例如 v=v0+at、F=ma);\n"
    "2) 按「章节标题 / 概念定义 / 例题 / 习题」分段, 保留原编号;\n"
    "3) 题目只转写题号与设问, 不要自己解答;\n"
    "4) 看不清的地方写 [不清], 不要编造内容。\n"
    "只输出转写结果。"
)


def render_pdf_pages(path, out_dir, dpi=120, max_pages=0):
    """把 PDF 页面渲染成 PNG, 供视觉模型"看课本"。

    优先用 poppler 的 pdftoppm(装了就能用), 否则退回抽取 PDF 内嵌图片。
    """
    imgs = []
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception:
        return imgs
    exe = shutil.which("pdftoppm")
    if exe:
        prefix = os.path.join(out_dir, "page")
        cmd = [exe, "-r", str(int(dpi)), "-png"]
        if max_pages:
            cmd += ["-f", "1", "-l", str(int(max_pages))]
        cmd += [path, prefix]
        try:
            subprocess.run(cmd, capture_output=True, timeout=900)
            base = os.path.basename(prefix)
            imgs = [os.path.join(out_dir, fn) for fn in sorted(os.listdir(out_dir))
                    if fn.startswith(base) and fn.lower().endswith(".png")]
        except Exception:
            imgs = []
    if not imgs:                      # 退路: 抽取 PDF 内嵌图片
        try:
            from pypdf import PdfReader
            rd = PdfReader(path)
            for i, pg in enumerate(rd.pages):
                if max_pages and i >= max_pages:
                    break
                for j, im in enumerate(getattr(pg, "images", []) or []):
                    fn = os.path.join(out_dir, "embed_%03d_%d_%s"
                                      % (i, j, getattr(im, "name", "img")))
                    with open(fn, "wb") as f:
                        f.write(im.data)
                    imgs.append(fn)
        except Exception:
            pass
    return imgs


def vision_read_page(image_path, cfg=None, prompt=None):
    """用视觉模型读一页教材/练习, 返回 (转写文本, 失败原因)。"""
    cfg = cfg or {}
    b64 = b64_image(image_path)
    if not b64:
        return "", "无法读取图片"
    prompt = prompt or VISION_READ_PROMPT
    r_url = (cfg.get("remote_url") or "").strip()
    r_key = (cfg.get("remote_key") or "").strip()
    r_mod = (cfg.get("remote_model") or "").strip()
    if r_url and r_key and r_mod and vision_capable(r_mod):
        try:
            return LLMClient.remote_chat_vision(r_url, r_key, r_mod, prompt,
                                                b64, temperature=0.2), ""
        except Exception as e:
            return "", "外部视觉接口失败: %s" % e
    base = (cfg.get("local_base") or LOCAL_DEFAULT).strip()
    model = (cfg.get("local_model") or LOCAL_MODEL_DEFAULT).strip()
    if not vision_capable(model):
        return "", "当前模型不支持视觉(本地可用 llava / qwen2.5-vl 等)"
    try:
        msgs = [{"role": "user", "content": prompt}]
        return LLMClient.ollama_chat(base, model, msgs, temperature=0.2,
                                     timeout=300, image_b64=b64), ""
    except Exception as e:
        return "", "本地视觉模型失败: %s" % e


def merge_paragraphs(lines, max_len=150):
    """把硬换行的文本粘回自然段(按句末标点或长度断句)。"""
    buf, out = "", []
    for ln in lines:
        s = ln.strip()
        if not s:
            if buf:
                out.append(buf)
                buf = ""
            continue
        buf = (buf + s) if buf else s
        if len(buf) >= max_len or buf[-1:] in "。；？！":
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return out


class MaterialBook:
    """教材知识地图: 章 → 节 → 知识点(段落) + 习题(题干)。"""

    def __init__(self, subject="物理", title=""):
        self.subject = subject
        self.title = title
        self.files = []       # [{name, kind, chars, note}]
        self.chapters = []    # [{title, sections:[{title, points:[], questions:[(号,题干)]}]}]

    # ------------------------------------------------------------ 构建 ----
    def section(self, chap=None, sec=None):
        chap = (chap or "").strip() or None      # 空串按"沿用上一级"处理
        sec = (sec or "").strip() or None
        if not self.chapters or (chap is not None and self.chapters[-1]["title"] != chap):
            self.chapters.append({"title": chap or "（未分章）", "sections": []})
        c = self.chapters[-1]
        if not c["sections"] or (sec is not None and c["sections"][-1]["title"] != sec):
            c["sections"].append({"title": sec or "（未分节）", "points": [],
                                  "questions": []})
        return c["sections"][-1]

    def add_point(self, text, chap=None, sec=None):
        t = (text or "").strip()
        cjk = sum(1 for c in t if "\u4e00" <= c <= "\u9fff")
        if cjk >= 12 and len(re.findall(r"\d\s*[.．]", t)) < 2:   # 排除目录/标题行
            self.section(chap, sec)["points"].append(t)

    def add_question(self, text, qno="", chap=None, sec=None):
        t = (text or "").strip()
        if sum(1 for c in t if "\u4e00" <= c <= "\u9fff") >= 8:   # 排除表格/数字碎片
            self.section(chap, sec)["questions"].append([str(qno), t])

    # ------------------------------------------------------------ 查询 ----
    def flat_points(self):
        out = []
        for c in self.chapters:
            for s in c["sections"]:
                for p in s["points"]:
                    out.append((c["title"], s["title"], p))
        return out

    def flat_questions(self):
        out = []
        for c in self.chapters:
            for s in c["sections"]:
                for q in s["questions"]:
                    out.append((c["title"], s["title"], q[0], q[1]))
        return out

    def stats(self):
        n_sec = sum(len(c["sections"]) for c in self.chapters)
        pts = self.flat_points()
        qs = self.flat_questions()
        return {"chapters": len(self.chapters), "sections": n_sec,
                "points": len(pts), "questions": len(qs),
                "point_chars": sum(len(p[2]) for p in pts),
                "question_chars": sum(len(q[3]) for q in qs),
                "files": len(self.files), "subject": self.subject}

    def to_dict(self):
        return {"subject": self.subject, "title": self.title, "files": self.files,
                "chapters": self.chapters, "stats": self.stats()}

    @staticmethod
    def from_dict(d):
        b = MaterialBook(d.get("subject", "物理"), d.get("title", ""))
        b.files = d.get("files", [])
        b.chapters = d.get("chapters", [])
        return b

    def save(self, path):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=1)
            return path
        except Exception:
            return None


class MaterialIngestor:
    """把课本/练习文件扫描成教材知识地图(章→节→知识点→习题)。"""

    def __init__(self, subject="物理", max_pdf_pages=0, vision_cfg=None,
                 use_vision=True, vision_max_pages=6):
        self.subject = subject
        self.max_pdf_pages = max_pdf_pages
        self.vision_cfg = vision_cfg or {}
        self.use_vision = use_vision
        self.vision_max_pages = vision_max_pages
        self.notes = []
        self.vision_pages = 0      # 成功"看"过的页数
        self.vision_fail = 0

    # ------------------------------------------------------------ 读文件 ----
    def read_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in MATERIAL_EXT[:3]:
            return read_text_auto(path), "文本"
        if ext == ".docx":
            return read_docx_text(path), "Word"
        if ext == ".pdf":
            txt, err = read_pdf_text(path, self.max_pdf_pages)
            if err:
                self.notes.append("%s: %s" % (os.path.basename(path), err))
            if len((txt or "").strip()) < 200 and self.use_vision:
                txt2 = self.read_pdf_by_vision(path)      # 无文字层 → 用视觉看
                if txt2:
                    return txt2, "PDF(视觉)"
            return txt, "PDF"
        if ext in MATERIAL_IMAGE_EXT:
            if not self.use_vision:
                return "", "图片(未启用视觉)"
            txt, err = vision_read_page(path, self.vision_cfg)
            if err:
                self.vision_fail += 1
                self.notes.append("%s: %s" % (os.path.basename(path), err))
                return "", "图片(视觉失败)"
            self.vision_pages += 1
            return txt, "图片(视觉)"
        return "", "跳过"

    def read_pdf_by_vision(self, path):
        """扫描版 PDF: 渲染页面 → 视觉模型逐页转写(像真人翻书看)。"""
        tmp = os.path.join(os.environ.get("TEMP") or os.path.expanduser("~"),
                           "ai_student_pages",
                           re.sub(r"[^\w.-]", "_", os.path.basename(path))[:40])
        pages = render_pdf_pages(path, tmp, max_pages=self.vision_max_pages)
        if not pages:
            self.notes.append("%s: 无法渲染页面(需 poppler 的 pdftoppm, 或用有文字层的 PDF)"
                              % os.path.basename(path))
            return ""
        out = []
        for pg in pages:
            txt, err = vision_read_page(pg, self.vision_cfg)
            if err:
                self.vision_fail += 1
                self.notes.append("%s: %s" % (os.path.basename(pg), err))
                break
            self.vision_pages += 1
            out.append(txt)
        return "\n".join(out)

    def list_files(self, paths):
        out = []
        for p in paths:
            if os.path.isdir(p):
                for root, _dirs, files in os.walk(p):
                    for fn in sorted(files):
                        if os.path.splitext(fn)[1].lower() in MATERIAL_EXT:
                            out.append(os.path.join(root, fn))
            elif os.path.isfile(p) and os.path.splitext(p)[1].lower() in MATERIAL_EXT:
                out.append(p)
        return out

    # ------------------------------------------------------------ 切分 ----
    @staticmethod
    def _clean_lines(text):
        out = []
        for ln in (text or "").splitlines():
            s = ln.replace("\u3000", " ").strip()
            if not s or RE_PAGE_NOISE.match(s) or RE_FIG_ONLY.match(s):
                continue
            if RE_TOC_LINE.search(s):          # 目录行 / 带页码的页眉
                continue
            out.append(s)
        return out

    @staticmethod
    def _norm_head(s):
        """规范化标题: 去掉尾部页码与多余空白(页眉常带页码)。"""
        return RE_HEAD_TAIL_NO.sub("", (s or "").strip()).strip()

    def segment_file(self, book, path):
        text, kind = self.read_file(path)
        name = os.path.basename(path)
        if not text:
            book.files.append({"name": name, "kind": kind, "chars": 0, "note": "无文本"})
            return
        book.files.append({"name": name, "kind": kind, "chars": len(text), "note": ""})
        lines = self._clean_lines(text)
        # 有章标题的(课本): 先跳过封面/目录/编写说明; 无章标题的(练习卷/讲义): 直接进正文
        has_chap = any(RE_CHAPTER.match(s) for s in lines)
        chap = sec = None
        mode = "front" if has_chap else "body"     # front | body | exercise
        buf, qno, qno_int = [], "", 0

        def flush():
            nonlocal buf, qno
            if not buf:
                return
            if mode == "exercise" and qno:
                book.add_question(" ".join(buf), qno, chap, sec)
            elif mode == "body":
                for para in merge_paragraphs(buf):
                    if sum(1 for c in para if "\u4e00" <= c <= "\u9fff") >= 6:
                        book.add_point(para, chap, sec)
            buf, qno = [], ""

        for s in lines:
            m_ch = RE_CHAPTER.match(s)
            if m_ch:
                title = self._norm_head("第%s章 %s" % (m_ch.group(1), m_ch.group(2)))
                if chap and (title == chap or chap.startswith(title[:8])):
                    continue                        # 每页页眉重复 → 丢弃
                flush()
                chap, sec, mode = title, None, "body"
                continue
            m_se = RE_SECTION.match(s)
            if m_se:
                title = self._norm_head(m_se.group(4) or s)
                if len(title) < 2 or (sec and title == sec):
                    continue                        # 页眉重复 / 无效标题
                flush()
                sec, mode = title, "body"
                continue
            if RE_BLOCK.match(s):
                flush()
                mode, qno_int = "exercise", 0
                continue
            if mode == "front":
                continue                            # 正文之前的封面/目录/编写说明
            m_q = RE_QUESTION.match(s)
            if mode == "exercise" and m_q:
                n = int(m_q.group(1))
                if qno_int and n != qno_int + 1:
                    # 题号断了 → 说明练习块已结束(后面是正文/实验步骤), 退出做题模式
                    flush()
                    mode = "body"
                    buf.append(s)
                    continue
                flush()
                qno, qno_int, buf = m_q.group(1), n, [m_q.group(2)]
                continue
            buf.append(s)
        flush()

    def ingest(self, paths, title=""):
        book = MaterialBook(self.subject, title or "教材投喂")
        for p in self.list_files(paths):
            try:
                self.segment_file(book, p)
            except Exception as e:
                self.notes.append("%s: %s" % (os.path.basename(p), e))
        self.prune(book)
        if self.vision_pages or self.vision_fail:
            self.notes.append("视觉模型: 成功读取 %d 页, 失败 %d 页"
                              % (self.vision_pages, self.vision_fail))
        return book

    @staticmethod
    def prune(book, min_chars=400):
        """清理封面/目录/页眉造成的空壳章节: 内容过少的章与节直接丢掉。"""
        keep_ch = []
        for c in book.chapters:
            secs = []
            for s in c["sections"]:
                chars = (sum(len(p) for p in s["points"])
                         + sum(len(q[1]) for q in s["questions"]))
                if len(s["points"]) >= 4 or s["questions"] or chars >= min_chars:
                    secs.append(s)
            c["sections"] = secs
            if secs:
                keep_ch.append(c)
        book.chapters = keep_ch
        return book

# --------------------------------------------------- 6-18岁 K12 知识池 --------
# 对应权利要求2/9: 4380个数据子集按时间序列排布, 知识点构成"知识地图"

GRADES = ["小学一年级", "小学二年级", "小学三年级", "小学四年级", "小学五年级",
          "小学六年级", "初中一年级", "初中二年级", "初中三年级",
          "高中一年级", "高中二年级", "高中三年级"]

KNOWLEDGE_POOL = {
    "数学": ["数的认识与比较", "20以内加减法", "乘法口诀", "除法与余数", "四则混合运算",
            "分数与小数", "倍数与因数", "图形周长面积", "简易方程", "负数与数轴",
            "百分数与比例", "观察物体与方位", "长方体与正方体", "圆的认识",
            "有理数运算", "整式与去括号", "一元一次方程", "二元一次方程组", "不等式与不等式组",
            "平面直角坐标系", "一次函数", "三角形全等", "勾股定理", "平行四边形",
            "分式与分式方程", "二次根式", "一元二次方程", "二次函数", "相似三角形",
            "锐角三角函数", "圆与切线", "统计与概率基础", "反比例函数", "集合与逻辑用语",
            "幂函数指数函数", "对数函数", "三角函数图像性质", "平面向量", "数列与等差等比",
            "导数与单调性", "排列组合", "空间立体几何基础"],
    "物理": ["自然观察与测量", "长度时间的测量", "运动快慢描述", "声音的产生传播",
            "光的直线传播", "光的反射", "光的折射", "透镜与成像", "物态变化",
            "质量与密度", "力的作用效果", "重力弹力摩擦力", "牛顿第一定律", "二力平衡",
            "压强与液体压强", "大气压强", "浮力与阿基米德原理", "功与功率",
            "杠杆与滑轮", "机械能及其转化", "内能与比热容", "电流电路概念",
            "欧姆定律", "电功率与焦耳定律", "电与磁", "磁场对电流的作用",
            "机械运动图像", "受力分析综合", "能量守恒思想"],
    "化学": ["物质的变化与性质", "空气与氧气", "水的组成净化", "分子原子离子",
            "元素周期表初步", "化学式与化合价", "质量守恒定律", "化学方程式",
            "碳和碳的氧化物", "燃烧与灭火", "金属与金属材料", "溶液与溶解度",
            "酸碱指示剂", "酸的性质", "碱的性质", "盐与化肥", "化学与生活",
            "离子反应入门", "氧化还原入门", "化学反应速率初步"],
    "生物": ["认识生物与细胞", "显微镜使用", "植物结构层次", "光合作用与呼吸作用",
            "人体营养与消化", "血液循环系统", "人体呼吸系统", "人体泌尿系统",
            "神经调节与反射", "激素调节", "动物的运动行为", "细菌真菌病毒",
            "生物多样性", "遗传变异初步", "生态系统", "生物技术入门"],
    "语文": ["拼音与识字", "词语积累", "句子与标点", "阅读启蒙", "看图写话",
            "古诗文背诵", "记叙文阅读", "说明文阅读", "议论文阅读", "文言文入门",
            "作文结构训练", "名著导读", "现代文精读", "古诗词鉴赏", "文言文进阶",
            "散文小说阅读", "写作立意与素材", "文化常识"],
    "英语": ["字母与自然拼读", "基础词汇300", "简单句型", "日常对话", "现在进行时",
            "一般过去时", "一般将来时", "比较级最高级", "阅读入门", "书面表达基础",
            "宾语从句入门", "定语从句入门", "非谓语动词入门", "虚拟语气初步",
            "完形填空技巧", "阅读理解策略", "写作进阶", "听力策略"],
}

# =============================================================== 成长曲线 =====
# 对应权利要求8/9: L-系统/S型生长算法模拟认知发展, 双时间轴比对
# 参考代码(4380天核心/高斯模型): ideal = 5 / (1 + exp(-10*(x-0.5)))

HORIZON_DAYS = 4380.0   # 12年 x 365天  (K12, 6-18岁)


def grade_of_day(sim_day):
    """sim_day(0..4379) 对应年级下标。"""
    g = int(clamp(math.floor(sim_day / 365.0), 0, 11))
    return g


def age_of_day(sim_day):
    """6岁 + sim_day/365 → (年, 天) 显示用。"""
    total = max(0, sim_day)
    years = int(total // 365) + 6
    days = int(total % 365)
    return years, days


def age_str(sim_day):
    y, d = age_of_day(sim_day)
    return "%d岁%d天" % (y, d)


def stage_of_day(sim_day):
    """认知发展阶段(参考 4380 天核心代码的认知阶段阈值)。"""
    if sim_day < 700:
        return "感知积累期", "🌱"
    elif sim_day < 1500:
        return "规则内化期", "🌿"
    elif sim_day < 2400:
        return "模型建立期", "🌳"
    else:
        return "公理推理期", "🏛"


class GrowthCurve:
    """S型理想成长曲线: 满分 5.0(参考代码注释: 逻辑回归曲线模拟早期缓慢、
    中期爆发、后期平稳)。"""

    @staticmethod
    def ideal(sim_day, horizon=HORIZON_DAYS):
        x = clamp(sim_day / horizon, 0.0, 1.0)
        return 5.0 / (1.0 + math.exp(-10.0 * (x - 0.5)))

    @staticmethod
    def inverse(score):
        """由成长分(0..5)反解达到该水平的等效天数(双时间轴核心)。"""
        s = clamp(score, 1e-6, 5.0 - 1e-6)
        x = 0.5 - math.log(5.0 / s - 1.0) / 10.0
        return clamp(x, 0.0, 1.0) * HORIZON_DAYS

# ====================================================== 认知状态(空白学生体) ==
# 对应权利要求5: 剥离知识内容、保留认知发展规律与学习行为模式的空白学生体
# 参考代码(AlphaGo Zero迁移工程): level/attention/fatigue/thinking_speed + 教学动作

DIM_KEYS = ["PER", "RUL", "MOD", "REA", "INT"]
DIM_NAMES = {"PER": "感知力", "RUL": "规则理解", "MOD": "建模能力",
             "REA": "推理能力", "INT": "科学直觉"}
DIM_ICONS = {"PER": "👁", "RUL": "🧩", "MOD": "🧱", "REA": "⚖", "INT": "💡"}

# (id, 名称, 图标, 各维基础增益, 疲劳增量, 注意力增量)
# 增益数值按"每天一次主要学习行为"标定, 并经效率×(1-当前维)衰减, 保证渐进收敛。
ACTIONS = [
    ("jiangjie", "讲解精读", "📖", {"PER": 0.030, "RUL": 0.012}, 0.05, -0.02),
    ("liti",    "例题演练", "🧮", {"RUL": 0.030, "MOD": 0.016, "REA": 0.006}, 0.08, -0.05),
    ("fansi",   "反思总结", "🧠", {"RUL": 0.008, "MOD": 0.012, "REA": 0.020, "INT": 0.008}, 0.02, -0.02),
    ("hudong",  "互动探究", "🤝", {"PER": 0.012, "MOD": 0.022, "REA": 0.006, "INT": 0.012}, 0.05, 0.05),
    ("xiuxi",   "休息恢复", "😴", {}, -0.45, 0.12),
]
ACT_BY_ID = {a[0]: a for a in ACTIONS}

STAGE_SPEED = {"感知积累期": 1.0, "规则内化期": 1.2, "模型建立期": 1.5, "公理推理期": 2.0}


class StudentState:
    """空白学生体: 不含具体知识, 只保留认知发展规律与学习行为模式。"""

    def __init__(self):
        # 空白学生体初始态(6岁感知期, 对齐榜样曲线的起点)
        self.dims = {"PER": 0.08, "RUL": 0.02, "MOD": 0.02, "REA": 0.01, "INT": 0.01}
        self.attention = 0.85          # 注意力
        self.fatigue = 0.15            # 疲劳度 0-1
        self.retention = 1.0           # 记忆保持率
        self.thinking_speed = 1.0      # 思维速度(随认知阶段成长)

    def aggregate(self):
        return sum(self.dims.values()) / len(self.dims)

    def score5(self):
        return self.aggregate() * 5.0

    def snapshot(self):
        return [self.dims[k] for k in DIM_KEYS], self.attention, self.fatigue, \
               self.retention, self.thinking_speed

    def load_snapshot(self, snap):
        dims, self.attention, self.fatigue, self.retention, self.thinking_speed = snap
        for i, k in enumerate(DIM_KEYS):
            self.dims[k] = dims[i]

    # -- 模拟克隆(供 MCTS 推演, 不污染真实状态) --------------------------------
    def clone(self):
        s = StudentState()
        s.dims = dict(self.dims)
        s.attention, s.fatigue = self.attention, self.fatigue
        s.retention, s.thinking_speed = self.retention, self.thinking_speed
        return s

    def apply(self, action_id, difficulty, stage_name, target=1.0, weight=1.0):
        """执行一次教学动作, 返回 (效果明细, 疲劳提醒, 效率, 契合度)。
        difficulty: 知识点难度(0..1, 最近发展区: 略高于当前水平时增益最大);
        target: 榜样曲线在当天给出的维度上限(0..1), 学生只能向标尺逼近 →
        保证"以榜样成长曲线为准绳"的收敛语义;
        weight: 数据驱动层拟合出的该动作策略权重(默认1.0)。"""
        act = ACT_BY_ID[action_id]
        eff = self.attention * (1.0 - 0.55 * self.fatigue) * (0.85 + 0.15 * self.retention)
        speed = STAGE_SPEED.get(stage_name, 1.0)
        skill = self.aggregate()
        zone = math.exp(-2.6 * ((difficulty - skill) - 0.18) ** 2)   # i+1 区最优
        zone = clamp(zone, 0.25, 1.0)
        details, fatigue_note = [], False

        for dim, base in act[3].items():
            room = max(0.0, min(target, 0.995) - self.dims[dim])
            g = base * eff * speed * zone * room * weight
            old = self.dims[dim]
            self.dims[dim] = min(0.995, old + g)
            if g > 1e-4:
                details.append((dim, g))
        # 疲劳 / 注意力 / 保持率
        self.fatigue = clamp(self.fatigue + act[4])
        self.attention = clamp(self.attention + act[5])
        if act[4] > 0.03:
            self.retention = clamp(self.retention - 0.0015, 0.70, 1.0)
        if action_id == "fansi":
            self.retention = clamp(self.retention + 0.015, 0.70, 1.0)
        # 过夜恢复(每次行为跨过一天)
        self.fatigue = self.fatigue * 0.55
        self.attention = self.attention + (0.88 - self.attention) * 0.22
        if self.fatigue > 0.62:
            fatigue_note = True
        return details, fatigue_note, eff, zone

    def night_decay(self):
        self.fatigue *= 0.55
        self.attention = self.attention + (0.88 - self.attention) * 0.22


# ==================================================== 学习轨迹系统 (v3) =======
# 核心升级: 从"学生状态模拟器"升级为可记录"如何学习 / 如何犯错 / 如何纠正 /
# 掌握度如何变化"的学习轨迹系统。职责边界清晰, 与既有 StudentState 不冲突:
#   StudentState     = 学生整体状态(认知维度 / 注意力 / 疲劳 / 记忆) —— 保留
#   SkillState       = 学生对某个具体知识 / 技能的掌握状态(会/不会)
#   ErrorRecord      = 某技能上反复出现的错误 / 认知误区
#   LearningEpisode  = 一次完整学习闭环(学习→评估→错误→纠正→掌握度更新→记录)
#   MemoryRecord     = 记忆 / 遗忘事件(遗忘曲线, 以 dict 记录)

ERROR_CATALOG = [
    ("concept", "概念错误", "对核心概念理解有误", "重新讲解概念并用生活类比"),
    ("formula", "公式错误", "公式记忆或选用错误", "重新推导公式并做变式练习"),
    ("calc", "计算错误", "计算过程粗心出错", "放慢步骤、逐行验算"),
    ("unit", "单位错误", "单位换算或标注遗漏", "强调单位量纲与换算"),
    ("read", "审题错误", "未抓住题目关键条件", "圈画关键条件、复述题意"),
    ("reason", "推理错误", "逻辑推理链条断裂", "拆解为多步小问题逐步推理"),
    ("forget", "知识遗忘", "前置知识记忆消退", "回看前置知识点并间隔复习"),
    ("attention", "注意力下降", "专注不足导致出错", "短暂休息后重新集中"),
    ("fatigue", "疲劳导致", "疲劳状态下判断力下降", "安排休息恢复"),
    ("prereq", "前置知识缺失", "缺少必要的前置技能", "回到前置知识补课"),
    ("model", "建模错误", "无法把问题抽象为模型", "示范建模过程"),
    ("misunderstand", "不理解题意", "读不懂题目要求", "逐句翻译题意、举例说明"),
    ("guess", "随机猜错", "凭感觉猜测", "要求说明解题依据"),
]
ERROR_BY_ID = {e[0]: e for e in ERROR_CATALOG}


def skill_id_of(subject, topic):
    """技能稳定标识(JSON 友好, 避免中文路径问题)。"""
    return "%s::%s" % (subject, topic)


class SkillState:
    """学生对某个具体知识/技能的掌握状态(会/不会 的量化层)。
    与 StudentState(整体状态)明确分离, 二者不冲突、不重复。"""

    def __init__(self, skill_id, skill_name, subject="", chapter=""):
        self.skill_id = skill_id
        self.skill_name = skill_name
        self.subject = subject
        self.chapter = chapter
        self.mastery = 0.0
        self.confidence = 0.5
        self.attempts = 0
        self.correct_count = 0
        self.error_count = 0
        self.last_seen = None
        self.forgetting_rate = 0.02
        self.misconception_count = 0
        self.successful_retry_count = 0

    def record_attempt(self, correct, retry_correct=False):
        self.attempts += 1
        if correct:
            self.correct_count += 1
        else:
            self.error_count += 1
        if retry_correct:
            self.successful_retry_count += 1

    def apply_forgetting(self, gap_days):
        """间隔复习遗忘: 越久未见, 掌握度衰减越多(遗忘曲线近似)。"""
        if gap_days is None or gap_days <= 0:
            return
        decay = self.forgetting_rate * min(gap_days, 365) / 365.0
        self.mastery = max(0.0, self.mastery - decay)

    def update_mastery(self, delta, correct=False, retry_correct=False):
        """按评估结果更新掌握度与置信度, 并维护计数器。"""
        self.record_attempt(correct, retry_correct)
        self.mastery = clamp(self.mastery + delta, 0.0, 1.0)
        if self.attempts > 0:
            target_conf = 0.5 + 0.5 * (self.correct_count / self.attempts)
            self.confidence = clamp(self.confidence * 0.7 + target_conf * 0.3, 0.0, 1.0)

    def to_dict(self):
        return {
            "skill_id": self.skill_id, "skill_name": self.skill_name,
            "subject": self.subject, "chapter": self.chapter,
            "mastery": round(self.mastery, 4),
            "confidence": round(self.confidence, 4),
            "attempts": self.attempts, "correct_count": self.correct_count,
            "error_count": self.error_count, "last_seen": self.last_seen,
            "forgetting_rate": self.forgetting_rate,
            "misconception_count": self.misconception_count,
            "successful_retry_count": self.successful_retry_count,
        }

    @classmethod
    def from_dict(cls, d):
        s = cls(d.get("skill_id", ""), d.get("skill_name", ""),
                d.get("subject", ""), d.get("chapter", ""))
        s.mastery = clamp(float(d.get("mastery", 0.0)), 0, 1)
        s.confidence = clamp(float(d.get("confidence", 0.5)), 0, 1)
        s.attempts = int(d.get("attempts", 0))
        s.correct_count = int(d.get("correct_count", 0))
        s.error_count = int(d.get("error_count", 0))
        s.last_seen = d.get("last_seen")
        s.forgetting_rate = float(d.get("forgetting_rate", 0.02))
        s.misconception_count = int(d.get("misconception_count", 0))
        s.successful_retry_count = int(d.get("successful_retry_count", 0))
        return s


class ErrorRecord:
    """某个技能上反复出现的错误/认知误区(回答"学生为什么不会 / 卡在哪里")。"""

    def __init__(self, skill_id, error_type, error_name="",
                 misconception="", correction_method=""):
        self.skill = skill_id
        self.error_type = error_type
        self.error_name = error_name or error_type
        self.misconception = misconception
        self.first_seen = None
        self.last_seen = None
        self.count = 0
        self.corrected = False
        self.correction_method = correction_method
        self.recurrence_count = 0

    def hit(self, day):
        self.count += 1
        if self.first_seen is None:
            self.first_seen = day
        if self.last_seen is not None and day > self.last_seen:
            self.recurrence_count += 1
        self.last_seen = day

    def mark_corrected(self):
        self.corrected = True

    def key(self):
        return "%s||%s" % (self.skill, self.error_type)

    def to_dict(self):
        return {
            "skill": self.skill, "error_type": self.error_type,
            "error_name": self.error_name, "misconception": self.misconception,
            "first_seen": self.first_seen, "last_seen": self.last_seen,
            "count": self.count, "corrected": self.corrected,
            "correction_method": self.correction_method,
            "recurrence_count": self.recurrence_count,
        }

    @classmethod
    def from_dict(cls, d):
        r = cls(d.get("skill", ""), d.get("error_type", ""),
                d.get("error_name", ""), d.get("misconception", ""),
                d.get("correction_method", ""))
        r.first_seen = d.get("first_seen")
        r.last_seen = d.get("last_seen")
        r.count = int(d.get("count", 0))
        r.corrected = bool(d.get("corrected", False))
        r.recurrence_count = int(d.get("recurrence_count", 0))
        return r


class LearningEpisode:
    """一次完整学习闭环的结构化记录(可落盘 jsonl, 供大模型训练 / 分析)。"""

    FIELDS = ("day", "age", "subject", "chapter", "skill", "before_mastery",
              "learning_action", "learning_material", "question", "student_answer",
              "correct", "error_type", "misconception", "confusion", "feedback",
              "correction", "retry", "retry_correct", "after_mastery",
              "attention", "fatigue", "motivation", "retention",
              "timestamp", "episode_id")

    def __init__(self, **kw):
        for f in self.FIELDS:
            setattr(self, f, kw.get(f))

    def to_dict(self):
        return {f: getattr(self, f) for f in self.FIELDS}

    @classmethod
    def from_dict(cls, d):
        return cls(**{f: d.get(f) for f in cls.FIELDS})


# ==================================================== 教育版 MCTS 规划器 =======
# 对应权利要求2/10: MCTS+UCB 动态路径规划, 模拟推演"动作->奖励->回传",
# 奖励函数=与榜样对齐度(参考 AlphaGo Zero 迁移工程 alignment_reward)

class MCTSNode:
    __slots__ = ("state", "parent", "action", "children", "visits", "value")

    def __init__(self, state, parent=None, action=None):
        self.state = state          # StudentState 快照
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0

    def ucb(self, c=1.4):
        if self.visits == 0:
            return float("inf")
        return self.value / self.visits + c * math.sqrt(
            math.log(self.parent.visits + 1) / self.visits)


class MCTSPlanner:
    """在教育仿真里做一步"模拟推演", 选择最优教学动作; 全部在克隆状态上运行,
    不修改真实学生。迭代次数自适应: 以时间预算为约束, 机器越快迭代越多。"""

    ACT_IDS = [a[0] for a in ACTIONS]

    def __init__(self, iterations=46, depth=4, time_budget_ms=70, min_iters=24):
        self.iterations = iterations
        self.depth = depth
        self.time_budget_ms = time_budget_ms
        self.min_iters = min_iters
        self.last_iters = iterations

    @staticmethod
    def _reward(st, day):
        """对齐奖励 = 能力水平 × 思维速度 × (1-|疲劳-0.3|) + 贴近理想曲线。"""
        agg = st.aggregate()
        align = agg * st.thinking_speed * (1.0 - abs(st.fatigue - 0.3))
        close = -abs(st.score5() - GrowthCurve.ideal(day)) * 0.35
        return align + close

    def decide(self, student, real_day, difficulty, stage_name, weights=None):
        t0 = now_ms()
        target = GrowthCurve.ideal(real_day) / 5.0
        root = MCTSNode(student.clone())
        root.visits = 1
        actions = self.ACT_IDS
        it = 0
        while True:
            if it >= self.min_iters and (now_ms() - t0) >= self.time_budget_ms:
                break
            if it >= 220:
                break
            it += 1
            # select
            node = root
            while node.children:
                node = max(node.children, key=lambda n: n.ucb())
            # expand: 以当前真实状态展开全部动作子节点(共享同一父状态以控规模)
            if not node.children:
                for a in actions:
                    s = student.clone()
                    w = weights.get(a, 1.0) if weights else 1.0
                    s.apply(a, difficulty, stage_name, target, w)
                    node.children.append(MCTSNode(s, node, a))
            # rollout
            leaf = random.choice(node.children)
            s = leaf.state.clone()
            for _ in range(self.depth):
                a = random.choice(actions)
                if s.fatigue > 0.75:
                    a = "xiuxi"
                w = weights.get(a, 1.0) if weights else 1.0
                s.apply(a, difficulty, stage_name, target, w)
            reward = self._reward(s, real_day)
            # backprop
            n = leaf
            while n:
                n.visits += 1
                n.value += reward
                n = n.parent
        self.last_iters = it
        # 自适应: 按本轮每迭代耗时, 把下一次迭代数收敛到时间预算内
        cost = max(0.01, (now_ms() - t0) / max(1, it))
        self.iterations = int(clamp(self.time_budget_ms / cost * 0.85, 24, 200))
        stats = sorted(((c.action, c.visits, c.value / max(1, c.visits))
                        for c in root.children),
                       key=lambda x: -x[1])
        best = stats[0][0] if stats else "jiangjie"
        return best, stats, now_ms() - t0

    @staticmethod
    def greedy_decide(student, difficulty, stage_name, day, weights=None):
        """快速启发式决策(用于大规模时间压缩模拟, 秒级跑完数千天)。"""
        if student.fatigue > 0.62:
            return "xiuxi"
        target = GrowthCurve.ideal(day) / 5.0
        eff = student.attention * (1.0 - 0.55 * student.fatigue)
        skill = student.aggregate()
        zone = math.exp(-2.6 * ((difficulty - skill) - 0.18) ** 2)
        best, best_v = "jiangjie", -1.0
        for aid in MCTSPlanner.ACT_IDS:
            act = ACT_BY_ID[aid]
            v = 0.0
            for dim, base in act[3].items():
                v += base * eff * max(0.0, target - student.dims[dim])
            v *= zone * (0.8 + 0.4 * random.random())
            if weights:
                v *= weights.get(aid, 1.0)
            if aid == "xiuxi":
                v = (student.fatigue - 0.2) * 2.0
            if v > best_v:
                best_v, best = v, aid
        return best


# ============================================================ 学生状态机 ======

class CognitiveStatus:
    """多维认知状态(对应权利要求10: 知识掌握度/认知发展度/心理匹配度)。"""

    def __init__(self, st: StudentState):
        self.st = st

    @property
    def knowledge(self):
        return self.st.aggregate()

    @property
    def cognitive(self):
        # 认知发展度: 高层能力(建模+推理+直觉)占比加权
        d = self.st.dims
        return (d["MOD"] * 0.4 + d["REA"] * 0.4 + d["INT"] * 0.2)

    @property
    def psychology(self):
        # 心理匹配度: 低疲劳 + 高注意 + 高保持 → 学习心理状态健康度
        return clamp(1.0 - self.st.fatigue * 0.5, 0, 1) * 0.5 + \
               self.st.attention * 0.3 + self.st.retention * 0.2

# ============================================================ AI学生引擎 ======

class AIStudentEngine:
    """ai学生引擎: 起点=学生初始学情(年级/姓名/状态), 终点=榜样模型知识库,
    中间路径由 MCTS/启发式动态规划; 全程产出思考日志事件流。"""

    def __init__(self, on_change=None):
        self.on_change = on_change
        self.role_key = "newton"
        self.grade_idx = 6                 # 默认: 初中一年级 (12岁起点)
        self.student_name = "小原"
        self.learn_state = "专注探究"
        self.student = StudentState()
        self.sim_day = 0                   # 引擎指导下的学习天数(打卡/模拟)
        self.history = deque(maxlen=3000)  # 思考日志事件
        self.perf_history = deque(maxlen=5000)  # (real_day, score5) 成长轨迹
        self.traj_rows = []                # 4380天逐日轨迹行(CSV 数据集)
        self.chat_mem_local = deque(maxlen=10)
        self.chat_mem_remote = deque(maxlen=10)
        self.last_plan = None
        self.topic_idx = 0
        self.auto_lesson_count = 0
        self.last_action = None
        self._finished_announced = False
        self.mcts = MCTSPlanner()                  # 自适应时间预算的路径规划器
        self.action_weights = {a[0]: 1.0 for a in ACTIONS}   # 数据驱动策略权重
        self.data_driven = False                   # 是否已从档案拟合权重
        self._t0 = None
        # ---- 学习轨迹系统状态(v3) ----
        self.skills = {}            # skill_id -> SkillState
        self.errors = {}            # error_key -> ErrorRecord
        self.episodes = []          # [LearningEpisode, ...]
        self.memory_records = []    # [dict, ...] 记忆/遗忘事件
        self._episode_flushed = 0
        self._memory_flushed = 0
        # ---- 修炼体系状态(v4): 九字秘法 + 境界/榜位 ----
        self._art_hint = None           # 当前正在修炼的秘法(结果记入该式独立修为)
        self._level_realm_seen = None   # 已到过的水平境界下标(用于触发"突破")
        # ---- 教材投喂状态(v4.1): 课本/练习驱动的自动学习 ----
        self.material = None            # MaterialBook 或 None
        self.mat_point = 0              # 知识点游标
        self.mat_question = 0           # 已做的教材题数
        self._q_seen = set()            # 已做过的题干指纹
        self._pending_question = ""     # 本轮正在做的教材题(写入 episode)

    # ------------------------------------------------------------ 基础 ----
    def role(self):
        return ROLE_MODELS[self.role_key]

    @property
    def base_days(self):
        return self.grade_idx * 365

    @property
    def allowed_exec(self):
        """从当前入学起点到 K12 顶点可执行的总学习日(4380-base)。"""
        return int(HORIZON_DAYS - self.base_days)

    @property
    def real_day(self):
        return int(min(HORIZON_DAYS - 1, self.base_days + self.sim_day))

    @property
    def remain_days(self):
        return max(0, int(self.allowed_exec - self.sim_day))

    def push_traj_row(self, action_id):
        """逐日记录一行成长轨迹(0-100岁数据轴)。"""
        try:
            subj, topic, _ = self.current_topic()
            equiv, gap, score, ideal = self.dual_timeline()
            self.traj_rows.append({
                "abs": abs_day_of(self), "age": age_str(self.real_day),
                "grade": self.grade_label(), "stage": self.stage()[0],
                "score": score, "ideal": ideal, "equiv": age_str(equiv),
                "gap": gap, "fat": round(self.student.fatigue, 4),
                "att": round(self.student.attention, 4),
                "act": ACT_BY_ID[action_id][1],
                "subj": subj, "topic": topic,
                "realm": realm_of_day(self.real_day)["name"],
                "rank": self.level_rating()["rank"],
                "dims": [round(self.student.dims[k], 4) for k in DIM_KEYS]})
            if len(self.traj_rows) > 6000:
                del self.traj_rows[0]
        except Exception:
            pass

    def emit(self, kind, msg, dur_ms=None):
        self.history.append((kind, msg, dur_ms))
        if self.on_change:
            try:
                self.on_change()
            except Exception:
                pass

    # ---------------------------------------------------- 学年 / 知识点游标 --
    def grade_label(self):
        return GRADES[grade_of_day(self.real_day)]

    def stage(self):
        return stage_of_day(self.real_day)

    def current_subject(self):
        if self.material is not None:
            return self.material.subject
        d = self.real_day
        role = self.role()
        focus = list(role["subjects"])
        if d < 700:                       # 低龄: 基础三科为主
            seq = ["语文", "数学", "英语", "数学", "语文"]
        elif d < 2400:
            seq = focus + ["语文", "英语"] + focus
        else:
            seq = focus + focus + ["语文"]
        return seq[(d // 9) % len(seq)]

    def current_topic(self):
        if self.material is not None:
            pts = self.material.flat_points()
            if pts:
                i = int(clamp(self.mat_point, 0, len(pts) - 1))
                return self.material.subject, pts[i][2][:26], i / float(len(pts))
        subj = self.current_subject()
        pool = KNOWLEDGE_POOL[subj]
        idx = (int(self.real_day // 3) + grade_of_day(self.real_day) * 3) % len(pool)
        return subj, pool[idx], idx / float(len(pool))

    def difficulty_of_topic(self):
        if self.material is not None:
            pts = self.material.flat_points()
            if pts:
                i = int(clamp(self.mat_point, 0, len(pts) - 1))
                pos = i / float(len(pts))
                ln = len(pts[i][2])
                return float(clamp(0.30 + 0.50 * pos + min(0.15, ln / 2000.0), 0.20, 0.95))
        _, _, frac = self.current_topic()
        return 0.35 + 0.55 * frac

    def milestone_note(self, real_day):
        """榜样模型中当前所处成长里程碑描述。"""
        age_y = real_day / 365.0 + 6.0
        ms = self.role()["milestones"]
        note = None
        for a, txt in ms:
            if age_y >= a:
                note = (a, txt)
            else:
                break
        if note is None:
            return "出生 ~ 学龄前: 以感知与语言积累为主"
        return "≈%d岁: %s" % (note[0], note[1])

    # ------------------------------------------------- 境界 · 榜位(v4) ------
    def realm(self):
        """按实际年龄所处的修炼境界。"""
        return realm_of_day(self.real_day)

    def role_timeline_note(self):
        """榜样时间轴: 返回 (已达成的里程碑列表, 下一个目标 或 None)。"""
        age_y = self.real_day / 365.0 + 6.0
        tl = ROLE_TIMELINE.get(self.role_key, [])
        done, nxt = [], None
        for item in tl:
            if age_y >= item[0]:
                done.append(item)
            elif nxt is None:
                nxt = item
        return done, nxt

    def _art_skill(self, key):
        """九字秘法某一式的修为(独立技能层, 随 skill_states.json 落盘)。"""
        art = ART_BY_KEY.get(key)
        if art is None:
            return None
        sid = art_skill_id(key)
        sk = self.skills.get(sid)
        if sk is None:
            sk = SkillState(sid, "%s·%s" % (art["ch"], art["name"]), "秘法",
                            realm_of_key(art["realm"])["name"])
            self.skills[sid] = sk
        return sk

    def art_mastery(self, key):
        sk = self.skills.get(art_skill_id(key))
        return sk.mastery if sk else 0.0

    def arts_summary(self):
        """九字秘法总览: 每式的修为/段位/修炼次数。"""
        out = []
        for art in NINE_ARTS:
            sk = self.skills.get(art_skill_id(art["key"]))
            m = sk.mastery if sk else 0.0
            out.append({
                "key": art["key"], "ch": art["ch"], "name": art["name"],
                "tip": art["tip"], "key_point": art["key_point"],
                "realm_key": art["realm"],
                "realm": realm_of_key(art["realm"])["name"],
                "mastery": round(m, 4), "tier": tier_of(m),
                "uses": (sk.attempts if sk else 0),
                "ok": (sk.correct_count if sk else 0),
                "err": (sk.error_count if sk else 0),
            })
        return out

    def current_model(self):
        """「创」式当前应该演化的物理模型(按修为推进)。"""
        score = self.student.score5()
        idx = int(clamp(score / 5.0, 0.0, 1.0) * (len(PHYSICS_MODELS) - 1))
        return PHYSICS_MODELS[int(idx)]

    def level_rating(self):
        """统一评价标准(v4): 修为 → 境界 / 段位 / 榜位 / 榜样等效水平 / 九字秘法。

        对应设计原稿: 不以分数计量而以水平计量; 可量化为"榜样几岁的水平";
        以 ai学生 作为同一把尺子, 给出境界内的榜位。返回值可直接落盘/导出/喂模型。
        """
        d = int(self.real_day)
        equiv_day, gap, score, ideal = self.dual_timeline()
        cur = realm_of_day(d)
        lvl = realm_of_day(equiv_day)
        lo, hi = lvl["day"]
        pos = clamp((equiv_day - lo) / max(1.0, float(hi - lo)), 0.0, 1.0)
        cross = realm_index(equiv_day) - realm_index(d)
        if cross > 0:
            trend, tcol = "越境 %d 级" % cross, OK
        elif cross < 0:
            trend, tcol = "待追 %d 级" % (-cross), BAD
        else:
            trend, tcol = "同境", WARN
        arts = self.arts_summary()
        avg = sum(a["mastery"] for a in arts) / float(len(arts)) if arts else 0.0
        unlocked = sum(1 for a in arts
                       if realm_index(realm_of_key(a["realm"])["day"][0]) <= realm_index(equiv_day))
        done, nxt = self.role_timeline_note()
        nr = next_realm_of(d)
        return {
            "day": d, "age": age_str(d), "grade": self.grade_label(),
            "score5": round(score, 3), "ideal5": round(ideal, 3),
            "realm": cur["key"], "realm_name": cur["name"], "realm_emoji": cur["emoji"],
            "level_realm": lvl["key"], "level_realm_name": lvl["name"],
            "level_realm_emoji": lvl["emoji"],
            "tier": tier_of(pos), "rank": int(round(pos * 100)),
            "rank_pos": round(pos, 4),
            # 跨境界的全局榜位(境界下标×100 + 境界内榜位), 便于横向比较与排序
            "rank_global": realm_index(equiv_day) * 100 + int(round(pos * 100)),
            "equiv_day": round(equiv_day, 1), "equiv_age": age_str(equiv_day),
            "gap_days": int(gap), "cross": int(cross), "trend": trend,
            "role": self.role_key, "role_label": self.role()["label"],
            "focus": cur["focus"], "task": cur["task"],
            "next_realm": (nr["name"] if nr else "已出师(K12终点)"),
            "milestone_done": [t[1] for t in done[-3:]],
            "milestone_next": (nxt[1] if nxt else ""),
            "milestone_next_age": (nxt[0] if nxt else None),
            "milestone_next_goal": (nxt[2] if nxt else ""),
            "arts": arts, "arts_avg": round(avg, 4),
            "arts_unlocked": unlocked, "arts_total": len(arts),
            "model": self.current_model(),
            "model_total": PHYSICS_MODEL_TARGET,
            "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _check_breakthrough(self):
        """修为跨过境界门槛 → 触发「突破」事件(修炼语汇, 对应 PPT 的进度条成就感)。"""
        try:
            rating = self.level_rating()
            idx = REALMS.index(realm_of_key(rating["level_realm"]))
            if self._level_realm_seen is None:
                self._level_realm_seen = idx
                return
            if idx > self._level_realm_seen:
                self._level_realm_seen = idx
                nxt = REALMS[idx + 1]["name"] if idx + 1 < len(REALMS) else "出师"
                self.emit("GOAL", "🌟 突破! 修为越过「%s」→ 当前水平境界「%s%s」"
                                  "(等效 %s %s · 榜位 %d/100); 下一境: %s"
                          % (REALMS[idx - 1]["name"], rating["level_realm_emoji"],
                             rating["level_realm_name"], rating["role_label"],
                             rating["equiv_age"], rating["rank"], nxt))
        except Exception:
            pass

    def practice_art(self, key, source="九字秘法"):
        """修炼一式秘法(推进1个学习日): 复用完整学习闭环, 结果记入该式独立修为。"""
        art = ART_BY_KEY.get(key)
        if art is None:
            return None, []
        self._art_hint = key
        try:
            ev = self.perform_action(art["action"], source="%s·%s" % (source, art["ch"]))
        finally:
            self._art_hint = None
        return art, (ev or [])

    # ------------------------------------------------ 教材投喂 · 自动学习 -----
    def load_material(self, book, reset=True):
        """装载教材知识地图(课本+练习), 之后 current_topic 走真实教材内容。"""
        self.material = book
        if reset:
            self.mat_point = 0
            self.mat_question = 0
            self._q_seen = set()
        self.emit("GOAL", "📚 教材已投喂: %s | 章%d 节%d 知识点%d 练习%d题"
                  % (book.title or book.subject, book.stats()["chapters"],
                     book.stats()["sections"], book.stats()["points"],
                     book.stats()["questions"]))
        return self.material_stats()

    def material_stats(self):
        if self.material is None:
            return {}
        pts = self.material.flat_points()
        st = dict(self.material.stats())
        i = int(clamp(self.mat_point, 0, max(0, len(pts) - 1)))
        st["point_cursor"] = i
        st["chapter_now"] = pts[i][0] if pts else ""
        st["section_now"] = pts[i][1] if pts else ""
        st["questions_done"] = self.mat_question
        return st

    def current_question(self):
        """当前节尚未做过的教材题(题干); 没有则返回 ""。"""
        if self.material is None:
            return ""
        qs = self.material.flat_questions()
        if not qs:
            return ""
        pts = self.material.flat_points()
        chap = sec = ""
        if pts:
            i = int(clamp(self.mat_point, 0, len(pts) - 1))
            chap, sec = pts[i][0], pts[i][1]
        for ch, se, _qno, qt in qs:                 # 优先: 当前节
            if ch == chap and se == sec and not self._q_done(qt):
                return qt
        for _ch, _se, _qno, qt in qs:               # 退化: 任意未做题
            if not self._q_done(qt):
                return qt
        return ""

    def _q_done(self, qt):
        return (qt or "").strip()[:40] in self._q_seen

    def _art_for_question(self, qtext):
        """按题干特征挑一式最该练的秘法。"""
        t = qtext or ""
        if any(k in t for k in ("受力", "平衡", "摩擦", "斜面", "绳", "杆", "拉力",
                                "支持力", "浮力", "压强")):
            return "fen"
        if any(k in t for k in ("证明", "推导", "验证", "公式")):
            return "tui"
        if any(k in t for k in ("实验", "测量", "作图", "轨道", "模型", "传送带")):
            return "chuang"
        if any(k in t for k in ("下列说法", "正确的是", "错误的是", "判断")):
            return "miao"
        if any(k in t for k in ("求", "计算", "多少", "多大", "速度", "加速度",
                                "位移", "时间")):
            return "jie"
        return "shan"

    def _analyze_question(self, qtext):
        """审题分析: 关键词 / 题型 / 已知量 / 目标量。"""
        t = qtext or ""
        kw = [k for k in PHY_KEYWORDS if k in t][:6]
        kind = "计算"
        for name, words in QUESTION_KINDS:
            if any(w in t for w in words):
                kind = name
                break
        given = re.findall(
            r"([A-Za-z\u4e00-\u9fa5]{1,4})\s*[=＝]\s*(-?\d+(?:\.\d+)?)\s*"
            r"([A-Za-z%°℃/²³·]{0,4})", t)
        asked = re.findall(r"(?:求|计算|问|探究)[:：]?\s*([^。？?；;]{2,26})", t)
        return {"kind": kind, "kw": kw, "given": given, "asked": asked}

    def material_think_chain(self, qtext):
        """一道题的思考过程(学生视角): 读题 → 删 → 解/分/合/列 → 路线。"""
        a = self._analyze_question(qtext)
        art_key = self._art_for_question(qtext)
        stage, icon = self.stage()
        head = (qtext or "").strip().replace("\n", " ")
        ev = [("SENSE", "📖 读题(第%d个学习日 · %s%s): %s"
               % (self.sim_day + 1, icon, stage,
                  head[:70] + ("…" if len(head) > 70 else "")))]
        if a["kw"]:
            ev.append(("SENSE", "🔎 划关键词: %s | 初判题型: %s | 该练的字: %s"
                       % ("、".join(a["kw"]), a["kind"],
                          ART_BY_KEY[art_key]["ch"])))
        ev.append(("ACT", "🀄 删: 把题干一句一句转成图与量, 转完的句子从脑子里删掉"
                   + ("; 抄出已知: " + ", ".join("%s=%s%s" % (g[0], g[1], g[2])
                                                for g in a["given"][:4])
                      if a["given"] else "")))
        if a["asked"]:
            ev.append(("PLAN", "🎯 要问的是: %s" % "；".join(a["asked"][:2])))
        arts = [art_key]
        if a["kind"] == "计算":
            arts += ["jie", "lie"]
        elif a["kind"] == "实验":
            arts += ["chuang", "lie"]
        elif a["kind"] in ("说明", "证明"):
            arts += ["tui", "miao"]
        else:
            arts += ["jie", "lie"]
        for k in dict.fromkeys(arts):
            if k == art_key:
                continue
            ev.append(("CURVE", "🀄 顺手过一遍「%s·%s」: %s"
                       % (ART_BY_KEY[k]["ch"], ART_BY_KEY[k]["name"],
                          ART_BY_KEY[k]["key_point"][:44])))
        ev.append(("PLAN", "🧭 本题路线: %s → 动笔"
                   % "→".join(ART_BY_KEY[k]["ch"] for k in dict.fromkeys(arts))))
        return ev

    def material_read_chain(self, topic):
        """精读一个知识点时的思考过程。"""
        st, icon = self.stage()
        tp = (topic or "").replace("\n", " ")
        return [
            ("SENSE", "📖 精读知识点(第%d个学习日 · %s%s): %s"
             % (self.sim_day + 1, icon, st, tp[:60])),
            ("ACT", "✏ 划线: 先找定义句与条件句(「当…时」「在…条件下」)"),
            ("ACT", "❓ 自问: 这个结论是从哪一步推出来的? 换个条件还成立吗?"),
            ("ACT", "🀄 推: 从母公式把它推一遍, 不背结论背来路"),
            ("CURVE", "🗺 归位: 挂到已有知识上(当前模型: %s)" % self.current_model()),
        ]

    def material_review_events(self, ep):
        """做完题后的复盘: 对/错 → 错因 → 纠正 → 掌握度与修为。"""
        if ep is None:
            return []
        ev = []
        if ep.correct:
            ev.append(("CURVE", "✓ 做对了: 「%s」掌握 %.0f%%→%.0f%%"
                       % ((ep.skill or "")[:20], (ep.before_mastery or 0) * 100,
                          (ep.after_mastery or 0) * 100)))
        else:
            ev.append(("TIP", "✗ 卡住了: %s —— %s"
                       % (ep.error_type or "错误", (ep.misconception or "")[:56])))
            if ep.correction:
                ev.append(("ACT", "🔁 纠正: %s" % ep.correction[:56]))
            if ep.retry_correct:
                ev.append(("CURVE", "✓ 重试后做出来了: 掌握 %.0f%%→%.0f%%"
                           % ((ep.before_mastery or 0) * 100,
                              (ep.after_mastery or 0) * 100)))
            else:
                ev.append(("TIP", "⏳ 这道还没通: 记下这个坎, 明天用「解」和「列」再练"))
        r = self.level_rating()
        ev.append(("STAGE", "📈 修为 %.2f/5 · %s%s·%s · 榜位 %d/100 · 等效 %s %s"
                   % (r["score5"], r["level_realm_emoji"], r["level_realm_name"],
                      r["tier"], r["rank"], r["role_label"], r["equiv_age"])))
        return ev

    def study_material_day(self, source="📚教材自动学习"):
        """教材驱动的一个学习日: 有题就做题, 没题就精读下一个知识点。

        返回这一天的完整思考事件列表(同时已写入思考日志与学习轨迹)。
        """
        if self.material is None:
            ev = [("TIP", "⚠ 还没投喂教材: 打开「📚 教材投喂 · 自动学习」选择课本/练习文件夹")]
            for e in ev:
                self.emit(*e)
            return ev
        if self.sim_day >= self.allowed_exec:
            self.emit("GOAL", "🏁 本学段的学习日已用完, 可切换年级或重置进度后继续")
            return []
        q = self.current_question()
        ev, act_ev = [], []
        if q:
            pre = self.material_think_chain(q)
            art_key = self._art_for_question(q)
            self._pending_question = q
            try:
                _art, act_ev = self.practice_art(art_key, source=source)
            finally:
                self._pending_question = ""
            self._q_seen.add(q.strip()[:40])
            self.mat_question += 1
        else:
            pre = self.material_read_chain(self.current_topic()[1])
            _art, act_ev = self.practice_art("shan", source=source)
            self.mat_point += 1
        for e in pre:
            self.emit(*e)
        post = self.material_review_events(self.episodes[-1] if self.episodes else None)
        for e in post:
            self.emit(*e)
        ev = pre + list(act_ev or []) + post
        return ev

    # ------------------------------------------------------ 双时间轴比对 ----
    def dual_timeline(self):
        """返回 (等效榜样天数, 超前/落后天数, 学生分5, 理想分5)。"""
        score = self.student.score5()
        ideal = GrowthCurve.ideal(self.real_day)
        equiv_day = min(GrowthCurve.inverse(score), HORIZON_DAYS - 1)
        gap_days = int(round(equiv_day - self.real_day))
        return equiv_day, gap_days, score, ideal

    def gap_status(self):
        _, gap, score, ideal = self.dual_timeline()
        if score >= ideal * 0.998 and gap >= 0:
            return "超前", OK
        if gap < -45:
            return "落后", BAD
        return "跟跑", WARN

    # -------------------------------------------------- 数据驱动层: 拟合 ----
    def fit_from_rows(self, rows):
        """从历史档案(逐日轨迹)拟合各教学动作的实际效果权重 → 数据驱动进化。
        逻辑: 统计相邻两天成长分增量按动作归因, 与全局均值比较后缩放为权重。"""
        try:
            rows = [r for r in rows if r.get("score") is not None]
            if len(rows) < 40:
                return 0
            label2id = {a[1]: a[0] for a in ACTIONS}
            per_act = {a[0]: [] for a in ACTIONS}
            for i in range(len(rows) - 1):
                try:
                    d = float(rows[i + 1]["score"]) - float(rows[i]["score"])
                    a = label2id.get(rows[i].get("act") or "")
                    if a in per_act:
                        per_act[a].append(d)
                except Exception:
                    continue
            means = {}
            for a, vals in per_act.items():
                means[a] = sum(vals) / len(vals) if vals else None
            have = [v for v in means.values() if v is not None]
            if not have:
                return 0
            gmean = sum(have) / len(have)
            new_w = {}
            for a, v in means.items():
                if v is None:
                    new_w[a] = 1.0
                    continue
                # 效果高于全局均值的动作获得更大权重(0.75~1.25), 平滑更新
                raw = 1.0 + (v - gmean) * 30.0
                new_w[a] = clamp(raw, 0.75, 1.25)
            old = self.action_weights
            for a in new_w:
                self.action_weights[a] = old[a] * 0.4 + new_w[a] * 0.6
            self.data_driven = True
            return len(rows)
        except Exception:
            return 0

    # ------------------------------------------------------ 学习行为执行 ----
    def perform_action(self, action_id, source="手动打卡", note=True):
        """真实执行一次教学动作(推进1个学习日), 返回思考事件列表。"""
        if self.sim_day >= self.allowed_exec:
            if not self._finished_announced:
                self._finished_announced = True
                self.emit("GOAL", "🏁 全部K12学习日(共%d天)已执行完毕! 空白学生体已长成, "
                                 "可切换榜样模型/年级继续探索。" % self.allowed_exec)
            return
        subj, topic, _ = self.current_topic()
        diff = self.difficulty_of_topic()
        stage, icon = self.stage()
        target = GrowthCurve.ideal(self.real_day) / 5.0
        w = self.action_weights.get(action_id, 1.0)
        details, tired, eff, zone = self.student.apply(action_id, diff, stage,
                                                       target, w)
        act = ACT_BY_ID[action_id]
        self.topic_idx += 1
        self.sim_day += 1
        self.auto_lesson_count += 1
        self.last_action = action_id
        self.perf_history.append((self.real_day, round(self.student.score5(), 4)))
        self.push_traj_row(action_id)
        ev = []
        ev.append(("SENSE", "👁 感知: %s, 目标知识点「%s·%s」(难度%.2f), 专注%.0f%% 疲劳%.0f%%"
                   % (subj, subj, topic, diff, self.student.attention * 100,
                      self.student.fatigue * 100)))
        ev.append(("ACT", "%s 执行「%s%s」 吸收效率×%.2f, 最近发展区契合×%.2f"
                   % (icon, act[1], act[1], eff, zone)))
        gain_txt = ", ".join("「%s」+%.3f" % (DIM_NAMES[k], g) for k, g in details)
        ev.append(("CURVE", "📈 生长: %s" % (gain_txt if gain_txt else "身心恢复, 疲劳缓解")))
        ev.append(("STAGE", "🪜 阶段: %s%s | 第%d个学习日(剩余%d天) | 年级:%s"
                   % (icon, stage, self.sim_day, self.remain_days, self.grade_label())))
        if tired:
            ev.append(("TIP", "💡 纠偏提示: 疲劳偏高, 榜样模型建议先「休息恢复」再继续, 避免无效学习。"))
        if note:
            for e in ev:
                self.emit(*e)
        self._assess_and_record(action_id, quiet=not note)
        self._check_breakthrough()
        return ev

    # ------------------------------------------------------ 学习轨迹闭环(v3) --
    def get_or_create_skill(self, subject=None, topic=None, chapter=None):
        """按学科+知识点取得(或创建)一个具体技能的掌握状态。"""
        subject = subject or self.current_subject()
        if topic is None:
            _, topic, _ = self.current_topic()
        sid = skill_id_of(subject, topic)
        sk = self.skills.get(sid)
        if sk is None:
            sk = SkillState(sid, topic, subject, chapter or self.grade_label())
            self.skills[sid] = sk
        return sk

    def _pick_error(self, skill, diff):
        """按技能掌握度与学生状态, 从错误目录中挑一个'最可能'的错误类型。"""
        low = skill.mastery < 0.30
        tired = self.student.fatigue > 0.60
        cand = []
        for eid, name, mis, cor in ERROR_CATALOG:
            w = 1.0
            if tired and eid in ("fatigue", "attention"):
                w += 2.0
            if low and eid in ("prereq", "concept", "misunderstand", "forget"):
                w += 1.5
            if not low and eid in ("calc", "unit", "read", "model", "reason", "guess"):
                w += 1.0
            cand.append((w, eid, name, mis, cor))
        total = sum(w for w, *_ in cand)
        r = random.random() * total
        acc = 0.0
        for w, eid, name, mis, cor in cand:
            acc += w
            if r <= acc:
                return eid, name, mis, cor
        return cand[-1][1], cand[-1][2], cand[-1][3], cand[-1][4]

    def _record_error(self, skill, error_id, error_name, misconception, correction):
        key = "%s||%s" % (skill.skill_id, error_id)
        rec = self.errors.get(key)
        if rec is None:
            rec = ErrorRecord(skill.skill_id, error_id, error_name,
                              misconception, correction)
            self.errors[key] = rec
        rec.hit(self.sim_day)
        skill.misconception_count += 1

    def _skill_gain(self, action_id, skill, diff, correct, retry_correct):
        """由 学习行为 + 学生状态 + 评估结果 共同决定技能掌握度变化。
        (合理模拟机制; 接口保留, 未来可替换为真实轨迹数据训练的模型)"""
        base = {"jiangjie": 0.06, "liti": 0.10, "fansi": 0.04,
                "hudong": 0.08, "xiuxi": 0.0}[action_id]
        eff = self.student.attention * (1.0 - 0.5 * self.student.fatigue)
        zone = clamp(math.exp(-2.6 * ((diff - skill.mastery) - 0.18) ** 2), 0.25, 1.0)
        gain = base * eff * zone * (1.0 - skill.mastery)
        if correct:
            pass
        elif retry_correct:
            gain *= 0.55
        else:
            gain *= 0.25
        return gain

    def _memory_record(self, skill):
        return {"episode_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "skill": skill.skill_id, "mastery": round(skill.mastery, 4),
                "retention": round(self.student.retention, 4), "day": self.sim_day,
                "forgetting_rate": skill.forgetting_rate}

    def _assess_and_record(self, action_id, quiet=False):
        """在已执行一次教学动作后, 完成『评估→错误→纠正→再试→掌握度更新→记录』
        学习闭环, 生成一条 LearningEpisode。返回 episode 或 None。"""
        try:
            subject, topic, _ = self.current_topic()
            skill = self.get_or_create_skill(subject, topic)
            if skill.last_seen is not None and self.sim_day > skill.last_seen:
                skill.apply_forgetting(self.sim_day - skill.last_seen)
            before = skill.mastery
            diff = self.difficulty_of_topic()
            act = ACT_BY_ID[action_id]
            rest = (action_id == "xiuxi")
            correct = None
            error_id = error_name = misconception = correction = ""
            confusion = feedback = ""
            question = student_answer = ""
            retry = retry_correct = False
            if not rest:
                question = "【%s·%s】请完成「%s」的练习(难度 %.2f)" % (
                    subject, skill.chapter, topic, diff)
                if self._pending_question:      # 教材投喂: 记录真实题目
                    qt = self._pending_question.strip().replace("\n", " ")
                    question = "【教材题】%s" % (qt[:170] + ("…" if len(qt) > 170 else ""))
                p = skill.mastery * self.student.attention * (1.0 - 0.45 * self.student.fatigue)
                p = clamp(p, 0.04, 0.97)
                correct = random.random() < p
                if correct:
                    student_answer = "作答正确(模拟): 已掌握「%s」的解法" % topic
                    feedback = "反馈: 解答正确, 强化并进入下一难度"
                else:
                    error_id, error_name, misconception, correction = self._pick_error(skill, diff)
                    self._record_error(skill, error_id, error_name, misconception, correction)
                    confusion = misconception
                    feedback = "反馈: 发现错误「%s」" % error_name
                    student_answer = "作答错误(模拟): %s" % misconception
                    retry = True
                    p2 = clamp((skill.mastery + 0.25) * self.student.attention
                               * (1.0 - 0.35 * self.student.fatigue), 0.10, 0.98)
                    retry_correct = random.random() < p2
                gain = self._skill_gain(action_id, skill, diff, correct, retry_correct)
                skill.update_mastery(gain, correct=correct, retry_correct=retry_correct)
                if self._art_hint:                    # 同步记入九字秘法的独立修为
                    art = ART_BY_KEY.get(self._art_hint)
                    a_sk = self._art_skill(self._art_hint) if art else None
                    if art and a_sk is not None:
                        a_before = a_sk.mastery
                        a_gain = self._skill_gain(art["action"], a_sk, diff,
                                                  correct, retry_correct)
                        a_sk.update_mastery(a_gain, correct=correct,
                                            retry_correct=retry_correct)
                        a_sk.last_seen = self.sim_day
                        self.memory_records.append(self._memory_record(a_sk))
                        if not quiet:
                            mark = "✓" if correct else ("✓重试" if retry_correct else "✗")
                            self.emit("PLAN", "🀄 秘法「%s·%s」修炼: %s 修为 %.0f%%→%.0f%% (%s)"
                                      % (art["ch"], art["name"], mark, a_before * 100,
                                         a_sk.mastery * 100, tier_of(a_sk.mastery)))
            else:
                student_answer = "(休息恢复, 无测评)"
                question = "(休息恢复)"
            skill.last_seen = self.sim_day
            motivation = clamp(self.student.attention * (1.0 - 0.4 * self.student.fatigue)
                               * (1.0 + STATE_EFFECT.get(self.learn_state, 0.0)), 0, 1)
            material_label = act[1]
            if self._art_hint and ART_BY_KEY.get(self._art_hint):
                material_label = "秘法·%s | %s" % (ART_BY_KEY[self._art_hint]["ch"], act[1])
            if self._pending_question:
                material_label += " | 教材题"
            ep = LearningEpisode(
                day=self.sim_day, age=round(6.0 + self.real_day / 365.0, 3),
                subject=subject, chapter=skill.chapter, skill=topic,
                before_mastery=round(before, 4), learning_action=action_id,
                learning_material=material_label, question=question,
                student_answer=student_answer, correct=correct, error_type=error_id,
                misconception=misconception, confusion=confusion, feedback=feedback,
                correction=correction, retry=retry, retry_correct=retry_correct,
                after_mastery=round(skill.mastery, 4),
                attention=round(self.student.attention, 4),
                fatigue=round(self.student.fatigue, 4),
                motivation=round(motivation, 4),
                retention=round(self.student.retention, 4),
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                episode_id=uuid.uuid4().hex)
            self.episodes.append(ep)
            self.memory_records.append(self._memory_record(skill))
            if not quiet:
                if rest:
                    self.emit("SENSE", "🧭 学习轨迹: 「%s」休息恢复, 掌握度保持 %.0f%%"
                              % (topic, skill.mastery * 100))
                else:
                    status = "✓正确" if correct else ("✓重试后正确" if retry_correct else "✗仍错误")
                    self.emit("SENSE", "🧭 学习轨迹: 「%s」%s %s %.0f%%→%.0f%%"
                              % (topic, act[1], status, before * 100, skill.mastery * 100))
            return ep
        except Exception:
            return None

    def trajectory_summary(self, n=20):
        """最近学习事件的文本摘要(供 GUI 展示)。"""
        lines = []
        for ep in reversed(self.episodes[-n:]):
            tag = ("✓" if ep.correct is True else ("✗" if ep.correct is False else "—"))
            line = "[第%d天] %s·%s | %s%s | 掌握 %.0f%%→%.0f%%" % (
                ep.day, ep.subject, ep.skill, ep.learning_material, tag,
                (ep.before_mastery or 0) * 100, (ep.after_mastery or 0) * 100)
            if ep.correct is False:
                line += " | 错误:%s" % (ep.error_type or "")
                if ep.retry_correct:
                    line += " | 重试后正确"
            lines.append(line)
        return lines


    # ------------------------------------------------------ MCTS 规划建议 ----
    def plan_mcts(self):
        stage, _ = self.stage()
        best, stats, ms = self.mcts.decide(
            self.student, self.real_day, self.difficulty_of_topic(), stage,
            weights=self.action_weights)
        subj, topic, _ = self.current_topic()
        rows = []
        rows.append(("PLAN", "🧭 路径规划(MCTS×%d迭代·自适应时间预算%dms, %.0fms): 在「%s·%s」节点扩展%d个教学动作分支, UCB回溯"
                     % (self.mcts.last_iters, self.mcts.time_budget_ms, ms,
                        subj, topic, len(stats))))
        detail = ", ".join("「%s」访问%d次/均值%.3f" % (ACT_BY_ID[a][1], v, q)
                           for a, v, q in stats)
        rows.append(("MCTS", "🌲 决策树: %s" % detail))
        if self.data_driven:
            _order = {a[0]: i for i, a in enumerate(ACTIONS)}
            rows.append(("STATUS", "🧬 数据驱动权重: %s" % ", ".join(
                "%s×%.2f" % (ACT_BY_ID[a][1], w)
                for a, w in sorted(self.action_weights.items(),
                                   key=lambda kv: _order[kv[0]]))))
        _, gap, score, ideal = self.dual_timeline()
        rows.append(("GOAL", "🎯 榜样比对: 学生成长分%.2f/5 vs %s同龄理想%.2f/5 → %s %d天"
                     % (score, self.role()["label"], ideal, self.gap_status()[0], abs(gap))))
        rows.append(("PLAN", "✅ 决策: 推荐动作「%s%s」, 下一知识锚点: %s·%s"
                     % (ACT_BY_ID[best][2], ACT_BY_ID[best][1], subj, topic)))
        for e in rows:
            self.emit(*e)
        self.last_plan = (best, subj, topic)
        return best

    # ---------------------------------------------------- 时间压缩模拟 ------
    def simulate_days(self, total_days, chunk=24, sink=None, stop_flag=None):
        """把 total_days 天的学习过程压缩到秒级跑完(对应专利: 时间压缩算法 /
        几分钟模拟十几年的有效性验证)。sink: 每推进 chunk 天回调一批事件。"""
        t0 = now_ms()
        done, fatigue_hits, rest_used = 0, 0, 0
        completed = False
        while done < total_days and not (stop_flag and stop_flag.is_set()):
            if self.sim_day >= self.allowed_exec:
                completed = True
                break
            batch = []
            for _ in range(chunk):
                if self.sim_day >= self.allowed_exec:
                    completed = True
                    break
                stage, _ = self.stage()
                diff = self.difficulty_of_topic()
                aid = MCTSPlanner.greedy_decide(self.student, diff, stage,
                                                self.real_day,
                                                self.action_weights)
                target = GrowthCurve.ideal(self.real_day) / 5.0
                w = self.action_weights.get(aid, 1.0)
                details, tired, _, _ = self.student.apply(aid, diff, stage,
                                                          target, w)
                self.topic_idx += 1
                self.sim_day += 1
                self.last_action = aid
                self.perf_history.append((self.real_day, round(self.student.score5(), 4)))
                self.push_traj_row(aid)
                self._assess_and_record(aid, quiet=True)
                done += 1
                if self.sim_day == self.allowed_exec:
                    self.emit("GOAL", "🏁 时间压缩: 全部%d个K12学习日执行完毕, 空白学生体长成!" % self.allowed_exec)
                if tired:
                    fatigue_hits += 1
                if aid == "xiuxi":
                    rest_used += 1
                if done == 1 or done % 50 == 0 or done == total_days:
                    act = ACT_BY_ID[aid]
                    gtxt = ", ".join("%s+%.3f" % (DIM_NAMES[k], g) for k, g in details[:3])
                    batch.append(("CURVE", "📈 压缩模拟 第%d天: %s「%s」(疲劳%.0f%% 专注%.0f%%) %s"
                                  % (done, act[2], act[1], self.student.fatigue * 100,
                                     self.student.attention * 100, gtxt)))
            if batch and sink:
                try:
                    sink(batch)
                except Exception:
                    pass
        ms = now_ms() - t0
        self.emit("SYSTEM", "⚙ 时间压缩算法: %d天学习过程 %.0fms 模拟完毕 (每毫秒≈%d天), "
                  "休息干预%d次, 疲劳告警%d次%s"
                  % (done, ms, max(1, int(done / max(1, ms))), rest_used, fatigue_hits,
                     " | ✅ 路径有效性验证: 终点可达" if completed else ""))
        return done

    # ------------------------------------------------------- 提示语构建 -----
    def role_facts(self):
        return "\n".join("  · %s" % t for _, t in self.role()["milestones"])

    def persona(self):
        stage, icon = self.stage()
        subj, topic, _ = self.current_topic()
        equiv_day, gap, score, ideal = self.dual_timeline()
        ey, ed = age_of_day(equiv_day)
        r = self.level_rating()
        return {
            "student": "%s·%s·%s" % (self.student_name, GRADES[grade_of_day(self.real_day)],
                                     self.learn_state),
            "state": "认知阶段:%s%s | 年龄:%s | 成长分:%.2f/5.0 | 疲劳:%.0f%% 专注:%.0f%%"
                     % (icon, stage, age_str(self.real_day), score,
                        self.student.fatigue * 100, self.student.attention * 100),
            "role": "榜样模型:%s —— 你的等效水平≈榜样 %s (%s%d天); 当前任务知识点:「%s·%s」"
                    % (self.role()["label"], age_str(equiv_day), self.gap_status()[0], abs(gap),
                       subj, topic),
            "cultivate": "修炼定位: 实际境界 %s%s / 水平境界 %s%s · %s · 榜位 %d/100 · "
                         "九字秘法平均修为 %.0f%%(%d/%d式已解锁) · 当前应演化的物理模型「%s」"
                         % (r["realm_emoji"], r["realm_name"],
                            r["level_realm_emoji"], r["level_realm_name"],
                            r["trend"], r["rank"], r["arts_avg"] * 100,
                            r["arts_unlocked"], r["arts_total"], r["model"]),
        }

    def build_system_prompt(self):
        p = self.persona()
        return (
            "你是「AI学生」教育预测引擎的成长导师。学生信息如下:\n"
            "- 学生: %(student)s\n"
            "- 实时学情: %(state)s\n"
            "- 路径比对: %(role)s\n"
            "- 修炼定位: %(cultivate)s\n"
            "榜样成长里程碑: \n%(facts)s\n\n"
            "教学法要求(专利启发式/项目式设计):\n"
            "1. 用苏格拉底式提问引导, 先给思路与拆解步骤, 不直接倾倒整题答案;\n"
            "2. 结合学生当前认知阶段与学习状态调整讲解深度;\n"
            "3. 学生焦虑时先共情(可引用其与榜样的差距给予鼓励), 再给最近发展区内的小任务;\n"
            "4. 物理题一律按九字秘法组织思路: 删(文字转图像)→解(知三求二)→"
            "分(隔离受力)→合(整体简力)→列(坐标列式)→秒(二级结论); 需要时用推(公式体系)、"
            "创(模型演化)、造(动手造物); 讲完要指出学生这一题练的是哪几个字;\n"
            "5. 跨学科联系(如物理规律->数学工具->生活现象), 回答控制在400字内, 中文。"
            % {"facts": self.role_facts(), **p}
        )

    def topic_hint_text(self):
        subj, topic, _ = self.current_topic()
        return "%s·%s" % (subj, topic)

# ======================================================= 配置持久化(轻量) =====

def cfg_load(path=CFG_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
            return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def cfg_save(data, path=CFG_PATH):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# ============================================================ 界面主题 ========
# 风格: Codex 式静谧深色界面 — 单一强调色 + 大面积中性灰, 去饱和、不花哨,
# 色彩仅用于"交互/主信息"与极简的状态区分, 信息层级靠留白、灰阶与字号。
BG       = "#0E1117"
PANEL    = "#161A22"
PANEL2   = "#12161D"
EDGE     = "#252B36"
TXT      = "#E8EAEE"
SUB      = "#8B919D"
ACC      = "#7A8CFF"      # 单一强调色(静谧靛蓝)
OK       = "#7E9A88"      # 低调绿灰
WARN     = "#A89A72"      # 低调沙金
BAD      = "#A98383"      # 低调砖红
VIOLET   = "#8A93B8"      # 低调灰蓝(等效榜样等中性标记)
INPUT_BG = "#10141B"
CHIP_BG  = "#1B2029"
LOG_BG   = "#0D1117"
FONT     = "Microsoft YaHei UI"
THINK_COLORS = {
    "SYS":   SUB, "SENSE": "#9AA6B8", "ACT": "#A2ADBD", "CURVE": "#8F9AAC",
    "STAGE": "#8A95A8", "PLAN": "#A6B1C1", "MCTS": "#939FAF", "GOAL": ACC,
    "TIP":   "#B3BDCB", "MODEL": "#9CA8B8", "CAM": "#8993A4", "STATUS": "#96A1B1",
}


def hex_rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mix(h1, h2, t):
    a, b = hex_rgb(h1), hex_rgb(h2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class RoundedRect:
    """在 canvas 上绘制圆角矩形 / 圆角渐变条 / 圆点。"""

    @staticmethod
    def poly(cv, x0, y0, x1, y1, r, **kw):
        pts = []
        r = max(0, min(r, (x1 - x0) / 2.0, (y1 - y0) / 2.0))
        for px, py in ((x0 + r, y0), (x1 - r, y0), (x1, y0), (x1, y0 + r),
                       (x1, y1 - r), (x1, y1), (x1 - r, y1), (x0 + r, y1),
                       (x0, y1), (x0, y1 - r), (x0, y0 + r), (x0, y0)):
            pts += [px, py]
        return cv.create_polygon(pts, smooth=True, **kw)

    @staticmethod
    def rect(cv, x0, y0, x1, y1, r, **kw):
        RoundedRect.poly(cv, x0, y0, x1, y1, r, **kw)

    @staticmethod
    def bar(cv, x0, y0, x1, y1, r, frac, color, bg=EDGE, border=None):
        """进度条(支持圆角): frac 0..1, 平滑渐变充填。"""
        RoundedRect.rect(cv, x0, y0, x1, y1, r, fill=bg, outline=bg)
        w = (x1 - x0) * clamp(frac, 0.0, 1.0)
        if w < r * 2 and w > 0:
            RoundedRect.rect(cv, x0, y0, x0 + w, y1, r if w >= r else w / 2.0,
                             fill=color, outline=color)
        elif w > 0:
            c0 = mix(color, "#FFFFFF", 0.12)
            RoundedRect.rect(cv, x0, y0, x0 + w, y1, r, fill=c0, outline=c0)
        if border:
            RoundedRect.rect(cv, x0, y0, x1, y1, r, outline=border, width=1)

    @staticmethod
    def dot(cv, cx, cy, rr, color, outline=None):
        cv.create_oval(cx - rr, cy - rr, cx + rr, cy + rr, fill=color,
                       outline=outline or color)


class ChatLog(tk.Text):
    """聊天记录区(带标签着色、自动滚动、清除)。"""

    def __init__(self, master, height=8, **kw):
        super().__init__(master, height=height, wrap="word", state="disabled",
                         bg=LOG_BG, fg=TXT, insertbackground=ACC,
                         relief="flat", bd=0, padx=12, pady=10,
                         font=(FONT, 10), spacing1=2, spacing3=4, **kw)
        for t in ("user", "ai", "err", "sys", "meta"):
            self.tag_config(t, foreground={"user": ACC, "ai": TXT,
                                            "err": BAD, "sys": SUB,
                                            "meta": SUB}[t])
        self.tag_config("bold", font=(FONT, 10, "bold"))

    def add(self, who, text):
        who = who if who in ("user", "ai", "err", "sys", "meta") else "meta"
        self.configure(state="normal")
        self.insert("end", who + "  ", ("bold", who) if who != "meta" else (who,))
        for seg in text.split("\n"):
            self.insert("end", seg + "\n", (who,))
        self.insert("end", "\n")
        self.configure(state="disabled")
        self.see("end")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


# ==================================================== 大模型 HTTP 客户端 =====

class LLMClient:
    """本地 Ollama / 外部 OpenAI 兼容 API (仅标准库 urllib)。"""

    @staticmethod
    def _post_json(url, payload, headers=None, timeout=180):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    @staticmethod
    def _get_json(url, timeout=8):
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    @staticmethod
    def _http_err(err):
        """把 urllib 异常转成可读文本(带服务端返回体, 便于定位问题)。"""
        body = ""
        try:
            body = err.read().decode("utf-8", "ignore")
        except Exception:
            body = ""
        code = getattr(err, "code", "")
        why = getattr(err, "reason", err)
        return "HTTP %s %s" % (code, (body[:300] if body else why))

    @staticmethod
    def ollama_chat(base, model, messages, temperature=0.7, timeout=240,
                    image_b64=None):
        base = base.strip().rstrip("/") or "http://127.0.0.1:11434"
        msgs = [dict(m) for m in messages]
        if image_b64:                       # Ollama 视觉: user 消息附带 images
            last = msgs[-1]
            last.setdefault("images", []).append(image_b64)
        out = LLMClient._post_json(base + "/api/chat", {
            "model": model, "messages": msgs, "stream": False,
            "options": {"temperature": temperature}}, timeout=timeout)
        return (out.get("message") or {}).get("content", "") or "(模型未返回内容)"

    @staticmethod
    def ollama_tags(base):
        base = base.strip().rstrip("/") or "http://127.0.0.1:11434"
        out = LLMClient._get_json(base + "/api/tags")
        return [m["name"] for m in out.get("models", [])]

    @staticmethod
    def remote_chat(base_url, api_key, model, messages, temperature=0.7,
                    timeout=300, retries=3):
        """OpenAI 兼容文本接口: 超时 300s, 失败自动重试(默认 3 次)。"""
        base_url = (base_url or "").strip().rstrip("/")
        if not base_url:
            raise RuntimeError("外部 API 未配置: 请先在「API密钥/模型设置」"
                               "填写接口地址(如 https://api.deepseek.com/v1)")
        url = base_url if base_url.endswith("/chat/completions") \
            else base_url + "/chat/completions"
        headers = {}
        if (api_key or "").strip():
            headers["Authorization"] = "Bearer " + api_key.strip()
        last = None
        tries = max(1, int(retries))
        for i in range(tries):
            try:
                out = LLMClient._post_json(url, {
                    "model": model, "messages": messages,
                    "temperature": temperature, "stream": False},
                    headers=headers, timeout=timeout)
                try:
                    return out["choices"][0]["message"]["content"]
                except Exception:
                    return str(out)[:2000]
            except urllib.error.HTTPError as e:
                last = RuntimeError(LLMClient._http_err(e))
                if getattr(e, "code", 0) in (400, 401, 403, 404, 422):
                    break                       # 参数/鉴权类错误重试无意义
            except Exception as e:
                last = e
            if i < tries - 1:
                time.sleep(1.5 * (i + 1))
        raise RuntimeError("外部API调用失败(密钥 %s): %s" % (mask_key(api_key), last))

    @staticmethod
    def remote_chat_vision(base_url, api_key, model, text, image_b64,
                           temperature=0.3, timeout=300, retries=3):
        """OpenAI 兼容视觉接口: 文本 + 图片(base64 data URI) 一起发送。"""
        base_url = (base_url or "").strip().rstrip("/")
        if not base_url:
            raise RuntimeError("外部 API 未配置: 视觉通道需要填写接口地址")
        url = base_url if base_url.endswith("/chat/completions") \
            else base_url + "/chat/completions"
        headers = {}
        if (api_key or "").strip():
            headers["Authorization"] = "Bearer " + api_key.strip()
        content = [{"type": "text", "text": text},
                   {"type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64," + image_b64}}]
        last = None
        tries = max(1, int(retries))
        for i in range(tries):
            try:
                out = LLMClient._post_json(url, {
                    "model": model,
                    "messages": [{"role": "user", "content": content}],
                    "temperature": temperature, "stream": False},
                    headers=headers, timeout=timeout)
                try:
                    return out["choices"][0]["message"]["content"]
                except Exception:
                    raise RuntimeError("视觉接口返回异常: %s" % str(out)[:300])
            except urllib.error.HTTPError as e:
                last = RuntimeError(LLMClient._http_err(e))
                if getattr(e, "code", 0) in (400, 401, 403, 404, 422):
                    break
            except Exception as e:
                last = e
            if i < tries - 1:
                time.sleep(1.5 * (i + 1))
        raise RuntimeError("外部API视觉调用失败(密钥 %s): %s"
                           % (mask_key(api_key), last))

# ==================================================== 分区容器控件 ===========

class ZoneCard(tk.Frame):
    """圆角分区卡片: 标题条 + 内容。"""

    def __init__(self, master, title, accent, body=None, **kw):
        super().__init__(master, bg=PANEL, highlightbackground=EDGE,
                         highlightthickness=1, **kw)
        self.accent = accent
        self.title = title
        head = tk.Frame(self, bg=PANEL2)
        head.pack(fill="x")
        self.dot = tk.Canvas(head, width=10, height=14, bg=PANEL2,
                             highlightthickness=0)
        self.dot.pack(side="left", padx=(12, 4), pady=8)
        RoundedRect.dot(self.dot, 5, 7, 4, accent)
        tk.Label(head, text=title, bg=PANEL2, fg=TXT, font=(FONT, 10, "bold")) \
            .pack(side="left")
        self.head_right = tk.Frame(head, bg=PANEL2)
        self.head_right.pack(side="right", padx=8)
        self.body = tk.Frame(self, bg=PANEL)
        self.body.pack(fill="both", expand=True, padx=6, pady=(2, 6))
        if body is not None:
            body(self.body)

    def add_head(self, widget):
        widget.pack(side="right", padx=2)


# ==================================================== 大模型分区(基类) =======

class ModelZone(ZoneCard):
    """本地/外部大模型对话分区共同逻辑: 气泡日志 + 输入行 + 后台调用。"""

    ZONE_ID = "base"

    def __init__(self, master, app, title, accent, hint=""):
        self.app = app
        self.busy = False
        super().__init__(master, title, accent)
        self.hint = hint
        self.log = ChatLog(self.body, height=9)
        self.log.pack(fill="both", expand=True)
        self.entry_row = tk.Frame(self.body, bg=PANEL)
        self.entry_row.pack(fill="x", pady=(6, 2))
        self.input = tk.Entry(self.entry_row, bg="#0E131B", fg=TXT,
                              insertbackground=ACC, relief="flat",
                              font=(FONT, 10))
        self.input.pack(side="left", fill="x", expand=True, ipady=6)
        self.input.bind("<Return>", lambda e: self.send())
        self.btn = tk.Button(self.entry_row, text="发送 ▶", command=self.send,
                             bg=accent, fg="#0B0E16", activebackground=accent,
                             relief="flat", font=(FONT, 9, "bold"),
                             padx=14, cursor="hand2")
        self.btn.pack(side="left", padx=(6, 0))
        self.build_config_ui()
        self.append_sys("就绪。%s" % hint)

    # ---- 子类可覆盖: 配置行 UI ----
    def build_config_ui(self):
        pass

    def append_sys(self, text):
        self.log.add("sys", text)

    def set_busy(self, flag, text=None):
        self.busy = flag
        self.btn.configure(state="disabled" if flag else "normal",
                           text="思考中…" if flag else "发送 ▶")

    def build_request_snapshot(self):
        """主线程内快照请求参数, 子线程只读快照(避免跨线程访问 tk 变量)。"""
        raise NotImplementedError

    def ask_model(self, snap, messages, cb_ok, cb_err):
        """子类实现: 后台请求模型; cb_ok(text, ms) / cb_err(msg) 在主线程。"""
        raise NotImplementedError

    def send(self):
        if self.busy:
            return
        text = self.input.get().strip()
        if not text:
            return
        self.input.delete(0, "end")
        self.log.add("user", text)
        self.set_busy(True)
        self.app.think("MODEL", "🤖 学生提问已提交「%s…」(%d字), 生成提示词并请求大模型…"
                       % (text[:18], len(text)))
        messages = [{"role": "system", "content": self.app.engine.build_system_prompt()}]
        mem = getattr(self.app.engine, self.mem_attr)
        messages += list(mem)
        messages.append({"role": "user", "content": text})
        self._last_user = text
        try:
            snap = self.build_request_snapshot()
        except Exception as e:
            snap = None
            self.app.think("TIP", "💡 请求参数缺失: %s" % e)

        def done_ok(out):
            content, ms = out
            mem.append({"role": "user", "content": text})
            mem.append({"role": "assistant", "content": content})
            self.set_busy(False)
            self.log.add("ai", content)
            self.app.think("MODEL", "🤖 大模型应答完成(%.1fs, 约%d Token), 已加入学生对话记忆"
                           % (ms / 1000.0, est_tokens(content)))

        def done_err(err):
            self.set_busy(False)
            self.log.add("err", "调用失败: %s" % err)
            self.app.think("MODEL", "⚠ 大模型调用失败: %s" % err)
            self.app.think("TIP", "💡 检查网络/地址/密钥, 或切换本地模型通道; 引擎离线成长(打卡/压缩模拟/MCTS)不受影响。")

        self.app.go_thread(lambda: self.ask_model(snap, messages, done_ok, done_err))


# ------------------------------------------------ 分区1: 本地大模型(Ollama) ---
LOCAL_DEFAULT = "http://127.0.0.1:11434"
LOCAL_MODEL_DEFAULT = "deepseek-r1:7b"
REMOTE_PRESETS = [
    ("DeepSeek(深度求索)", "https://api.deepseek.com/v1", "deepseek-chat"),
    ("阿里云百炼·通义千问", "https://dashscope.aliyuncs.com/compatible-mode/v1",
     "qwen-plus"),
    ("阿里云百炼·视觉(qwen-vl-plus)",
     "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-vl-plus"),
    ("OpenAI", "https://api.openai.com/v1", "gpt-4o-mini"),
    ("Kimi(月之暗面)", "https://api.moonshot.cn/v1", "moonshot-v1-8k"),
    ("通义千问(阿里)", "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus"),
    ("智谱GLM", "https://open.bigmodel.cn/api/paas/v4", "glm-4-flash"),
]


class LocalZone(ModelZone):
    """分区1: 启动时自动探测并调用本地大模型(默认 deepseek-r1:7b)。"""
    ZONE_ID = "local"
    mem_attr = "chat_mem_local"

    def __init__(self, master, app):
        super().__init__(master, app, "① 本地大模型 · Ollama(deepseek-r1:7b)",
                         ACC,
                         "启动时已自动探测本机 Ollama, 消息默认路由到本地模型")
        self.state = "probing"
        self.detected_models = []

    def build_config_ui(self):
        bar = tk.Frame(self.body, bg=PANEL)
        bar.pack(fill="x", pady=(0, 4))
        self.status_dot = tk.Canvas(bar, width=12, height=14, bg=PANEL,
                                    highlightthickness=0)
        self.status_dot.pack(side="left", padx=(2, 2))
        self.status_txt = tk.Label(bar, text="探测本地模型…", bg=PANEL, fg=SUB,
                                   font=(FONT, 9))
        self.status_txt.pack(side="left")
        tk.Label(bar, text="模型:", bg=PANEL, fg=SUB, font=(FONT, 9)) \
            .pack(side="left", padx=(10, 2))
        self.model_var = tk.StringVar(value=LOCAL_MODEL_DEFAULT)
        self.model_cb = ttk.Combobox(bar, textvariable=self.model_var, width=18,
                                     font=(FONT, 9), values=[LOCAL_MODEL_DEFAULT])
        self.model_cb.pack(side="left")
        self.probe_btn = tk.Button(bar, text="重试探测", command=lambda
                                   b=self.app.cfg_local_base():
                                   self.app.go_thread(lambda: self.probe(b)),
                                   bg=PANEL2, fg=ACC, relief="flat",
                                   activebackground=PANEL2, font=(FONT, 9),
                                   cursor="hand2")
        self.probe_btn.pack(side="left", padx=(8, 0))
        self.launch_btn = tk.Button(bar, text="启动Ollama", command=self.try_launch,
                                    bg=PANEL2, fg=ACC, relief="flat",
                                    activebackground=PANEL2, font=(FONT, 9),
                                    cursor="hand2")
        self.launch_btn.pack(side="left", padx=(4, 0))
        tk.Label(bar, text="地址:", bg=PANEL, fg=SUB, font=(FONT, 9)) \
            .pack(side="left", padx=(8, 2))
        self.base_var = tk.StringVar(value=LOCAL_DEFAULT)
        e_base = tk.Entry(bar, textvariable=self.base_var, bg="#0E131B",
                          fg=TXT, relief="flat", font=(FONT, 8), width=16)
        e_base.pack(side="left")
        e_base.bind("<FocusOut>", lambda _e: self.app.cfg_dirty())
        tk.Label(bar, text="", bg=PANEL).pack(side="left", expand=True)

    # ---- 探测 / 状态(均在守护线程执行, UI 操作经 push_ui 回主线程) ----
    def set_status(self, color, text):
        self.app.push_ui(lambda: self._set_status(color, text))

    def _set_status(self, color, text):
        self.status_txt.configure(text=text, fg=color)
        RoundedRect.dot(self.status_dot, 6, 7, 4, color)
        self.app.status_set(color, "本地模型: " + text)

    def probe(self, base=None):
        if base is None:               # 调用方必须在主线程快照地址(tk变量不可跨线程读)
            base = self.app.cfg_local_base()
        try:
            models = LLMClient.ollama_tags(base)
        except Exception as e:
            self.app.push_ui(lambda: self._probe_fail(str(e)))
            return
        self.app.push_ui(lambda: self._probe_ok(models))

    def _probe_ok(self, models):
        self.detected_models = list(models)
        vals = models or [LOCAL_MODEL_DEFAULT]
        self.model_cb.configure(values=vals)
        pref = next((m for m in models if "deepseek" in m.lower()), None)
        if pref is None:
            pref = next((m for m in models if "r1" in m.lower() or "qwen" in m.lower()),
                        None) or (models[0] if models else LOCAL_MODEL_DEFAULT)
        if self.model_var.get() not in models:
            self.model_var.set(pref)
        self._set_status(OK, "已连接 ✓ %d个本地模型, 默认 %s" % (len(models), pref))
        self.append_sys("本地大模型已就绪: %s (Ollama)" % ", ".join(models[:5]))
        self.app.think("MODEL", "✅ 本地大模型通道就绪: %s, 当前选择 %s"
                       % (", ".join(models[:6]) or "无", pref))
        self.app.cfg_dirty()

    def _probe_fail(self, err):
        self.detected_models = []
        self._set_status(BAD, "未连接 · 未检测到本机 Ollama")
        self.append_sys("探测失败: %s" % err[:160])
        self.app.think("MODEL", "⚠ 本地大模型探测失败: %s\n   → 1) 启动 Ollama  2) 执行 ollama pull deepseek-r1:7b  3) 点「重试探测」" % err)

    def try_launch(self):
        try:
            import shutil
            exe = shutil.which("ollama")
            if not exe:
                raise FileNotFoundError("未找到 ollama 程序")
            subprocess.Popen([exe, "serve"], creationflags=0x08000000)
            self.append_sys("已尝试启动 Ollama serve… 稍候点击「重试探测」。")
        except Exception as e:
            self.append_sys("无法自动启动: %s (请手动打开 Ollama 桌面程序)" % e)
            self.app.think("TIP", "💡 请手动启动 Ollama: 开始菜单搜索 Ollama 运行, 之后执行 ollama pull deepseek-r1:7b")

    # ---- 请求 ----
    def build_request_snapshot(self):
        return (self.app.cfg_local_base(),
                self.model_var.get().strip() or LOCAL_MODEL_DEFAULT)

    def ask_model(self, snap, messages, cb_ok, cb_err):
        base, model = snap

        def work():
            t0 = now_ms()
            try:
                out = LLMClient.ollama_chat(base, model, messages)
                return out, now_ms() - t0
            except urllib.error.HTTPError as e:
                body = ""
                try:
                    body = e.read().decode("utf-8")[:200]
                except Exception:
                    pass
                raise RuntimeError("本地模型 HTTP %s: %s" % (e.code, body))
            except Exception as e:
                raise RuntimeError("无法访问本地模型(%s): %s" % (base, e))
        try:
            out = work()
            self.app.push_ui(lambda: cb_ok(out))
        except Exception as e:
            self.app.push_ui(lambda: cb_err(str(e)))


# ------------------------------------------- 分区2: 外部大模型 API 区 ---------
class RemoteZone(ModelZone):
    ZONE_ID = "remote"
    mem_attr = "chat_mem_remote"

    def __init__(self, master, app):
        self._loaded_preset = False
        super().__init__(master, app, "② 外部大模型 API · OpenAI兼容",
                         VIOLET,
                         "接入 DeepSeek / OpenAI / Kimi / 通义 等云端大模型")
        self.set_status(SUB, "未配置密钥")

    def build_config_ui(self):
        bar = tk.Frame(self.body, bg=PANEL)
        bar.pack(fill="x")
        tk.Label(bar, text="接口:", bg=PANEL, fg=SUB, font=(FONT, 9)) \
            .pack(side="left")
        self.preset_var = tk.StringVar()
        self.preset_cb = ttk.Combobox(bar, textvariable=self.preset_var,
                                      width=14, font=(FONT, 9),
                                      values=[p[0] for p in REMOTE_PRESETS],
                                      state="readonly")
        self.preset_cb.pack(side="left")
        self.preset_cb.bind("<<ComboboxSelected>>", self.apply_preset)
        self.test_btn = tk.Button(bar, text="测试连接", command=self.test_conn,
                                  bg=PANEL2, fg=ACC, relief="flat",
                                  font=(FONT, 9), cursor="hand2")
        self.test_btn.pack(side="right")
        self.status_dot = tk.Canvas(bar, width=12, height=14, bg=PANEL,
                                    highlightthickness=0)
        self.status_dot.pack(side="right", padx=4)
        self.status_txt = tk.Label(bar, text="", bg=PANEL, fg=SUB, font=(FONT, 9))
        self.status_txt.pack(side="right")
        form = tk.Frame(self.body, bg=PANEL)
        form.pack(fill="x", pady=(2, 4))
        for i, (lab, key) in enumerate((("地址", "base"), ("密钥", "key"),
                                        ("模型", "model"))):
            tk.Label(form, text=lab, bg=PANEL, fg=SUB, font=(FONT, 9)) \
                .grid(row=0, column=i * 2, sticky="e", padx=(0, 3))
            if key == "base":
                self.url_var = tk.StringVar()
                e = tk.Entry(form, textvariable=self.url_var, bg="#0E131B",
                             fg=TXT, relief="flat", font=(FONT, 9), width=34)
                e.grid(row=0, column=i * 2 + 1, sticky="we", padx=(0, 8))
                e.bind("<FocusOut>", self.cfg_dirty)
            elif key == "key":
                self.key_var = tk.StringVar()
                e = tk.Entry(form, textvariable=self.key_var, bg="#0E131B",
                             fg=TXT, relief="flat", show="●", font=(FONT, 9),
                             width=30)
                e.grid(row=0, column=i * 2 + 1, sticky="we", padx=(0, 8))
                e.bind("<FocusOut>", self.cfg_dirty)
            else:
                self.m_var = tk.StringVar()
                e = tk.Entry(form, textvariable=self.m_var, bg="#0E131B",
                             fg=TXT, relief="flat", font=(FONT, 9), width=22)
                e.grid(row=0, column=i * 2 + 1, sticky="we", padx=(0, 8))
                e.bind("<FocusOut>", self.cfg_dirty)
        form.columnconfigure(3, weight=1)
        self.apply_preset(None)
        if not self._loaded_preset:
            self.preset_var.set(REMOTE_PRESETS[0][0])
            self.url_var.set(REMOTE_PRESETS[0][1])
            self.m_var.set(REMOTE_PRESETS[0][2])

    def cfg_dirty(self, _e=None):
        self.app.cfg_dirty()

    def apply_preset(self, _e=None):
        name = self.preset_var.get()
        for n, url, m in REMOTE_PRESETS:
            if n == name:
                self.url_var.set(url)
                self.m_var.set(m)
                break

    def set_status(self, color, text):
        self.app.push_ui(lambda: self._set_status(color, text))

    def _set_status(self, color, text):
        self.status_txt.configure(text=text, fg=color)
        RoundedRect.dot(self.status_dot, 6, 7, 4, color)
        self.app.status_set(color, "外部API: " + text)

    # ---- 请求 ----
    def build_request_snapshot(self):
        return (self.url_var.get().strip(), self.key_var.get().strip(),
                self.m_var.get().strip())

    def ask_model(self, snap, messages, cb_ok, cb_err):
        url, key, model = snap

        def work():
            if not url:
                raise RuntimeError("请先填写接口地址(如 https://api.deepseek.com/v1)")
            t0 = now_ms()
            out = LLMClient.remote_chat(url, key, model, messages)
            return out, now_ms() - t0
        try:
            out = work()
            self.app.push_ui(lambda: cb_ok(out))
        except Exception as e:
            self.app.push_ui(lambda: cb_err(str(e)))

    def test_conn(self):
        if self.busy:
            return
        self._set_status(WARN, "测试中…")
        self.test_btn.configure(state="disabled")
        try:
            snap = self.build_request_snapshot()
        except Exception:
            snap = ("", "", "")
        url, key, model = snap

        def work():
            try:
                return LLMClient.remote_chat(
                    url, key, model,
                    [{"role": "user", "content": "你好, 请只回复: 连接成功"}])
            except Exception as e:
                return "ERR:" + str(e)

        def done(out):
            self.test_btn.configure(state="normal")
            if out.startswith("ERR:"):
                self._set_status(BAD, "失败")
                self.log.add("err", "连接测试失败: " + out[4:])
                self.app.think("MODEL", "⚠ 外部API连接测试失败: %s" % out[4:])
            else:
                self._set_status(OK, "连接成功 ✓")
                self.log.add("sys", "连接测试通过, 模型回复: %s" % out[:120])
                self.app.think("MODEL", "✅ 外部大模型API通道测试通过, 返回: %s" % out[:80])

        def run():
            out = work()
            self.app.push_ui(lambda: done(out))
        self.app.go_thread(run)

# ==================================================== 分区3: 思考区 ==========

class ThinkZone(ZoneCard):
    """③ 思考区: AI学生的实时思维链(感知/阶段/比对/规划/决策/生长…)。"""

    def __init__(self, master, app):
        self.app = app
        super().__init__(master, "③ 思考区 · AI学生思维链", "#9AA6B8")
        for text, cmd in (("清空", self.clear_all), ("导出…", self.export)):
            tk.Button(self.head_right, text=text, command=cmd, bg=PANEL2,
                      fg=ACC, relief="flat", font=(FONT, 9), cursor="hand2",
                      padx=6).pack(side="left", padx=2)
        self.text = tk.Text(self.body, wrap="word", state="disabled",
                            bg=LOG_BG, fg=TXT, relief="flat", bd=0,
                            padx=10, pady=6, font=(FONT, 9), spacing1=0,
                            spacing3=1, cursor="arrow")
        self.text.pack(fill="both", expand=True)
        for k, c in THINK_COLORS.items():
            self.text.tag_config("k_" + k, foreground=c)
        self.text.tag_config("tm", foreground="#6B7482")
        self.text.tag_config("dur", foreground="#6B7482")
        self.lines = 0

    def feed(self, kind, msg, dur=None, ts=None):
        ts = ts or now_str()
        self.text.configure(state="normal")
        pre = "[" + ts + "] "
        dur_s = (" (%.0fms)" % dur) if dur else ""
        self.text.insert("end", pre, "tm")
        self.text.insert("end", msg + dur_s + "\n",
                         ("k_" + kind) if kind in THINK_COLORS else ())
        self.lines += 1
        if self.lines > 2600:
            self.text.delete("1.0", "20.0")
            self.lines -= 20
        self.text.configure(state="disabled")
        self.text.see("end")

    def feed_event(self, ev):
        kind, msg, dur = ev
        self.feed(kind, msg, dur)

    def clear_all(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
        self.lines = 0

    def export(self):
        from tkinter import filedialog
        default = os.path.join(os.path.expanduser("~"),
                               "ai学生思考日志_%s.txt"
                               % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        path = filedialog.asksaveasfilename(title="导出思考日志",
                                            initialfile=os.path.basename(default),
                                            initialdir=os.path.dirname(default),
                                            defaultextension=".txt",
                                            filetypes=[("文本文件", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                for kind, msg, dur in self.app.engine.history:
                    f.write("[%s] %s\n" % (kind, msg))
            self.feed("SYS", "📁 思考日志已导出: %s" % path)
        except Exception as e:
            self.feed("SYS", "⚠ 导出失败: %s" % e)


# ==================================================== 分区4: 成长进度区 =======

class TBar(tk.Canvas):
    """双时间轴进度条(榜样 vs 学生), 平滑动画。"""

    def __init__(self, master, label, color, height=46):
        super().__init__(master, bg=PANEL, highlightthickness=0, height=height)
        self.label, self.color = label, color
        self.cur, self.target = 0.0, 0.0
        self.caption = ""
        self._cap_last = None

    def set_target(self, frac, caption=None):
        self.target = clamp(frac, 0.0, 1.0)
        if caption is not None:
            self.caption = caption

    def animate(self):
        d = self.target - self.cur
        if abs(d) > 0.0004:
            self.cur += d * 0.16
        else:
            self.cur = self.target
        if self.caption != self._cap_last or abs(d) > 0.0004:
            self._cap_last = self.caption
            self._draw()

    def _draw(self):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 20 or h < 10:
            return
        self.delete("all")
        y0, y1 = 24.0, h - 8.0
        bw = w - 16.0
        RoundedRect.bar(self, 8, y0, 8 + bw, y1, (y1 - y0) / 2.0, self.cur,
                        self.color, bg=mix(EDGE, "#232936", 0.5),
                        border=EDGE)
        self.create_text(10, 10, anchor="w", text=self.label, fill=TXT,
                         font=(FONT, 9, "bold"))
        self.create_text(w - 10, 10, anchor="e",
                         text="%.1f%%" % (self.cur * 100), fill=self.color,
                         font=(FONT, 9, "bold"))
        if self.caption:
            self.create_text(10, y0 + (y1 - y0) / 2.0 + 1, anchor="w",
                             text=self.caption, fill=SUB, font=(FONT, 7))
        if self.cur > 0.003:
            self.create_text(8 + bw * self.cur / 2.0, (y0 + y1) / 2.0,
                             text="", font=(FONT, 6))


class ProgressZone(ZoneCard):
    """④ 成长进度: 榜样进度条 + 学生进度条 + S型成长曲线 + 教学动作面板。"""

    def __init__(self, master, app):
        self.app = app
        self.sim_stop = threading.Event()
        self.sim_running = False
        super().__init__(master, "④ 成长进度 · 双时间轴", "#8F9DAE")
        b = self.body
        self.line0 = tk.Label(b, text="", bg=PANEL, fg=SUB, font=(FONT, 8),
                              anchor="w")
        self.line0.pack(fill="x", padx=6)
        self.bar_model = TBar(b, "🌟 榜样模型同龄完成度(终点: 知识库)", WARN, 44)
        self.bar_model.pack(fill="x", padx=4, pady=(2, 0))
        self.bar_stu = TBar(b, "🎓 当下学生综合成长分(起点: 初始学情)", ACC, 44)
        self.bar_stu.pack(fill="x", padx=4, pady=(2, 0))
        self.gap_lab = tk.Label(b, text="", bg=PANEL, fg=SUB, font=(FONT, 8),
                                anchor="w")
        self.gap_lab.pack(fill="x", padx=6, pady=(2, 0))
        self.curve = tk.Canvas(b, bg=PANEL, highlightthickness=0, height=140)
        self.curve.pack(fill="x", padx=4)
        self.curve.bind("<Configure>", lambda e: self._draw_curve())
        row_a = tk.Frame(b, bg=PANEL)
        row_a.pack(fill="x", pady=(4, 0), padx=2)
        for aid in ("jiangjie", "liti", "fansi", "hudong", "xiuxi"):
            a = ACT_BY_ID[aid]
            tk.Button(row_a, text="%s %s" % (a[2], a[1]), command=lambda x=aid:
                      self.app.do_action(x), bg=PANEL2, fg=TXT, relief="flat",
                      activebackground="#202634", font=(FONT, 9), padx=4,
                      cursor="hand2").pack(side="left", expand=True, fill="x",
                                            padx=2)
        row_b = tk.Frame(b, bg=PANEL)
        row_b.pack(fill="x", pady=(3, 2), padx=2)
        tk.Button(row_b, text="🎯 MCTS规划并执行最优路径", command=self.mcts_go,
                  bg=mix(PANEL2, "#1D2434", 0.5), fg=ACC, relief="flat",
                  font=(FONT, 9), cursor="hand2").pack(side="left", padx=2,
                                                       ipady=2)
        tk.Button(row_b, text="📚4380天档案", command=lambda:
                  self.app.archive_all_btn(), bg=PANEL2, fg=VIOLET,
                  relief="flat", font=(FONT, 9), cursor="hand2") \
            .pack(side="left", padx=(4, 0), ipady=2)
        self.pilot_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row_b, text="✈ 自动领航", variable=self.pilot_var,
                       command=self.toggle_pilot, bg=PANEL, fg=ACC,
                       selectcolor=PANEL2, activebackground=PANEL,
                       activeforeground=ACC, font=(FONT, 9), cursor="hand2",
                       relief="flat", bd=0, highlightthickness=0) \
            .pack(side="left", padx=(8, 0))
        tk.Label(row_b, text="⚡压缩模拟", bg=PANEL, fg=WARN,
                 font=(FONT, 9)).pack(side="left", padx=(8, 2))
        self.sim_n = tk.Spinbox(row_b, from_=30, to=4380, increment=30,
                                width=6, bg="#0E131B", fg=TXT, relief="flat",
                                buttonbackground="#202634", font=(FONT, 9))
        self.sim_n.delete(0, "end")
        self.sim_n.insert(0, "365")
        self.sim_n.pack(side="left")
        self.sim_btn = tk.Button(row_b, text="▶ 开始", command=self.sim_toggle,
                                 bg="#1C2622", fg="#9DB9A8", relief="flat",
                                 font=(FONT, 9, "bold"), cursor="hand2",
                                 padx=8)
        self.sim_btn.pack(side="left", padx=(4, 0))

    # ------------------------------------------------ 引擎动作入口 ----------
    def mcts_go(self):
        if self.sim_running:
            return
        self.app.think("SYS", "🌲 正在推演最优教学动作(蒙特卡洛树搜索)…")
        self.app.root.after(30, self.app.engine.plan_mcts)
        self.app.root.after(400, self.app.maybe_apply_plan)

    def toggle_pilot(self):
        if self.pilot_var.get():
            self.app.think("SYS", "✈ 自动领航已开启: 引擎将按MCTS/启发式逐日驱动空白学生体成长(每2秒=1个学习日)")
            self.app.schedule_pilot()
        else:
            self.app.think("SYS", "✈ 自动领航已关闭")

    def sim_toggle(self):
        if self.sim_running:
            self.sim_stop.set()
            return
        try:
            n = int(self.sim_n.get())
        except Exception:
            n = 365
        n = int(clamp(n, 1, 4380))
        self.sim_running = True
        self.sim_stop.clear()
        self.sim_btn.configure(text="■ 停止", bg="#291E1E", fg="#C09B9B")
        self.app.think("SYS", "⚡ 时间压缩模拟启动: 目标%d天, 即将在数秒内跑完并验证路径有效性…" % n)
        self.app.think("GOAL", "🎯 终点参照: %s 知识库; 若模拟结束成长分接近同龄理想线 → 路径有效"
                       % self.app.engine.role()["label"])

        def work():
            def sink(batch):
                self.app.push_ui(lambda: self._sim_sink(batch))
            try:
                self.app.engine.simulate_days(n, chunk=60, sink=sink,
                                              stop_flag=self.sim_stop)
            except Exception as e:
                self.app.push_ui(lambda: self.app.think("SYS", "⚠ 模拟异常: %s" % e))
            finally:
                self.app.push_ui(self._sim_done)
        threading.Thread(target=work, daemon=True).start()

    def _sim_sink(self, batch):
        for ev in batch:
            self.app.think_text(*ev)
        self.app.engine_ui_refresh()

    def _sim_done(self):
        self.sim_running = False
        self.sim_btn.configure(text="▶ 开始", bg="#1C2622", fg="#9DB9A8")
        self.pilot_var.set(False)
        try:                                    # 4380天数据集落盘
            csv_p = self.app.vault.save_csv(self.app.engine)
            traj = self.app.vault.save_learning_trajectory(self.app.engine)
            self.app.vault.save_level_rating(self.app.engine)
            if csv_p:
                self.app.toast("📊 4380天数据集已归档",
                               "逐日成长轨迹已写入:\n%s\n(数据仓库按学习日存放视频/分析/片段数据, "
                               "0-100岁规范见「数据规范_0-100岁.txt」)" % csv_p, VIOLET, 10)
            # 自动生成 4380 天逐日档案(Word+Markdown+JSON)
            n_fit = self.app.engine.fit_from_rows(self.app.engine.traj_rows)
            if n_fit:
                self.app.think("SYS", "🧬 数据驱动层: 本轮模拟%d天轨迹已回读拟合, "
                                      "教学动作权重已更新(下次学习即生效)" % n_fit)
            if traj:
                self.app.think("SYS", "🧭 学习轨迹已落盘: %d条事件 / %d技能 / %d错误记录 / %d记忆事件"
                               % (traj.get("episodes", 0), traj.get("skills", 0),
                                  traj.get("errors", 0), traj.get("memory", 0)))
            if len(self.app.engine.traj_rows) >= 100:
                self.app.archive_all_btn(auto=True)
        except Exception:
            pass
        self.app.engine_ui_refresh()

    # ------------------------------------------------ 图形绘制 ----------
    def set_targets(self):
        """按引擎当前学情刷新两条进度条目标(榜样同龄理想 vs 学生实际)。"""
        eng = self.app.engine
        score = eng.student.score5()
        ideal = GrowthCurve.ideal(eng.real_day)
        equiv_day, gap = eng.dual_timeline()[:2]
        self.bar_model.set_target(
            ideal / 5.0,
            caption="同龄里程碑: %s" % eng.milestone_note(eng.real_day)[:42])
        self.bar_stu.set_target(
            score / 5.0,
            caption="等效榜样 %s · %s %d天 · 成长分%.2f" % (
                age_str(equiv_day), eng.gap_status()[0], abs(gap), score))

    def refresh(self):
        """由 App 每 ~80ms 调用: 双进度条动画 + 顶栏信息。"""
        self.set_targets()
        self.bar_model.animate()
        self.bar_stu.animate()
        self.gap_lab.configure(text=self._gap_text())

    def _gap_text(self):
        eng = self.app.engine
        equiv_day, gap, score, ideal = eng.dual_timeline()
        st, col = eng.gap_status()
        cur_grade = eng.grade_label()
        r = eng.level_rating()
        return ("双时间轴 | 实际: %s(%s) | 等效榜样: %s | %s %d天 | 阶段: %s%s | "
                "修炼: %s%s·%s 榜位%d/100 | "
                "剩余K12: %d天   \t当前知识点: %s"
                % (age_str(eng.real_day), cur_grade, age_str(equiv_day), st,
                   abs(gap), eng.stage()[1], eng.stage()[0],
                   r["level_realm_emoji"], r["level_realm_name"], r["tier"], r["rank"],
                   eng.remain_days, eng.topic_hint_text()))

    def _draw_curve(self):
        c = self.curve
        w, h = c.winfo_width(), c.winfo_height()
        if w < 40 or h < 40:
            return
        c.delete("all")
        eng = self.app.engine
        ml, mr, mt, mb = 6, 10, 8, 26
        pw, ph = w - ml - mr, h - mt - mb
        def X(d): return ml + d / HORIZON_DAYS * pw
        def Y(s): return mt + (1.0 - clamp(s / 5.0, 0, 1)) * ph
        # 网格 + 年龄轴
        for d in range(0, int(HORIZON_DAYS) + 1, 365):
            c.create_line(X(d), mt, X(d), mt + ph, fill="#232936", dash=(1, 4))
        for d in range(0, int(HORIZON_DAYS) + 1, 730):
            c.create_line(X(d), mt + ph, X(d), mt + ph + 4, fill=SUB)
            c.create_text(X(d), mt + ph + 8, text="%d岁" % (6 + d // 365),
                          fill=SUB, font=(FONT, 7))
        # 理想榜样线(S型)
        pts = []
        for i in range(0, 91):
            d = i / 90.0 * HORIZON_DAYS
            pts += [X(d), Y(GrowthCurve.ideal(d))]
        c.create_line(pts, fill=WARN, width=2)
        c.create_text(ml + pw - 2, mt + 4, anchor="ne", text="— 榜样理想生长线(S型)",
                      fill=WARN, font=(FONT, 7))
        # 学生实际轨迹
        hist = list(eng.perf_history)
        if hist:
            pts2 = []
            for d, s in hist:
                pts2 += [X(d), Y(s)]
            if len(pts2) >= 4:
                c.create_line(pts2, fill=ACC, width=2)
            d0, s0 = hist[-1]
            c.create_oval(X(d0) - 4, Y(s0) - 4, X(d0) + 4, Y(s0) + 4,
                          fill="#FFFFFF", outline=ACC, width=2)
            c.create_text(X(d0) + 6, Y(s0) - 10, anchor="w", fill=TXT,
                          text="你", font=(FONT, 8, "bold"))
        # 等效榜样年龄刻度(双时间轴)
        equiv_day, gap, _, _ = eng.dual_timeline()
        c.create_line(X(equiv_day), mt, X(equiv_day), mt + ph,
                      fill=VIOLET, dash=(4, 3))
        c.create_text(X(equiv_day), mt + ph + 8, text="⇤等效%s" % age_str(equiv_day),
                      fill=VIOLET, font=(FONT, 7))
        # 认知维度迷你条(底部)
        dims = eng.student.dims
        cell = pw / 5.0
        for i, k in enumerate(DIM_KEYS):
            x0 = ml + cell * i + 4
            v = clamp(dims[k], 0, 1)
            c.create_text(x0, mt + ph + 16, anchor="w",
                          text="%s%s %.0f%%" % (DIM_ICONS[k], DIM_NAMES[k], v * 100),
                          fill=SUB, font=(FONT, 7))
            RoundedRect.bar(c, x0 + 52, mt + ph + 19, x0 + cell - 6, mt + ph + 23,
                            2, v, mix(ACC, VIOLET, i / 4.0), bg=mix(EDGE, "#232936", 0.5))

# ==================================================== 摄像头模块 =============
# 需求: 一键打开本机摄像头 / 录制视频并存储 / 双模型分析
#      (常规分析=本地模型, 加强评估打分=外部大模型API) / 结果实时驱动进度条

# 数据仓库: 统一英文路径(OpenCV 在 Windows 下对中文路径支持差, 会静默失败)
CAM_DIR = r"C:\ai_student_data"
try:                                        # 无写权限时自动降级, 仍保持英文路径
    os.makedirs(CAM_DIR, exist_ok=True)
except Exception:
    CAM_DIR = os.path.join(os.path.expanduser("~"), "ai_student_data")
    try:
        os.makedirs(CAM_DIR, exist_ok=True)
    except Exception:
        pass
AGE0_DAYS = 6 * 365            # 6岁 = 出生后第2190天(0-100岁数据轴起点)


def abs_day_of(engine):
    """学生在0-100岁(36500天)数据轴上的绝对日: 6-18岁K12段=2190..6569。"""
    try:
        return AGE0_DAYS + int(engine.real_day)
    except Exception:
        return AGE0_DAYS


def day_label(absd):
    y, d = absd // 365, absd % 365
    return "D%05d_%d岁%d天" % (absd, y, d)


def _xml_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def docx_build(path, title, blocks):
    """零依赖生成 Word 文档(docx=zip+OOXML)。blocks: [(style, text)...]
    style ∈ h1/h2/h3/p/li; 纯标准库实现, Word/WPS 可直接打开。"""
    import zipfile
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    paras = []
    for style, text in blocks:
        t = _xml_escape(text)
        if style == "h1":
            paras.append('<w:p><w:pPr><w:spacing w:before="120" w:after="120"/>'
                         '</w:pPr><w:r><w:rPr><w:b/><w:sz w:val="36"/>'
                         '<w:color w:val="1F4E79"/></w:rPr>'
                         '<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % t)
        elif style == "h2":
            paras.append('<w:p><w:pPr><w:spacing w:before="80" w:after="80"/>'
                         '</w:pPr><w:r><w:rPr><w:b/><w:sz w:val="28"/>'
                         '<w:color w:val="2E74B5"/></w:rPr>'
                         '<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % t)
        elif style == "h3":
            paras.append('<w:p><w:pPr><w:spacing w:before="60" w:after="40"/>'
                         '</w:pPr><w:r><w:rPr><w:b/><w:sz w:val="24"/>'
                         '<w:color w:val="404040"/></w:rPr>'
                         '<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % t)
        elif style == "li":
            paras.append('<w:p><w:pPr><w:ind w:left="360"/></w:pPr><w:r>'
                         '<w:rPr><w:sz w:val="21"/></w:rPr>'
                         '<w:t xml:space="preserve">• %s</w:t></w:r></w:p>' % t)
        else:
            paras.append('<w:p><w:r><w:rPr><w:sz w:val="21"/></w:rPr>'
                         '<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % t)
    xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/'
           'wordprocessingml/2006/main"><w:body>%s'
           '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
           '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/>'
           '</w:sectPr></w:body></w:document>' % "".join(paras))
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
          'content-types"><Default Extension="rels" ContentType="application/'
          'vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/word/document.xml" ContentType="application/'
          'vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
          '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
            '2006/relationships"><Relationship Id="rId1" Type="http://schemas.'
            'openxmlformats.org/officeDocument/2006/relationships/officeDocument"'
            ' Target="word/document.xml"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", xml)
    return path


def docx_build_rich(path, title, blocks, images=()):
    """生成 Word 档案: 优先 python-docx(A4/2cm 页边距/可嵌采样帧),
    未安装 python-docx 时自动回退到内置零依赖 OOXML 实现。"""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    if HAVE_DOCX:
        try:
            from docx import Document
            from docx.shared import Cm
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            doc = Document()
            sec = doc.sections[0]
            sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)       # A4
            for a in ("top_margin", "bottom_margin", "left_margin",
                      "right_margin"):
                setattr(sec, a, Cm(2.0))                               # 页边距 2cm
            h = doc.add_heading(str(title), level=0)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for style, text in blocks:
                if style in ("h1", "h2", "h3"):
                    doc.add_heading(str(text), level=int(style[1]))
                elif style == "li":
                    doc.add_paragraph(str(text), style="List Bullet")
                else:
                    doc.add_paragraph(str(text))
            for img_path, caption in (images or ()):
                try:
                    if img_path and os.path.exists(img_path):
                        doc.add_picture(img_path, width=Cm(16.0))
                        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                        doc.add_paragraph(str(caption))
                except Exception:
                    doc.add_paragraph("(图片未能嵌入: %s)" % caption)
            doc.save(path)
            return path
        except Exception:
            pass
    return docx_build(path, title, blocks)


def md_build(path, title, sections):
    """Markdown 档案: sections = [(h2标题, [行...])...]"""
    lines = ["# %s" % title, ""]
    for head, rows in sections:
        lines.append("## %s" % head)
        lines.append("")
        for r in rows:
            lines.append("- %s" % r)
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


class DataVault:
    """ai学生数据仓库(0-100岁 ai数据人 持久化层):
        ai学生_数据仓库/
         ├ 影像/D00001_0岁0天/…        —— 视频片段(按学习日时间戳存放)
         ├ 分析/D00001_0岁0天/…        —— 抓帧与双模型分析结果(按日)
         ├ 数据集/D00001.json…         —— 每日片段数据(逐日结构化记录)
         ├ 数据集/成长轨迹_4380天.csv   —— K12 4380天逐日轨迹
         └ 数据集/数据规范_0-100岁.txt  —— 通用数据结构说明(通向0-100岁ai数据学生)
    """

    def __init__(self):
        self.root = CAM_DIR
        self._lk = threading.Lock()

    def ensure(self):
        for sub in ("影像", "分析", "数据集"):
            os.makedirs(os.path.join(self.root, sub), exist_ok=True)
        return self.root

    def day_dir(self, engine, sub):
        absd = abs_day_of(engine)
        p = os.path.join(self.root, sub, day_label(absd))
        os.makedirs(p, exist_ok=True)
        return p

    def video_path(self, engine):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.day_dir(engine, "影像"),
                            "视频_%s_%s.mp4" % (day_label(abs_day_of(engine)), ts))

    def snapshot_path(self, engine):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.day_dir(engine, "分析"),
                            "抓帧_%s_%s.jpg" % (day_label(abs_day_of(engine)), ts))

    def day_json(self, engine):
        absd = abs_day_of(engine)
        return os.path.join(self.root, "数据集", "%s.json" % day_label(absd))

    def record_day(self, engine, section, payload):
        """按学习日写入/更新片段数据(视频/分析/动作 追加到当日记录)。"""
        try:
            with self._lk:
                self.ensure()
                absd = abs_day_of(engine)
                p = self.day_json(engine)
                data = {}
                if os.path.exists(p):
                    try:
                        with open(p, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except Exception:
                        data = {}
                if "基础" not in data:
                    data["基础"] = {"绝对日": absd, "年龄": age_str(engine.real_day),
                                    "0-100岁数据轴": "0~36500天",
                                    "学生": engine.student_name,
                                    "年级": engine.grade_label(),
                                    "认知阶段": engine.stage()[0],
                                    "建立时间": datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S")}
                data.setdefault("动作历史", [])
                if section == "action":
                    data["动作历史"].append(payload)
                data.setdefault("视频片段", [])
                if section == "video":
                    data["视频片段"].append(payload)
                data.setdefault("分析结果", [])
                if section == "analysis":
                    data["分析结果"].append(payload)
                data["最新快照"] = {
                    "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "维度": {k: round(v, 4) for k, v in engine.student.dims.items()},
                    "成长分": round(engine.student.score5(), 4),
                    "理想分": round(GrowthCurve.ideal(engine.real_day), 4),
                    "等效榜样": age_str(engine.dual_timeline()[0]),
                    "差距天数": engine.dual_timeline()[1],
                    "疲劳": round(engine.student.fatigue, 4),
                    "专注": round(engine.student.attention, 4),
                    "知识点": "%s·%s" % (engine.current_subject(),
                                       engine.current_topic()[1])}
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=1)
            return p
        except Exception:
            return None

    def save_csv(self, engine):
        """4380天逐日成长轨迹 CSV(压缩模拟后必存, 也是数据集主线)。"""
        try:
            self.ensure()
            p = os.path.join(self.root, "数据集", "成长轨迹_4380天.csv")
            rows = engine.traj_rows
            if not rows:
                return p
            with open(p, "w", encoding="utf-8-sig", newline="") as f:
                f.write("绝对日,年龄,年级,认知阶段,成长分,理想分,等效榜样,差距天数,"
                        "疲劳,专注,动作,学科,知识点\n")
                for r in rows:
                    f.write("%(abs)d,%(age)s,%(grade)s,%(stage)s,%(score).4f,"
                            "%(ideal).4f,%(equiv)s,%(gap)d,%(fat).4f,%(att).4f,"
                            "%(act)s,%(subj)s,%(topic)s\n" % r)
            return p
        except Exception:
            return None

    # -------------------------------------------- 按日档案(Word+Markdown) ---
    def day_doc_dir(self, engine):
        p = os.path.join(self.root, "数据集", day_label(abs_day_of(engine)))
        os.makedirs(p, exist_ok=True)
        return p

    def day_doc_blocks(self, label, base, snap, actions, videos, analyses):
        """组装当日学情档案内容(Word 与 Markdown 共用)。"""
        h1 = "%s 学情档案 · AI学生" % label
        blocks = [(h1 if False else "h1", h1),
                  ("p", "生成时间: %s | 本档案由 AI学生引擎自动生成, "
                        "服务于大模型后期数据存储与训练(可回读进化)。"
                        % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]
        secs = [("一、基础信息", base), ("二、认知快照", snap),
                ("三、当日学习动作", actions or ["(当日暂无手动打卡)"]),
                ("四、视频片段", videos or ["(当日未录制)"]),
                ("五、双模型分析结果", analyses or ["(当日未分析)"])]
        sections = []
        for head, rows in secs:
            sections.append((head, rows))
            blocks.append(("h2", head))
            for r in rows:
                blocks.append(("li", r))
        return blocks, sections

    def _day_payloads(self, engine):
        p = self.day_json(engine)
        data = {}
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        base = data.get("基础") or {
            "绝对日": abs_day_of(engine), "年龄": age_str(engine.real_day),
            "学生": engine.student_name, "年级": engine.grade_label(),
            "认知阶段": engine.stage()[0]}
        snap = data.get("最新快照") or {}
        base_rows = ["%s: %s" % (k, v) for k, v in base.items()]
        snap_rows = (["维度: %s" % ", ".join("%s=%.3f" % (DIM_NAMES[k], v)
                                            for k, v in (snap.get("维度") or {}).items())]
                     if snap.get("维度") else [])
        for k in ("成长分", "理想分", "等效榜样", "差距天数", "疲劳", "专注", "知识点"):
            if snap.get(k) is not None:
                snap_rows.append("%s: %s" % (k, snap[k]))
        acts = ["%s | 动作:%s | 学科:%s | 知识点:%s" % (
            a.get("时间", ""), a.get("动作", ""), a.get("学科", ""),
            a.get("知识点", "")) for a in data.get("动作历史", [])]
        vids = ["%s | %s (%.0f秒)" % (v.get("时间", ""), os.path.basename(
            str(v.get("文件", ""))), float(v.get("时长秒") or 0))
            for v in data.get("视频片段", [])]
        ans = ["%s | 综合评分:%s\n    常规观察: %s\n    加强评分: %s" % (
            a.get("时间", ""), a.get("综合评分", "N/A"),
            (a.get("本地常规观察") or "(无)")[:120],
            (a.get("外部加强评分") or "(无)")[:120])
            for a in data.get("分析结果", [])]
        return base_rows, snap_rows, acts, vids, ans

    def archive_day(self, engine):
        """生成/更新当日档案: 文件夹 数据集/D#####_X岁X天/ 内放 .md/.docx/.json。"""
        try:
            label = day_label(abs_day_of(engine))
            d = self.day_doc_dir(engine)
            base_rows, snap_rows, acts, vids, ans = self._day_payloads(engine)
            blocks, sections = self.day_doc_blocks(
                label, base_rows, snap_rows, acts, vids, ans)
            md_build(os.path.join(d, "%s_学情档案.md" % label), label + " 学情档案",
                     sections)
            docx_build(os.path.join(d, "%s_学情档案.docx" % label),
                       label + " 学情档案", blocks)
            src = self.day_json(engine)
            if os.path.exists(src):
                import shutil
                shutil.copy(src, os.path.join(d, "%s.json" % label))
            return d
        except Exception:
            return None

    def row_to_blocks(self, r):
        """由轨迹行(压缩模拟)生成档案内容。"""
        label = day_label(r["abs"])
        base = ["绝对日: %d" % r["abs"], "年龄: %s" % r["age"],
                "年级: %s" % r["grade"], "认知阶段: %s" % r["stage"]]
        snap = ["成长分: %.4f/5 | 理想分: %.4f/5" % (r["score"], r["ideal"]),
                "等效榜样: %s | 差距: %+d天" % (r["equiv"], r["gap"]),
                "疲劳: %.3f | 专注: %.3f" % (r["fat"], r["att"]),
                "维度: %s" % ", ".join("%s=%.3f" % (DIM_NAMES[DIM_KEYS[i]], v)
                                     for i, v in enumerate(r.get("dims", []))
                                     if i < 5)]
        acts = ["压缩模拟执行「%s」: %s·%s" % (r["act"], r["subj"], r["topic"])]
        return self.day_doc_blocks(label, base, snap, acts, [], [])

    def build_all_docs(self, engine, progress=None, stop_flag=None):
        """把 6-18岁 4380 天逐日生成档案(文件夹+文件名自动命名), 返回统计。"""
        seen, ok = {}, 0
        rows = list(engine.traj_rows)
        total = len(rows)
        if progress:
            progress(0, total, "开始")
        for i, r in enumerate(rows):
            if stop_flag and stop_flag.is_set():
                break
            seen[r["abs"]] = r
        uniq = sorted(seen.values(), key=lambda r: r["abs"])
        for i, r in enumerate(uniq):
            if stop_flag and stop_flag.is_set():
                break
            try:
                label = day_label(r["abs"])
                d = os.path.join(self.root, "数据集", label)
                os.makedirs(d, exist_ok=True)
                blocks, sections = self.row_to_blocks(r)
                md_build(os.path.join(d, "%s_学情档案.md" % label),
                         label + " 学情档案", sections)
                docx_build(os.path.join(d, "%s_学情档案.docx" % label),
                           label + " 学情档案", blocks)
                with open(os.path.join(d, "%s.json" % label), "w",
                          encoding="utf-8") as f:
                    json.dump(r, f, ensure_ascii=False, indent=1)
                ok += 1
                if progress and (i % 100 == 0 or i == len(uniq) - 1):
                    progress(ok, len(uniq), None)
            except Exception:
                continue
        return ok, len(uniq)

    def build_corpus(self, engine):
        """生成大模型训练语料 jsonl(逐日一条, 含维度/动作/话题)。"""
        try:
            self.ensure()
            p = os.path.join(self.root, "数据集", "训练语料_4380天.jsonl")
            n = 0
            with open(p, "w", encoding="utf-8") as f:
                for r in engine.traj_rows:
                    f.write(json.dumps({
                        "abs_day": r["abs"], "age": r["age"], "grade": r["grade"],
                        "stage": r["stage"], "score": r["score"],
                        "ideal": r["ideal"], "gap": r["gap"],
                        "fatigue": r["fat"], "attention": r["att"],
                        "action": r["act"], "subject": r["subj"],
                        "topic": r["topic"], "dims": r.get("dims", [])},
                        ensure_ascii=False) + "\n")
                    n += 1
            return p, n
        except Exception:
            return None, 0

    # ------------------------------------------------ 回读与进化 ----
    def scan(self):
        """扫描数据仓库, 返回可回读统计(供引擎进化)。"""
        stats = {"days": 0, "docs": 0, "videos": 0, "analyses": 0, "latest": None}
        try:
            self.ensure()
            for f in os.listdir(os.path.join(self.root, "数据集")):
                fp = os.path.join(self.root, "数据集", f)
                if f.startswith("D") and f.endswith(".json") and os.path.isfile(fp):
                    stats["days"] += 1
                    stats["latest"] = fp
                elif os.path.isdir(fp):
                    n = len([x for x in os.listdir(fp) if x.endswith(".docx")])
                    stats["docs"] += n
            for sub in ("影像", "分析"):
                base = os.path.join(self.root, sub)
                if os.path.isdir(base):
                    for d in os.listdir(base):
                        dp = os.path.join(base, d)
                        if os.path.isdir(dp):
                            cnt = len(os.listdir(dp))
                            if sub == "影像":
                                stats["videos"] += cnt
                            else:
                                stats["analyses"] += cnt
            return stats
        except Exception:
            return stats

    def load_day(self, engine):
        """读取当前学习日的片段数据(json)。"""
        try:
            p = self.day_json(engine)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def load_trajectory(self):
        """回读 4380天成长轨迹 CSV → 轨迹行列表(供数据驱动拟合/进化)。"""
        try:
            import csv
            p = os.path.join(self.root, "数据集", "成长轨迹_4380天.csv")
            if not os.path.exists(p):
                return []
            rows = []
            with open(p, "r", encoding="utf-8-sig", newline="") as f:
                rd = csv.DictReader(f)
                for r in rd:
                    try:
                        rows.append({
                            "abs": int(r["绝对日"]), "age": r["年龄"],
                            "grade": r["年级"], "stage": r["认知阶段"],
                            "score": float(r["成长分"]), "ideal": float(r["理想分"]),
                            "equiv": r["等效榜样"], "gap": int(r["差距天数"]),
                            "fat": float(r["疲劳"]), "att": float(r["专注"]),
                            "act": r["动作"], "subj": r["学科"],
                            "topic": r["知识点"]})
                    except Exception:
                        continue
            return rows
        except Exception:
            return []

    def write_manifest(self):
        """0-100岁 ai数据学生 通用数据结构说明(一次写入)。"""
        try:
            self.ensure()
            p = os.path.join(self.root, "数据集", "数据规范_0-100岁.txt")
            if os.path.exists(p):
                return p
            doc = (
                "AI学生数据仓库 · 0-100岁 ai数据学生(ai数据人) 通用数据结构规范\n"
                "=" * 60 + "\n"
                "1. 时间轴: 按出生第0天~第36500天(0-100岁)连续编号; 6-18岁K12段\n"
                "   为绝对日 2190~6569 (4380天, 12年×365天, 与专利一致)。\n"
                "2. 每日片段数据(三格式自动生成, 文件夹与文件名按日自动命名):\n"
                "   数据集/D#####_X岁X天/D#####_X岁X天_学情档案.md   (Markdown)\n"
                "   数据集/D#####_X岁X天/D#####_X岁X天_学情档案.docx (Word文档)\n"
                "   数据集/D#####_X岁X天/D#####.json               (结构化记录)\n"
                "3. 视频与画面: 影像/ 与 分析/ 目录按天存放, 文件名带第N天+时间戳。\n"
                "4. 成长轨迹: 数据集/成长轨迹_4380天.csv 逐日一行; 训练语料:\n"
                "   数据集/训练语料_4380天.jsonl (逐日一条, 可直接喂给大模型训练)。\n"
                "5. 回读进化: 程序启动时扫描本仓库, 按历史档案执行经验回放, 提升\n"
                "   学生保持率(记忆)等参数 —— 数据越积累, ai学生越聪明。\n"
                "6. 扩展: 同一数据结构可直接覆盖18-24岁(高等教育/职业训练)乃至\n"
                "   0-100岁全龄段, 汇聚后即为该学生的「ai数据人」; 行业化后成为\n"
                "   行业专有知识库, 与专利『ai数据人的通用数据结构』一致。\n"
                "=" * 60 + "\n")
            with open(p, "w", encoding="utf-8") as f:
                f.write(doc)
            return p
        except Exception:
            return None


    # ------------------------------------------------ 学习轨迹持久化(v3) ----
    def episodes_path(self):
        return os.path.join(self.root, "数据集", "learning_episodes.jsonl")

    def skills_path(self):
        return os.path.join(self.root, "数据集", "skill_states.json")

    def errors_path(self):
        return os.path.join(self.root, "数据集", "errors.jsonl")

    def memory_path(self):
        return os.path.join(self.root, "数据集", "memory_records.jsonl")

    def rating_path(self):
        return os.path.join(self.root, "数据集", "level_rating.json")

    def save_level_rating(self, engine):
        """落盘统一评价标准快照: 境界/段位/榜位/榜样等效年龄/九字秘法修为。"""
        try:
            self.ensure()
            with open(self.rating_path(), "w", encoding="utf-8") as f:
                json.dump(engine.level_rating(), f, ensure_ascii=False, indent=1)
            return self.rating_path()
        except Exception:
            return None

    def save_learning_trajectory(self, engine):
        """把 学习事件/技能状态/错误记录/记忆事件 落盘(增量追加, 可反复调用)。"""
        try:
            self.ensure()
            new_eps = engine.episodes[engine._episode_flushed:]
            if new_eps:
                with open(self.episodes_path(), "a", encoding="utf-8") as f:
                    for ep in new_eps:
                        f.write(json.dumps(ep.to_dict(), ensure_ascii=False) + "\n")
                engine._episode_flushed = len(engine.episodes)
            with open(self.skills_path(), "w", encoding="utf-8") as f:
                json.dump({sid: s.to_dict() for sid, s in engine.skills.items()},
                          f, ensure_ascii=False, indent=1)
            with open(self.errors_path(), "w", encoding="utf-8") as f:
                for r in engine.errors.values():
                    f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
            new_mem = engine.memory_records[engine._memory_flushed:]
            if new_mem:
                with open(self.memory_path(), "a", encoding="utf-8") as f:
                    for m in new_mem:
                        f.write(json.dumps(m, ensure_ascii=False) + "\n")
                engine._memory_flushed = len(engine.memory_records)
            return {"episodes": len(new_eps), "skills": len(engine.skills),
                    "errors": len(engine.errors), "memory": len(new_mem)}
        except Exception:
            return None

    def load_learning_trajectory(self, engine):
        """启动回读: 恢复技能状态/错误记录/历史学习事件(经验回放与数据驱动进化)。"""
        loaded = {"skills": 0, "errors": 0, "episodes": 0, "memory": 0}
        try:
            self.ensure()
            sp = self.skills_path()
            if os.path.exists(sp):
                with open(sp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for sid, d in data.items():
                        engine.skills[sid] = SkillState.from_dict(d)
                    loaded["skills"] = len(data)
            ep_p = self.episodes_path()
            if os.path.exists(ep_p):
                with open(ep_p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            engine.episodes.append(LearningEpisode.from_dict(json.loads(line)))
                            loaded["episodes"] += 1
                        except Exception:
                            pass
                engine._episode_flushed = len(engine.episodes)
            er_p = self.errors_path()
            if os.path.exists(er_p):
                with open(er_p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            r = ErrorRecord.from_dict(json.loads(line))
                            engine.errors[r.key()] = r
                            loaded["errors"] += 1
                        except Exception:
                            pass
            mem_p = self.memory_path()
            if os.path.exists(mem_p):
                with open(mem_p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            engine.memory_records.append(json.loads(line))
                            loaded["memory"] += 1
                        except Exception:
                            pass
                engine._memory_flushed = len(engine.memory_records)
        except Exception:
            pass
        return loaded


def vision_capable(model_name):
    """粗略判断模型是否支持图像输入(视觉模型)。"""
    n = (model_name or "").lower()
    for k in ("vl", "vision", "llava", "minicpm", "4o", "4v", "glm-4v",
              "qwen-vl", "qwen2-vl", "qwen2.5-vl", "gemini", "claude",
              "internvl", "moondream", "deepseek-vl", "gpt-5", "step-",
              "pixtral", "yi-vl", "cogvlm", "omni", "phi-3.5-vision",
              "phi-4-multimodal", "vision-preview", "multimodal", "janus"):
        if k in n:
            return True
    return False


class CameraWorker(threading.Thread):
    """摄像头采集线程: 预览帧 + 画面统计 + 视频录制(可选), 全程守护线程。"""

    def __init__(self, panel, source):
        super().__init__(daemon=True)
        self.panel = panel
        self.source = source
        self.stop_evt = threading.Event()
        self.fail_msg = None
        self.writer = None
        self.rec_path = None
        self.frames_total = 0

    def stop(self):
        self.stop_evt.set()

    def run(self):
        global cv2
        app = self.panel.app
        try:
            if not HAVE_CV2:
                raise RuntimeError("程序缺少 OpenCV 组件(打包版应内置), 无法打开摄像头")
            if self.source is None or str(self.source).strip() == "":
                raise RuntimeError("摄像头源为空")
            src = str(self.source).strip()
            cap = None
            used_backend = "ANY"
            if src.isdigit():
                idx = int(src)
                # 后端链式回退: DSHOW → MSMF → ANY (兼容各机型/驱动)
                tried = []
                for bk in ("DSHOW", "MSMF", "ANY"):
                    try:
                        if bk == "DSHOW":
                            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                        elif bk == "MSMF":
                            cap = cv2.VideoCapture(idx, cv2.CAP_MSMF)
                        else:
                            cap = cv2.VideoCapture(idx)
                        if cap.isOpened():
                            used_backend = bk
                            break
                        tried.append(bk)
                        cap.release()
                        cap = None
                    except Exception:
                        tried.append(bk)
                        cap = None
                if cap is None or not cap.isOpened():
                    raise RuntimeError(self._fail_hint(tried))
            else:
                cap = cv2.VideoCapture(src)
                used_backend = "URL/RTSP"
                if not cap.isOpened():
                    raise RuntimeError("无法打开摄像头源(%s)。请检查 RTSP/HTTP 地址、账号密码与网络, "
                                       "或改回本机摄像头编号 0" % src)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
            prev_gray = None
            tick = 0
            no_frame = 0
            first_frame_done = False
            while not self.stop_evt.is_set():
                ok, frame = cap.read()
                if not ok or frame is None:
                    no_frame += 1
                    if no_frame >= 40:      # ~4秒无画面 → 判定失败(占用/隐私/权限)
                        raise RuntimeError(
                            "摄像头已打开但取不到画面。常见原因: ①Windows隐私设置禁止桌面应用使用摄像头"
                            "(设置→隐私和安全性→摄像头→开启「允许桌面应用访问摄像头」) ②摄像头正被其他"
                            "程序占用(视频会议/浏览器/OBS/本程序多开) ③安全软件拦截。处理后重新打开即可。")
                    time.sleep(0.1)
                    continue
                no_frame = 0
                if not first_frame_done:
                    first_frame_done = True
                    app.push_ui(lambda: self.panel.on_first_frame(used_backend))
                # 画面统计(活跃度/亮度), 用于文本类模型的常规分析
                small = cv2.resize(frame, (80, 56))
                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                bri = float(gray.mean()) / 255.0
                act = 0.0
                if prev_gray is not None:
                    act = float(cv2.absdiff(gray, prev_gray).mean()) / 255.0
                prev_gray = gray
                self.panel.last_metrics = (round(act, 3), round(bri, 3))
                self.panel.last_frame = frame
                # 预览(镜像)帧
                disp = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
                if HAVE_PIL:
                    img = Image.fromarray(rgb)
                    img = img.resize((self.panel.pw, self.panel.ph), Image.LANCZOS)
                    try:
                        self.panel.fq.put_nowait((img, self.frames_total))
                    except Exception:
                        try:
                            self.panel.fq.get_nowait()
                        except Exception:
                            pass
                        try:
                            self.panel.fq.put_nowait((img, self.frames_total))
                        except Exception:
                            pass
                # 录制
                if self.panel.rec_requested and self.writer is None:
                    if self._open_writer(frame):
                        app.push_ui(lambda: self.panel.on_record_started(self.rec_path))
                if self.panel.rec_requested and self.writer is not None:
                    self.writer.write(frame)
                    self.frames_total += 1
                elif not self.panel.rec_requested and self.writer is not None:
                    self._close_writer()
                    app.push_ui(lambda: self.panel.on_record_stopped(self.rec_path, self.frames_total))
                    self.frames_total = 0
                tick += 1
                if tick % 90 == 0:      # 每~10s 推送一条视觉感知事件
                    app.push_ui(lambda a=act, b=bri:
                                app.think("CAM", "📷 视觉感知: 画面活跃度%.0f%%, 亮度%.0f%% "
                                                  "(用于本地模型常规学情分析)" % (a * 100, b * 100)))
                time.sleep(0.09)
        except Exception as e:
            self.fail_msg = str(e)
        finally:
            self._close_writer()
            try:
                cap.release()
            except Exception:
                pass
            app.push_ui(self.panel.on_worker_end)
            if self.fail_msg:
                app.push_ui(lambda: self.panel.on_worker_fail(self.fail_msg))

    def _open_writer(self, first_frame):
        try:
            h, w = first_frame.shape[:2]
            w4 = (w // 2) * 2
            h4 = (h // 2) * 2
            path = None
            try:                                    # 数据仓库按天存放
                path = self.panel.app.vault.video_path(self.panel.app.engine)
            except Exception:
                path = None
            if not path:
                name = ascii_safe(self.panel.app.engine.student_name, "student")
                os.makedirs(CAM_DIR, exist_ok=True)
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(CAM_DIR, "record_%s_%s.mp4" % (name, ts))
            # 先写到英文临时路径(规避 cv2.VideoWriter 中文路径静默失败), 停止后搬运
            temp_dir = os.path.join(CAM_DIR, "temp")
            try:
                os.makedirs(temp_dir, exist_ok=True)
            except Exception:
                temp_dir = CAM_DIR
            for codec, ext in (("mp4v", "mp4"), ("MJPG", "avi")):
                try:
                    tmp = os.path.join(temp_dir,
                                       "rec_%s.%s" % (uuid.uuid4().hex, ext))
                    wr = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*codec), 12.0,
                                         (w4, h4))
                    if wr.isOpened():
                        self.writer = wr
                        self.rec_tmp = tmp
                        self.rec_path = path if ext == "mp4" else \
                            path.replace(".mp4", ".avi")
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _close_writer(self):
        try:
            if self.writer is not None:
                self.writer.release()
        except Exception:
            pass
        self.writer = None
        # 英文临时文件 → 最终(可能含中文)路径: Python 文件操作支持中文, OpenCV 不参与
        tmp = getattr(self, "rec_tmp", None)
        dst = getattr(self, "rec_path", None)
        self.rec_tmp = None
        if tmp and dst:
            try:
                d = os.path.dirname(dst)
                if d:
                    os.makedirs(d, exist_ok=True)
                if os.path.exists(tmp):
                    shutil.move(tmp, dst)
            except Exception:
                try:
                    os.replace(tmp, dst)
                except Exception:
                    pass


def re_safe_name(name):
    import re as _re
    return _re.sub(r"[\\/:*?\"<>| ]+", "_", str(name or "学生")).strip("_") or "学生"


# ================================ 中文路径 / 视觉 / 网络 兼容工具 =============
# 背景: Windows 下 OpenCV 对含中文的路径支持差 —— cv2.imwrite / cv2.VideoCapture /
#      cv2.VideoWriter 经常"静默失败"(不报错, 但文件没写出来)。以下工具统一规避:
#      ① 视频先复制到英文临时目录再交给 OpenCV; ② 图片一律 imencode+tofile /
#      fromfile+imdecode; ③ 文件名统一转 ASCII 安全字符; ④ 密钥只显示首尾4位。

def ascii_safe(name, default="file", keep=48):
    """把(可能含中文的)名称转成 ASCII 安全文件名, 保持可读且唯一。"""
    raw = str(name or "")
    s = re.sub(r"[^0-9A-Za-z_-]+", "_", raw).strip("_")
    s = re.sub(r"_{2,}", "_", s)[:keep].strip("_")
    if not s:
        s = "%s_%s" % (default,
                       hashlib.md5(raw.encode("utf-8", "ignore")).hexdigest()[:6])
    return s


def mask_key(key):
    """思考区/日志中不出现完整 API Key(只保留前4位与后4位)。"""
    k = str(key or "").strip()
    if not k:
        return "(未配置)"
    if len(k) <= 8:
        return "*" * len(k)
    return "%s****%s" % (k[:4], k[-4:])


def imwrite_u(path, img, quality=88):
    """写图片: imencode + tofile(兼容中文路径, 不依赖 cv2.imwrite)。"""
    if img is None or not HAVE_CV2:
        return False
    try:
        ok, buf = cv2.imencode(".jpg", img,
                               [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
        if not ok:
            return False
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        buf.tofile(path)                 # numpy 走宽字符 API, 支持中文路径
        return True
    except Exception:
        return False


def imread_u(path):
    """读图片: fromfile + imdecode(兼容中文路径)。"""
    import numpy as np
    try:
        data = np.fromfile(path, dtype=np.uint8)
        if data.size == 0:
            return None
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def b64_image(path):
    """读取图片文件返回 base64 字符串(供视觉模型使用)。"""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except Exception:
        return None


def stage_video(path):
    """把(可能含中文路径的)视频复制到英文临时目录, 返回(临时路径, 临时目录)。"""
    ext = os.path.splitext(str(path))[1].lower()
    if ext not in (".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".m4v",
                   ".webm", ".mpg", ".mpeg", ".ts", ".3gp"):
        ext = ".mp4"
    temp_dir = os.path.join(CAM_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    dst = os.path.join(temp_dir, "input_%s%s" % (uuid.uuid4().hex, ext))
    shutil.copyfile(path, dst)
    return dst, temp_dir


def parse_score(text):
    """从模型回复中提取 0-100 专注评分(取不到返回 None)。"""
    t = str(text or "")
    for pat in (r"专注评分[:：]?\s*(\d{1,3})", r"评分[:：]?\s*(\d{1,3})",
                r"score[^0-9]{0,6}(\d{1,3})", r"(?<!\d)(\d{1,3})(?!\d)\s*分"):
        m = re.search(pat, t, re.I)
        if m:
            try:
                v = int(m.group(1))
                if 0 <= v <= 100:
                    return v
            except Exception:
                pass
    return None


# =========================================== 上传视频 → 双模型 → 档案 =========
# 链路: 中文路径视频 → 英文临时副本 → 采样6帧+蒙太奇 → 本地常规观察 ‖ 外部加强
#      评分 → Word/Markdown/JSON 档案。GUI 与 --test-video 共用这一份实现。

VIDEO_SAMPLES = 6


def video_default_cfg():
    """两个模型通道的配置: 配置文件 + 环境变量兜底(不硬编码任何密钥)。

    可选环境变量: AI_STUDENT_API_URL / AI_STUDENT_API_KEY / AI_STUDENT_API_MODEL
                   AI_STUDENT_LOCAL_BASE / AI_STUDENT_LOCAL_MODEL
    """
    c = cfg_load()
    loc = c.get("local", {}) or {}
    rem = c.get("remote", {}) or {}
    return {"local_base": str(os.environ.get("AI_STUDENT_LOCAL_BASE")
                              or loc.get("base") or LOCAL_DEFAULT),
            "local_model": str(os.environ.get("AI_STUDENT_LOCAL_MODEL")
                               or loc.get("model") or LOCAL_MODEL_DEFAULT),
            "remote_url": str(os.environ.get("AI_STUDENT_API_URL")
                              or rem.get("url") or ""),
            "remote_key": str(os.environ.get("AI_STUDENT_API_KEY")
                              or rem.get("key") or ""),
            "remote_model": str(os.environ.get("AI_STUDENT_API_MODEL")
                                or rem.get("model") or "")}


def resolved_cfg(cfg=None):
    """界面快照(可能为空或读取失败) + 配置文件/环境变量兜底; 空值不覆盖有效值。"""
    out = video_default_cfg()
    for k, v in (cfg or {}).items():
        if str(v or "").strip():
            out[k] = v
    return out


def _video_info_line(info, vision_ok=True):
    """画面统计一行描述; 模型不支持视觉时明确写出降级说明。"""
    s_ = ("时长%.0f秒, 采样%d帧, 画面活跃度%.0f%%, 亮度%.0f%%"
          % (info.get("时长秒", 0), info.get("采样帧", 0),
             info.get("活跃度均值", 0) * 100, info.get("亮度均值", 0) * 100))
    if not vision_ok:
        s_ += "，当前模型不支持图像输入，以下为画面统计与采样说明。"
    return s_


def run_video_analysis(path, cfg=None, log=None, on_stage=None, do_remote=True):
    """完整视频分析链路(无 GUI 依赖, 便于命令行验证)。

    返回 dict: ok / folder / info / local / remote / score / files / error。
    任何一路失败都不中断: 档案照常生成, 失败原因写入档案与思考区。
    """
    cfg = resolved_cfg(cfg)
    res = {"ok": False, "folder": None, "info": {}, "local": "", "remote": "",
           "score": None, "files": [], "error": "", "temp": None}

    def say(kind, msg):
        if log:
            try:
                log(kind, msg)
            except Exception:
                pass

    def stage(msg):
        if on_stage:
            try:
                on_stage(msg)
            except Exception:
                pass

    if not HAVE_CV2:
        res["error"] = "缺少 OpenCV(opencv-python) 组件, 无法读取视频"
        say("CAM", "⚠ " + res["error"])
        return res
    src = str(path or "")
    if not src or not os.path.exists(src):
        res["error"] = "找不到视频文件: %s" % src
        say("CAM", "⚠ " + res["error"])
        return res
    temp_video = None
    try:
        # ① 复制到英文临时路径(规避 OpenCV 中文路径静默失败)
        stage("采样中: 复制到英文临时路径…")
        temp_video, _tdir = stage_video(src)
        res["temp"] = temp_video
        say("SYS", "① 视频已复制到英文临时路径: %s" % os.path.basename(temp_video))
        cap = cv2.VideoCapture(temp_video)
        try:
            if not cap.isOpened():
                raise RuntimeError("OpenCV 无法打开该视频(格式不支持或文件损坏)")
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 0) or 25.0
            dur = total / fps
            fw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            n = min(VIDEO_SAMPLES, max(2, total))
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe = ascii_safe(os.path.splitext(os.path.basename(src))[0], "video")
            folder = os.path.join(CAM_DIR, "上传视频", "%s_%s" % (safe, ts))
            os.makedirs(folder, exist_ok=True)
            idxs = [int(total * (i + 0.5) / n) for i in range(n)]
            frames, acts, saved = [], [], []
            prev_gray = None
            for i, idx in enumerate(idxs):
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ok, fr = cap.read()
                if not ok or fr is None:
                    continue
                frames.append(fr)
                small = cv2.resize(fr, (80, 56))
                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                bri = float(gray.mean()) / 255.0
                act = 0.0
                if prev_gray is not None:
                    act = float(cv2.absdiff(gray, prev_gray).mean()) / 255.0
                prev_gray = gray
                acts.append((act, bri))
                fp = os.path.join(folder, "frame_%02d.jpg" % (i + 1))   # 英文名
                if imwrite_u(fp, fr):
                    saved.append(fp)
        finally:
            cap.release()
        if not frames:
            raise RuntimeError("视频没有可解码的画面(采样帧全为空)")
        say("SENSE", "② 采样完成: %d 帧已保存(frame_01.jpg…)" % len(saved))
        act_avg = sum(a for a, _b in acts) / max(1, len(acts))
        bri_avg = sum(b for _a, b in acts) / max(1, len(acts))
        while len(frames) < 6:                    # 帧数不足时补齐 2x3 蒙太奇
            frames.append(frames[-1])
        rows = [cv2.hconcat(frames[0:3]), cv2.hconcat(frames[3:6])]
        montage = None
        for r in rows:
            r2 = cv2.resize(r, (900, max(1, int(900 * r.shape[0] / r.shape[1]))))
            montage = r2 if montage is None else cv2.vconcat([montage, r2])
        mp = os.path.join(folder, "montage.jpg")
        if imwrite_u(mp, montage):
            saved.append(mp)
        b64 = b64_image(mp)
        info = {"文件": os.path.basename(src), "时长秒": round(dur, 1),
                "帧率": round(fps, 1), "总帧": total,
                "分辨率": "%dx%d" % (fw, fh), "采样帧": len(acts),
                "活跃度均值": round(act_avg, 3), "亮度均值": round(bri_avg, 3)}
        res["info"] = info
        # ② 双通道并行: 本地Ollama(常规观察) ‖ 外部API(加强评分)
        ev1, ev2 = threading.Event(), threading.Event()

        def chan_local():
            base = cfg.get("local_base") or LOCAL_DEFAULT
            lmodel = cfg.get("local_model") or LOCAL_MODEL_DEFAULT
            try:
                stage("调用本地模型(常规观察): %s" % lmodel)
                vis = lmodel if vision_capable(lmodel) else None
                prompt = ("你是「AI学生」学习行为分析员。这是学生上传的一段学习视频"
                          "(%s)。请给出『常规观察结论』: 学生在视频中的学习状态、"
                          "可能的行为模式与改进建议(≤150字, 中文, 不编造细节)。"
                          % _video_info_line(info))
                if vis and b64:
                    res["local"] = LLMClient.ollama_chat(
                        base, vis, [{"role": "user", "content": prompt}],
                        image_b64=b64, timeout=300).strip()
                    say("MODEL", "③ 本地视觉模型 %s 完成常规观察" % vis)
                else:
                    res["local"] = LLMClient.ollama_chat(
                        base, lmodel, [{"role": "user", "content": prompt}],
                        timeout=300).strip()
                    say("MODEL", "③ 本地模型 %s(文本通道)完成常规观察" % lmodel)
            except Exception as e:
                res["local"] = "常规分析失败: %s" % e
                say("MODEL", "⚠ 本地常规观察失败(不影响档案生成): %s" % e)
            finally:
                ev1.set()

        def chan_remote():
            url = (cfg.get("remote_url") or "").strip()
            key = (cfg.get("remote_key") or "").strip()
            model = (cfg.get("remote_model") or "").strip()
            try:
                if not do_remote or not (url and model):
                    res["remote"] = ("外部 API 未配置, 加强评分跳过"
                                     "(请在「🔑API密钥/模型设置」填 地址+密钥+模型)")
                    say("MODEL", "⚠ 外部 API 未配置, 加强评分跳过; 请点工具栏"
                                 "「🔑API密钥」填写 地址/密钥/模型 后重试(档案已生成)")
                    return
                stage("调用外部 API(加强评分): %s" % model)
                vok = vision_capable(model)
                say("MODEL", "④ 外部通道: 模型 %s · 密钥 %s · 视觉输入 %s"
                    % (model, mask_key(key), "是" if (vok and b64) else "否"))
                prompt = ("你是教育评估专家。基于学生上传学习视频的多帧采样(%s), "
                          "给出加强评估:\n专注评分: 0-100整数\n状态等级: 高度专注/"
                          "基本专注/轻度分心/明显走神/疲劳困倦\n一句话建议: ≤40字"
                          % _video_info_line(info, bool(vok and b64)))
                if vok and b64:
                    res["remote"] = LLMClient.remote_chat_vision(
                        url, key, model, prompt, b64, timeout=300).strip()
                else:
                    res["remote"] = LLMClient.remote_chat(
                        url, key, model, [{"role": "user", "content": prompt}],
                        timeout=300).strip()
                res["score"] = parse_score(res["remote"])
                say("MODEL", "⑤ 外部加强评分完成%s" % (
                    " · 专注评分 %s" % res["score"]
                    if res["score"] is not None else ""))
            except Exception as e:
                res["remote"] = "加强评分失败: %s" % e
                say("MODEL", "⚠ 外部加强评分失败(不影响档案生成): %s" % e)
            finally:
                ev2.set()

        t1 = threading.Thread(target=chan_local, daemon=True)
        t2 = threading.Thread(target=chan_remote, daemon=True)
        t1.start()
        t2.start()
        ev1.wait(420)
        ev2.wait(420)
        # ③ 生成 AI学生档案: Word + Markdown + JSON
        stage("生成档案: Word / Markdown / JSON…")
        label = "AI学生档案_%s" % ts
        secs = [("一、视频信息", ["%s: %s" % (k, v) for k, v in info.items()]),
                ("二、常规观察(本地模型)", [res["local"] or "(未执行)"]),
                ("三、加强评分(外部API)", [res["remote"] or "(未执行)"]),
                ("四、综合建议", [
                    "专注评分: %s" % (res["score"]
                                      if res["score"] is not None else "未取得"),
                    "本地通道看行为、外部通道做量化, 两者互为校验; "
                    "评分已同步驱动成长进度条。",
                    "请结合视频中的实际学习行为调整学习节奏与休息安排。"])]
        md_p = os.path.join(folder, "%s.md" % label)
        md_build(md_p, label, secs)
        blk = [("p", "视频: %s | %s" % (info["文件"], _video_info_line(info)))]
        for head, rows_ in secs:
            blk.append(("h2", head))
            for r in rows_:
                blk.append(("li", r))
        imgs = [(mp, "多帧蒙太奇(采样帧拼贴)")]
        for p in saved[:3]:
            if p != mp and p.endswith(".jpg"):
                imgs.append((p, "采样帧"))
        dx_p = os.path.join(folder, "%s.docx" % label)
        docx_build_rich(dx_p, label, blk, images=imgs)
        js_p = os.path.join(folder, "%s.json" % label)
        with open(js_p, "w", encoding="utf-8") as f:
            json.dump({"信息": info, "常规观察": res["local"],
                       "加强评分": res["remote"], "综合评分": res["score"],
                       "采样帧": [os.path.basename(x) for x in saved],
                       "生成时间": datetime.datetime.now().strftime(
                           "%Y-%m-%d %H:%M:%S")},
                      f, ensure_ascii=False, indent=2)
        res["folder"] = folder
        res["files"] = [dx_p, md_p, js_p] + saved
        res["ok"] = True
        say("SYS", "⑥ 档案已生成(Word/Markdown/JSON/采样帧/蒙太奇): %s" % folder)
    except Exception as e:
        res["error"] = str(e)
        say("CAM", "⚠ 视频分析失败: %s" % e)
    finally:
        try:
            if temp_video and os.path.exists(temp_video):
                os.remove(temp_video)             # 清理临时视频
        except Exception:
            pass
    return res


class CameraPanel(tk.Frame):
    """右上角摄像头模块: 一键打开 / 录制存储 / 本地+外部双模型视觉分析。"""

    def __init__(self, master, app):
        super().__init__(master, bg=PANEL, highlightbackground=EDGE,
                         highlightthickness=1, width=352)
        self.app = app
        self.pack_propagate(False)
        self.worker = None
        self.rec_requested = False
        self.recording = False
        self.analyzing = False
        self.last_frame = None
        self.last_metrics = (0.0, 0.0)
        self.fq = queue.Queue(maxsize=2)
        self._photo = None
        self.pw, self.ph = 336, 176

        # ---- 标题行 ----
        head = tk.Frame(self, bg=PANEL2)
        head.pack(fill="x")
        tk.Canvas(head, width=10, height=14, bg=PANEL2, highlightthickness=0) \
            .pack(side="left", padx=(10, 4), pady=8)
        tk.Label(head, text="📷 摄像头 · 视觉学情感知", bg=PANEL2, fg=TXT,
                 font=(FONT, 10, "bold")).pack(side="left")
        self.st_label = tk.Label(head, text="待开启", bg=PANEL2, fg=SUB,
                                 font=(FONT, 8))
        self.st_label.pack(side="right", padx=8)

        # ---- 画面 ----
        self.video = tk.Label(self, bg="#050A14", fg=SUB, text="",
                              font=(FONT, 9), compound="center",
                              anchor="center")
        self.video.pack(fill="x", padx=6, pady=(4, 2))
        self.draw_placeholder("摄像头未开启\n点击下方「一键打开摄像头」\n支持外接: 源填 1/2… 或 RTSP/HTTP 地址")

        # ---- 按钮行1 ----
        r1 = tk.Frame(self, bg=PANEL)
        r1.pack(fill="x", padx=6)
        self.open_btn = tk.Button(r1, text="📷 一键打开摄像头", command=self.toggle,
                                  bg="#1C2433", fg=ACC, relief="flat",
                                  font=(FONT, 9, "bold"), cursor="hand2")
        self.open_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
        self.rec_btn = tk.Button(r1, text="● 开始录制", command=self.rec_toggle,
                                 bg="#26221C", fg="#C2B08C", relief="flat",
                                 font=(FONT, 9, "bold"), cursor="hand2",
                                 state="disabled")
        self.rec_btn.pack(side="left", expand=True, fill="x", padx=2)
        self.ai_btn = tk.Button(r1, text="🤖 AI双模型分析", command=self.ai_analyze,
                                bg="#1C2622", fg="#9DB9A8", relief="flat",
                                font=(FONT, 9, "bold"), cursor="hand2",
                                state="disabled")
        self.ai_btn.pack(side="left", expand=True, fill="x", padx=(2, 0))

        # ---- 按钮行2 ----
        r2 = tk.Frame(self, bg=PANEL)
        r2.pack(fill="x", padx=6, pady=(2, 0))
        tk.Label(r2, text="源:", bg=PANEL, fg=SUB, font=(FONT, 8)).pack(side="left")
        self.src_var = tk.StringVar(value="0")
        e = tk.Entry(r2, textvariable=self.src_var, bg="#0E131B", fg=TXT,
                     relief="flat", font=(FONT, 8), width=7)
        e.pack(side="left", padx=(2, 2))
        self.apply_btn = tk.Button(r2, text="应用", command=self.apply_source,
                                   bg=PANEL2, fg=ACC, relief="flat",
                                   font=(FONT, 8), cursor="hand2")
        self.apply_btn.pack(side="left")
        self.rec_lab = tk.Label(r2, text="未在录制", bg=PANEL, fg=SUB,
                                font=(FONT, 8), anchor="w")
        self.rec_lab.pack(side="left", padx=(6, 0), fill="x", expand=True)
        self.folder_btn = tk.Button(r2, text="📂记录夹", command=self.open_folder,
                                    bg=PANEL2, fg=ACC, relief="flat",
                                    font=(FONT, 8), cursor="hand2")
        self.folder_btn.pack(side="right")

        # ---- 算力通道 / 实时同步分析行 ----
        r3 = tk.Frame(self, bg=PANEL)
        r3.pack(fill="x", padx=6, pady=(3, 0))
        tk.Label(r3, text="☁ 算力:", bg=PANEL, fg=SUB, font=(FONT, 8)) \
            .pack(side="left")
        self.cloud_var = tk.StringVar(value="本机优先")
        cb = ttk.Combobox(r3, textvariable=self.cloud_var, width=11,
                          values=("本机优先", "阿里云百炼·视觉", "阿里云EAS·自定义"),
                          state="readonly", font=(FONT, 8))
        cb.pack(side="left", padx=(2, 6))
        cb.bind("<<ComboboxSelected>>", self.cloud_selected)
        self.assess_btn = tk.Button(r3, text="⚡本机算力评估", command=self.assess_local,
                                    bg=PANEL2, fg=ACC, relief="flat",
                                    font=(FONT, 8), cursor="hand2")
        self.assess_btn.pack(side="left")
        self.rt_var = tk.BooleanVar(value=False)
        tk.Checkbutton(r3, text="🔄实时双模型同步分析", variable=self.rt_var,
                       command=self.rt_toggle, bg=PANEL, fg=TXT,
                       selectcolor=PANEL2, activebackground=PANEL,
                       activeforeground=TXT, font=(FONT, 8), cursor="hand2",
                       relief="flat", bd=0, highlightthickness=0) \
            .pack(side="right")
        self.rt_iv = tk.Spinbox(r3, from_=8, to=240, increment=5, width=3,
                                bg=INPUT_BG, fg=TXT, relief="flat",
                                buttonbackground="#202634", font=(FONT, 8))
        self.rt_iv.delete(0, "end")
        self.rt_iv.insert(0, "15")
        self.rt_iv.pack(side="right", padx=(2, 0))
        tk.Label(r3, text="秒/轮", bg=PANEL, fg=SUB, font=(FONT, 8)) \
            .pack(side="right", padx=(0, 4))

        # ---- 状态提示 ----
        self.info = tk.Label(self, text="分析链路: 本地常规观察 ‖ 外部加强评分(双通道并行) → 实时刷新进度条",
                             bg=PANEL, fg="#6B7482", font=(FONT, 7), anchor="w")
        self.info.pack(fill="x", padx=8, pady=(2, 4))
        # 实时分析循环句柄
        self._rt_job = None
        self._closing = False
        self.llm_tok_s = 0.0
        self._tok_ema = None

    # ------------------------------------------------ 基础控制 ----------
    def draw_placeholder(self, text):
        self.video.configure(image="", text=text, fg=SUB)

    def cam_active(self):
        return self.worker is not None and self.worker.is_alive()

    def toggle(self):
        if self.cam_active():
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        if self.cam_active():
            return
        if self.rec_requested:
            self.rec_requested = False
        self.draw_placeholder("正在打开摄像头…")
        self.st_label.configure(text="打开中…", fg=WARN)
        self.worker = CameraWorker(self, self.src_var.get())
        self.worker.start()

    def stop_camera(self):
        if self.worker is not None:
            w = self.worker
            self.worker = None
            if self.rec_requested:
                self.rec_requested = False
            w.stop()
        self.recording = False
        self.rec_btn.configure(text="● 开始录制", state="disabled")
        self.ai_btn.configure(state="disabled")
        self.st_label.configure(text="已关闭", fg=SUB)
        self.rec_lab.configure(text="未在录制", fg=SUB)
        self.draw_placeholder("摄像头已关闭\n再次点击「一键打开摄像头」")

    def apply_source(self):
        self.stop_camera()
        self.start_camera()

    def on_worker_end(self):
        if self.worker is None or not self.worker.is_alive():
            self.worker = None
            self.recording = False
            self.rec_btn.configure(text="● 开始录制", state="disabled")
            self.ai_btn.configure(state="disabled")

    def on_worker_fail(self, msg):
        self.worker = None
        self.st_label.configure(text="打开失败", fg=BAD)
        self.draw_placeholder("摄像头打开失败\n%s" % msg)
        self.app.think("CAM", "⚠ 摄像头打开失败: %s" % msg)

    # ------------------------------------------------ 视频帧显示 ----------
    def tick(self):
        """由 App 每 ~70ms 调用: 显示最新预览帧。"""
        try:
            img, _n = self.fq.get_nowait()
        except Exception:
            return
        if HAVE_PIL:
            self._photo = ImageTk.PhotoImage(img)
            self.video.configure(image=self._photo, text="")

    # ------------------------------------------------ 录制控制 ----------
    def rec_toggle(self):
        if not self.cam_active():
            return
        if not self.recording and not self.rec_requested:
            self.rec_requested = True
            self.rec_btn.configure(text="◼ 停止录制", bg="#291E1E", fg="#C09B9B")
            self.rec_lab.configure(text="等待写入…", fg=WARN)
        elif self.recording:
            self.rec_requested = False
            self.rec_btn.configure(text="● 开始录制", bg="#26221C", fg="#C2B08C")
            self.rec_lab.configure(text="正在保存…", fg=WARN)
        # recording 状态由 worker 线程回调切换

    def on_record_started(self, path):
        self.recording = True
        self.rec_lab.configure(text="● 录制中: %s" % os.path.basename(path), fg=OK)
        self.st_label.configure(text="录制中", fg=OK)
        self.app.think("CAM", "🎥 开始录制学习影像 → %s" % path)

    def on_record_stopped(self, path, frames):
        self.recording = False
        self.rec_btn.configure(text="● 开始录制", bg="#26221C", fg="#C2B08C")
        self.rec_lab.configure(text="已保存 %d 帧" % frames, fg=SUB)
        self.st_label.configure(text="待开启" if not self.cam_active() else "运行中", fg=SUB)
        try:                                # 按学习日写入视频片段索引
            self.app.vault.record_day(self.app.engine, "video", {
                "文件": path, "帧数": frames, "时长秒": round(frames / 12.0, 1),
                "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        except Exception:
            pass
        self.app.think("CAM", "💾 录制完成: %s (%d帧≈%.0f秒) — 已按学习日归档至数据仓库"
                       % (path, frames, frames / 12.0))

    def open_folder(self):
        try:
            os.makedirs(CAM_DIR, exist_ok=True)
            os.startfile(CAM_DIR)
        except Exception as e:
            self.app.think("CAM", "⚠ 无法打开记录夹: %s" % e)

    # ------------------------------------------------ 双模型并行视觉分析 ----
    def ai_analyze(self):
        """单帧双模型同步分析(并行: 本地‖外部)。"""
        if self.analyzing:
            return
        if not self.cam_active():
            self.app.toast("📷 摄像头未开启", "请先点击「一键打开摄像头」, 再进行视觉分析", WARN)
            return
        self._cycle("单帧双模型分析")

    def rt_toggle(self):
        """🔄 实时双模型同步分析开关。"""
        if self.rt_var.get():
            if not self.cam_active():
                self.start_camera()
            self.app.toast("🔄 实时同步分析已开启",
                           "每 %s 秒对实时画面做一轮「本地‖外部」双模型并行分析, 结果实时刷新进度条"
                           % self.rt_iv.get(), OK)
            self.app.cfg_dirty()
        else:
            self.app.toast("🔄 实时同步分析已关闭", "", SUB)
            self.app.cfg_dirty()
        self._rt_pump()

    def _rt_pump(self):
        if not self.rt_var.get() or self._closing:
            return
        delay = 1200 if not self.cam_active() else 400
        try:
            interval = max(5, min(600, int(self.rt_iv.get()))) * 1000
        except Exception:
            interval = 15000
        self._rt_job = self.app.root.after(delay, self._rt_step)
        self._rt_interval_ms = interval

    def _rt_step(self):
        self._rt_job = None
        if not self.rt_var.get():
            return
        if self.analyzing:
            self._rt_pump()          # 上一轮仍在跑 → 稍后再来, 不重叠
            return
        if not self.cam_active():
            self._rt_pump()
            return
        self._cycle("实时轮")
        self._rt_job = self.app.root.after(self._rt_interval_ms, self._rt_step)

    def _capture_snap(self):
        if not self.cam_active():
            return None
        frame = self.last_frame
        if frame is None or not HAVE_CV2:
            return None
        if self.recording or self.rec_requested:
            self.rec_requested = False
        try:
            snap = self.app.vault.snapshot_path(self.app.engine)
        except Exception:
            os.makedirs(CAM_DIR, exist_ok=True)
            snap = os.path.join(CAM_DIR, "frame_%s.jpg"
                                % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        # imencode + tofile: 兼容中文路径, 不会像 cv2.imwrite 那样静默失败
        if imwrite_u(snap, frame):
            return snap
        return None

    def _cycle(self, tag):
        """一轮完整分析: 抓帧 → 本地‖外部两通道并行 → 合并→评分→进度条→左上角弹窗。"""
        if self.analyzing:
            return
        snap = self._capture_snap()
        if not snap:
            self.app.think("CAM", "⚠ 本轮分析无可用画面, 已跳过")
            return
        act, bri = self.last_metrics
        student = self.app.engine.persona()
        local_snap = self.app.local.build_request_snapshot() if \
            hasattr(self.app, "local") else ("", "")
        remote_snap = self.app.remote.build_request_snapshot() if \
            hasattr(self.app, "remote") else ("", "", "")
        cloud_opt = self.cloud_var.get()
        base, lmodel = local_snap
        r_url, r_key, r_model = remote_snap
        self.analyzing = True
        self.ai_btn.configure(state="disabled")
        self.info.configure(text="%s进行中: 本地‖外部 双通道并行…" % tag, fg=WARN)
        res = {"local": None, "lerr": None, "remote": None, "rerr": None,
               "score": None}
        ev_local, ev_remote = threading.Event(), threading.Event()

        # -------- 通道A: 常规学情观察(本地 Ollama 优先; 云模式下可路由云端) ----
        detected = list(getattr(self.app.local, "detected_models", []) or [])

        def chan_local():
            try:
                prompt = self._prompt_regular(snap, act, bri, student)
                t0 = now_ms()
                out = None
                used = None
                if cloud_opt == "本机优先":
                    # 本地优先: 有视觉模型则看图, 否则文本统计观察
                    vis_model = None
                    if lmodel and vision_capable(lmodel):
                        vis_model = lmodel
                    else:
                        vis_model = next((m for m in detected
                                          if vision_capable(m)), None)
                    if vis_model:
                        b64 = self._read_b64(snap)
                        out = LLMClient.ollama_chat(base, vis_model,
                                                    [{"role": "user", "content": prompt}],
                                                    image_b64=b64, timeout=300)
                        used = "本地视觉模型:%s" % vis_model
                    elif lmodel:
                        out = LLMClient.ollama_chat(base, lmodel,
                                                    [{"role": "user", "content": prompt}],
                                                    timeout=300)
                        used = "本地文本模型:%s" % lmodel
                    elif detected:
                        out = LLMClient.ollama_chat(base, detected[0],
                                                    [{"role": "user", "content": prompt}],
                                                    timeout=300)
                        used = "本地文本模型:%s" % detected[0]
                elif r_url and r_key and r_model:
                    # 云算力模式: 常规观察走云端(文本, 轻量)
                    out = LLMClient.remote_chat(r_url, r_key, r_model,
                                                [{"role": "user", "content": prompt}],
                                                timeout=300)
                    used = "云算力文本:%s" % r_model
                if out:
                    res["local"] = (out or "").strip()
                    dur = now_ms() - t0
                    tok = est_tokens(res["local"])
                    inst = tok / max(1.0, dur) * 1000.0
                    self._tok_ema = inst if self._tok_ema is None \
                        else self._tok_ema * 0.6 + inst * 0.4
                    self.llm_tok_s = self._tok_ema
                    if used:
                        self.app.push_ui(lambda u=used: self.app.think(
                            "CAM", "🧠 常规观察通道: %s (%.1f token/s)"
                            % (u, self._tok_ema)))
                else:
                    res["lerr"] = "本机模型未连接且未配置云算力 → 常规通道跳过"
            except Exception as e:
                res["lerr"] = str(e)
            finally:
                ev_local.set()

        # -------- 通道B: 外部大模型 · 加强评估与打分(与通道A并行) ----------
        def chan_remote():
            try:
                if not (r_url and r_key and r_model):
                    res["rerr"] = "外部API未配置(②区: 地址/密钥/模型) → 加强评分跳过"
                    return
                prompt = self._prompt_score(snap, act, bri, student)
                if vision_capable(r_model):
                    b64 = self._read_b64(snap)
                    out = LLMClient.remote_chat_vision(r_url, r_key, r_model,
                                                       prompt, b64, timeout=300)
                else:
                    out = LLMClient.remote_chat(r_url, r_key, r_model,
                                                [{"role": "user", "content": prompt}],
                                                timeout=300)
                res["remote"] = (out or "").strip()
                res["score"] = self._parse_score(res["remote"])
            except Exception as e:
                res["rerr"] = str(e)
            finally:
                ev_remote.set()

        def merger():
            threading.Thread(target=chan_local, daemon=True).start()
            threading.Thread(target=chan_remote, daemon=True).start()
            ev_local.wait()
            ev_remote.wait()
            self._integrate(tag, snap, act, bri, student, res, cloud_opt)

        self.app.go_thread(merger)

    # -------- 提示词 ----
    def _prompt_regular(self, snap, act, bri, student):
        return ("你是「AI学生」系统的视觉学情观察员(常规分析通道)。学习画面统计:\n"
                "- 画面活跃度 %.0f%%(动作幅度) | 亮度 %.0f%%\n- 抓帧: %s\n学生: %s | %s\n\n"
                "输出『常规学情观察结论』: 当下状态(专注/困倦/分心/正常) + 下一步引导"
                "(≤150字, 中文, 不编造画面细节)。"
                % (act * 100, bri * 100, os.path.basename(snap),
                   student["student"], student["state"]))

    def _prompt_score(self, snap, act, bri, student):
        return ("你是教育评估专家(加强评分通道, 与常规观察通道并行)。对这名学生的本次学习状态"
                "做加强评估打分:\n- 活跃度 %.0f%% | 亮度 %.0f%%\n- 学生: %s\n\n"
                "输出格式(严格遵守):\n专注评分: 0-100整数\n状态等级: 高度专注/基本专注/轻度分心/"
                "明显走神/疲劳困倦\n一句话建议: ≤40字"
                % (act * 100, bri * 100, student["student"]))

    @staticmethod
    def _read_b64(snap):
        import base64
        with open(snap, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")

    # -------- 结果合并: 双通道→评分→进度条→左上角弹窗 --------
    def _integrate(self, tag, snap, act, bri, student, res, cloud_opt):
        app = self.app
        local_txt, remote_txt = res["local"], res["remote"]
        score = res["score"]
        # 日志分流到两个对话分区 + 思考区
        if local_txt:
            app.push_ui(lambda: app.local.log.add("ai", "【视觉·常规观察·本地】\n" + local_txt))
        if remote_txt:
            app.push_ui(lambda: app.remote.log.add("ai", "【视觉·加强评分·外部】\n" + remote_txt[:900]))
        if res["lerr"]:
            app.push_ui(lambda: app.think("CAM", "⏭ [常规通道] %s" % res["lerr"]))
        if res["rerr"]:
            app.push_ui(lambda: app.think("CAM", "⏭ [评分通道] %s" % res["rerr"]))
        if local_txt:
            app.push_ui(lambda: app.think("CAM", "🧠 常规观察(本地): %s" % local_txt[:300]))
        if remote_txt:
            app.push_ui(lambda: app.think("CAM", "🎯 加强评分(外部): %s" % remote_txt[:300]))
        # 本地算力实测记录(评估用)
        self._save_analysis_log(snap, act, bri, local_txt, remote_txt, score)
        # 整合驱动进度条
        def done():
            note = self._apply_score_ui(score, remote_txt or local_txt)
            self.analyzing = False
            st = "正常" if self.cam_active() else "已关闭"
            self.ai_btn.configure(state="normal" if self.cam_active() else "disabled")
            self.info.configure(text="%s完成 ✓ 评分已整合 | 摄像头:%s" % (tag, st), fg=OK)
            title = "🎯 %s完成 · 加强评分 %s" % (tag, ("%d分" % score) if score is not None else "N/A")
            body = note
            if local_txt:
                body += "\n常规观察: " + local_txt[:80] + ("…" if len(local_txt) > 80 else "")
            self.app.toast(title, body, VIOLET if score else ACC, 6)
            if self.llm_tok_s and self.llm_tok_s < 6.0:
                self.app.toast("⚡ 本机算力偏弱", "本地实测约 %.1f token/s。建议点「⚡本机算力评估」查看结论, 或切换 ☁ 阿里云算力模式增强视觉分析" % self.llm_tok_s, WARN, 9)
        app.push_ui(done)

    def _apply_score_ui(self, score, text):
        """评分/观察 → 学生状态与进度条联动(主线程)。"""
        app = self.app
        eng = app.engine
        st = eng.student
        if score is None:
            st.attention = clamp(st.attention + 0.01)
            note = "常规观察驱动: 注意力校准 +1%, 成长进度保持平稳"
        else:
            st.attention = clamp(st.attention * 0.5 + score / 100.0 * 0.5)
            st.retention = clamp(st.retention * 0.6 + score / 100.0 * 0.4, 0.5, 1.0)
            if score >= 70:
                g = (score - 70) / 30.0 * 0.004
                for k in DIM_KEYS:
                    st.dims[k] = min(1.0, st.dims[k] + g * (1.0 - st.dims[k]))
                note = ("评分 %d分(≥70) → 专注/保持上调, 认知微量生长+%.3f, 学生进度条已实时推进"
                        % (score, g))
            elif score < 45:
                st.fatigue = min(1.0, st.fatigue + 0.03)
                note = ("评分 %d分(<45) → 疑似疲劳/走神, 疲劳度上调; 建议休息或切换学习状态"
                        % score)
            else:
                note = "评分 %d分 → 学情平稳, 维持当前学习路径" % score
        eng.emit("GOAL", "🎯 %s" % note)
        app.engine_ui_refresh()
        return note

    def _parse_score(self, text):
        import re as _re
        m = _re.search(r"[评分|评分[:：\s]*]?\s*(\d{1,3})\s*分", text)
        if not m:
            m = _re.search(r"(?<!\d)(\d{1,3})(?!\d)\s*分", text)
        if not m:
            m = _re.search(r"score[^0-9]{0,6}(\d{1,3})", text, _re.I)
        if m:
            try:
                s = int(m.group(1))
                if 0 <= s <= 100:
                    return s
            except Exception:
                pass
        return None

    def _apply_score(self, score, text):
        """(保留的简单版本, 主流程已改用 _apply_score_ui)"""
        return self._apply_score_ui(score, text)

    def _save_analysis_log(self, snap, act, bri, local_text, ext_text, score):
        try:
            eng = self.app.engine
            folder = self.app.vault.day_dir(eng, "分析")
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            p = os.path.join(folder, "分析结果_%s.txt" % ts)
            with open(p, "w", encoding="utf-8") as f:
                f.write("时间: %s | 学生: %s\n" % (datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"), eng.student_name))
                f.write("学习日: %s | 抓帧: %s | 活跃度%.0f%% 亮度%.0f%%\n"
                        % (day_label(abs_day_of(eng)), os.path.basename(snap),
                           act * 100, bri * 100))
                f.write("【本地·常规观察】\n%s\n" % (local_text or "(未执行)"))
                f.write("【外部·加强评分】\n%s\n" % (ext_text or "(未执行)"))
                f.write("综合评分: %s\n" % (score if score is not None else "N/A"))
            self.app.vault.record_day(eng, "analysis", {
                "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "抓帧": snap, "结果文件": p,
                "活跃度": round(act, 3), "亮度": round(bri, 3),
                "本地常规观察": (local_text or "")[:2000],
                "外部加强评分": (ext_text or "")[:2000],
                "综合评分": score})
        except Exception:
            pass

    def _analysis_done(self):
        self.analyzing = False
        self.ai_btn.configure(state="normal" if self.cam_active() else "disabled")
        self.info.configure(text="分析完成 ✓ 评分已整合, 成长进度条已更新",
                            fg=OK)

    # ============================================ 云算力 / 本机算力评估 ======
    BAILIAN_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    BAILIAN_MODEL = "qwen-vl-plus"

    def cloud_selected(self, _e=None):
        mode = self.cloud_var.get()
        app = self.app
        app.cfg_dirty()
        if mode == "阿里云百炼·视觉":
            app.remote.url_var.set(self.BAILIAN_URL)
            app.remote.m_var.set(self.BAILIAN_MODEL)
            try:
                app.remote.preset_var.set("通义千问(阿里)")
            except Exception:
                pass
            app.toast("☁ 阿里云百炼 · 云端算力已接管视觉通道",
                      "接口已切至 DashScope(qwen-vl-plus)。请在②外部API区粘贴「阿里云百炼API-Key」"
                      "并点「测试连接」; 实时分析将自动改用云端视觉大模型(本地通道继续并行)", ACC, 10)
            app.think("CAM", "☁ 算力模式→阿里云百炼: 视觉加强评分走 qwen-vl-plus; "
                             "请确保②区密钥为百炼API-Key")
        elif mode == "阿里云EAS·自定义":
            app.toast("☁ 阿里云EAS 自定义端点模式",
                      "在②外部API区填写: 接口地址=EAS调用地址(https://…aliyuncs.com/api/predict/…) "
                      "或兼容OpenAI的 /v1 地址; 密钥=EAS Token; 模型=EAS部署的模型名", ACC, 10)
            app.think("CAM", "☁ 算力模式→阿里云EAS: 请在②区配置自定义推理端点")
        else:
            app.toast("💻 算力模式→本机优先", "常规观察优先使用本地 Ollama, "
                      "外部通道仍做加强评分; 本地不足时可点「⚡本机算力评估」获得结论", ACC, 7)
            app.think("CAM", "☁ 算力模式→本机优先: 本地模型常规观察 ‖ 外部模型加强评分")

    # ------------------------------------------------ 本机算力评估 ----
    def assess_local(self):
        if self.analyzing:
            return
        self.assess_btn.configure(state="disabled")
        self.app.go_thread(self._assess_worker)

    def _assess_worker(self):
        app = self.app
        out_lines = []
        cpu = os.cpu_count() or 0
        ram_gb = 0
        gpu_name, vram_gb = None, 0
        try:                                        # RAM
            import ctypes as _c
            from ctypes import wintypes

            class _M(_c.Structure):
                _fields_ = [("dwLength", wintypes.DWORD),
                            ("dwMemoryLoad", wintypes.DWORD),
                            ("ullTotalPhys", _c.c_ulonglong),
                            ("ullAvailPhys", _c.c_ulonglong),
                            ("ullTotalPageFile", _c.c_ulonglong),
                            ("ullAvailPageFile", _c.c_ulonglong),
                            ("ullTotalVirtual", _c.c_ulonglong),
                            ("ullAvailVirtual", _c.c_ulonglong),
                            ("ullAvailExtendedVirtual", _c.c_ulonglong)]
            m = _M()
            m.dwLength = _c.sizeof(_M)
            if _c.windll.kernel32.GlobalMemoryStatusEx(_c.byref(m)):
                ram_gb = m.ullTotalPhys // (1024 ** 3)
        except Exception:
            pass
        try:                                        # NVIDIA GPU
            r = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total",
                 "--format=csv,noheader"],
                capture_output=True, text=True, timeout=6,
                creationflags=0x08000000)
            if r.returncode == 0 and r.stdout.strip():
                gpu_name = r.stdout.strip().splitlines()[0].split(",")[0].strip()
                try:
                    vram_gb = float(r.stdout.strip().splitlines()[0].split(",")[1]
                                    .replace("MiB", "").strip()) / 1024.0
                except Exception:
                    vram_gb = 0.0
        except Exception:
            pass
        # 评分
        pts = 0
        if cpu >= 8:
            pts += 1
        if ram_gb >= 16:
            pts += 1
        if vram_gb >= 8:
            pts += 2
        elif vram_gb >= 4:
            pts += 1
        if pts >= 3 and vram_gb >= 4:
            tier = "A"
        elif pts >= 2:
            tier = "B"
        else:
            tier = "C"
        advice = {
            "A": "本机算力充足: 本地可流畅运行 7B~14B 文本模型, 亦可尝试轻量视觉模型(llava/qwen2.5vl)。",
            "B": "本机算力中等: 本地适合 ≤7B 文本模型的常规观察; 视觉理解/大模型加强评分建议由外部或阿里云算力承担。",
            "C": "本机算力紧张: 本地仅适合轻量文本任务。建议开启「阿里云百炼·视觉」或EAS端点, 由云端GPU完成视觉分析。",
        }[tier]
        out_lines.append("CPU 核数: %d | 内存: %d GB" % (cpu, ram_gb))
        out_lines.append("GPU: %s (%d GB VRAM)" % (gpu_name or "未检测到NVIDIA独显", vram_gb))
        out_lines.append("本地模型: %s | 实测吞吐: %.1f token/s"
                         % (", ".join(app.local.detected_models[:4]) or "未连接Ollama",
                            self.llm_tok_s))
        out_lines.append("算力等级: %s | %s" % (tier, advice))
        title = "⚡ 本机算力评估 · 等级%s" % tier
        body = "\n".join(out_lines)

        def done():
            self.assess_btn.configure(state="normal")
            app.think("CAM", "⚡ 本机算力评估:\n" + body)
            color = OK if tier == "A" else (WARN if tier == "B" else BAD)
            app.toast(title, body, color, 14)
            if tier in ("B", "C"):
                app.toast("☁ 建议借用阿里云算力", "点右上角摄像头「算力」下拉框 → 阿里云百炼·视觉, "
                          "粘贴百炼API-Key后, 视觉加强评分即由云端GPU执行", ACC, 14)
        app.push_ui(done)

    # ------------------------------------------------ 视频上传分析 ----
    def analyze_video_file(self, path, busy_hint="📁 视频上传分析"):
        """上传本地视频 → 采样多帧 → 本地‖外部双模型并行分析 → 生成AI学生档案。"""
        if self.analyzing:
            self.app.toast(busy_hint, "上一轮分析仍在进行, 请稍候", WARN, 5)
            return
        if not HAVE_CV2:
            self.app.toast(busy_hint, "缺少 OpenCV 组件, 无法读取视频", BAD, 6)
            return
        self.analyzing = True
        self.info.configure(text="%s: 采样帧+双模型并行分析…" % busy_hint, fg=WARN)
        # ★ 配置快照必须在主线程取: tk 变量不可跨线程读, 否则子线程会抛
        #   RuntimeError("main thread is not in main loop") 而静默死掉。
        try:
            base, lmodel = self.app.local.build_request_snapshot()
        except Exception:
            base, lmodel = LOCAL_DEFAULT, LOCAL_MODEL_DEFAULT
        try:
            r_url, r_key, r_model = self.app.remote.build_request_snapshot()
        except Exception:
            r_url, r_key, r_model = "", "", ""
        cfg = {"local_base": base, "local_model": lmodel,
               "remote_url": r_url, "remote_key": r_key,
               "remote_model": r_model}

        def on_stage(msg):              # 状态栏: 采样中→本地模型→外部API→档案
            self.app.push_ui(lambda: self.info.configure(
                text="%s: %s" % (busy_hint, msg), fg=WARN))

        def log(kind, msg):             # 思考区是 tk 控件 → 必须回主线程写
            self.app.push_ui(lambda: self.app.think(kind, msg))

        def work():
            res = run_video_analysis(path, cfg=cfg, on_stage=on_stage, log=log)
            ok = bool(res.get("ok"))
            self.app.push_ui(lambda: self.app.status_set(
                ACC if ok else BAD, "视频分析: %s" % ("完成" if ok else "失败")))
            if ok:
                folder = res.get("folder")
                info = res.get("info") or {}
                self.app.push_ui(lambda: self._video_done(folder, info, res))
            else:
                err = res.get("error") or "未知错误"
                self.app.push_ui(lambda: self._video_fail(err))

        self.app.go_thread(work)

    def _video_done(self, folder, info, res):
        self.analyzing = False
        self.info.configure(text="视频分析完成 ✓ AI学生档案已生成", fg=OK)
        score = res.get("score")
        self._apply_score_ui(score, (res.get("remote") or "") + (res.get("local") or ""))
        if res.get("local"):
            self.app.think("CAM", "📁 视频常规观察: %s" % res["local"][:220])
        if res.get("remote"):
            self.app.think("CAM", "🎯 视频加强评分: %s" % res["remote"][:220])
        self.app.toast("📁 AI学生档案已生成",
                       "「%s」(%.0f秒) 双模型分析完成%s\n档案: %s\n(评分已实时驱动进度条)"
                       % (info["文件"], info["时长秒"],
                          (" · 评分%d分" % score) if score is not None else "",
                          folder), VIOLET, 12)
        self.app.think("SYS", "📁 视频档案目录: %s (含 Word/Markdown/JSON/采样帧/蒙太奇)" % folder)

    def _video_fail(self, msg):
        self.analyzing = False
        self.info.configure(text="视频分析失败", fg=BAD)
        self.app.toast("📁 视频分析失败", msg[:240], BAD, 10)
        self.app.think("CAM", "⚠ 视频上传分析失败: %s" % msg)

    def close(self):
        self._closing = True
        if self._rt_job is not None:
            try:
                self.app.root.after_cancel(self._rt_job)
            except Exception:
                pass
            self._rt_job = None
        self.stop_camera()

STATE_OPTS = ["专注探究", "巩固练习", "反思总结", "困惑求助", "劳逸结合"]
STATE_EFFECT = {"专注探究": 0.05, "巩固练习": 0.0, "反思总结": -0.02,
                "困惑求助": -0.06, "劳逸结合": 0.03}


class TopInfoBar(tk.Frame):
    """顶部学生信息: 姓名/年级/学习状态/榜样模型 + 实时状态徽章。"""

    def __init__(self, master, app):
        super().__init__(master, bg=PANEL, highlightbackground=EDGE,
                         highlightthickness=1)
        self.app = app
        eng = app.engine
        # ---- 标题行 ----
        r0 = tk.Frame(self, bg=PANEL)
        r0.pack(fill="x", padx=12, pady=(8, 2))
        tk.Label(r0, text="🎓 AI学生 · 教育预测引擎", bg=PANEL, fg=TXT,
                 font=(FONT, 13, "bold")).pack(side="left")
        tk.Label(r0, text="专利思想: 起点=学生学情 | 终点=榜样知识库 | MCTS路径 | 双时间轴",
                 bg=PANEL, fg=SUB, font=(FONT, 8)).pack(side="left", padx=12)
        tk.Label(r0, text=datetime.datetime.now().strftime("%Y-%m-%d"),
                 bg=PANEL, fg=SUB, font=(FONT, 8)).pack(side="right")
        tk.Button(r0, text="💾 保存设置", command=app.save_cfg, bg=PANEL2,
                  fg=ACC, relief="flat", font=(FONT, 8), cursor="hand2"
                  ).pack(side="right", padx=4)
        # ---- 信息编辑行 ----
        r1 = tk.Frame(self, bg=PANEL)
        r1.pack(fill="x", padx=12, pady=2)
        for lab, w in (("👦 姓名:", 1), ("📚 年级:", 2), ("💪 学习状态:", 3),
                       ("🏆 榜样模型:", 4)):
            tk.Label(r1, text=lab, bg=PANEL, fg=SUB, font=(FONT, 9)).pack(side="left")
            if w == 1:
                self.name_var = tk.StringVar(value=eng.student_name)
                ent = tk.Entry(r1, textvariable=self.name_var, width=8,
                               bg="#0E131B", fg=TXT, relief="flat",
                               font=(FONT, 9), insertbackground=ACC)
                ent.pack(side="left", padx=(2, 10), ipady=2)
                self.name_var.trace_add("write", lambda *a: self.on_name())
            elif w == 2:
                self.grade_var = tk.StringVar(value=GRADES[eng.grade_idx])
                cb = ttk.Combobox(r1, textvariable=self.grade_var, width=10,
                                  values=GRADES, state="readonly",
                                  font=(FONT, 9))
                cb.pack(side="left", padx=(2, 10))
                cb.bind("<<ComboboxSelected>>", self.on_grade)
            elif w == 3:
                self.state_var = tk.StringVar(value=eng.learn_state)
                cb = ttk.Combobox(r1, textvariable=self.state_var, width=9,
                                  values=STATE_OPTS, state="readonly",
                                  font=(FONT, 9))
                cb.pack(side="left", padx=(2, 10))
                cb.bind("<<ComboboxSelected>>", self.on_state)
            else:
                self.role_keys = list(ROLE_MODELS.keys())
                self.role_var = tk.StringVar(
                    value="%s %s" % (ROLE_MODELS[eng.role_key]["emoji"],
                                     ROLE_MODELS[eng.role_key]["label"]))
                cb = ttk.Combobox(r1, textvariable=self.role_var,
                                  width=17,
                                  values=["%s %s" % (ROLE_MODELS[k]["emoji"],
                                                     ROLE_MODELS[k]["label"])
                                          for k in self.role_keys],
                                  state="readonly", font=(FONT, 9))
                cb.pack(side="left", padx=(2, 4))
                cb.bind("<<ComboboxSelected>>", self.on_role)
        # ---- 徽章行 ----
        self.chips = {}
        r2 = tk.Frame(self, bg=PANEL)
        r2.pack(fill="x", padx=12, pady=(2, 0))
        for key in ("age", "grade", "stage", "score", "equiv", "gap",
                    "fatigue", "attention", "remain", "topic"):
            lab = tk.Label(r2, bg=CHIP_BG, fg=SUB, font=(FONT, 8), padx=8,
                           pady=2, anchor="center")
            lab.pack(side="left", padx=(0, 6))
            self.chips[key] = lab
        # ---- 任务/里程碑行 ----
        r3 = tk.Frame(self, bg=PANEL)
        r3.pack(fill="x", padx=12, pady=(3, 8))
        self.task_lab = tk.Label(r3, text="", bg=PANEL, fg=WARN,
                                 font=(FONT, 8), anchor="w")
        self.task_lab.pack(side="left", fill="x", expand=True)

    # ---- 事件 ----
    def on_name(self):
        v = self.name_var.get().strip() or "小原"
        self.app.engine.student_name = v
        self.app.cfg_dirty()

    def on_grade(self, _e=None):
        idx = GRADES.index(self.grade_var.get())
        eng = self.app.engine
        old = eng.grade_idx
        eng.grade_idx = idx
        eng.sim_day = min(eng.sim_day, eng.allowed_exec)
        eng._finished_announced = False
        eng.emit("STATUS", "📊 学情校准: 年级 %s→%s (起点=%s, 可执行学习日%d, 剩余%d天)"
                 % (GRADES[old], GRADES[idx], age_str(eng.base_days),
                    eng.allowed_exec, eng.remain_days))
        self.app.cfg_dirty()

    def on_state(self, _e=None):
        eng = self.app.engine
        v = self.state_var.get()
        old = eng.learn_state
        eng.learn_state = v
        d = STATE_EFFECT.get(v, 0.0)
        if d:
            eng.student.attention = clamp(eng.student.attention + d)
            eng.emit("SENSE", "👁 学习状态: %s→%s, 注意力%s%.0f%%(视觉分析基准同步更新)"
                     % (old, v, "+" if d >= 0 else "", d * 100))
        self.app.cfg_dirty()

    def on_role(self, _e=None):
        eng = self.app.engine
        val = self.role_var.get()
        for k in self.role_keys:
            r = ROLE_MODELS[k]
            if val.startswith(r["emoji"]):
                eng.role_key = k
                break
        eng.emit("GOAL", "🎯 榜样模型切换: 终点 = %s | %s" % (eng.role()["label"],
                                                            eng.role()["desc"]))
        self.app.cfg_dirty()

    # ---- 刷新徽章(每秒多次, 只改文本) ----
    def refresh(self):
        eng = self.app.engine
        equiv_day, gap, score, ideal = eng.dual_timeline()
        st, col = eng.gap_status()
        ch = self.chips
        ch["age"].configure(text="📅 %s" % age_str(eng.real_day))
        ch["grade"].configure(text="📚 %s" % eng.grade_label())
        ch["stage"].configure(text="%s %s" % (eng.stage()[1], eng.stage()[0]))
        ch["score"].configure(text="⭐ 成长分 %.2f/5" % score, fg=ACC)
        ch["equiv"].configure(text="🏁 等效榜样 %s" % age_str(equiv_day), fg=VIOLET)
        ch["gap"].configure(text="%s %d天" % (st, abs(gap)), fg=col)
        ch["fatigue"].configure(text="😴 疲劳 %.0f%%" % (eng.student.fatigue * 100),
                                fg=WARN if eng.student.fatigue > 0.6 else SUB)
        ch["attention"].configure(text="👀 专注 %.0f%%" % (eng.student.attention * 100),
                                  fg=OK if eng.student.attention > 0.6 else SUB)
        ch["remain"].configure(text="⏳ 剩%d天" % eng.remain_days)
        ch["topic"].configure(text="📖 %s" % eng.topic_hint_text())
        self.task_lab.configure(text="🎯 当前任务: 掌握「%s」· 榜样里程碑: %s"
                                % (eng.current_topic()[1], eng.milestone_note(eng.real_day)))

# ==================================================== 左上角信息弹窗 =========

class Toaster:
    """窗口左上角弹出的通知卡片(清爽无边框堆叠, 自动消失)。"""

    MAX_CARDS = 4

    def __init__(self, root, y_provider):
        self.root = root
        self.y_provider = y_provider
        self.cards = []          # 每项: (frame, expire_job)
        self.frame = tk.Frame(root, bg=BG)
        self.frame.place(x=14, y=10)

    def show(self, title, body, color=ACC, ttl=7):
        card = tk.Frame(self.frame, bg=PANEL, highlightbackground=EDGE,
                        highlightthickness=1)
        tk.Canvas(card, width=8, height=10, bg=PANEL, highlightthickness=0) \
            .pack(side="left", padx=(8, 2), pady=6)
        tk.Label(card, text=title, bg=PANEL, fg=color,
                 font=(FONT, 9, "bold")).pack(side="top", anchor="w",
                                              padx=(2, 10), pady=(6, 0))
        if body:
            tk.Label(card, text=body, bg=PANEL, fg=TXT, justify="left",
                     wraplength=430, font=(FONT, 8), anchor="w").pack(
                side="top", anchor="w", padx=(10, 10), pady=(1, 6))
        job = self.root.after(int(ttl * 1000), lambda: self.dismiss(card))
        self.cards.append((card, job))
        self._rebuild()

    def dismiss(self, card):
        for c, j in self.cards:
            if c is card:
                try:
                    self.root.after_cancel(j)
                except Exception:
                    pass
                self.cards.remove((c, j))
                break
        self._rebuild()

    def _rebuild(self):
        for c, _j in self.cards:
            c.pack_forget()
        y = int(self.y_provider()) + 10 if self.y_provider else 10
        self.frame.place(x=14, y=y)
        for c, _j in list(reversed(self.cards[-self.MAX_CARDS:])):
            c.pack(side="top", fill="x", pady=(0, 6))
        self.frame.lift()
        if not self.cards:
            self.frame.place_forget()


# ==================================================== 新手引导动画 ===========

class GuideOverlay(tk.Canvas):
    """全屏引导层: 聚光灯高亮目标控件 + 呼吸边框动画 + 分步解说卡片, 自动播放。"""

    def __init__(self, app):
        super().__init__(app.root, bg="#0A0C10", highlightthickness=0,
                         cursor="hand2")
        self.app = app
        self.steps = self._build_steps()
        self.idx = 0
        self._job = None
        self._pulse = 0
        self.visible = False
        self._nav_done = False
        app.root.bind("<Configure>", lambda e: self._redraw())

    def _build_steps(self):
        a = self.app
        return [
            (a.btn_cam, "📷 摄像头 · 一键打开",
             "程序启动会自动打开本机摄像头(源=0)。此按钮一键开/关;\n画面、录制与实时双模型分析在「摄像头窗口」(菜单→摄像头)。"),
            (a.btn_rec, "● 录制学习视频",
             "一键开始/停止录制。视频自动按「学习日+时间戳」命名,\n存入数据仓库 影像/ 目录, 与当日档案联动。"),
            (a.btn_api, "🔑 API密钥 · 模型设置",
             "打开设置窗口: 填外部大模型API密钥(DeepSeek/阿里云百炼/\nOpenAI…)并测试连接; 本地Ollama启动时自动探测(默认 deepseek-r1:7b)。"),
            (a.btn_up, "📁 上传视频 → AI学生档案",
             "选择本地视频(mp4/avi/mov…), 采样多帧后由 本地‖外部 两个大模型\n并行分析画面, 生成AI学生档案(Word/Markdown/JSON), 评分实时驱动进度条。"),
            (a.btn_chat, "💬 双模型对话",
             "打开对话窗口: 左侧本地Ollama, 右侧外部大模型API;\n提问后, 思考区同步展示AI学生的思维链。"),
            (a.btn_arch, "📚 4380天档案",
             "一键把6-18岁4380天逐日生成 Word+Markdown+JSON 档案与训练语料\n(jsonl), 供大模型训练; 程序启动会回读档案并自我进化。"),
            (a.progress, "🎯 成长进度区",
             "双时间轴进度条: 榜样同龄完成度 vs 学生综合成长;\n下方: 五类教学动作打卡 · MCTS规划并执行 · 自动领航 · 压缩模拟\n(数秒跑完4380天) · S曲线展示成长轨迹与等效年龄。"),
            (a.thinkzone, "🧠 思考区",
             "AI学生思维链全程可视化: 感知→榜样比对→路径规划(MCTS)→\n教学决策→纠偏; 重要通知在左上角弹出, 约7秒自动消失。"),
            (None, "📦 数据仓库 · 0-100岁目标",
             "所有数据按天存放于 %s\n训练语料可直接喂大模型; 每次启动回读档案 → 经验回放+\n数据驱动权重 = 越用越聪明。最终目标: 0-100岁 ai数据学生。" % CAM_DIR),
        ]

    def restart(self, auto=False):
        self.idx = 0
        self.visible = True
        self.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Misc.tkraise(self)
        self._redraw()
        self._schedule()

    def _target_box(self):
        w = self.steps[self.idx][0]
        if w is None or not w.winfo_exists() or not w.winfo_ismapped():
            return None
        try:
            x0 = w.winfo_rootx() - self.app.root.winfo_rootx()
            y0 = w.winfo_rooty() - self.app.root.winfo_rooty()
            return (x0 - 8, y0 - 8, x0 + w.winfo_width() + 8,
                    y0 + w.winfo_height() + 8)
        except Exception:
            return None

    def _redraw(self):
        if not self.visible:
            return
        self.delete("draw")
        w = self.winfo_width() or self.app.root.winfo_width()
        h = self.winfo_height() or self.app.root.winfo_height()
        if w < 10 or h < 10:
            return
        box = self._target_box()
        # 半透明压暗(四块遮罩围出聚光区)
        fill = "#0A0C10"
        if box:
            x0, y0, x1, y1 = box
            for rect in ((0, 0, w, y0), (0, y1, w, h), (0, y0, x0, y1),
                         (x1, y0, w, y1)):
                self.create_rectangle(*rect, fill=fill, stipple="gray50",
                                      outline="", tags="draw")
            col = ACC if self._pulse % 2 == 0 else VIOLET
            self.create_rectangle(x0, y0, x1, y1, outline=col, width=3,
                                  tags="draw")
        else:
            self.create_rectangle(0, 0, w, h, fill=fill, stipple="gray50",
                                  outline="", tags="draw")
        # 解说卡片
        title, desc = self.steps[self.idx][1], self.steps[self.idx][2]
        lines = desc.split("\n")
        cw = min(680, w - 60)
        lh = 17
        card_h = 66 + lh * len(lines)
        cx, cy = w / 2.0, h - card_h - 70
        RoundedRect.rect(self, cx - cw / 2, cy, cx + cw / 2, cy + card_h, 10,
                         fill=PANEL, outline=ACC, width=2, tags="draw")
        self.create_text(cx, cy + 24, text="%d / %d · %s"
                         % (self.idx + 1, len(self.steps), title),
                         fill=ACC, font=(FONT, 11, "bold"), tags="draw")
        for i, ln in enumerate(lines):
            self.create_text(cx, cy + 52 + i * lh, text=ln, fill=TXT,
                             font=(FONT, 9), anchor="n", justify="center",
                             tags="draw")
        # 导航按钮(只创建一次, 不参与重绘删除, 避免销毁挂起事件崩溃)
        if not self._nav_done:
            self.create_window(cx - 160, cy + card_h + 22, tags="nav",
                               window=self._mk_btn("← 上一步", self.prev))
            self.create_window(cx, cy + card_h + 22, tags="nav",
                               window=self._mk_btn("下一步 →", self.next))
            self.create_window(cx + 160, cy + card_h + 22, tags="nav",
                               window=self._mk_btn("跳过引导 ✕", self.skip))
            self._nav_done = True

    def _mk_btn(self, text, cmd):
        b = tk.Button(self, text=text, command=cmd, bg=PANEL2, fg=TXT,
                      relief="flat", font=(FONT, 9, "bold"), cursor="hand2",
                      padx=10, pady=2)
        return b

    def _schedule(self):
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
        self._job = self.after(7000, self.next)
        self._pulse += 1
        self.after(450, self._pulse_tick)

    def _pulse_tick(self):
        if self.visible:
            self._redraw()
            self.after(450, self._pulse_tick)

    def prev(self):
        self.idx = max(0, self.idx - 1)
        self._redraw()
        self._schedule()

    def next(self):
        if self.idx >= len(self.steps) - 1:
            self.skip()
            return
        self.idx += 1
        self._redraw()
        self._schedule()

    def skip(self):
        self.visible = False
        try:
            self.place_forget()
        except Exception:
            pass
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        try:
            self.app.cfg["guide_done"] = 1
            self.app.cfg_dirty()
        except Exception:
            pass
        self.app.toast("🎬 引导完成", "菜单「帮助→新手引导动画」可随时再看一遍; "
                       "「帮助→使用文档」查看完整图文说明", ACC, 7)


# ==================================================== 使用文档生成 ===========

def write_usage_doc(vault):
    """生成图文使用文档(Markdown + Word), 返回 docx 路径。"""
    try:
        vault.ensure()
        md_p = os.path.join(vault.root, "使用文档.md")
        doc_p = os.path.join(vault.root, "使用文档.docx")
        sections = [
            ("一、快速开始", [
                "双击 ai学生.exe 启动。程序会自动: ①探测本地Ollama大模型(默认 deepseek-r1:7b) ②打开本机摄像头 ③回读数据仓库档案并自我进化。",
                "界面: 顶部=菜单栏+工具栏(功能集成), 下方仅保留「思考区」与「成长进度区」两处核心信息, 其余功能收纳在三个窗口: 摄像头窗口 / 双模型对话 / API设置。"]),
            ("二、顶栏与菜单(功能总入口)", [
                "工具栏按钮: 📷摄像头一键打开 · ●录制 · 🔑API密钥 · 📁上传视频 · 💬双模型对话 · 📚4380天档案 · 🎬引导。",
                "顶栏右侧: 学生信息(姓名/年级/学习状态/榜样模型), 修改即生效并自动保存。",
                "菜单栏: 文件(保存/导出思考日志/打开数据仓库/退出) · 学生(重置进度) · 模型(API设置/探测/测试) · 摄像头(窗口/开录/实时分析/算力评估/算力通道) · 数据(上传视频/生成档案/使用文档) · 帮助(引导动画/使用文档/关于)。"]),
            ("三、摄像头(一键打开)", [
                "点「📷一键打开摄像头」或菜单 摄像头→一键打开; 启动时也会自动打开(源=0)。",
                "外接摄像头: 在摄像头窗口把「源」改为 1/2… 后点应用; 网络摄像头填 RTSP/HTTP 地址。",
                "录制: 点「●录制」再点一次停止; 视频自动按「学习日+时间戳」命名, 存入数据仓库 影像/ 目录。",
                "实时双模型同步分析: 摄像头窗口勾选「🔄实时双模型同步分析」并设周期(默认15秒), 每轮 本地‖外部 两通道并行, 评分实时驱动进度条, 结果在左上角弹窗。",
                "打不开摄像头时, 按画面提示检查: Windows隐私设置允许桌面应用、关闭占用摄像头的程序、换源; 点「⚡本机算力评估」可得硬件等级与建议。"]),
            ("四、API密钥与模型设置", [
                "菜单 模型→🔑API密钥/模型设置 打开设置窗口: 本地Ollama地址/模型 + 探测; 外部API预设(DeepSeek/OpenAI/Kimi/通义/智谱)填地址/密钥/模型后点测试连接。",
                "阿里云百炼(视觉加强评分): 点「🔑API密钥」→「☁ 百炼·视觉 qwen-vl-plus」一键填好地址与模型 → 粘贴百炼API-Key →「🖼 测试视觉」验证; 摄像头窗口「☁算力」选 阿里云百炼·视觉 亦可。",
                "阿里云EAS: 选 阿里云EAS·自定义, 在API设置填 EAS调用地址/EAS Token/模型名。"]),
            ("五、上传视频 → 双模型分析 → AI学生档案", [
                "菜单 数据→上传视频(或工具栏📁): 选择 mp4/avi/mov/mkv/wmv。",
                "程序自动: 采样6帧 → 生成多帧蒙太奇 → 本地大模型常规观察 ‖ 外部大模型加强评分(0-100) 并行 → 生成AI学生档案(Word+Markdown+JSON+采样帧), 存入数据仓库 上传视频/ 目录, 评分实时驱动进度条。"]),
            ("六、双模型对话", [
                "工具栏「💬双模型对话」: 左侧=本地Ollama(默认 deepseek-r1:7b, 自动探测), 右侧=外部大模型API。",
                "发送问题后: 大模型回复在对应窗口; 思考区同步显示 感知→榜样比对→路径规划→决策 的思维链。"]),
            ("七、成长进度区(双时间轴)", [
                "两条进度条: 🌟榜样同龄完成度(终点=榜样知识库) vs 🎓学生综合成长分(起点=初始学情), 附等效榜样年龄与超前/落后天数。",
                "五个教学动作(讲解/例题/反思/互动/休息)=按天打卡, 每天推进一个学习日; MCTS按钮=规划并自动执行最优路径; ✈自动领航=引擎每1.5秒自主决策一天; ⚡压缩模拟=数秒跑完4380天并验证路径有效性。",
                "S型曲线: 理想榜样线(橙色) 与 你的成长轨迹(青色), 紫色刻度=等效榜样年龄。"]),
            ("八、思考区与左上角弹窗", [
                "思考区=AI学生思维链(感知/阶段/生长/规划/决策/榜样比对/纠偏), 可导出为txt。",
                "重要通知(评分/评估/档案)在窗口左上角弹出, 约7秒自动消失。"]),
            ("九、4380天数据仓库与进化(0-100岁目标)", [
                "数据仓库: %s  结构: 影像/ 分析/ 按天存放; 数据集/ 含逐日JSON与档案。",
                "「📚4380天档案」=一键把6-18岁4380天逐日生成 Word+Markdown+JSON 档案 + 成长轨迹CSV + 训练语料jsonl(可直接喂大模型训练)。",
                "回读进化: 每次启动读取历史档案 → 经验回放(保持率提升) + 数据驱动层(从轨迹拟合教学动作权重) → 档案越多 ai学生越聪明; 数据规范见 数据规范_0-100岁.txt, 同一结构可扩展至0-100岁 ai数据学生。"]),
            ("十、常见问题", [
                "摄像头无法打开: ①Windows 设置→隐私和安全性→摄像头→允许桌面应用 ②关闭占用摄像头的程序 ③外接摄像头改源1/2 ④查看摄像头窗口内的诊断提示。",
                "本地模型未连接: 安装 Ollama 并运行, 再执行 ollama pull deepseek-r1:7b, 点①区「重试探测」。",
                "外部API失败: 检查密钥/地址/模型名与账户余额; 视觉评分需视觉模型(qwen-vl-plus/gpt-4o等)。",
                "配置与数据位置: 配置 %s ; 数据 %s 。"]),
        ]
        md_build(md_p, "AI学生 · 使用文档", sections)
        blocks = [("h1", "AI学生 · 教育预测引擎 使用文档"),
                  ("p", "生成时间: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]
        for head, rows in sections:
            blocks.append(("h2", head))
            for r in rows:
                blocks.append(("li", r))
        docx_build(doc_p, "AI学生 · 使用文档", blocks)
        return doc_p
    except Exception:
        return None


# ==================================================== 学习轨迹窗口(v3) ======

class TrajectoryPanel(tk.Frame):
    """⑤ 学习轨迹窗口: 技能掌握度 + 最近学习事件(学习闭环) + 错误堵点。"""

    def __init__(self, master, app):
        super().__init__(master, bg=PANEL)
        self.app = app
        head = tk.Frame(self, bg=PANEL2)
        head.pack(fill="x")
        tk.Label(head, text="🧭 学习轨迹 · 学习闭环记录", bg=PANEL2, fg=TXT,
                 font=(FONT, 10, "bold")).pack(side="left", padx=10, pady=8)
        for text, cmd in (("刷新", self.refresh), ("导出…", self.export)):
            tk.Button(head, text=text, command=cmd, bg=PANEL2, fg=ACC,
                      relief="flat", font=(FONT, 9), cursor="hand2",
                      padx=6).pack(side="right", padx=2, pady=6)
        self.text = tk.Text(self, wrap="word", bg=LOG_BG, fg=TXT, relief="flat",
                            bd=0, padx=10, pady=6, font=(FONT, 9))
        self.text.pack(fill="both", expand=True)
        self.text.tag_config("skill", foreground=ACC)
        self.text.tag_config("err", foreground=BAD)
        self.text.tag_config("ok", foreground=OK)
        self.text.tag_config("meta", foreground=SUB)
        self.refresh()

    def _fmt_episode(self, ep):
        tag = ("✓" if ep.correct is True else ("✗" if ep.correct is False else "—"))
        line = ("[第%d天] %s·%s | %s%s | 掌握 %s%%→%s%%" % (
            ep.day, ep.subject, ep.skill, ep.learning_material, tag,
            int((ep.before_mastery or 0) * 100), int((ep.after_mastery or 0) * 100)))
        if ep.correct is False:
            line += " | 错误:%s" % (ep.error_type or "")
            if ep.retry_correct:
                line += " | 重试后正确"
        return line + "\n"

    def refresh(self):
        eng = self.app.engine
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", "当前技能掌握度(共%d个技能):\n" % len(eng.skills), "meta")
        for sid, sk in list(eng.skills.items())[-12:]:
            self.text.insert("end", "  %s · 掌握度 %.0f%% · 练习%d次 正确%d 错误%d\n"
                             % (sk.skill_name, sk.mastery * 100, sk.attempts,
                                sk.correct_count, sk.error_count), "skill")
        if eng.errors:
            self.text.insert("end", "\n高频错误 / 认知堵点:\n", "meta")
            top = sorted(eng.errors.values(), key=lambda r: -r.count)[:8]
            for r in top:
                self.text.insert("end", "  %s · %s ×%d (复发%d)\n"
                                 % (r.skill, r.error_name, r.count,
                                    r.recurrence_count), "err")
        self.text.insert("end", "\n最近学习事件(倒序):\n", "meta")
        for ep in reversed(eng.episodes[-30:]):
            self.text.insert("end", self._fmt_episode(ep),
                             "err" if ep.correct is False else "ok")
        self.text.configure(state="disabled")
        self.text.see("end")

    def export(self):
        from tkinter import filedialog
        default = os.path.join(os.path.expanduser("~"),
                               "ai学生学习轨迹_%s.jsonl"
                               % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        path = filedialog.asksaveasfilename(
            title="导出学习轨迹", initialfile=os.path.basename(default),
            initialdir=os.path.dirname(default), defaultextension=".jsonl",
            filetypes=[("JSONL", "*.jsonl"), ("文本文件", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                for ep in self.app.engine.episodes:
                    f.write(json.dumps(ep.to_dict(), ensure_ascii=False) + "\n")
            self.app.toast("🧭 学习轨迹已导出",
                           "%d 条事件\n%s" % (len(self.app.engine.episodes), path),
                           ACC, 8)
        except Exception as e:
            self.app.toast("🧭 导出失败", str(e), BAD, 8)


# ============================================================ 修炼窗口 =======

class LevelPanel(tk.Frame):
    """⑥ 修炼窗口: 境界阶梯 + 榜位 + 九字秘法(删解秒分合列推创造)。"""

    def __init__(self, master, app):
        super().__init__(master, bg=PANEL)
        self.app = app
        head = tk.Frame(self, bg=PANEL2)
        head.pack(fill="x")
        tk.Label(head, text="🀄 修炼 · 境界榜位 · 九字秘法", bg=PANEL2, fg=TXT,
                 font=(FONT, 10, "bold")).pack(side="left", padx=10, pady=8)
        for text, cmd in (("刷新", self.refresh), ("导出…", self.export)):
            tk.Button(head, text=text, command=cmd, bg=PANEL2, fg=ACC,
                      relief="flat", font=(FONT, 9), cursor="hand2",
                      padx=6).pack(side="right", padx=2, pady=6)

        self.rank_cv = tk.Canvas(self, bg=PANEL, highlightthickness=0, height=74)
        self.rank_cv.pack(fill="x", padx=8, pady=(6, 0))
        self.rank_cv.bind("<Configure>", lambda e: self._draw_rank())

        tip = tk.Label(self, text="点下面任意一个字即为「修炼一式」: 推进1个学习日, "
                                  "并记入该式的独立修为与段位。",
                       bg=PANEL, fg=SUB, font=(FONT, 8), anchor="w")
        tip.pack(fill="x", padx=10)
        self.arts_frame = tk.Frame(self, bg=PANEL)
        self.arts_frame.pack(fill="x", padx=8, pady=(2, 0))
        self.art_btns = {}
        for i, art in enumerate(NINE_ARTS):
            b = tk.Button(self.arts_frame, text="", height=3, justify="center",
                          command=lambda k=art["key"]: self.app.practice_art(k),
                          bg=PANEL2, fg=TXT, relief="flat", font=(FONT, 9),
                          cursor="hand2", activebackground="#202634")
            b.grid(row=i // 5, column=i % 5, padx=3, pady=3, sticky="nsew")
            self.art_btns[art["key"]] = b
        for c in range(5):
            self.arts_frame.columnconfigure(c, weight=1)

        self.text = tk.Text(self, wrap="word", bg=LOG_BG, fg=TXT, relief="flat",
                            bd=0, padx=10, pady=6, font=(FONT, 9), height=13)
        self.text.pack(fill="both", expand=True, padx=8, pady=6)
        for tag, col in (("bl", ACC), ("ok", OK), ("warn", WARN),
                         ("bad", BAD), ("meta", SUB)):
            self.text.tag_config(tag, foreground=col)
        self.refresh()

    # ------------------------------------------------------ 榜位可视化 ----
    def _draw_rank(self):
        c = self.rank_cv
        w, h = c.winfo_width(), c.winfo_height()
        if w < 80 or h < 40:
            return
        c.delete("all")
        try:
            r = self.app.engine.level_rating()
        except Exception:
            return
        ml, mr = 12, 12
        # 榜位进度条(境界内)
        RoundedRect.bar(c, ml, 26, w - mr, 44, 8, r["rank_pos"], ACC, "#1B2029", EDGE)
        c.create_text(ml, 14, text="%s %s · 段位 %s · 榜位 %d/100"
                      % (r["level_realm_emoji"], r["level_realm_name"],
                         r["tier"], r["rank"]),
                      anchor="w", fill=TXT, font=(FONT, 9, "bold"))
        c.create_text(w - mr, 14, text="等效 %s %s"
                      % (r["role_label"], r["equiv_age"]),
                      anchor="e", fill=VIOLET, font=(FONT, 9))
        # 四境界刻度
        pw = w - ml - mr
        for i, rm in enumerate(REALMS):
            x = ml + pw * (i / float(len(REALMS)))
            rs = realm_index(r["equiv_day"])
            col = ACC if i == rs else EDGE
            c.create_line(x, 50, x, 58, fill=col)
            c.create_text(x + 3, 63, text="%s%s" % (rm["emoji"], rm["name"]),
                          anchor="w", fill=(TXT if i == rs else SUB), font=(FONT, 8))
        c.create_text(w - mr, 63, text="实际境界 %s%s · %s"
                      % (r["realm_emoji"], r["realm_name"], r["trend"]),
                      anchor="e", fill=SUB, font=(FONT, 8))

    # ---------------------------------------------------------- 刷新 ----
    def refresh(self):
        eng = self.app.engine
        try:
            r = eng.level_rating()
        except Exception:
            return
        # 九宫格: 每一式的修为与段位
        for a in r["arts"]:
            m = a["mastery"]
            col = OK if m >= 0.85 else (ACC if m >= 0.6 else
                                        (WARN if m >= 0.3 else TXT))
            btn = self.art_btns.get(a["key"])
            if btn is not None:
                btn.configure(text="%s %s\n%s %.0f%%"
                                   % (a["ch"], a["name"], a["tier"], m * 100),
                              fg=col)
        # 明细
        t = self.text
        t.configure(state="normal")
        t.delete("1.0", "end")
        t.insert("end", "修为 %.2f / 5.00   |   实际境界 %s%s(%s)   |   水平境界 %s%s   |   %s\n"
                 % (r["score5"], r["realm_emoji"], r["realm_name"], r["grade"],
                    r["level_realm_emoji"], r["level_realm_name"], r["trend"]), "bl")
        t.insert("end", "统一量度: 你现在的水平 ≈ %s %s · %s · 榜位 %d/100(境界内 %s)\n"
                 % (r["role_label"], r["equiv_age"], r["tier"], r["rank"], r["tier"]), "meta")
        t.insert("end", "与同龄(实际年龄)相比: %s   |   距 K12 顶点还剩 %d 天   |   下一境: %s\n"
                 % (r["trend"], eng.remain_days, r["next_realm"]), "meta")
        t.insert("end", "\n当前境界要务: %s —— %s\n" % (r["focus"], r["task"]), "warn")
        t.insert("end", "九字秘法总修为 %.0f%% (%d/%d 式已解锁)\n"
                 % (r["arts_avg"] * 100, r["arts_unlocked"], r["arts_total"]), "bl")
        for a in r["arts"]:
            t.insert("end", "  %s %s(%s·%s) 修为 %.0f%% · %s · 修炼%d次(对%d/错%d)\n"
                     % (a["ch"], a["name"], a["realm"], a["tier"], a["mastery"] * 100,
                        a["tip"], a["uses"], a["ok"], a["err"]),
                     ("ok" if a["mastery"] >= 0.6 else
                      ("warn" if a["mastery"] >= 0.25 else "bad")))
        t.insert("end", "\n榜样时间轴(%s):\n" % r["role_label"], "bl")
        for txt in r["milestone_done"]:
            t.insert("end", "  ✓ %s\n" % txt, "ok")
        if r["milestone_next"]:
            t.insert("end", "  → 下一目标(约%d岁): %s%s\n"
                     % (r["milestone_next_age"], r["milestone_next"],
                        ("  [%s]" % r["milestone_next_goal"]) if r["milestone_next_goal"] else ""),
                     "warn")
        t.insert("end", "\n「创」式当前应演化的物理模型: %s   (模型库 %d/%d)\n"
                 % (r["model"], len(PHYSICS_MODELS), r["model_total"]), "bl")
        t.configure(state="disabled")

    def export(self):
        from tkinter import filedialog
        default = os.path.join(os.path.expanduser("~"),
                               "ai学生_修炼档案_%s.json"
                               % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        path = filedialog.asksaveasfilename(
            title="导出修炼档案", initialfile=os.path.basename(default),
            initialdir=os.path.dirname(default), defaultextension=".json",
            filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.app.engine.level_rating(), f,
                          ensure_ascii=False, indent=1)
            self.app.toast("🀄 修炼档案已导出", path, ACC, 8)
        except Exception as e:
            self.app.toast("🀄 导出失败", str(e), BAD, 8)


# ============================================================ 主程序 App ====

class App:
    """AI学生 图形主程序: 顶栏学生信息+摄像头 | 四分区(GUI) | 状态栏。"""

    def __init__(self, root):
        self.root = root
        self._closing = False
        self.cfg = cfg_load()
        self.ui_q = queue.Queue()
        self.engine = AIStudentEngine()
        self.vault = DataVault()
        self.vault.ensure()
        self.vault.write_manifest()
        self._load_cfg_to_engine()
        self._feed_idx = 0
        self._save_job = None
        self._pilot_next = 0.0
        self._curve_key = None
        self._archiving = False
        self._last_arch_abs = None
        self._guide = None
        self.material_days_left = 0        # 教材自动学习剩余天数(0=未在跑)

        # ---------- 样式(干净利落) ----------
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TCombobox", fieldbackground=INPUT_BG, background="#232C3A",
                        foreground=TXT, arrowcolor=ACC, bordercolor=EDGE,
                        lightcolor=EDGE, darkcolor=EDGE, selectbackground="#1A2230",
                        selectforeground=TXT, padding=2)
        style.map("TCombobox", fieldbackground=[("readonly", INPUT_BG)])
        root.option_add("*TCombobox*Listbox.background", "#1A2230")
        root.option_add("*TCombobox*Listbox.foreground", TXT)
        root.option_add("*TCombobox*Listbox.selectBackground", "#26364A")
        root.option_add("*Menu.background", PANEL2)
        root.option_add("*Menu.foreground", TXT)
        root.option_add("*Menu.activeBackground", "#26364A")
        root.option_add("*Menu.activeForeground", TXT)
        root.configure(bg=BG)

        # ================= 菜单栏(传统软件式, 功能高度集成) =================
        mb = tk.Menu(root, tearoff=0, font=(FONT, 9))
        m_file = tk.Menu(mb, tearoff=0, font=(FONT, 9))
        m_file.add_command(label="💾 保存设置", command=self.save_cfg)
        m_file.add_command(label="📤 导出思考日志", command=lambda: self.thinkzone.export())
        m_file.add_command(label="📂 打开数据仓库", command=lambda: self.camera.open_folder())
        m_file.add_separator()
        m_file.add_command(label="退出", command=self.close)
        mb.add_cascade(label="文件", menu=m_file)
        m_stu = tk.Menu(mb, tearoff=0, font=(FONT, 9))
        m_stu.add_command(label="♻ 重置学习进度(重新开始)", command=self.reset_progress)
        mb.add_cascade(label="学生", menu=m_stu)
        m_model = tk.Menu(mb, tearoff=0, font=(FONT, 9))
        m_model.add_command(label="🔑 API密钥 / 模型设置…", command=self.open_settings)
        m_model.add_command(label="探测本地 Ollama 模型",
                            command=lambda b=self.cfg_local_base():
                            self.go_thread(lambda: self.local.probe(b)))
        m_model.add_command(label="测试外部 API 连接", command=lambda: self.remote.test_conn())
        mb.add_cascade(label="模型", menu=m_model)
        m_cam = tk.Menu(mb, tearoff=0, font=(FONT, 9))
        m_cam.add_command(label="📷 摄像头窗口…", command=self.open_camera_dlg)
        m_cam.add_command(label="一键打开/关闭摄像头", command=self.toggle_camera)
        m_cam.add_command(label="开始/停止录制", command=lambda: self.camera.rec_toggle())
        m_cam.add_command(label="🔄 实时双模型同步分析", command=lambda: (self.camera.rt_var.set(True), self.camera.rt_toggle()))
        m_cam.add_command(label="⚡ 本机算力评估", command=lambda: self.camera.assess_local())
        m_cam.add_separator()
        m_cam.add_command(label="☁ 算力: 本机优先", command=lambda: self.set_cloud("本机优先"))
        m_cam.add_command(label="☁ 算力: 阿里云百炼·视觉", command=lambda: self.set_cloud("阿里云百炼·视觉"))
        m_cam.add_command(label="☁ 算力: 阿里云EAS·自定义", command=lambda: self.set_cloud("阿里云EAS·自定义"))
        mb.add_cascade(label="摄像头", menu=m_cam)
        m_data = tk.Menu(mb, tearoff=0, font=(FONT, 9))
        m_data.add_command(label="📁 上传视频 → 双模型分析 → AI学生档案", command=self.upload_video)
        m_data.add_command(label="📚 生成 4380天 档案(Word+MD+JSON+语料)", command=self.archive_all_btn)
        m_data.add_command(label="📂 打开数据仓库", command=lambda: self.camera.open_folder())
        m_data.add_command(label="🧭 学习轨迹窗口…", command=self.open_traj)
        m_data.add_command(label="🀄 修炼 · 境界榜位 · 九字秘法…", command=self.open_level)
        m_data.add_command(label="📚 教材投喂 · 自动学习…", command=self.ingest_material)
        m_data.add_command(label="📖 使用文档(生成并打开)", command=self.open_usage_doc)
        mb.add_cascade(label="数据", menu=m_data)
        m_help = tk.Menu(mb, tearoff=0, font=(FONT, 9))
        m_help.add_command(label="🎬 新手引导动画", command=self.start_guide)
        m_help.add_command(label="📖 使用文档", command=self.open_usage_doc)
        m_help.add_command(label="关于", command=lambda: tk.messagebox.showinfo(
            "关于", "%s v%s\n专利思想: ai学生教育预测模型\n数据仓库: %s"
            % (APP_NAME, APP_VER, CAM_DIR)))
        mb.add_cascade(label="帮助", menu=m_help)
        root.configure(menu=mb)
        self.menu = mb

        # ================= 顶栏工具栏(集成大部分功能) =================
        bar = tk.Frame(root, bg=PANEL, highlightbackground=EDGE,
                       highlightthickness=1)
        bar.pack(fill="x")
        self.toolbar = bar
        self.btn_cam = tk.Button(bar, text="📷 一键打开摄像头", command=self.toggle_camera,
                                 bg="#1C2433", fg=ACC, relief="flat",
                                 font=(FONT, 9, "bold"), cursor="hand2")
        self.btn_cam.pack(side="left", padx=(10, 2), pady=6)
        self.btn_rec = tk.Button(bar, text="● 录制", command=lambda: self.camera.rec_toggle(),
                                 bg=PANEL2, fg="#C2B08C", relief="flat",
                                 font=(FONT, 9), cursor="hand2")
        self.btn_rec.pack(side="left", padx=2, pady=6)
        self.btn_api = tk.Button(bar, text="🔑 API密钥", command=self.open_settings,
                                 bg=PANEL2, fg=ACC, relief="flat",
                                 font=(FONT, 9, "bold"), cursor="hand2")
        self.btn_api.pack(side="left", padx=2, pady=6)
        self.btn_up = tk.Button(bar, text="📁 上传视频", command=self.upload_video,
                                bg=PANEL2, fg=WARN, relief="flat",
                                font=(FONT, 9, "bold"), cursor="hand2")
        self.btn_up.pack(side="left", padx=2, pady=6)
        self.btn_chat = tk.Button(bar, text="💬 双模型对话", command=self.open_chat,
                                  bg=PANEL2, fg=TXT, relief="flat",
                                  font=(FONT, 9), cursor="hand2")
        self.btn_chat.pack(side="left", padx=2, pady=6)
        self.btn_arch = tk.Button(bar, text="📚 4380天档案", command=self.archive_all_btn,
                                  bg=PANEL2, fg=VIOLET, relief="flat",
                                  font=(FONT, 9), cursor="hand2")
        self.btn_arch.pack(side="left", padx=2, pady=6)
        self.btn_traj = tk.Button(bar, text="🧭 学习轨迹", command=self.open_traj,
                                  bg=PANEL2, fg=TXT, relief="flat",
                                  font=(FONT, 9), cursor="hand2")
        self.btn_traj.pack(side="left", padx=2, pady=6)
        self.btn_level = tk.Button(bar, text="🀄 修炼·九字秘法", command=self.open_level,
                                   bg="#1C2433", fg=ACC, relief="flat",
                                   font=(FONT, 9, "bold"), cursor="hand2")
        self.btn_level.pack(side="left", padx=2, pady=6)
        self.btn_mat = tk.Button(bar, text="📚 教材投喂", command=self.toggle_material,
                                 bg=PANEL2, fg=WARN, relief="flat",
                                 font=(FONT, 9, "bold"), cursor="hand2")
        self.btn_mat.pack(side="left", padx=2, pady=6)
        self.btn_guide = tk.Button(bar, text="🎬 引导", command=self.start_guide,
                                   bg=PANEL2, fg=TXT, relief="flat",
                                   font=(FONT, 9), cursor="hand2")
        self.btn_guide.pack(side="left", padx=2, pady=6)
        # ---- 学生信息(内嵌顶栏右侧, 少数信息外露) ----
        self.name_var = tk.StringVar(value=self.engine.student_name)
        tk.Label(bar, text="👦", bg=PANEL, font=(FONT, 9)).pack(side="right", padx=(0, 1))
        e_name = tk.Entry(bar, textvariable=self.name_var, width=7, bg=INPUT_BG,
                          fg=TXT, relief="flat", font=(FONT, 9),
                          insertbackground=ACC)
        e_name.pack(side="right", padx=(0, 6), pady=6, ipady=2)
        self.name_var.trace_add("write", lambda *a: self._on_name())
        self.grade_var = tk.StringVar(value=GRADES[self.engine.grade_idx])
        cb_g = ttk.Combobox(bar, textvariable=self.grade_var, width=9,
                            values=GRADES, state="readonly", font=(FONT, 9))
        cb_g.pack(side="right", padx=2, pady=6)
        cb_g.bind("<<ComboboxSelected>>", self._on_grade)
        self.state_var = tk.StringVar(value=self.engine.learn_state)
        cb_s = ttk.Combobox(bar, textvariable=self.state_var, width=8,
                            values=STATE_OPTS, state="readonly", font=(FONT, 9))
        cb_s.pack(side="right", padx=2, pady=6)
        cb_s.bind("<<ComboboxSelected>>", self._on_state)
        self.role_keys = list(ROLE_MODELS.keys())
        self.role_var = tk.StringVar(value="%s %s" % (
            ROLE_MODELS[self.engine.role_key]["emoji"],
            ROLE_MODELS[self.engine.role_key]["label"]))
        cb_r = ttk.Combobox(bar, textvariable=self.role_var, width=15,
                            values=["%s %s" % (ROLE_MODELS[k]["emoji"],
                                               ROLE_MODELS[k]["label"])
                                    for k in self.role_keys],
                            state="readonly", font=(FONT, 9))
        cb_r.pack(side="right", padx=2, pady=6)
        cb_r.bind("<<ComboboxSelected>>", self._on_role)
        # ---- 关键徽章行(仅少数信息) ----
        chip_row = tk.Frame(bar, bg=PANEL)
        chip_row.pack(fill="x", padx=10, pady=(0, 6))
        self.chips = {}
        for key in ("cam", "score", "equiv", "gap", "stage", "remain", "fat", "att"):
            lab = tk.Label(chip_row, bg=CHIP_BG, fg=SUB, font=(FONT, 8), padx=7,
                           pady=1, anchor="center")
            lab.pack(side="left", padx=(0, 5))
            self.chips[key] = lab
        tk.Label(chip_row, text="", bg=PANEL).pack(side="left", expand=True)

        # ================= 主区(仅思考区 + 成长进度) =================
        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=8, pady=8)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)
        self.thinkzone = ThinkZone(main, self)
        self.thinkzone.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        self.progress = ProgressZone(main, self)
        self.progress.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        # ================= 三个功能窗口(初始隐藏, 工具栏唤起) ==========
        # 摄像头窗口
        dlg_c = tk.Toplevel(root)
        dlg_c.title("📷 摄像头 · 录制与双模型实时分析")
        dlg_c.geometry("396x470")
        dlg_c.configure(bg=BG)
        self.camera = CameraPanel(dlg_c, self)
        self.camera.pack(fill="both", expand=True, padx=6, pady=6)
        dlg_c.withdraw()
        self.dlg_camera = dlg_c
        # 双模型对话窗口
        dlg_t = tk.Toplevel(root)
        dlg_t.title("💬 双模型对话 · 本地 deepseek-r1:7b ‖ 外部API")
        dlg_t.geometry("1100x580")
        dlg_t.configure(bg=BG)
        self.local = LocalZone(dlg_t, self)
        self.local.grid(row=0, column=0, sticky="nsew", padx=(6, 3), pady=6)
        self.remote = RemoteZone(dlg_t, self)
        self.remote.grid(row=0, column=1, sticky="nsew", padx=(3, 6), pady=6)
        dlg_t.columnconfigure(0, weight=1)
        dlg_t.columnconfigure(1, weight=1)
        dlg_t.rowconfigure(0, weight=1)
        dlg_t.withdraw()
        self.dlg_chat = dlg_t
        # API密钥/模型设置窗口
        dlg_s = tk.Toplevel(root)
        dlg_s.title("🔑 API密钥 · 模型设置")
        dlg_s.geometry("600x360")
        dlg_s.configure(bg=BG)
        self.settings_dlg = dlg_s
        self._build_settings(dlg_s)
        dlg_s.withdraw()
        # 学习轨迹窗口
        dlg_tr = tk.Toplevel(root)
        dlg_tr.title("🧭 学习轨迹 · 学习闭环记录")
        dlg_tr.geometry("720x560")
        dlg_tr.configure(bg=BG)
        self.traj = TrajectoryPanel(dlg_tr, self)
        self.traj.pack(fill="both", expand=True, padx=6, pady=6)
        dlg_tr.withdraw()
        self.dlg_traj = dlg_tr
        # 修炼窗口(境界榜位 + 九字秘法)
        dlg_lv = tk.Toplevel(root)
        dlg_lv.title("🀄 修炼 · 境界榜位 · 九字秘法")
        dlg_lv.geometry("880x640")
        dlg_lv.configure(bg=BG)
        self.level = LevelPanel(dlg_lv, self)
        self.level.pack(fill="both", expand=True, padx=6, pady=6)
        dlg_lv.withdraw()
        self.dlg_level = dlg_lv

        self.status = tk.Label(root, text="启动中…", bg=PANEL2, fg=SUB,
                               font=(FONT, 8), anchor="w", padx=12, pady=3)
        self.status.pack(fill="x", side="bottom")

        self.toaster = Toaster(root, lambda: (bar.winfo_height() or 120) + 34)

        # ---------- 恢复用户设置到控件 ----------
        self._apply_cfg_to_ui()
        try:                                # 外部API未配置 → 给一次明确指引
            if not (self.remote.key_var.get() or "").strip():
                self.think("TIP", "外部API未配置: 点工具栏「🔑API密钥」→ 填 地址/密钥/模型"
                                  " → 保存并关闭; 之后上传视频才会做外部加强评分"
                                  "(不配置也能生成档案)")
                self.toast("🔑 外部API未配置",
                           "点工具栏「🔑 API密钥」→ 填 地址/密钥/模型 → 保存并关闭;\n"
                           "之后上传视频才会做外部加强评分(不配置也能生成档案)",
                           WARN, 10)
        except Exception:
            pass
        self.status_set(SUB, "就绪 · 引擎启动")
        root.protocol("WM_DELETE_WINDOW", self.close)
        # ---------- 启动序列 ----------
        root.after(500, lambda b=self.cfg_local_base():
                   self.go_thread(lambda: self.local.probe(b)))
        root.after(1200, self._welcome)
        root.after(1600, self._startup_camera)
        self._tick()

    # ------------------------------------------------ 工具栏/窗口 ----
    def _on_name(self):
        v = self.name_var.get().strip() or "小原"
        self.engine.student_name = v
        self.cfg_dirty()

    def _on_grade(self, _e=None):
        idx = GRADES.index(self.grade_var.get())
        eng = self.engine
        old = eng.grade_idx
        eng.grade_idx = idx
        eng.sim_day = min(eng.sim_day, eng.allowed_exec)
        eng._finished_announced = False
        eng.emit("STATUS", "📊 学情校准: 年级 %s→%s (起点=%s, 剩余%d天)"
                 % (GRADES[old], GRADES[idx], age_str(eng.base_days),
                    eng.remain_days))
        self.cfg_dirty()

    def _on_state(self, _e=None):
        eng = self.engine
        v = self.state_var.get()
        old = eng.learn_state
        eng.learn_state = v
        d = STATE_EFFECT.get(v, 0.0)
        if d:
            eng.student.attention = clamp(eng.student.attention + d)
            eng.emit("SENSE", "👁 学习状态: %s→%s, 注意力%s%.0f%%"
                     % (old, v, "+" if d >= 0 else "", d * 100))
        self.cfg_dirty()

    def _on_role(self, _e=None):
        eng = self.engine
        for k in self.role_keys:
            r = ROLE_MODELS[k]
            if self.role_var.get().startswith(r["emoji"]):
                eng.role_key = k
                break
        eng.emit("GOAL", "🎯 榜样模型切换: 终点 = %s | %s"
                 % (eng.role()["label"], eng.role()["desc"]))
        self.cfg_dirty()

    def toolbar_refresh(self):
        eng = self.engine
        ch = self.chips
        equiv_day, gap, score, ideal = eng.dual_timeline()
        st, col = eng.gap_status()
        cam_on = self.camera.cam_active()
        rec = self.camera.recording
        ch["cam"].configure(
            text="📷 摄像头: %s" % ("●录制中" if rec else ("运行中" if cam_on else "已关闭")),
            fg=(OK if (cam_on and not rec) else (BAD if not cam_on else WARN)))
        ch["score"].configure(text="⭐ 成长分 %.2f/5" % score, fg=ACC)
        ch["equiv"].configure(text="🏁 等效榜样 %s" % age_str(equiv_day), fg=VIOLET)
        ch["gap"].configure(text="%s %d天" % (st, abs(gap)), fg=col)
        ch["stage"].configure(text="%s %s" % (eng.stage()[1], eng.stage()[0]))
        ch["remain"].configure(text="⏳ 剩%d天" % eng.remain_days)
        ch["fat"].configure(text="😴 %.0f%%" % (eng.student.fatigue * 100),
                            fg=WARN if eng.student.fatigue > 0.6 else SUB)
        ch["att"].configure(text="👀 %.0f%%" % (eng.student.attention * 100))
        self.btn_cam.configure(text="📷 关闭摄像头" if cam_on else "📷 一键打开摄像头")

    def toggle_camera(self):
        if self.camera.cam_active():
            self.camera.stop_camera()
        else:
            self.camera.start_camera()
            self.open_camera_dlg()
        self.toolbar_refresh()

    def open_camera_dlg(self):
        try:
            self.dlg_camera.deiconify()
            self.dlg_camera.lift()
        except Exception:
            pass

    def open_chat(self):
        try:
            self.dlg_chat.deiconify()
            self.dlg_chat.lift()
        except Exception:
            pass

    def open_traj(self):
        try:
            self.traj.refresh()
            self.dlg_traj.deiconify()
            self.dlg_traj.lift()
        except Exception:
            pass

    def open_level(self):
        try:
            self.level.refresh()
            self.dlg_level.deiconify()
            self.dlg_level.lift()
            self.vault.save_level_rating(self.engine)
        except Exception:
            pass

    def open_settings(self):
        try:
            self.settings_dlg.deiconify()
            self.settings_dlg.lift()
        except Exception:
            pass

    def set_cloud(self, mode):
        self.camera.cloud_var.set(mode)
        self.camera.cloud_selected()

    def reset_progress(self):
        if not tk.messagebox.askyesno(
                "重置学习进度", "将清空当前学习进度(维度/天数/轨迹)并从当前年级重新开始,\n"
                "数据仓库中的历史档案不会被删除。确定?"):
            return
        eng = self.engine
        eng.student = StudentState()
        eng.sim_day = 0
        eng.auto_lesson_count = 0
        eng.perf_history.clear()
        eng.traj_rows.clear()
        eng.skills.clear()
        eng.errors.clear()
        eng.episodes.clear()
        eng.memory_records.clear()
        eng._episode_flushed = 0
        eng._memory_flushed = 0
        eng._finished_announced = False
        eng.emit("SYS", "♻ 学习进度已重置: 空白学生体重新出发(%s)"
                 % GRADES[eng.grade_idx])
        self.save_cfg()
        self.engine_ui_refresh()
        self.toast("♻ 已重置", "空白学生体已重新出发; 历史档案保留在数据仓库", ACC, 6)

    def upload_video(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="选择要分析的学习视频",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                       ("所有文件", "*.*")])
        if not path:
            return
        self.toast("📁 开始视频分析",
                   "将采样多帧, 由本地‖外部两个大模型并行分析并生成AI学生档案…", ACC, 8)
        self.camera.analyze_video_file(path)

    def open_usage_doc(self):
        try:
            p = write_usage_doc(self.vault)
            if p and os.path.exists(p):
                os.startfile(p)
                self.toast("📖 使用文档", "已生成并打开:\n%s" % p, ACC, 8)
        except Exception as e:
            self.toast("📖 使用文档", "打开失败: %s" % e, BAD, 8)

    def start_guide(self, auto=False):
        if auto:
            try:
                if self.cfg.get("guide_done"):
                    return
            except Exception:
                pass
        if not hasattr(self, "_guide") or self._guide is None:
            self._guide = GuideOverlay(self)
        self._guide.restart(auto)

    def _build_settings(self, top):
        """🔑 API密钥/模型设置

        ① 本地 Ollama 地址/模型; ② 外部 API(预设→地址→API密钥→模型→测试连接)。
        密钥输入框常显且可点「显示」核对, 测试/保存结果直接反馈在本窗口内。
        """
        try:
            top.geometry("780x620")
            top.minsize(700, 540)
        except Exception:
            pass
        body = tk.Frame(top, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)
        tk.Label(body, text="🔑 API密钥 · 模型设置", bg=BG, fg=TXT,
                 font=(FONT, 13, "bold")).grid(row=0, column=0, columnspan=6,
                                               sticky="w")
        tk.Label(body, text="外部大模型API用于「上传视频→加强评分」与视觉分析; "
                            "配置保存在 %s" % CFG_PATH,
                 bg=BG, fg=SUB, font=(FONT, 8), justify="left", wraplength=720) \
            .grid(row=1, column=0, columnspan=6, sticky="w", pady=(2, 8))

        # ---------------- ① 本地 Ollama ----------------
        tk.Label(body, text="① 本地大模型 (Ollama)", bg=BG, fg=ACC,
                 font=(FONT, 10, "bold")).grid(row=2, column=0, columnspan=6,
                                               sticky="w", pady=(6, 2))
        tk.Label(body, text="地址:", bg=BG, fg=SUB, font=(FONT, 9)).grid(
            row=3, column=0, sticky="e", padx=(0, 6))
        e1 = tk.Entry(body, textvariable=self.local.base_var, width=36,
                      bg=INPUT_BG, fg=TXT, relief="flat", font=(FONT, 9),
                      insertbackground=ACC)
        e1.grid(row=3, column=1, columnspan=2, sticky="we", padx=(0, 12), ipady=3)
        tk.Label(body, text="模型:", bg=BG, fg=SUB, font=(FONT, 9)).grid(
            row=3, column=3, sticky="e", padx=(0, 6))
        e2 = tk.Entry(body, textvariable=self.local.model_var, width=20,
                      bg=INPUT_BG, fg=TXT, relief="flat", font=(FONT, 9),
                      insertbackground=ACC)
        e2.grid(row=3, column=4, sticky="we", padx=(0, 12), ipady=3)
        tk.Button(body, text="探测", command=lambda b=self.cfg_local_base():
                  self.go_thread(lambda: self.local.probe(b)), bg=PANEL2, fg=ACC,
                  relief="flat", font=(FONT, 9), cursor="hand2", padx=10).grid(
            row=3, column=5, sticky="e")

        # ---------------- ② 外部大模型 API ----------------
        tk.Label(body, text="② 外部大模型 API (上传视频加强评分 / 视觉分析)",
                 bg=BG, fg=VIOLET, font=(FONT, 10, "bold")).grid(
            row=4, column=0, columnspan=6, sticky="w", pady=(16, 2))
        tk.Label(body, text="接口预设:", bg=BG, fg=SUB, font=(FONT, 9)).grid(
            row=5, column=0, sticky="e", padx=(0, 6))
        cb = ttk.Combobox(body, textvariable=self.remote.preset_var, width=20,
                          values=[p[0] for p in REMOTE_PRESETS],
                          state="readonly", font=(FONT, 9))
        cb.grid(row=5, column=1, sticky="we", padx=(0, 12))
        cb.bind("<<ComboboxSelected>>", self.remote.apply_preset)
        tk.Button(body, text="应用预设", command=self.remote.apply_preset,
                  bg=PANEL2, fg=ACC, relief="flat", font=(FONT, 9),
                  cursor="hand2", padx=10).grid(row=5, column=2, sticky="w")

        tk.Label(body, text="接口地址:", bg=BG, fg=SUB, font=(FONT, 9)).grid(
            row=6, column=0, sticky="e", padx=(0, 6), pady=(6, 0))
        e4 = tk.Entry(body, textvariable=self.remote.url_var, width=54,
                      bg=INPUT_BG, fg=TXT, relief="flat", font=(FONT, 9),
                      insertbackground=ACC)
        e4.grid(row=6, column=1, columnspan=5, sticky="we", padx=(0, 12),
                pady=(6, 0), ipady=3)

        tk.Label(body, text="API密钥:", bg=BG, fg=WARN, font=(FONT, 9, "bold")) \
            .grid(row=7, column=0, sticky="e", padx=(0, 6), pady=(6, 0))
        self.key_entry = tk.Entry(body, textvariable=self.remote.key_var, width=54,
                                  bg=INPUT_BG, fg=TXT, relief="flat",
                                  font=(FONT, 10), show="*",
                                  insertbackground=ACC)
        self.key_entry.grid(row=7, column=1, columnspan=3, sticky="we",
                            pady=(6, 0), ipady=4)
        self.show_key_var = tk.BooleanVar(value=False)
        tk.Checkbutton(body, text="显示", variable=self.show_key_var,
                       command=self._toggle_key_show, bg=BG, fg=SUB,
                       selectcolor=BG, activebackground=BG, activeforeground=TXT,
                       font=(FONT, 9), cursor="hand2").grid(
            row=7, column=4, sticky="w", padx=(8, 0), pady=(6, 0))
        tk.Button(body, text="测试连接", command=self._test_api_from_settings,
                  bg=PANEL2, fg=ACC, relief="flat", font=(FONT, 9),
                  cursor="hand2", padx=10).grid(row=7, column=5, sticky="e",
                                                padx=(6, 0), pady=(6, 0))
        tk.Label(body, text="把整段密钥粘贴进来即可(可含 sk- 前缀); Ctrl+V 粘贴",
                 bg=BG, fg=SUB, font=(FONT, 8)).grid(row=8, column=1,
                                                     columnspan=3, sticky="w",
                                                     padx=(2, 0))
        tk.Button(body, text="🖼 测试视觉", command=self._test_api_vision,
                  bg=PANEL2, fg=VIOLET, relief="flat", font=(FONT, 9),
                  cursor="hand2", padx=8).grid(row=8, column=5, sticky="e",
                                               pady=(2, 0))

        tk.Label(body, text="模型名:", bg=BG, fg=SUB, font=(FONT, 9)).grid(
            row=9, column=0, sticky="e", padx=(0, 6), pady=(6, 0))
        e3 = tk.Entry(body, textvariable=self.remote.m_var, width=30,
                      bg=INPUT_BG, fg=TXT, relief="flat", font=(FONT, 9),
                      insertbackground=ACC)
        e3.grid(row=9, column=1, sticky="we", padx=(0, 12), pady=(6, 0), ipady=3)
        tk.Label(body, text="视觉评分填 qwen-vl-plus / gpt-4o; 纯文本填 deepseek-chat",
                 bg=BG, fg=SUB, font=(FONT, 8)).grid(row=9, column=2,
                                                     columnspan=3, sticky="w",
                                                     pady=(6, 0))

        self.api_state = tk.Label(body, text="", bg=BG, fg=SUB, font=(FONT, 9),
                                  justify="left", wraplength=720)
        self.api_state.grid(row=10, column=0, columnspan=6, sticky="w",
                            pady=(12, 0))

        tk.Label(body, text="☁ 阿里云百炼(DashScope): 先在阿里云百炼控制台创建API-Key, "
                            "点下面「百炼·视觉」自动填好地址与 qwen-vl-plus, 再把"
                            "API-Key粘到「API密钥」→ 保存; 用「🖼 测试视觉」验证",
                 bg=BG, fg=SUB, font=(FONT, 8), justify="left", wraplength=720) \
            .grid(row=11, column=0, columnspan=6, sticky="w", pady=(14, 2))

        tk.Button(body, text="☁ 百炼·文本 qwen-plus",
                  command=lambda: self._fill_bailian("qwen-plus"), bg=PANEL2,
                  fg=WARN, relief="flat", font=(FONT, 9), cursor="hand2",
                  padx=8).grid(row=12, column=0, sticky="w", pady=(10, 0))
        tk.Button(body, text="☁ 百炼·视觉 qwen-vl-plus",
                  command=lambda: self._fill_bailian("qwen-vl-plus"), bg=PANEL2,
                  fg=WARN, relief="flat", font=(FONT, 9), cursor="hand2",
                  padx=8).grid(row=12, column=1, sticky="w", pady=(10, 0))
        tk.Button(body, text="📂 直接编辑配置文件", command=self._open_cfg_file,
                  bg=PANEL2, fg=SUB, relief="flat", font=(FONT, 9),
                  cursor="hand2", padx=10).grid(row=12, column=2, columnspan=2,
                                                sticky="w", pady=(10, 0))
        tk.Button(body, text="💾 保存并关闭",
                  command=lambda: self._save_settings(top), bg="#1C2433",
                  fg=ACC, relief="flat", font=(FONT, 10, "bold"),
                  cursor="hand2", padx=14).grid(row=12, column=4, columnspan=2,
                                                sticky="e", pady=(10, 0))
        for c in (1, 2, 4):
            body.columnconfigure(c, weight=1)
        for w in (e1, e2, e3, e4, self.key_entry):
            w.bind("<FocusOut>", lambda _e: self.cfg_dirty())
            w.bind("<Return>", lambda _e: self._save_settings(top))
        self.refresh_api_state()

    def _toggle_key_show(self):
        """显示/隐藏 API 密钥输入框内容。"""
        try:
            self.key_entry.configure(show="" if self.show_key_var.get() else "*")
        except Exception:
            pass

    def refresh_api_state(self):
        """设置窗口内显示: 外部API是否已配置完整(地址+密钥+模型)。"""
        try:
            url = self.remote.url_var.get().strip()
            key = self.remote.key_var.get().strip()
            model = self.remote.m_var.get().strip()
        except Exception:
            return
        ok = bool(url and key and model)
        if ok:
            txt = "✅ 外部API已配置: %s · %s · 密钥 %s" % (url, model, mask_key(key))
        else:
            txt = ("⚠ 外部API未配置完整(需要 地址 + API密钥 + 模型名): "
                   "地址%s · 密钥%s · 模型%s"
                   % ("✓" if url else "✗", "✓" if key else "✗",
                      "✓" if model else "✗"))
        if hasattr(self, "api_state"):
            try:
                self.api_state.configure(text=txt, fg=(OK if ok else WARN))
            except Exception:
                pass

    def _save_settings(self, top=None):
        """保存配置并明确反馈"存了什么"。"""
        try:
            self.save_cfg()
        except Exception as e:
            self.toast("🔑 保存失败", str(e), BAD, 8)
            return
        self.refresh_api_state()
        try:
            url = self.remote.url_var.get().strip()
            key = self.remote.key_var.get().strip()
            model = self.remote.m_var.get().strip()
        except Exception:
            url = key = model = ""
        if hasattr(self, "api_state"):
            try:
                self.api_state.configure(
                    text=("💾 已保存到 %s\n地址: %s · 模型: %s · 密钥: %s"
                          % (CFG_PATH, url or "(空)", model or "(空)",
                             mask_key(key))), fg=(OK if key else WARN))
            except Exception:
                pass
        self.think("MODEL", "🔑 外部API设置已保存: 地址=%s 模型=%s 密钥=%s"
                   % (url or "(空)", model or "(空)", mask_key(key)))
        self.toast("🔑 已保存API设置",
                   "地址: %s\n模型: %s\n密钥: %s\n上传视频时外部通道即按此配置执行"
                   % (url or "(空)", model or "(空)", mask_key(key)), ACC, 9)
        if top is not None:
            try:
                top.withdraw()
            except Exception:
                pass

    def _test_api_from_settings(self):
        """测试连接: 结果写回设置窗口(聊天窗口平时隐藏, 那里看不到反馈)。"""
        try:
            url, key, model = self.remote.build_request_snapshot()
        except Exception:
            url, key, model = "", "", ""
        try:
            if not url or not model:
                self.api_state.configure(text="⚠ 请先填写接口地址与模型名", fg=BAD)
                return
            self.api_state.configure(text="⏳ 正在测试连接(最长300秒)…", fg=WARN)
        except Exception:
            pass
        self.think("MODEL", "🔌 测试外部API: %s · %s · 密钥 %s"
                   % (url, model, mask_key(key)))

        def work():
            try:
                out = LLMClient.remote_chat(
                    url, key, model,
                    [{"role": "user", "content": "你好, 请只回复: 连接成功"}],
                    timeout=60)
                return ("ok", str(out))
            except Exception as e:
                return ("err", str(e))

        def done(kind, out):
            try:
                if kind == "ok":
                    self.api_state.configure(text="✅ 连接成功: %s" % out[:150],
                                             fg=OK)
                    self.toast("🔑 外部API连接成功", "模型: %s\n回复: %s"
                               % (model, out[:80]), OK, 8)
                    self.think("MODEL", "✅ 外部API测试通过(%s): %s"
                               % (model, out[:80]))
                else:
                    self.api_state.configure(text="❌ 连接失败: %s" % out[:300],
                                             fg=BAD)
                    self.toast("🔑 外部API连接失败", out[:220], BAD, 10)
                    self.think("MODEL", "⚠ 外部API测试失败: %s" % out[:200])
            except Exception:
                pass

        def run():
            r = work()
            self.push_ui(lambda: done(*r))
        self.go_thread(run)

    def _open_cfg_file(self):
        """用记事本直接编辑配置文件(填 remote.key 后保存, 重启程序生效)。"""
        try:
            self.save_cfg()
            if not os.path.exists(CFG_PATH):
                cfg_save({}, CFG_PATH)
            try:
                subprocess.Popen(["notepad.exe", CFG_PATH])
            except Exception:
                os.startfile(CFG_PATH)
            self.toast("🔑 配置文件已打开",
                       "把 remote 段里的 key 填成你的API密钥, 保存后回程序点"
                       "「保存并关闭」", ACC, 12)
        except Exception as e:
            self.toast("🔑 打开配置文件失败", str(e), BAD, 8)


    def _fill_bailian(self, model=None):
        """一键填入阿里云百炼(DashScope OpenAI兼容)地址与模型, 并把光标送到密钥框。"""
        m = model or CameraPanel.BAILIAN_MODEL
        if "vl" in m:
            self.set_cloud("阿里云百炼·视觉")      # 先切算力模式(它会改地址/模型)
        self.remote.url_var.set(CameraPanel.BAILIAN_URL)
        self.remote.m_var.set(m)
        try:                                     # 预设名放最后, 保证不被覆盖
            self.remote.preset_var.set(
                "阿里云百炼·视觉(qwen-vl-plus)" if "vl" in m
                else "阿里云百炼·通义千问")
        except Exception:
            pass
        self.cfg_dirty()
        try:
            self.key_entry.focus_set()
        except Exception:
            pass
        self.refresh_api_state()
        self.toast("☁ 阿里云百炼已填好",
                   "地址: %s\n模型: %s\n现在把「阿里云百炼API-Key」粘贴到上面的"
                   "「API密钥」框 → 保存并关闭" % (CameraPanel.BAILIAN_URL, m),
                   ACC, 12)
        self.think("MODEL", "☁ 已切换到阿里云百炼: %s · %s(把百炼API-Key填进密钥框即可)"
                   % (CameraPanel.BAILIAN_URL, m))

    def _test_api_vision(self):
        """用一张合成测试图走一遍"发图→视觉模型回答", 直接验证视觉通道。"""
        try:
            url, key, model = self.remote.build_request_snapshot()
        except Exception:
            url, key, model = "", "", ""
        if not url or not model:
            try:
                self.api_state.configure(text="⚠ 请先填写接口地址与模型名", fg=BAD)
            except Exception:
                pass
            return
        if not vision_capable(model):
            try:
                self.api_state.configure(
                    text="⚠ 该模型名看不出视觉能力: %s(视觉请用 qwen-vl-plus / gpt-4o)"
                    % model, fg=WARN)
            except Exception:
                pass
        else:
            try:
                self.api_state.configure(text="🖼 正在把测试图发给 %s …" % model, fg=WARN)
            except Exception:
                pass
        self.think("MODEL", "🖼 视觉通道测试: %s · %s · 密钥 %s"
                   % (url, model, mask_key(key)))

        def make_img():
            if not HAVE_CV2:
                return None
            import numpy as np
            img = np.zeros((240, 320, 3), dtype=np.uint8)
            img[:, :] = (60, 60, 60)
            cv2.rectangle(img, (20, 150), (300, 210), (90, 90, 120), -1)
            cv2.circle(img, (160, 90), 40, (0, 200, 255), -1)
            p = os.path.join(CAM_DIR, "temp", "vision_test.jpg")
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
            except Exception:
                pass
            return p if imwrite_u(p, img) else None

        def work():
            try:
                p = make_img()
                b64 = b64_image(p) if p else None
                if not b64:
                    return ("err", "无法生成测试图片(OpenCV不可用)")
                out = LLMClient.remote_chat_vision(
                    url, key, model,
                    "这是一张测试图片。请一句话描述你看到的形状与颜色, 并回复"
                    "「视觉通道正常」。", b64, timeout=90)
                return ("ok", str(out))
            except Exception as e:
                return ("err", str(e))

        def done(kind, out):
            try:
                if kind == "ok":
                    self.api_state.configure(text="✅ 视觉通道正常: %s" % out[:150],
                                             fg=OK)
                    self.toast("🖼 视觉通道正常", "模型 %s 回复: %s"
                               % (model, out[:80]), OK, 9)
                    self.think("MODEL", "✅ 视觉通道测试通过(%s): %s"
                               % (model, out[:80]))
                else:
                    self.api_state.configure(text="❌ 视觉测试失败: %s" % out[:300],
                                             fg=BAD)
                    self.toast("🖼 视觉测试失败", out[:220], BAD, 10)
                    self.think("MODEL", "⚠ 视觉通道测试失败: %s" % out[:200])
            except Exception:
                pass

        def run():
            r = work()
            self.push_ui(lambda: done(*r))
        self.go_thread(run)

    # ------------------------------------------------ 配置 ----
    def _load_cfg_to_engine(self):
        eng = self.engine
        c = self.cfg.get("student", {})
        eng.student_name = str(c.get("name", "小原"))[:12] or "小原"
        g = c.get("grade")
        if g in GRADES:
            eng.grade_idx = GRADES.index(g)
        else:
            eng.grade_idx = int(clamp(int(c.get("grade_idx", 6)), 0, 11))
        if c.get("state") in STATE_OPTS:
            eng.learn_state = c["state"]
        rk = c.get("role")
        if rk in ROLE_MODELS:
            eng.role_key = rk
        s = self.cfg.get("sim", {})
        eng.sim_day = int(clamp(int(s.get("day", 0)), 0, HORIZON_DAYS - 1))
        dims = s.get("dims")
        if isinstance(dims, dict):
            for k in DIM_KEYS:
                if k in dims:
                    eng.student.dims[k] = clamp(float(dims[k]), 0.0, 1.0)
        eng.student.attention = clamp(float(s.get("attention", 0.85)), 0, 1)
        eng.student.fatigue = clamp(float(s.get("fatigue", 0.15)), 0, 1)
        eng.student.retention = clamp(float(s.get("retention", 1.0)), 0.4, 1)
        eng.auto_lesson_count = int(s.get("lessons", 0))

    def _apply_cfg_to_ui(self):
        try:
            self.name_var.set(self.engine.student_name)
            self.grade_var.set(GRADES[self.engine.grade_idx])
            self.state_var.set(self.engine.learn_state)
            self.role_var.set("%s %s" % (ROLE_MODELS[self.engine.role_key]["emoji"],
                                         ROLE_MODELS[self.engine.role_key]["label"]))
        except Exception:
            pass
        try:
            self.local.base_var.set(str(self.cfg.get("local", {}).get("base",
                                    LOCAL_DEFAULT)))
            m = self.cfg.get("local", {}).get("model")
            if m:
                self.local.model_var.set(str(m))
        except Exception:
            pass
        try:
            r = self.cfg.get("remote", {})
            if r.get("url"):
                self.remote.url_var.set(str(r["url"]))
            if r.get("key"):
                self.remote.key_var.set(str(r["key"]))
            if r.get("model"):
                self.remote.m_var.set(str(r["model"]))
        except Exception:
            pass
        try:
            cm = self.cfg.get("camera", {})
            self.camera.src_var.set(str(cm.get("source", "0")))
            if cm.get("cloud") in ("本机优先", "阿里云百炼·视觉", "阿里云EAS·自定义"):
                self.camera.cloud_var.set(cm["cloud"])
            if cm.get("interval"):
                try:
                    self.camera.rt_iv.delete(0, "end")
                    self.camera.rt_iv.insert(0, str(int(cm["interval"])))
                except Exception:
                    pass
        except Exception:
            pass

    def cfg_dirty(self):
        if self._save_job is not None:
            try:
                self.root.after_cancel(self._save_job)
            except Exception:
                pass
        self._save_job = self.root.after(1600, self.save_cfg)

    def save_cfg(self):
        self._save_job = None
        eng = self.engine
        cfg = {"student": {"name": eng.student_name,
                           "grade": GRADES[eng.grade_idx],
                           "grade_idx": eng.grade_idx,
                           "state": eng.learn_state, "role": eng.role_key},
               "sim": {"day": eng.sim_day, "lessons": eng.auto_lesson_count,
                       "attention": round(eng.student.attention, 4),
                       "fatigue": round(eng.student.fatigue, 4),
                       "retention": round(eng.student.retention, 4),
                       "dims": {k: round(eng.student.dims[k], 4)
                                for k in DIM_KEYS}}}
        try:
            cfg["local"] = {"base": self.local.base_var.get(),
                            "model": self.local.model_var.get()}
        except Exception:
            pass
        try:
            cfg["remote"] = {"url": self.remote.url_var.get(),
                             "key": self.remote.key_var.get(),
                             "model": self.remote.m_var.get()}
        except Exception:
            pass
        try:
            cfg["camera"] = {"source": self.camera.src_var.get(),
                             "cloud": self.camera.cloud_var.get(),
                             "auto": True,
                             "interval": self.camera.rt_iv.get()}
        except Exception:
            pass
        cfg_save(cfg, CFG_PATH)

    def cfg_local_base(self):
        try:
            return self.local.base_var.get().strip() or LOCAL_DEFAULT
        except Exception:
            return LOCAL_DEFAULT

    # ------------------------------------------------ 线程与队列 ----
    def go_thread(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    def push_ui(self, fn):
        try:
            self.ui_q.put(fn)
        except Exception:
            pass

    def _drain_ui(self):
        for _ in range(64):
            try:
                fn = self.ui_q.get_nowait()
            except Exception:
                return
            try:
                fn()
            except Exception:
                pass

    def think(self, kind, msg, dur=None):
        self.engine.emit(kind, msg, dur)
        self.feed_pending()

    def think_text(self, kind, msg):
        """思考区直接输出(不入引擎历史, 用于压缩模拟等批量日志)。"""
        try:
            self.thinkzone.feed(kind, msg)
        except Exception:
            pass

    def feed_pending(self):
        h = self.engine.history
        try:
            while self._feed_idx < len(h):
                ev = h[self._feed_idx]
                self._feed_idx += 1
                self.thinkzone.feed(ev[0], ev[1], ev[2] if len(ev) > 2 else None)
        except Exception:
            pass

    def toast(self, title, body="", color=ACC, ttl=7):
        try:
            self.toaster.show(title, body, color, ttl)
        except Exception:
            pass

    def status_set(self, color, text):
        try:
            self.status.configure(text="● %s" % text, fg=color)
        except Exception:
            pass

    # ------------------------------------------------ 引擎联动 ----
    def engine_ui_refresh(self):
        self.feed_pending()
        try:
            self.progress.set_targets()
        except Exception:
            pass
        try:
            self.toolbar_refresh()
        except Exception:
            pass
        try:                                  # 修炼面板(窗口已创建且可见时刷新)
            if self.dlg_level.state() != "withdrawn":
                self.level.refresh()
        except Exception:
            pass

    def do_action(self, aid):
        if self.engine.real_day >= HORIZON_DAYS - 1:
            self.toast("🏁 K12 全部完成", "已学满4380天; 可切换榜样模型/年级继续", VIOLET)
            return
        eng = self.engine
        subj, topic, _ = eng.current_topic()
        eng.perform_action(aid, "④面板打卡")
        try:
            self.vault.record_day(eng, "action", {
                "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "动作": ACT_BY_ID[aid][1], "学科": subj, "知识点": topic,
                "成长分": round(eng.student.score5(), 4),
                "学习日序号": eng.sim_day})
            # 学习日切换 → 生成/更新当日档案(Word+Markdown+JSON 三格式)
            absd = abs_day_of(eng)
            if absd != self._last_arch_abs:
                self._last_arch_abs = absd
                self.vault.archive_day(eng)
            if eng.sim_day % 100 == 0:
                self.vault.save_csv(eng)
            self.vault.save_learning_trajectory(eng)
        except Exception:
            pass
        self.engine_ui_refresh()

    def practice_art(self, key):
        """修炼一式九字秘法: 推进1个学习日, 并把结果记入该式的独立修为。"""
        art = ART_BY_KEY.get(key)
        if art is None:
            return
        eng = self.engine
        if eng.real_day >= HORIZON_DAYS - 1:
            self.toast("🏁 K12 全部完成", "已学满4380天; 可切换榜样模型/年级继续", VIOLET)
            return
        got, _ev = eng.practice_art(key, source="🀄修炼面板")
        if not got:
            return
        subj, topic, _ = eng.current_topic()
        try:
            self.vault.record_day(eng, "action", {
                "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "动作": "秘法·%s" % art["ch"], "学科": subj, "知识点": topic,
                "成长分": round(eng.student.score5(), 4),
                "学习日序号": eng.sim_day})
            self.vault.save_learning_trajectory(eng)
            self.vault.save_level_rating(eng)
        except Exception:
            pass
        sk = eng.skills.get(art_skill_id(key))
        m = sk.mastery if sk else 0.0
        self.toast("🀄 秘法「%s·%s」修炼" % (art["ch"], art["name"]),
                   "%s\n当前修为 %.0f%% · 段位 %s\n%s"
                   % (art["tip"], m * 100, tier_of(m), art["key_point"]), ACC, 6)
        self.engine_ui_refresh()

    # -------------------------------------------- 教材投喂 · 自动学习 -------
    def toggle_material(self):
        if getattr(self, "material_days_left", 0) > 0:
            self.stop_material()
        else:
            self.ingest_material()

    def ingest_material(self):
        """选择课本/练习(文件夹或单个文件) → 扫描切分 → 装载并开始自动学习。"""
        from tkinter import filedialog
        path = filedialog.askdirectory(
            title="选择课本/练习所在文件夹(若只想投一个文件, 点取消后再选)")
        if not path:
            path = filedialog.askopenfilename(
                title="选择单个课本/练习文件",
                filetypes=[("教材/练习", "*.pdf *.docx *.txt *.md *.png *.jpg *.jpeg"),
                           ("全部文件", "*.*")])
        if not path:
            return
        self.think("SYS", "📚 教材投喂: 正在扫描并切分 %s …" % path)
        self.toast("📚 正在解析教材", "%s\nPDF 需 pypdf; 图片/扫描页需视觉模型" % path,
                   ACC, 6)

        def work():
            ing = MaterialIngestor()
            bk = ing.ingest([path],
                            title=os.path.basename(str(path).rstrip("\\/")) or "教材")
            self.push_ui(lambda: self._material_ready(bk, ing))

        self.go_thread(work)

    def _material_ready(self, book, ing):
        st = book.stats()
        self.engine.load_material(book)
        try:
            self.vault.ensure()
            book.save(os.path.join(CAM_DIR, "数据集", "material_map.json"))
            self.vault.save_level_rating(self.engine)
        except Exception:
            pass
        for n in ing.notes[:4]:
            self.think("TIP", "⚠ %s" % n)
        self.think("GOAL", "📚 知识地图: 章%d 节%d 知识点%d 练习%d题 — 开始按真实课本自动学习"
                   % (st["chapters"], st["sections"], st["points"], st["questions"]))
        self.toast("📚 教材已装载",
                   "章%d 节%d 知识点%d 练习%d题\n接下来按课本顺序自动学习(点按钮可停)"
                   % (st["chapters"], st["sections"], st["points"], st["questions"]),
                   ACC, 8)
        self.material_days_left = 30
        self._material_tick()

    def _material_tick(self):
        try:
            if self._closing or getattr(self, "material_days_left", 0) <= 0:
                self.btn_mat.configure(text="📚 教材投喂")
                return
            self.material_days_left -= 1
            self.btn_mat.configure(text="⏸ 停止(%d天)" % self.material_days_left)
            self.engine.study_material_day()
        except Exception as e:
            self.think("TIP", "⚠ 自动学习中断: %s" % e)
            self.material_days_left = 0
        self.engine_ui_refresh()
        if getattr(self, "material_days_left", 0) > 0:
            self.root.after(1400, self._material_tick)

    def stop_material(self):
        self.material_days_left = 0
        self.btn_mat.configure(text="📚 教材投喂")
        self.think("SYS", "⏸ 教材自动学习已暂停(再点「📚 教材投喂」可继续投喂其它材料)")

    def archive_all_btn(self, auto=False):
        """一键把 6-18岁 4380 天逐日生成档案(Word+Markdown+JSON+训练语料)。"""
        if self._archiving:
            self.toast("📚 档案生成中", "正在后台生成 4380 天档案, 请稍候…", WARN, 5)
            return
        if not self.engine.traj_rows:
            self.toast("📚 暂无轨迹数据", "请先打卡/MCTS/压缩模拟几天, 再生成档案", WARN, 6)
            return
        self._archiving = True

        def progress(ok, total, tag):
            if tag:
                self.push_ui(lambda: self.status_set(WARN, "📚 4380天档案生成开始…"))
            else:
                self.push_ui(lambda: self.think_text(
                    "SYS", "📚 档案生成进度: %d/%d 天" % (ok, total)))

        def work():
            try:
                ok, total = self.vault.build_all_docs(self.engine, progress)
                corp_p, n = self.vault.build_corpus(self.engine)
                self.vault.save_learning_trajectory(self.engine)
                self.push_ui(lambda: self.toast(
                    "📚 4380天档案生成完成",
                    "逐日档案 %d/%d 天(Word+Markdown+JSON) + 训练语料 %d 条\n%s"
                    % (ok, total, n, self.vault.root), VIOLET, 12))
                self.push_ui(lambda: self.think_text(
                    "SYS", "📚 数据集已就绪: %d天档案(三格式) + 训练语料 %d条 → 可用于大模型训练, "
                           "程序下次启动将回读并经验回放进化" % (ok, n)))
            except Exception as e:
                self.push_ui(lambda: self.toast("📚 档案生成失败", str(e)[:200], BAD, 8))
            finally:
                self._archiving = False
        self.go_thread(work)

    def maybe_apply_plan(self):
        eng = self.engine
        if eng.last_plan:
            aid = eng.last_plan[0]
            eng.last_plan = None
            eng.perform_action(aid, "MCTS最优路径")
            self.engine_ui_refresh()

    # ------------------------------------------------ 周期任务 ----
    def _tick(self):
        if self._closing:
            return
        self._drain_ui()
        try:
            self.camera.tick()
        except Exception:
            pass
        try:
            self.progress.refresh()
        except Exception:
            pass
        try:
            self.toolbar_refresh()
        except Exception:
            pass
        # 曲线按需重绘(引擎推进时才重画, 避免每帧重建)
        key = (len(self.engine.perf_history), int(self.engine.real_day))
        if key != self._curve_key:
            self._curve_key = key
            try:
                self.progress._draw_curve()
            except Exception:
                pass
        # 自动领航
        if self.progress.pilot_var.get() and not self.progress.sim_running \
                and time.time() >= self._pilot_next:
            self._pilot_next = time.time() + 1.5
            self.pilot_step()
        self.root.after(80, self._tick)

    def pilot_step(self):
        eng = self.engine
        if eng.real_day >= HORIZON_DAYS - 1:
            self.progress.pilot_var.set(False)
            self.toast("🏁 自动领航结束", "4380天K12学习历程全部完成, 空白学生体已长成", VIOLET)
            return
        stage, _ = eng.stage()
        if eng.auto_lesson_count % 7 == 0:
            eng.plan_mcts()
            aid = eng.last_plan[0] if eng.last_plan else "jiangjie"
            eng.last_plan = None
        else:
            aid = MCTSPlanner.greedy_decide(eng.student, eng.difficulty_of_topic(),
                                            stage, eng.real_day,
                                            eng.action_weights)
        eng.perform_action(aid, "自动领航", note=False)
        try:
            if eng.sim_day % 10 == 0:
                self.vault.record_day(eng, "action", {
                    "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "动作": ACT_BY_ID[aid][1], "来源": "自动领航",
                    "成长分": round(eng.student.score5(), 4)})
            absd = abs_day_of(eng)
            if absd != self._last_arch_abs:
                self._last_arch_abs = absd
                self.vault.archive_day(eng)
            if eng.sim_day % 200 == 0:
                self.vault.save_csv(eng)
        except Exception:
            pass
        self.engine_ui_refresh()
        self.toast("✈ 自动领航 第%d天" % eng.sim_day,
                   "执行「%s」 · 成长分 %.2f/5 · %s"
                   % (ACT_BY_ID[aid][1], eng.student.score5(),
                      eng.topic_hint_text()), ACC, 3)

    # ------------------------------------------------ 启动/关闭 ----
    def _welcome(self):
        eng = self.engine
        eng.emit("SYS", "🎓 %s v%s 启动 | 空白学生体: %s · %s · 榜样终点:%s"
                % (APP_NAME, APP_VER, eng.student_name,
                   GRADES[eng.grade_idx], eng.role()["label"]))
        eng.emit("STATUS", "📊 起点学情: %s(%s) | 剩余K12学习日 %d | 成长分 %.2f/5"
                % (age_str(eng.real_day), eng.grade_label(), eng.remain_days,
                   eng.student.score5()))
        eng.emit("GOAL", "🎯 终点参照: %s | %s" % (eng.role()["label"],
                                                 eng.milestone_note(eng.real_day)))
        # ---- 回读数据仓库 → 经验回放进化 ----
        try:
            stats = self.vault.scan()
            if stats.get("days"):
                boost = min(0.12, 0.01 * math.log(1 + stats["days"]))
                eng.student.retention = clamp(eng.student.retention + boost, 0.5, 1.0)
                eng.emit("SYS", "📚 数据仓库回读: 已读取 %d 天历史档案(%d份Word/%d段视频/"
                         "%d份分析), 经验回放启动 → 记忆保持率 +%.1f%%"
                         % (stats["days"], stats.get("docs", 0),
                            stats.get("videos", 0), stats.get("analyses", 0),
                            boost * 100))
                eng.emit("GOAL", "🧬 进化机制: 档案越多 → ai学生越强; 目标: 0-100岁ai数据学生"
                         " (当前K12段=绝对日%d~6569)" % AGE0_DAYS)
            rows = self.vault.load_trajectory()
            n = eng.fit_from_rows(rows)
            loaded = self.vault.load_learning_trajectory(eng)
            if loaded and (loaded.get("episodes") or loaded.get("skills")
                           or loaded.get("errors")):
                eng.emit("SYS", "🧭 学习轨迹回读: %d技能 / %d错误 / %d学习事件 已恢复, "
                                "经验回放继续"
                         % (loaded.get("skills", 0), loaded.get("errors", 0),
                            loaded.get("episodes", 0)))
            if n:
                _ord = {a[0]: i for i, a in enumerate(ACTIONS)}
                eng.emit("SYS", "🧬 数据驱动层: 已回读%d天轨迹并拟合教学动作权重 → %s"
                         % (n, ", ".join("%s×%.2f" % (ACT_BY_ID[a][1], w)
                                        for a, w in sorted(
                                            eng.action_weights.items(),
                                            key=lambda kv: _ord[kv[0]]))))
        except Exception:
            pass
        self.feed_pending()
        self.toast("🎓 %s 已就绪" % APP_NAME,
                   "①本地模型自动探测(默认 deepseek-r1:7b) | ②外部API加强评分 | "
                   "④打卡/MCTS/压缩模拟 | 摄像头: 一键打开·录制·双模型实时分析 | "
                   "数据仓库: %s" % CAM_DIR, ACC, 12)

    def _startup_camera(self):
        try:
            self.camera.start_camera()
        except Exception:
            pass

    def close(self):
        if self._closing:
            return
        self._closing = True
        try:
            self.progress.sim_stop.set()
        except Exception:
            pass
        try:
            self.camera.close()
        except Exception:
            pass
        try:
            self.vault.save_csv(self.engine)
            self.vault.save_learning_trajectory(self.engine)
        except Exception:
            pass
        self.save_cfg()
        try:
            self.root.destroy()
        except Exception:
            pass


# ============================================================ 自检 ===========

def run_selftest():
    """逻辑自检(无界面): 成长曲线/MCTS/学生生长/时间压缩/配置等。"""
    log = []
    fails = 0
    total_checks = [0]

    def check(name, ok, detail=""):
        nonlocal fails
        total_checks[0] += 1
        if not ok:
            fails += 1
        log.append("[%s] %s %s" % ("PASS" if ok else "FAIL", name, detail))
        print("[%s] %s %s" % ("PASS" if ok else "FAIL", name, detail))

    # 1) S型曲线单调 + 反函数往返
    ok_curve = True
    for i in range(0, 101):
        d = i / 100.0 * HORIZON_DAYS
        v = GrowthCurve.ideal(d)
        if not (0 <= v <= 5):
            ok_curve = False
        d2 = GrowthCurve.inverse(v)
        if abs(d2 - d) > 3.0:
            ok_curve = False
    ok_curve = ok_curve and GrowthCurve.ideal(0) < GrowthCurve.ideal(2000) < \
        GrowthCurve.ideal(4379)
    check("成长曲线: 单调有界且反函数往返", ok_curve)

    # 2) 空白学生体: 5000次随机教学行为(含休息), 边界与单调性
    st = StudentState()
    before = st.aggregate()
    ok_bounds, up = True, 0
    for i in range(5000):
        aid = ACTIONS[i % 5][0] if i % 7 else "xiuxi"
        d = 0.3 + (i % 100) / 100.0 * 0.6
        st.apply(aid, d, "规则内化期")
        if not all(0 <= st.dims[k] <= 1.0 for k in DIM_KEYS) or \
                not (0 <= st.fatigue <= 1.0) or not (0 <= st.attention <= 1.0):
            ok_bounds = False
    check("空白学生体: 状态有界", ok_bounds,
          "期末 aggregate=%.4f (起始%.4f)" % (st.aggregate(), before))

    # 3) MCTS 决策 + 自适应迭代
    t0 = now_ms()
    eng_t = AIStudentEngine()
    best, stats, ms = MCTSPlanner(iterations=46, depth=4).decide(
        eng_t.student, eng_t.real_day, eng_t.difficulty_of_topic(), eng_t.stage()[0])
    ok_mcts = best in ACT_BY_ID and len(stats) == len(ACTIONS) and ms < 3000
    check("MCTS决策: 返回合法动作且快速", ok_mcts,
          "best=%s %.0fms" % (best, ms))
    best2, _s2, _ms2 = eng_t.mcts.decide(
        eng_t.student, eng_t.real_day, eng_t.difficulty_of_topic(),
        eng_t.stage()[0], weights=eng_t.action_weights)
    check("MCTS自适应: 迭代数随时间预算收敛", 24 <= eng_t.mcts.last_iters <= 220,
          "last_iters=%d (预算%dms)" % (eng_t.mcts.last_iters,
                                       eng_t.mcts.time_budget_ms))

    # 4) 时间压缩: 从小一(6岁)完整模拟4380天
    eng = AIStudentEngine()
    eng.grade_idx = 0
    t0 = now_ms()
    done = eng.simulate_days(4380, chunk=200)
    dur = now_ms() - t0
    final = eng.student.score5()
    ideal_f = GrowthCurve.ideal(eng.real_day)
    ok_sim = done == 4380 and 0.5 < final <= 5.0 and len(eng.perf_history) > 500
    check("时间压缩: 4380天模拟完整性与成长收敛", ok_sim,
          "done=%d 用时%.0fms 成长分=%.3f/5 同龄理想=%.3f" % (done, dur, final, ideal_f))
    if not ok_sim:
        log.append("模拟轨迹: " + str(list(eng.perf_history)[::400][:14]))
    # 各认知阶段均被触发
    stages = set()
    for d in range(0, 4380, 40):
        stages.add(stage_of_day(d)[0])
    check("认知阶段演进: 四阶段齐备", len(stages) == 4, str(sorted(stages)))
    # 双时间轴
    equiv, gap, sc, iv = eng.dual_timeline()
    check("双时间轴: 等效年龄在有效区间", 0 <= equiv <= HORIZON_DAYS - 1,
          "gap=%d天 score=%.2f" % (gap, sc))
    # 数据驱动层: 从4380天轨迹拟合动作权重
    n_fit = eng.fit_from_rows(eng.traj_rows)
    w_ok = n_fit >= 1000 and all(0.75 <= w <= 1.25
                                 for w in eng.action_weights.values())
    check("数据驱动层: 轨迹回读拟合动作权重", w_ok and eng.data_driven,
          "拟合%d天, 权重=%s" % (n_fit, ", ".join(
              "%.2f" % w for w in eng.action_weights.values())))

    # 4.5) 学习轨迹系统(v3): 4380天压缩模拟应产生大量学习事件与技能状态
    ok_traj = (len(eng.episodes) >= 1000 and len(eng.skills) >= 1
               and len(eng.memory_records) >= 1000)
    check("学习轨迹: 4380天压缩模拟产生学习事件", ok_traj,
          "episodes=%d skills=%d errors=%d memory=%d"
          % (len(eng.episodes), len(eng.skills), len(eng.errors),
             len(eng.memory_records)))

    # 4.6) SkillState / ErrorRecord / LearningEpisode 闭环与持久化往返
    eng_v = AIStudentEngine()
    eng_v.grade_idx = 6
    eng_v.sim_day = 120
    subj, topic, _ = eng_v.current_topic()
    sk0 = eng_v.get_or_create_skill(subj, topic)
    before0 = sk0.mastery
    ep0 = eng_v._assess_and_record("liti", quiet=True)
    after_skill = eng_v.get_or_create_skill(subj, topic)
    ok_ep = (ep0 is not None and ep0.skill == topic and ep0.episode_id
             and abs(ep0.before_mastery - before0) < 1e-6
             and ep0.after_mastery is not None)
    ok_skill = after_skill.attempts >= 1 and 0.0 <= after_skill.mastery <= 1.0
    check("学习轨迹: LearningEpisode 闭环与 SkillState 更新", ok_ep and ok_skill,
          "事件%d条 掌握%.3f→%.3f" % (len(eng_v.episodes), before0,
                                       after_skill.mastery))
    eng_v._record_error(after_skill, "formula", "公式错误", "公式记忆有误", "重新推导")
    rec = ErrorRecord("x::y", "calc", "计算错误", "计算粗心", "逐行验算")
    rec.hit(3); rec.hit(5); rec.hit(5)
    check("学习轨迹: ErrorRecord 记录与复发统计",
          rec.count == 3 and rec.recurrence_count >= 1,
          "count=%d recurrence=%d" % (rec.count, rec.recurrence_count))
    import tempfile as _tf4
    import shutil as _shutil
    vroot2 = os.path.join(_tf4.gettempdir(), "ai_student_traj_test")
    _shutil.rmtree(vroot2, ignore_errors=True)
    v3 = DataVault()
    v3.root = vroot2
    v3.ensure()
    eng_v._episode_flushed = 0
    eng_v._memory_flushed = 0
    v3.save_learning_trajectory(eng_v)
    files_ok = (os.path.exists(v3.episodes_path()) and
                os.path.exists(v3.skills_path()) and
                os.path.exists(v3.errors_path()) and
                os.path.exists(v3.memory_path()))
    eng_v2 = AIStudentEngine()
    loaded = v3.load_learning_trajectory(eng_v2)
    load_ok = (loaded and loaded.get("episodes", 0) >= 1
               and loaded.get("skills", 0) >= 1)
    check("学习轨迹: 持久化与回读(episodes/skills/errors/memory)",
          files_ok and load_ok, str(loaded))
    _shutil.rmtree(vroot2, ignore_errors=True)

    # 5) 知识点游标多样性
    eng3 = AIStudentEngine()
    subs = set()
    for dd in range(0, 1600, 20):
        eng3.sim_day = dd
        subs.add(eng3.current_subject())
    check("知识点游标: 学科轮换覆盖多科", len(subs) >= 3, str(sorted(subs)))

    # 6) 提示词
    p = eng_t.build_system_prompt()
    check("导师提示词构建", eng_t.student_name in p and "AI学生" in p,
          "%d字" % len(p))

    # 7) 配置往返
    import tempfile
    tpath = os.path.join(tempfile.gettempdir(), "ai_student_cfg_test.json")
    cfg_save({"a": 1, "学生": "小原"}, tpath)
    back = cfg_load(tpath)
    check("配置存取往返", back.get("a") == 1 and back.get("学生") == "小原", tpath)
    try:
        os.remove(tpath)
    except Exception:
        pass

    # 8) 按日档案: Word+Markdown+JSON 自动生成 & 回读
    import tempfile as _tf
    import shutil
    vroot = os.path.join(_tf.gettempdir(), "ai_student_vault_test")
    shutil.rmtree(vroot, ignore_errors=True)
    vault = DataVault()
    vault.root = vroot
    vault.ensure()
    vault.write_manifest()
    eng.record_test_flag = None
    vault.record_day(eng, "action", {"时间": "2026-01-01 00:00:00",
                                     "动作": "反思总结", "学科": "物理",
                                     "知识点": "万有引力"})
    d = vault.archive_day(eng)
    ok_docs = False
    if d:
        ok_docs = (os.path.exists(os.path.join(d, os.path.basename(
            vault.day_json(eng)).replace(".json", "_学情档案.md"))) and
            os.path.exists(os.path.join(d, os.path.basename(
                vault.day_json(eng)).replace(".json", "_学情档案.docx"))))
    corp_p, n = vault.build_corpus(eng)
    stats = vault.scan()
    check("按日档案: 三格式生成 + 语料 + 回读扫描",
          ok_docs and n > 100 and stats.get("days", 0) >= 1 and
          stats.get("docs", 0) >= 1,
          "语料%d条, 档案%d天, %s" % (n, stats.get("days", 0), vroot))
    shutil.rmtree(vroot, ignore_errors=True)

    # 8) 摄像头可用性(仅提示)
    if HAVE_CV2:
        cap = None
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(0)
            ok_cam = cap.isOpened()
        except Exception:
            ok_cam = False
        if cap is not None:
            cap.release()
        print("[INFO] 本机摄像头可用: %s (自检不依赖摄像头)" % ok_cam)
        log.append("[INFO] 本机摄像头可用: %s" % ok_cam)
    else:
        print("[INFO] OpenCV 未安装, 跳过摄像头探测")
        log.append("[INFO] OpenCV 未安装, 跳过摄像头探测")

    # 9) 中文路径 + 上传视频链路: 合成视频(中文名/中文目录) → 完整分析 → 档案
    if HAVE_CV2:
        import tempfile as _tf3
        probe_dir = os.path.join(_tf3.gettempdir(), "ai学生_中文目录_自检")
        old_cam = globals().get("CAM_DIR")
        try:
            shutil.rmtree(probe_dir, ignore_errors=True)
            os.makedirs(probe_dir, exist_ok=True)
            import numpy as _np
            src_video = os.path.join(probe_dir, "自检视频_中文名.mp4")
            writer = None
            for codec, ext in (("mp4v", ".mp4"), ("MJPG", ".avi")):
                try:
                    cand = os.path.join(probe_dir, "自检视频_中文名" + ext)
                    writer = cv2.VideoWriter(cand, cv2.VideoWriter_fourcc(*codec),
                                             12.0, (320, 240))
                    if writer.isOpened():
                        src_video = cand
                        break
                    writer.release()
                    writer = None
                except Exception:
                    writer = None
            ok_syn = False
            if writer is not None:
                for i in range(48):
                    fr = _np.full((240, 320, 3), 40, dtype=_np.uint8)
                    cv2.circle(fr, (40 + (i * 5) % 260, 120), 26, (0, 200, 255), -1)
                    writer.write(fr)
                writer.release()
                ok_syn = True
            globals()["CAM_DIR"] = os.path.join(probe_dir, "data vault")
            res_v = run_video_analysis(
                src_video,
                cfg={"local_base": "http://127.0.0.1:9",   # 未监听端口 → 立即失败
                     "local_model": LOCAL_MODEL_DEFAULT,
                     "remote_url": "", "remote_key": "", "remote_model": ""},
                do_remote=False) if ok_syn else {"ok": False}
            folder_v = res_v.get("folder") or ""
            names = os.listdir(folder_v) if os.path.isdir(folder_v) else []
            docx_ok = False
            for fn in names:
                if fn.endswith(".docx"):
                    try:
                        with zipfile.ZipFile(os.path.join(folder_v, fn)) as z:
                            docx_ok = "word/document.xml" in z.namelist()
                    except Exception:
                        docx_ok = False
            frames_ok = any(fn.startswith("frame_") for fn in names)
            md_ok = any(fn.endswith(".md") for fn in names)
            js_ok = any(fn.endswith(".json") for fn in names)
            check("上传视频链路: 中文路径→英文临时→采样6帧→档案(Word/MD/JSON)",
                  bool(ok_syn and res_v.get("ok") and docx_ok and frames_ok
                       and md_ok and js_ok),
                  "档案=%s · Word=%s 采样帧=%s MD=%s JSON=%s"
                  % (os.path.basename(folder_v), docx_ok, frames_ok, md_ok, js_ok))
        except Exception as e:
            check("上传视频链路: 中文路径→英文临时→采样6帧→档案(Word/MD/JSON)",
                  False, "异常: %s" % e)
        finally:
            if old_cam:
                globals()["CAM_DIR"] = old_cam
            shutil.rmtree(probe_dir, ignore_errors=True)
    else:
        print("[INFO] OpenCV 未安装, 跳过上传视频链路自检")
        log.append("[INFO] OpenCV 未安装, 跳过上传视频链路自检")

    # 16) 境界体系: 四境首尾相接, 连续覆盖 6-18 岁
    ok_realm = True
    for i in range(len(REALMS) - 1):
        if REALMS[i]["day"][1] != REALMS[i + 1]["day"][0]:
            ok_realm = False
    ok_realm = (ok_realm and REALMS[0]["day"][0] < 0
                and REALMS[-1]["day"][1] == 12 * 365
                and [r["age"][0] for r in REALMS] == [0, 6, 12, 15])
    seq = [realm_of_day(d)["name"] for d in (0, 2189, 2190, 3284, 3285, 4379, 99999)]
    ok_realm = ok_realm and seq == ["立榜境", "立榜境", "分科境", "分科境",
                                    "精进境", "精进境", "精进境"]
    check("境界体系: 四境连续覆盖 6-18 岁", ok_realm,
          "→".join(seq[:6]) + " (越界钳位=%s)" % seq[-1])

    # 17) 统一评价标准: 修为提升 → 水平境界与榜位单调不降
    eng_r = AIStudentEngine()
    eng_r.grade_idx = 0
    prev_key, ok_rank, n_step = -1, True, 0
    for _ in range(44):
        r = eng_r.level_rating()
        key = r["rank_global"]
        if key < prev_key:
            ok_rank = False
        prev_key = key
        n_step += 1
        eng_r.simulate_days(100, chunk=100)
    r = eng_r.level_rating()
    check("统一评价: 修为提升→水平境界/榜位单调不降", ok_rank,
          "期末 修为%.2f → %s%s·%s 榜位%d/100(全局%d) 等效%s %s · 采样%d次"
          % (r["score5"], r["level_realm_emoji"], r["level_realm_name"],
             r["tier"], r["rank"], r["rank_global"], r["role_label"],
             r["equiv_age"], n_step))

    # 18) 九字秘法: 九式各有独立修为, 且与知识点技能分层
    eng_a = AIStudentEngine()
    eng_a.grade_idx = 0
    for a in NINE_ARTS:
        eng_a.practice_art(a["key"])
    arts = eng_a.arts_summary()
    kp_skills = [s for s in eng_a.skills if not s.startswith(ART_SKILL_PREFIX)]
    ok_art = (len(arts) == 9 and len(kp_skills) >= 1
              and all(x["mastery"] > 0 for x in arts)
              and all(eng_a.skills.get(art_skill_id(a["key"])) is not None
                      for a in NINE_ARTS))
    check("九字秘法: 九式独立修为且与知识点技能分层", ok_art,
          "九式均>0 · 平均修为%.0f%% · 知识点技能%d个"
          % (sum(x["mastery"] for x in arts) / 9 * 100, len(kp_skills)))

    # 19) 修炼档案落盘: 统一评价标准可导出且字段完整
    ok_dump, note_dump = False, ""
    try:
        import tempfile as _tf5
        dv = DataVault()
        dv.root = os.path.join(_tf5.gettempdir(), "ai_student_rating_test")
        p = dv.save_level_rating(eng_a)
        need = ("realm_name", "level_realm_name", "tier", "rank", "rank_global",
                "equiv_age", "trend", "arts", "arts_avg", "model", "next_realm",
                "milestone_done")
        data = {}
        if p and os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        ok_dump = (bool(p) and all(k in data for k in need)
                   and len(data.get("arts", [])) == 9)
        note_dump = "%s · 字段%d项 · 九式%d" % (os.path.basename(p or ""),
                                              len(data), len(data.get("arts", [])))
        shutil.rmtree(dv.root, ignore_errors=True)
    except Exception as e:
        note_dump = "异常: %s" % e
    check("修炼档案: 统一评价标准落盘(level_rating.json)", ok_dump, note_dump)

    # 20-22) 教材投喂 + 自动学习(内置样例, 不依赖外部文件)
    try:
        import tempfile as _tf6
        mdir = os.path.join(_tf6.gettempdir(), "ai_student_material_test")
        os.makedirs(mdir, exist_ok=True)
        txt_p = os.path.join(mdir, "样例教材.txt")
        with open(txt_p, "w", encoding="utf-8") as f:
            f.write("\n".join([
                "第一章 运动的描述",
                "1.1 质点 参考系",
                "在研究物体运动时，如果物体的大小和形状对所研究的问题没有影响，",
                "就可以把它看成一个有质量的点，这样的点叫作质点。",
                "第一章 运动的描述",                       # 页眉重复 → 必须过滤
                "练习与应用",
                "1. 以下各种说法中，哪些指时间间隔？哪些指时刻？",
                "2. 某市出租汽车的收费标准是 2.00 元/km，其中的千米说的是路程还是位移？",
                "实验：探究小车速度随时间变化的规律",
                "1. 了解打点计时器的构造，然后把它固定好。",  # 题号断裂 → 不算题
                "第二章 匀变速直线运动的研究",
                "1. 匀变速直线运动的速度与时间的关系",
                "速度公式描述了速度随时间的变化规律，是运动学的核心关系式之一。",
            ]))
        ing_m = MaterialIngestor()
        bk = ing_m.ingest([txt_p], title="样例教材")
        st_m = bk.stats()
        qs_m = bk.flat_questions()
        names_m = [c["title"] for c in bk.chapters]
        ok_mat = (st_m["points"] >= 2 and len(qs_m) >= 2
                  and names_m.count("第一章 运动的描述") == 1
                  and not any("打点计时器" in q[3] for q in qs_m))
        check("教材投喂: 切分章/节/知识点/习题(过滤页眉与断号)", ok_mat,
              "章%d 节%d 知识点%d 练习%d · 同名章=%d"
              % (st_m["chapters"], st_m["sections"], st_m["points"],
                 len(qs_m), names_m.count("第一章 运动的描述")))

        eng_m = AIStudentEngine()
        eng_m.grade_idx = 0
        eng_m.load_material(bk)
        for _ in range(4):
            eng_m.study_material_day(source="🧪自检")
        eps_m = [e for e in eng_m.episodes if "教材题" in (e.question or "")]
        n_art = sum(1 for a in NINE_ARTS if eng_m.art_mastery(a["key"]) > 0)
        check("教材自动学习: 真实题干进入学习事件并产生秘法修为",
              len(eng_m.episodes) >= 3 and bool(eps_m) and n_art >= 1,
              "学习事件%d条 · 含教材题%d条 · 已练秘法%d式"
              % (len(eng_m.episodes), len(eps_m), n_art))

        p_map = bk.save(os.path.join(mdir, "material_map.json"))
        ok_map = bool(p_map) and os.path.exists(p_map)
        if ok_map:
            with open(p_map, "r", encoding="utf-8") as f:
                d_map = json.load(f)
            ok_map = d_map.get("stats", {}).get("questions") == len(qs_m)
        check("教材知识地图: material_map.json 可落盘回读", ok_map,
              os.path.basename(p_map or ""))
        shutil.rmtree(mdir, ignore_errors=True)
    except Exception as e:
        check("教材投喂: 切分章/节/知识点/习题(过滤页眉与断号)", False, "异常: %s" % e)
        check("教材自动学习: 真实题干进入学习事件并产生秘法修为", False, "见上条异常")
        check("教材知识地图: material_map.json 可落盘回读", False, "见上条异常")

    print("-" * 66)
    print("SELFTEST RESULT: %s (%d/%d)" % (
        "ALL PASS" if fails == 0 else "%d FAILED" % fails,
        total_checks[0] - fails, total_checks[0]))
    env = os.environ.get("AI_STUDENT_TEST_LOG")
    if env:
        try:
            with open(env, "w", encoding="utf-8") as f:
                f.write("\n".join(log))
                f.write("\nRESULT: %s\n" % ("ALL PASS" if fails == 0 else "FAILED"))
        except Exception:
            pass
    return 1 if fails else 0


# ============================================================ 入口 ===========

def cli_test_video(path, do_remote=True):
    """命令行执行完整视频分析链路(无 GUI), 便于验证"上传视频→档案"。"""
    print("=" * 66)
    print("AI学生 · 视频分析链路命令行自检")
    print("视频: %s" % path)
    print("-" * 66)
    res = run_video_analysis(
        path, do_remote=do_remote,
        log=lambda kind, msg: print("  [%s] %s" % (kind, msg)),
        on_stage=lambda msg: print("  ... %s" % msg))
    if not res.get("ok"):
        print("-" * 66)
        print("结果: 失败 —— %s" % (res.get("error") or "未知错误"))
        return 1
    info = res.get("info") or {}
    print("-" * 66)
    print("视频信息: %s" % json.dumps(info, ensure_ascii=False))
    print("采样帧数: %s" % info.get("采样帧"))
    print("本地观察: %s" % (res.get("local") or "(未执行)"))
    print("外部评分: %s" % (res.get("remote") or "(未执行)"))
    print("综合评分: %s" % (res.get("score")
                          if res.get("score") is not None else "未取得"))
    print("档案路径: %s" % res.get("folder"))
    print("档案文件: %s" % ", ".join(os.path.basename(p)
                                     for p in res.get("files", [])))
    print("=" * 66)
    return 0


def cli_ingest(paths, subject="物理", study_days=0, out_dir="", use_vision=False):
    """命令行: 投喂教材(课本/练习) → 输出知识地图, 可选立刻自动学习若干天。"""
    print("=" * 66)
    print("教材投喂 · 知识地图构建")
    print("=" * 66)
    t0 = now_ms()
    ing = MaterialIngestor(subject=subject, use_vision=use_vision)
    book = ing.ingest(paths, title="命令行投喂")
    dur = now_ms() - t0
    st = book.stats()
    print("文件 %d 个 | 章 %d | 节 %d | 知识点 %d | 练习 %d 题 | 耗时 %.0f ms"
          % (st["files"], st["chapters"], st["sections"], st["points"],
             st["questions"], dur))
    print("文本量: 知识点 %d 字 | 题目 %d 字"
          % (st["point_chars"], st["question_chars"]))
    for n in ing.notes[:8]:
        print("  注意:", n)
    print("-" * 66)
    print("章节目录(示例):")
    for c in book.chapters[:6]:
        print("  %s" % c["title"])
        for s in c["sections"][:5]:
            print("     - %s (知识点%d · 练习%d)"
                  % (s["title"], len(s["points"]), len(s["questions"])))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        print("知识地图已保存:", book.save(os.path.join(out_dir, "material_map.json")))
    if study_days > 0:
        eng = AIStudentEngine()
        eng.grade_idx = 0                       # 从小学一年级(6岁)开始长
        eng.load_material(book)
        print("-" * 66)
        print("自动学习 %d 天(学生视角的思考过程):" % study_days)
        for i in range(study_days):
            ev = eng.study_material_day(source="🧪命令行")
            print("\n【第 %d 天】" % (i + 1))
            for e in ev:
                print("   [%s] %s" % (e[0], e[1]))
        r = eng.level_rating()
        print("-" * 66)
        print("阶段结果: 修为 %.2f/5 | %s%s·%s | 榜位 %d/100 | 等效 %s %s | 九字平均 %.0f%%"
              % (r["score5"], r["level_realm_emoji"], r["level_realm_name"],
                 r["tier"], r["rank"], r["role_label"], r["equiv_age"],
                 r["arts_avg"] * 100))
    print("=" * 66)
    return 0


def main(argv):
    if "--selftest" in argv:
        return run_selftest()
    for i, a in enumerate(list(argv)):          # 命令行视频自检(无窗口)
        if a == "--test-video" and i + 1 < len(argv):
            return cli_test_video(argv[i + 1], "--no-remote" not in argv)
        if a.startswith("--test-video="):
            return cli_test_video(a.split("=", 1)[1], "--no-remote" not in argv)
    for i, a in enumerate(list(argv)):          # 命令行: 教材投喂(+可选自动学习)
        if a == "--ingest":
            rest = argv[i + 1:]
            paths, study, out_dir = [], 0, ""
            k = 0
            while k < len(rest):
                b = rest[k]
                if b == "--study" and k + 1 < len(rest):
                    try:
                        study = int(rest[k + 1])
                    except Exception:
                        study = 0
                    k += 2
                    continue
                if b == "--out" and k + 1 < len(rest):
                    out_dir = rest[k + 1]
                    k += 2
                    continue
                if not b.startswith("--"):
                    paths.append(b)
                k += 1
            if not paths:
                print('用法: python ai学生_v4.py --ingest "课本.pdf或文件夹" '
                      '[--study 10] [--out 输出目录]')
                return 2
            return cli_ingest(paths, study_days=study, out_dir=out_dir)
    root = tk.Tk()
    root.title("%s v%s" % (APP_NAME, APP_VER))
    root.geometry("1600x980")
    root.minsize(1240, 820)
    root.configure(bg=BG)
    app = App(root)
    smoke = "--smoke" in argv
    if smoke:
        root.withdraw()
        root.after(1800, app.close)
        root.after(2600, lambda: root.quit())
    try:
        root.mainloop()
    except Exception as e:
        print("MAINLOOP ERR:", e)
        return 1
    if smoke:
        env = os.environ.get("AI_STUDENT_SMOKE_LOG")
        if env:
            try:
                with open(env, "w", encoding="utf-8") as f:
                    f.write("SMOKE OK\n")
            except Exception:
                pass
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
