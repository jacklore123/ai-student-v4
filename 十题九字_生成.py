# -*- coding: utf-8 -*-
r"""
十题九字 · 解题示范生成器 (课本例题样式)
--------------------------------------------------------------------------------
按设计原稿(PPT 第31-32页)的写法: ①删(量的清单) ②解(方程→代入→结果) …,
让"该有的九字"按题目需要出现; 用 DeepSeek 生成 10 道必修一第一、二章题目的解答,
产出 JSON / Word(.docx) / 纯文本 三份原料(PDF 与 PPT 由后续脚本转换)。

用法:
  set DEEPSEEK_API_KEY=sk-...
  python 十题九字_生成.py
  python 十题九字_生成.py --limit 2 --out 十题输出
"""

import os
import sys
import json
import argparse
import datetime
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))


def load_mod(name, fname):
    path = os.path.join(HERE, fname)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


CORE = load_mod("ai_student_verify", "ai学生_验证核心.py")
APP = load_mod("ai_student_app", "ai学生_v4.py")

# 10 道题: 全部落在必修一第一、二章, 且数据完整(不依赖插图), 便于验证与阅读
QUESTIONS = [
    ("T01", "第一章 运动的描述", "位移与路程",
     "某人从 A 点出发向东走 40 m 到达 B 点，接着向北走 30 m 到达 C 点。"
     "求：(1) 全过程的路程；(2) 全过程位移的大小和方向。"),
    ("T02", "第一章 运动的描述", "平均速度",
     "一辆汽车沿直线从甲地驶向乙地，前一半路程的平均速度为 20 m/s，"
     "后一半路程的平均速度为 30 m/s。求全程的平均速度。"),
    ("T03", "第一章 运动的描述", "加速度",
     "一物体做匀加速直线运动，初速度为 2 m/s，3 s 末速度变为 8 m/s。"
     "求物体的加速度，并说明方向。"),
    ("T04", "第一章 运动的描述", "v-t 图像与加速度",
     "某物体沿直线运动：0～4 s 内速度由 0 均匀增大到 8 m/s；4～6 s 内速度保持 8 m/s；"
     "6～10 s 内均匀减速到 0。求各段的加速度，以及 0～10 s 内的总位移。"),
    ("T05", "第二章 匀变速直线运动的研究", "刹车问题(陷阱题)",
     "某新能源汽车在平直路面上以 12 m/s 的速度匀速行驶，刹车后做匀减速直线运动，"
     "2 s 末的速度为 8 m/s。求：(1) 刹车后汽车的加速度；"
     "(2) 刹车后 10 s 内汽车通过的位移大小。"),
    ("T06", "第二章 匀变速直线运动的研究", "知三求二",
     "汽车以 10 m/s 的初速度做匀加速直线运动，加速度为 2 m/s²。"
     "求它 4 s 内的位移以及 4 s 末的速度。"),
    ("T07", "第二章 匀变速直线运动的研究", "自由落体",
     "一物体自由下落，落地时速度是 30 m/s，可近似看作自由落体运动，g 取 10 m/s²。"
     "求：(1) 物体落地所用总时间；(2) 物体落地前最后 1 s 内的位移大小。"),
    ("T08", "第二章 匀变速直线运动的研究", "自由落体估算",
     "为了估测井口到水面的距离，让一个小石块从井口自由落下，经过 2.5 s 后听到石块击水声，"
     "声音在空气中的传播速度为 340 m/s，g 取 10 m/s²。估算井口到水面的距离。"),
    ("T09", "第二章 匀变速直线运动的研究", "反应时间测量",
     "用直尺做反应时间测量实验：某同学捏住直尺上端，被测者手指贴在直尺下端，"
     "直尺自由下落 20 cm 时被测者捏住直尺。g 取 10 m/s²。求被测者的反应时间。"),
    ("T10", "第二章 匀变速直线运动的研究", "初速度为零的推论",
     "一物体做初速度为零的匀加速直线运动。求：(1) 前 1 s 内、前 2 s 内、前 3 s 内"
     "位移之比；(2) 第 1 s 内、第 2 s 内、第 3 s 内位移之比。"),
]


