# -*- coding: utf-8 -*-
r"""
================================================================================
 AI学生 · 验证核心 (九字真言 × DeepSeek)
================================================================================
 目的: 独立、最小、可证伪地验证一件事 ——
       「按九字真言(删解秒分合列推创造)调用大模型解题」能不能作为 ai学生 的核心。

 为什么要单独做: 主程序(ai学生_v4.py)是产品, 这一份是"实验台"。
 它不依赖 tkinter / numpy / opencv, 只用标准库(urllib), 方便反复跑对比实验。

 用法:
   # 1) 从课本 PDF 抽取指定章节的题目 → 题库
   python ai学生_验证核心.py --build-bank "F:\高中物理课本\物理必修一课本.pdf" \
          --chapters 第一章,第二章 --out 验证题库

   # 2) 只看提示词, 不调用 API(检查九字真言协议)
   python ai学生_验证核心.py --bank 验证题库\必修一_第一二章.json --dry-run --limit 1

   # 3) 真跑(DeepSeek)
   set DEEPSEEK_API_KEY=sk-xxxxxxxx
   python ai学生_验证核心.py --bank 验证题库\必修一_第一二章.json --limit 10

 密钥来源(按优先级): --key-file 指定的文件 → 环境变量 DEEPSEEK_API_KEY →
   主程序配置 %USERPROFILE%\.ai_student_config.json 里的 remote_key。

 输出: 验证结果/<时间戳>/ answers.jsonl(每题一行) + report.md(汇总) + prompt_预览.txt
================================================================================
"""

import os
import sys
import re
import json
import time
import argparse
import urllib.request
import urllib.error
import datetime

DEFAULT_BASE = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

# ---------------------------------------------------------------- 九字真言 ----
# 释义取自设计原稿; 这里作为"解题内核协议"写进系统提示词, 强制模型按结构输出。

NINE_ARTS = [
    ("删", "图像化拆解", "文字转图像, 转完一句删一句: 把题干逐句转成图/符号与量的清单"),
    ("解", "方程求解", "找能把已知与未知连起来的方程; 必修一运动学五个量, 知三求二"),
    ("秒", "二级结论速判", "命中常见二级结论可秒判, 但必须写出适用条件, 不许无条件套用"),
    ("分", "隔离受力", "受力分析 + 正交分解 + 隔离法(数清接触点, 每一点都可能有力)"),
    ("合", "整体简力", "整体法简化受力: 先判断内力成对性, 再决定整体还是隔离"),
    ("列", "坐标列式", "建立坐标系, 按轴列出方程; 未知数与方程个数必须对齐"),
    ("推", "公式体系推导", "从母公式把用到的公式推一遍, 不背结论背来路"),
    ("创", "模型演化", "把题目归到物理模型上, 在脑中演化一遍理想化过程"),
    ("造", "动手造物", "需要时给出可动手验证的方案(器材/步骤/预期现象)"),
]
ART_ORDER = [a[0] for a in NINE_ARTS]

SYSTEM_PROMPT = (
    "你是「AI学生」的解题内核。解题必须严格按下面的「九字真言」执行, 不得跳步:\n"
    + "\n".join("%s %s: %s" % (ch, name, rule) for ch, name, rule in NINE_ARTS) +
    "\n\n【硬性要求】\n"
    "1. 严格按下列格式输出, 每个标签单独一行:\n"
    "【读题】题干给了什么、问什么(一句话)\n"
    "【删】…\n【解】…\n【秒】…\n【分】…\n【合】…\n【列】…\n【推】…\n【创】…\n【造】…\n"
    "【答案】最终结果(数值必须带单位, 矢量必须说明方向)\n"
    "【自检】检查量纲、方向、是否回答了全部设问\n"
    "2. 本题用不到的字, 该行写「略」, 不要为了凑齐九字而硬写;\n"
    "3. 不允许只给答案: 每个用到的字下面必须写出推理内容;\n"
    "4. 遇到题目信息不足(如图中数据看不到), 就在对应位置写「题目信息不足: …」, "
    "并说明还需要什么条件, 不许编造数据;\n"
    "5. 中文作答, 公式用纯文本(如 v=v0+at)。"
)


def build_messages(question, chapter="", grade="高中一年级"):
    """把一道题装进九字真言协议。"""
    head = "【题目】%s" % question.strip()
    if chapter:
        head = "【章节】%s\n%s" % (chapter, head)
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "%s\n学段: %s\n请按九字真言解题。" % (head, grade)}]


# --------------------------------------------------- 课本例题样式(PPT第31-32页) --
# 设计原稿里的示范是这样解题的:
#   ①删  V0=12m/s  V=8m/s  t=2s          ← 把题干删成"量的清单"
#   ②解  a=(V-V0)/t=(8-12)/2=-2 m/s²      ← 方程→代入→结果
#      再发现"10 s"是陷阱: V0=12  V=0  a=-2 ← 用同一个字继续推进
#   （1）根据 ______ 可得物体落地所用总时间为 ______   ← 用"根据…可得…"结句
# 下面这套提示词就是把这种写法固化下来, 保证"该有的九字"按题目需要出现。

SYSTEM_PROMPT_PPT = (
    "你是「AI学生」的解题内核。解题必须严格按「九字真言」执行, 并且像课本例题"
    "那样把每一步写实(一句话对应一个式子, 不写空话):\n\n"
    "「九字真言」(只写这道题用得到的字, 用不到的字写「略」, 不许硬凑):\n"
    "删 文字转图像, 转完一句删一句 —— 把题干转成『量的清单』, 逐条写成 "
    "V0=12 m/s、v=8 m/s、t=2 s 这种形式; 列进清单的句子就不再回看\n"
    "解 方程解的思维(必修一的知三求二) —— 写出方程、代入数值、算出结果, "
    "并说明运动学五个量里已知哪三个、求哪一个\n"
    "秒 结合常见的二级结论秒杀 —— 必须先写『适用条件』, 条件不满足不许秒\n"
    "分 受力分析 + 正交分解 + 隔离法 —— 数清接触点, 每一点都可能有力\n"
    "合 整体法, 简化受力 —— 先判断内力成对性, 再决定整体还是隔离\n"
    "列 按坐标系列出平衡状态方程 —— 未知数与方程个数必须对齐\n"
    "推 对课本公式做记忆编程, 图像化地推出公式体系 —— 用『根据……可得……』结句\n"
    "创 高中108个物理模型 —— 把题归到模型上, 在脑海里演化理想化过程\n"
    "造 动手做物理实体 —— 给出可动手验证的方案(器材/步骤/预期现象)\n\n"
    "【输出格式(严格遵守)】\n"
    "先写一行【读题】: 一句话说清给了什么、问什么。\n"
    "然后按顺序写用到的字, 每个字一行且编号连续, 形如:\n"
    "① 删 V0=12 m/s、v=8 m/s、t=2 s(把文字转成量, 转完即删)\n"
    "② 解 a=(v-V0)/t=(8-12)/2=-2 m/s²(知三求二: 知 V0、v、t, 求 a)\n"
    "③ 秒/分/合/列/推/创/造 …(按需出现, 用不到的直接写「略」)\n"
    "最后必须写:\n【答案】…(数值带单位; 矢量说明方向; 多问逐问作答)\n"
    "【自检】…(必须做三件事: ①量纲检查 ②把结果回代原方程验算 "
    "③检查有没有被『10 s 内』『上升到最高点后又落回』这类陷阱骗到)\n\n"
    "【硬性要求】\n"
    "1. 删 这一行必须出现量的清单, 不能用一句空话代替;\n"
    "2. 解 必须写出方程与代入过程, 不许只给结果;\n"
    "3. 每一步的数字都要能对上: 例如 v0=12 m/s、t=2 s、v=8 m/s 时 "
    "a=(v-v0)/t=(8-12)/2=-2 m/s², 不能算成 -4;\n"
    "4. 信息不足(图中数据看不清等)就写『题目信息不足: 缺……』, 绝不编造数据;\n"
    "5. 中文作答, 公式用纯文本(如 v=v0+at)。"
)