def resolve_key(args):
    if args.key_file and os.path.exists(args.key_file):
        with open(args.key_file, "r", encoding="utf-8") as f:
            k = f.read().strip()
            if k:
                return k
    for env in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY"):
        if os.environ.get(env):
            return os.environ[env].strip()
    return ""


def parse_steps(text):
    """把 ①删 ②解 … 的编号步骤拆出来(兼容【】标签写法)。"""
    steps = []
    for line in (text or "").splitlines():
        s = line.strip()
        if not s:
            continue
        steps.append(s)
    return steps


def build_docx(results, out_dir):
    blocks = [("h1", "AI学生 · 十题九字解题示范"),
              ("p", "生成时间: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
              ("p", "题目范围: 人教版《物理》必修第一册 第一章、第二章"),
              ("p", "解题内核: 九字真言（删·解·秒·分·合·列·推·创·造）+ DeepSeek"),
              ("p", "写法: 遵照设计原稿的例题样式 —— ① 删（把题干转成量的清单）、"
                    "② 解（方程→代入→结果），按需出现其余各字。"), ("p", "")]
    for r in results:
        blocks.append(("h2", "%s【%s】%s" % (r["id"], r["tag"], r["chapter"])))
        blocks.append(("h3", "题目"))
        blocks.append(("p", r["question"]))
        blocks.append(("h3", "九字解题过程"))
        if r.get("ok"):
            for s in parse_steps(r.get("raw", "")):
                blocks.append(("p", s))
        else:
            blocks.append(("p", "（本题调用失败: %s）" % r.get("error", "")))
        blocks.append(("p", ""))
    path = os.path.join(out_dir, "十题九字_解题示范.docx")
    APP.docx_build(path, "十题九字解题示范", blocks)
    return path


def build_txt(results, out_dir):
    lines = ["AI学生 · 十题九字解题示范",
             "生成时间: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "解题内核: 九字真言(删解秒分合列推创造) + DeepSeek", ""]
    for r in results:
        lines += ["=" * 60,
                  "%s【%s】%s" % (r["id"], r["tag"], r["chapter"]),
                  "题目: %s" % r["question"], "-" * 60]
        lines += parse_steps(r.get("raw", "")) if r.get("ok") else ["(失败: %s)" % r.get("error")]
        lines.append("")
    path = os.path.join(out_dir, "十题九字_解题示范.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    ap = argparse.ArgumentParser(description="十题九字解题示范生成器")
    ap.add_argument("--out", default="十题输出")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--base", default="https://api.deepseek.com")
    ap.add_argument("--key-file", default="")
    args = ap.parse_args()

    key = resolve_key(args)
    if not key:
        print("缺少 API 密钥: 设置 DEEPSEEK_API_KEY 或用 --key-file")
        return 2
    os.makedirs(args.out, exist_ok=True)
    results = []
    qs = QUESTIONS[:args.limit] if args.limit else QUESTIONS
    print("=" * 66)
    print("十题九字 · 解题示范生成 | 模型 %s | 共 %d 题" % (args.model, len(qs)))
    print("=" * 66)
    for qid, chapter, tag, text in qs:
        msgs = CORE.build_messages_ppt(text, chapter)
        raw, usage, ms, err = CORE.call_chat(args.base, key, args.model, msgs,
                                             temperature=0.2, timeout=300, retries=3)
        if err:
            print("[%s] 失败: %s" % (qid, err))
            results.append({"id": qid, "chapter": chapter, "tag": tag,
                            "question": text, "ok": False, "error": err})
            continue
        p = CORE.parse_arts(raw)
        results.append({"id": qid, "chapter": chapter, "tag": tag,
                        "question": text, "ok": True, "ms": round(ms),
                        "usage": usage, "arts_used": p["used"],
                        "answer": p["answer"], "self_check": p["check"],
                        "raw": raw})
        print("[%s] %s | 用时 %.1fs | 用字: %s | 答案: %s"
              % (qid, tag, ms / 1000.0, "".join(p["used"]),
                 CORE.shorten(p["answer"], 46)))
    jp = os.path.join(args.out, "十题九字_解题示范.json")
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    dp = build_docx(results, args.out)
    tp = build_txt(results, args.out)
    print("-" * 66)
    print("已生成:")
    for p in (jp, dp, tp):
        print("  %s  (%.1f KB)" % (p, os.path.getsize(p) / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