def build_messages_ppt(question, chapter="", grade="高中一年级"):
    """课本例题样式(①删②解…), 用于生成给学生看的解题示范。"""
    head = "【题目】%s" % question.strip()
    if chapter:
        head = "【章节】%s\n%s" % (chapter, head)
    return [{"role": "system", "content": SYSTEM_PROMPT_PPT},
            {"role": "user", "content": "%s\n学段: %s\n请按九字真言解题。" % (head, grade)}]


# ------------------------------------------------------------------ API ------

def resolve_key(args):
    if args.key_file and os.path.exists(args.key_file):
        with open(args.key_file, "r", encoding="utf-8") as f:
            k = f.read().strip()
            if k:
                return k
    for env in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY"):
        if os.environ.get(env):
            return os.environ[env].strip()
    cfg = os.path.join(os.path.expanduser("~"), ".ai_student_config.json")
    try:
        with open(cfg, "r", encoding="utf-8") as f:
            d = json.load(f)
        rk = ((d.get("remote") or {}).get("key") or d.get("remote_key") or "").strip()
        if rk:
            return rk
    except Exception:
        pass
    return ""


def call_chat(base, key, model, messages, temperature=0.2, timeout=300, retries=3):
    """OpenAI 兼容 /chat/completions, 返回 (文本, usage, 毫秒, 错误)。"""
    url = (base or DEFAULT_BASE).rstrip("/") + "/chat/completions"
    payload = {"model": model, "messages": messages, "stream": False,
               "temperature": temperature}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json",
               "User-Agent": "ai-student-verify/1.0"}
    if key:                                   # 本地 Ollama 等无需密钥
        headers["Authorization"] = "Bearer %s" % key
    last_err = ""
    for attempt in range(retries):
        t0 = time.time()
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                out = json.loads(resp.read().decode("utf-8", "ignore"))
            ms = (time.time() - t0) * 1000
            text = ((out.get("choices") or [{}])[0].get("message") or {}).get("content", "")
            return text or "(空响应)", out.get("usage") or {}, ms, ""
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "ignore")[:300]
            except Exception:
                pass
            last_err = "HTTP %s %s" % (e.code, body)
        except Exception as e:
            last_err = str(e)
        time.sleep(1.5 * (attempt + 1))
    return "", {}, 0.0, last_err


def is_local(base):
    b = (base or "").lower()
    return b.startswith("http://127.") or b.startswith("http://localhost") \
        or b.startswith("http://[::1]")


MOCK_TEMPLATE = (
    "【读题】这是一道{kind}题, 题干关键信息: {q}\n"
    "【删】把题干转成图与量的清单(此处为 mock 模拟输出, 非真实解题)\n"
    "【解】列出可用的关系式, 已知与未知一一对应\n"
    "【秒】略\n【分】略\n【合】略\n"
    "【列】按坐标系列出方程\n"
    "【推】由母公式推出所用公式\n"
    "【创】归入对应物理模型\n【造】略\n"
    "【答案】(mock) 模拟答案: 用于验证报告链路, 不代表真实结果\n"
    "【自检】(mock) 量纲检查通过、未遗漏设问"
)


# -------------------------------------------------------------- 结果解析 -----

def parse_arts(text):
    """从模型输出里抽取九个字各自的段落, 计算覆盖率与结构完整度。

    兼容两种写法: ① 删 / ② 解 …(课本例题样式) 与 【删】…(标签样式)。
    """
    body = text or ""
    seg = {}
    for ch in ART_ORDER:
        m = re.search(r"【\s*%s\s*】(.*?)(?=【|\Z)" % ch, body, re.S)
        seg[ch] = (m.group(1).strip() if m else "")
    if not any(seg.values()):                      # 退一步: 识别 ① 删 / ② 解 写法
        order = []
        for line in body.splitlines():
            m = re.match(r"^\s*(?:[①②③④⑤⑥⑦⑧⑨⑩]|\d{1,2}\s*[.．、)）])\s*"
                         r"([删解秒分合列推创造])\s*[:：]?\s*(.*)$", line.strip())
            if not m:
                continue
            ch, rest = m.group(1), m.group(2).strip()
            if ch not in seg:
                seg[ch] = ""
            seg[ch] = (seg[ch] + " " + rest).strip()
            if ch not in order:
                order.append(ch)
        if not order:                              # 再退一步: 正文里出现的字
            for ch in ART_ORDER:
                if re.search(r"(?:^|\s)%s\s*[:：]" % ch, body):
                    seg[ch] = "(正文中提及)"
    used = [ch for ch in ART_ORDER if seg[ch] and "略" not in seg[ch][:4]]
    ans = ""
    m = re.search(r"【\s*答案\s*】(.*?)(?=【|\Z)", body, re.S)
    if m:
        ans = m.group(1).strip()
    chk = ""
    m = re.search(r"【\s*自检\s*】(.*?)(?=【|\Z)", body, re.S)
    if m:
        chk = m.group(1).strip()
    return {"segments": seg, "used": used, "n_used": len(used),
            "answer": ans, "check": chk,
            "structured": bool(ans) and len(used) >= 1}


def shorten(s, n=150):
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s[:n] + ("…" if len(s) > n else "")


# ------------------------------------------------------------ 题库与抽取 -----

def load_core_module():
    """复用主程序的教材解析器(在同一目录时可用); 失败返回 None。"""
    try:
        import importlib.util
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "ai学生_v4.py")
        if not os.path.exists(path):
            return None
        spec = importlib.util.spec_from_file_location("ai_student_core", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ai_student_core"] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print("[提示] 无法复用主程序解析器(%s), 将使用简易切分。" % e)
        return None


def build_bank_from_pdf(pdf_path, chapters, out_dir, subject="物理"):
    """从课本抽取指定章的题目, 存成题库 json。"""
    mod = load_core_module()
    if mod is None:
        print("需要与 ai学生_v4.py 放在同一目录才能解析 PDF。")
        return None
    ing = mod.MaterialIngestor(subject=subject)
    book = ing.ingest([pdf_path], title=os.path.basename(pdf_path))
    want = [c.strip() for c in (chapters or []) if c.strip()]
    items = []
    for chap, sec, qno, qtext in book.flat_questions():
        if want and not any(w in chap for w in want):
            continue
        if not looks_like_question(qtext):
            continue
        items.append({"id": "", "chapter": chap,
                      "section": clean_section(sec), "no": qno, "text": qtext})
    for i, it in enumerate(items, 1):
        it["id"] = "Q%03d" % i
    os.makedirs(out_dir, exist_ok=True)
    name = "%s_%s.json" % (os.path.splitext(os.path.basename(pdf_path))[0],
                           "".join(want) if want else "全部")
    out = os.path.join(out_dir, name)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"source": pdf_path, "chapters": want, "count": len(items),
                   "items": items}, f, ensure_ascii=False, indent=1)
    print("题库已生成: %s (共 %d 题)" % (out, len(items)))
    for it in items[:8]:
        print("  %s [%s|%s-%s] %s" % (it["id"], it["chapter"][:8], it["section"][:8],
                                      it["no"], shorten(it["text"], 60)))
    return out


# 只保留"像题"的条目: 实验步骤/正文片段不是题, 进题库会污染验证结论
Q_MARKERS = ("？", "?", "求", "多少", "多大", "是否", "为什么", "判断", "计算",
             "证明", "说明", "画出", "比较", "正确的是", "错误的是", "等于",
             "如何", "怎样", "试分析", "表达式")


def looks_like_question(t):
    t = (t or "").strip()
    if sum(1 for c in t if "\u4e00" <= c <= "\u9fff") < 12:
        return False
    return any(m in t for m in Q_MARKERS)


def clean_section(s):
    """章节标签清洗: 丢掉被版面切出来的碎片标签。"""
    s = (s or "").strip()
    if len(s) < 2 or len(s) > 12 or "。" in s or re.search(r"\d", s):
        return ""
    return s


def load_bank(path):
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    if isinstance(d, list):
        items = d
    else:
        items = d.get("items") or []
    out = []
    for i, it in enumerate(items, 1):
        if isinstance(it, str):
            it = {"text": it}
        txt = (it.get("text") or it.get("question") or "").strip()
        if len(txt) >= 6:
            out.append({"id": it.get("id") or "Q%03d" % i,
                        "chapter": it.get("chapter", ""),
                        "section": it.get("section", ""),
                        "text": txt})
    return out


# ---------------------------------------------------------------- 主流程 -----

def run_verify(items, args, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    key = resolve_key(args)
    jsonl = os.path.join(out_dir, "answers.jsonl")
    raw_dir = os.path.join(out_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    results = []
    n = 0
    for it in items:
        if args.limit and n >= args.limit:
            break
        n += 1
        msgs = build_messages(it["text"], it.get("chapter", ""), args.grade)
        if args.dry_run:
            preview = os.path.join(out_dir, "prompt_预览.txt")
            with open(preview, "w", encoding="utf-8") as f:
                for msg in msgs:
                    f.write("===== %s =====\n%s\n\n" % (msg["role"], msg["content"]))
            print("干跑(dry-run): 只生成提示词, 不调用 API。")
            print("提示词预览: %s" % preview)
            print("-" * 66)
            print("题目: %s" % shorten(it["text"], 200))
            print("-" * 66)
            print(msgs[1]["content"])
            return results
        if not key:
            print("!! 没有找到 API 密钥: 请设置环境变量 DEEPSEEK_API_KEY, "
                  "或用 --key-file 指定密钥文件, 或在主程序里配置外部API。")
            if not is_local(args.base) and not args.mock:
                return results
        print("[%d/%d] %s %s" % (n, min(args.limit or len(items), len(items)),
                                 it["id"], shorten(it["text"], 46)))
        if args.mock:
            kind = "计算" if any(m in it["text"] for m in ("求", "多少", "多大")) else "判断"
            text = MOCK_TEMPLATE.format(kind=kind, q=shorten(it["text"], 50))
            usage, ms, err = {"total_tokens": 0}, 1.0, ""
        else:
            text, usage, ms, err = call_chat(args.base, key, args.model, msgs,
                                             args.temperature, args.timeout,
                                             args.retries)
        if err:
            print("      调用失败: %s" % err)
            rec = {"id": it["id"], "chapter": it.get("chapter", ""),
                   "question": it["text"], "ok": False, "error": err}
        else:
            p = parse_arts(text)
            with open(os.path.join(raw_dir, "%s.txt" % it["id"]), "w",
                      encoding="utf-8") as f:
                f.write(text)
            rec = {"id": it["id"], "chapter": it.get("chapter", ""),
                   "section": it.get("section", ""), "question": it["text"],
                   "ok": True, "ms": round(ms), "usage": usage,
                   "arts_used": p["used"], "n_arts": p["n_used"],
                   "structured": p["structured"], "answer": p["answer"],
                   "self_check": p["check"], "segments": p["segments"],
                   "raw": text}
            print("      用时 %.1fs | 用了 %d 个字: %s | 答案: %s"
                  % (ms / 1000.0, p["n_used"], "".join(p["used"]),
                     shorten(p["answer"], 40)))
        results.append(rec)
        with open(jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return results


def write_report(results, out_dir, args, items):
    if not results:
        return None
    ok = [r for r in results if r.get("ok")]
    struct = [r for r in ok if r.get("structured")]
    arts = {}
    for r in ok:
        for ch in r.get("arts_used", []):
            arts[ch] = arts.get(ch, 0) + 1
    avg_ms = sum(r.get("ms", 0) for r in ok) / float(len(ok)) if ok else 0
    lines = ["# ai学生验证核心 · 九字真言解题报告", "",
             "- 时间: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "- 模型: %s @ %s" % (args.model, args.base),
             "- 题目: 题库 %s, 本轮 %d 题" % (args.bank or "-", len(results)),
             "- 成功: %d | 结构完整: %d | 平均用时: %.1fs"
             % (len(ok), len(struct), avg_ms / 1000.0), "",
             "## 九字使用分布", ""]
    for ch, name, _rule in NINE_ARTS:
        lines.append("- %s %s: %d 次" % (ch, name, arts.get(ch, 0)))
    lines += ["", "## 逐题结果", ""]
    for r in results:
        lines.append("### %s %s" % (r["id"], r.get("chapter", "")))
        lines.append("")
        lines.append("**题目**: %s" % shorten(r.get("question", ""), 200))
        lines.append("")
        if not r.get("ok"):
            lines.append("**失败**: %s" % r.get("error", ""))
            lines.append("")
            continue
        lines.append("- 用了: %s (%d 个)" % ("".join(r.get("arts_used", [])),
                                             r.get("n_arts", 0)))
        lines.append("- 答案: %s" % shorten(r.get("answer", ""), 120))
        lines.append("")
        for ch in ART_ORDER:
            seg = (r.get("segments") or {}).get(ch, "")
            if seg and "略" not in seg[:4]:
                lines.append("**【%s】** %s" % (ch, shorten(seg, 220)))
                lines.append("")
    path = os.path.join(out_dir, "report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("-" * 66)
    print("报告: %s" % path)
    print("成功 %d/%d · 结构完整 %d · 九字分布: %s"
          % (len(ok), len(results), len(struct),
             ", ".join("%s%d" % (k, v) for k, v in arts.items()) or "无"))
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="AI学生 · 验证核心 (九字真言 × DeepSeek)")
    ap.add_argument("--bank", help="题库 json(或含 items 的 json)")
    ap.add_argument("--build-bank", help="从课本 PDF 抽取题目建题库")
    ap.add_argument("--chapters", default="", help="抽取哪些章, 逗号分隔, 如 第一章,第二章")
    ap.add_argument("--out", default="验证结果", help="输出目录")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题(0=全部)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--key-file", default="")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--grade", default="高中一年级")
    ap.add_argument("--dry-run", action="store_true", help="只生成提示词, 不调用 API")
    ap.add_argument("--mock", action="store_true",
                    help="用模拟回答跑通全流程(验证报告与解析链路, 非真实解题)")
    args = ap.parse_args(argv)

    if args.build_bank:
        chs = [c.strip() for c in (args.chapters or "").split(",") if c.strip()]
        p = build_bank_from_pdf(args.build_bank, chs, args.out)
        if not args.bank:
            return 0 if p else 1
        args.bank = p

    if not args.bank:
        ap.print_help()
        return 2
    items = load_bank(args.bank)
    if not items:
        print("题库为空: %s" % args.bank)
        return 1
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    print("=" * 66)
    print("ai学生验证核心 · 九字真言 × %s" % args.model)
    print("题库: %s | 题目 %d 道 | 输出: %s" % (args.bank, len(items), out_dir))
    print("=" * 66)
    results = run_verify(items, args, out_dir)
    if results:
        write_report(results, out_dir, args, items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
