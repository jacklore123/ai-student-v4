# -*- coding: utf-8 -*-
r"""
AI学生核心 —— 九字真言解题内核 (界面对照: 设计原稿 PPT 第29页)
第29页把 MOBA 界面与学习界面并列: 普攻/大招/推塔/进度条99%  ↔  九字真言+境界进度。
本界面 = 题面区 + 九字技能面板(普攻/连招/大招) + 推塔进度条 + 九字解题过程。
内核: 九字真言协议 + DeepSeek; CLI 版见 ai学生_验证核心.py。运行: python ai学生核心.py
"""

import os
import sys
import json
import queue
import threading
import datetime
import importlib.util

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

HERE = os.path.dirname(os.path.abspath(__file__))
# 打包成 exe 后 HERE 指向临时解包目录, 而密钥文件要放在"exe 旁边"
APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) \
    if getattr(sys, "frozen", False) else HERE
KEY_FILE = os.path.join(APP_DIR, "deepseek_key.txt")
BG, PANEL, PANEL2, EDGE = "#0E1117", "#161A22", "#12161D", "#252B36"
TXT, SUB, ACC, WARN, OK = "#E8EAEE", "#8B919D", "#7A8CFF", "#A89A72", "#7E9A88"
FONT = "Microsoft YaHei UI"


def load_mod(name, fname):
    path = os.path.join(HERE, fname)
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fatal(msg):
    """打包后无控制台, 出错必须落盘+弹窗, 否则表现为"点了没反应"。"""
    import traceback
    tb = traceback.format_exc() if sys.exc_info()[0] else str(msg)
    base = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, "frozen", False) else HERE
    try:
        with open(os.path.join(base, "ai学生核心_启动日志.txt"), "a",
                  encoding="utf-8") as f:
            f.write("[%s] HERE=%s exe=%s\n%s\n"
                    % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       HERE, sys.executable, tb))
    except Exception:
        pass
    try:
        r = tk.Tk()
        r.withdraw()
        messagebox.showerror("AI学生核心 启动失败",
                             "%s\n\n详情已写入: ai学生核心_启动日志.txt" % str(msg)[-1200:])
        r.destroy()
    except Exception:
        pass


# 九字内核: 优先静态导入(打包时才能正确收集它内部 import 的模块),
# 若不可用再退回动态加载同目录的 ai学生_验证核心.py(源码方式运行)。
try:
    import ai_student_core as CORE
except Exception:
    CORE = load_mod("ai_student_verify", "ai学生_验证核心.py")
if CORE is None:
    fatal("缺少九字内核模块 ai_student_core.py / ai学生_验证核心.py")
    raise SystemExit(2)

SKILL_GROUPS = [
    ("普攻 · 基础", [("删", "图像化拆解"), ("解", "方程求解"), ("列", "坐标列式")]),
    ("连招 · 建模", [("秒", "二级结论速判"), ("分", "隔离受力"), ("合", "整体简力")]),
    ("大招 · 体系", [("推", "公式体系推导"), ("创", "模型演化"), ("造", "动手造物")]),
]
SKILL_RULE = {ch: rule for ch, _n, rule in CORE.NINE_ARTS}
SKILL_NAME = {a[0]: a[1] for a in CORE.NINE_ARTS}


class CoreApp:
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.questions, self.done, self.cur, self.busy = [], 0, 0, False
        self.key = ""
        root.title("AI学生核心 · 九字真言解题")
        root.geometry("1180x760")
        root.configure(bg=BG)
        self._build()
        self._load_questions()
        self._load_key()
        self._tick()

    def _build(self):
        bar = tk.Frame(self.root, bg=PANEL, highlightbackground=EDGE, highlightthickness=1)
        bar.pack(fill="x")
        tk.Label(bar, text="🀄 AI学生核心", bg=PANEL, fg=TXT,
                 font=(FONT, 13, "bold")).pack(side="left", padx=(12, 6), pady=8)
        tk.Label(bar, text="· 九字真言解题 ·", bg=PANEL, fg=SUB,
                 font=(FONT, 9)).pack(side="left")
        self.lab_model = tk.Label(bar, text="", bg=PANEL, fg=SUB, font=(FONT, 9))
        self.lab_model.pack(side="right", padx=10)
        pf = tk.Frame(self.root, bg=PANEL2)
        pf.pack(fill="x")
        tk.Label(pf, text="推塔进度", bg=PANEL2, fg=WARN,
                 font=(FONT, 9, "bold")).pack(side="left", padx=(12, 6), pady=6)
        self.pb = ttk.Progressbar(pf, orient="horizontal", length=700,
                                  mode="determinate", maximum=100)
        self.pb.pack(side="left", pady=6)
        self.lab_pb = tk.Label(pf, text="0%", bg=PANEL2, fg=TXT, font=(FONT, 9, "bold"))
        self.lab_pb.pack(side="left", padx=8)
        self.lab_arts = tk.Label(pf, text="本轮用字: —", bg=PANEL2, fg=ACC, font=(FONT, 9))
        self.lab_arts.pack(side="right", padx=12)
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=8, pady=8)
        left = tk.Frame(body, bg=PANEL)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(body, bg=PANEL, width=390)
        right.pack(side="right", fill="y", padx=(8, 0))
        right.pack_propagate(False)
        tk.Label(left, text="题目（可从右侧题库取，也可直接粘贴）", bg=PANEL, fg=SUB,
                 font=(FONT, 9)).pack(anchor="w", padx=8, pady=(6, 0))
        self.txt_q = tk.Text(left, height=7, wrap="word", bg=PANEL2, fg=TXT,
                             relief="flat", bd=0, padx=8, pady=6, font=(FONT, 10))
        self.txt_q.pack(fill="x", padx=8, pady=4)
        row = tk.Frame(left, bg=PANEL)
        row.pack(fill="x", padx=8)
        self.btn_solve = tk.Button(row, text="⚔ 按九字真言解题", command=self.solve,
                                   bg="#1C2433", fg=ACC, relief="flat",
                                   font=(FONT, 10, "bold"), cursor="hand2", padx=10)
        self.btn_solve.pack(side="left", ipady=3)
        for t, c, col in (("🎲 下一题", self.next_q, TXT), ("💾 导出", self.export, OK),
                          ("🔑 密钥", self.ask_key, WARN)):
            tk.Button(row, text=t, command=c, bg=PANEL2, fg=col, relief="flat",
                      font=(FONT, 9), cursor="hand2").pack(side="left", padx=6, ipady=3)
        tk.Label(left, text="九字解题过程（①删 ②解 … 按需出现）", bg=PANEL, fg=SUB,
                 font=(FONT, 9)).pack(anchor="w", padx=8, pady=(8, 0))
        self.txt_out = tk.Text(left, wrap="word", bg=BG, fg=TXT, relief="flat", bd=0,
                               padx=10, pady=8, font=(FONT, 10))
        self.txt_out.pack(fill="both", expand=True, padx=8, pady=(2, 8))
        for tag, col in (("ans", TXT), ("warn", WARN), ("dim", SUB), ("ok", OK)):
            self.txt_out.tag_config(tag, foreground=col)
        tk.Label(right, text="题库（必修一 第一、二章 · 10 题）", bg=PANEL, fg=SUB,
                 font=(FONT, 9)).pack(anchor="w", padx=8, pady=(6, 2))
        self.lst = tk.Listbox(right, height=7, bg=PANEL2, fg=TXT, relief="flat", bd=0,
                              font=(FONT, 9), selectbackground="#26364A",
                              highlightthickness=0)
        self.lst.pack(fill="x", padx=8)
        self.lst.bind("<<ListboxSelect>>", self.pick_q)
        tk.Label(right, text="九字技能面板（点一下看释义）", bg=PANEL, fg=SUB,
                 font=(FONT, 9)).pack(anchor="w", padx=8, pady=(10, 2))
        self.skill_btns = {}
        for gname, skills in SKILL_GROUPS:
            gf = tk.Frame(right, bg=PANEL)
            gf.pack(fill="x", padx=8, pady=2)
            tk.Label(gf, text=gname, bg=PANEL, fg=WARN, font=(FONT, 8)).pack(anchor="w")
            r2 = tk.Frame(gf, bg=PANEL)
            r2.pack(fill="x")
            for ch, name in skills:
                b = tk.Button(r2, text="%s\n%s" % (ch, name), height=2, width=12,
                              command=lambda c=ch: self.show_skill(c),
                              bg=PANEL2, fg=TXT, relief="flat", font=(FONT, 9),
                              cursor="hand2")
                b.pack(side="left", expand=True, fill="x", padx=2, pady=2)
                self.skill_btns[ch] = b
        self.lab_skill = tk.Label(right, text="", bg=PANEL, fg=SUB, wraplength=350,
                                  justify="left", font=(FONT, 8))
        self.lab_skill.pack(fill="x", padx=10, pady=(6, 8))

    def _load_questions(self):
        p = os.path.join(HERE, "十题输出", "十题九字_解题示范.json")
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    self.questions = json.load(f)
            except Exception:
                self.questions = []
        for it in self.questions:
            self.lst.insert("end", "%s %s" % (it.get("id", ""), it.get("tag", "")))
        if self.questions:
            self.lst.selection_set(0)
            self.pick_q()

    def _load_key(self):
        """只认: ①exe 旁的 deepseek_key.txt ②环境变量 DEEPSEEK_API_KEY。
        **不再回退主程序配置** —— 那里的密钥可能是别家的, 会直接导致 401。"""
        self.key, self.key_src = "", "-"
        for p in (KEY_FILE, os.path.join(HERE, "deepseek_key.txt")):
            if self.key:
                break
            try:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        k = f.read().strip()
                    if k:
                        self.key, self.key_src = k, "密钥文件"
            except Exception:
                pass
        if not self.key:
            for env in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY"):
                if os.environ.get(env):
                    self.key, self.key_src = os.environ[env].strip(), "环境变量"
                    break
        self.lab_model.configure(
            text="模型: deepseek-chat | 密钥: %s（%s）"
                 % ("已配置" if self.key else "未配置", self.key_src))

    def pick_q(self, _e=None):
        sel = self.lst.curselection()
        if not sel or not self.questions:
            return
        self.cur = sel[0]
        it = self.questions[self.cur]
        self.txt_q.delete("1.0", "end")
        self.txt_q.insert("end", it.get("question", ""))
        self.txt_out.delete("1.0", "end")
        if it.get("ok"):
            self.txt_out.insert("end", "（上次解答）\n", "dim")
            self.txt_out.insert("end", "答案: %s\n" % it.get("answer", ""), "ans")
            self._set_arts(it.get("arts_used", []))

    def next_q(self):
        if self.questions:
            self.lst.selection_clear(0, "end")
            n = (self.cur + 1) % len(self.questions)
            self.lst.selection_set(n)
            self.pick_q()

    def show_skill(self, ch):
        self.lab_skill.configure(text="【%s】%s\n%s"
                                 % (ch, SKILL_NAME.get(ch, ""), SKILL_RULE.get(ch, "")))

    def _set_arts(self, arts):
        for ch, b in self.skill_btns.items():
            b.configure(bg="#1C2433" if ch in arts else PANEL2,
                        fg=ACC if ch in arts else TXT)
        self.lab_arts.configure(text="本轮用字: %s" % (" ".join(arts) if arts else "—"))

    def _progress(self):
        pct = int(self.done / float(len(self.questions)) * 100) if self.questions else 0
        self.pb["value"] = pct
        self.lab_pb.configure(text="%d%%" % pct)

    def solve(self):
        if self.busy:
            return
        if not self.key:
            self.ask_key()
            if not self.key:
                return
        q = self.txt_q.get("1.0", "end").strip()
        if len(q) < 6:
            messagebox.showinfo("AI学生核心", "请先写/选一道题")
            return
        self.busy = True
        self.btn_solve.configure(text="解题中…", state="disabled")
        self.txt_out.delete("1.0", "end")
        self.txt_out.insert("end", "按九字真言解题中…\n", "dim")
        chap = ""
        if self.questions and self.cur < len(self.questions):
            chap = self.questions[self.cur].get("chapter", "")
        key = self.key

        def work():
            msgs = CORE.build_messages_ppt(q, chap)
            raw, usage, ms, err = CORE.call_chat(
                "https://api.deepseek.com", key, "deepseek-chat", msgs,
                temperature=0.2, timeout=300, retries=3)
            self.q.put((q, raw, usage, ms, err))

        threading.Thread(target=work, daemon=True).start()

    def _tick(self):
        try:
            while True:
                q, raw, usage, ms, err = self.q.get_nowait()
                self._show_result(q, raw, usage, ms, err)
        except queue.Empty:
            pass
        self.root.after(120, self._tick)

    def _show_result(self, q, raw, usage, ms, err):
        self.busy = False
        self.btn_solve.configure(text="⚔ 按九字真言解题", state="normal")
        self.txt_out.delete("1.0", "end")
        if err:
            self.txt_out.insert("end", "调用失败: %s\n" % err, "warn")
            return
        p = CORE.parse_arts(raw)
        self.txt_out.insert("end", raw, "ans")
        self._set_arts(p["used"])
        self.done += 1
        self._progress()
        self.txt_out.insert("end", "\n——— 用时 %.1fs · 用字 %d 个 · token %s ———\n"
                            % (ms / 1000.0, p["n_used"],
                               (usage or {}).get("total_tokens", "-")), "dim")
        try:
            d = os.path.join(HERE, "核心解题记录")
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "core_solves.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(
                    {"ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     "question": q, "arts": p["used"], "answer": p["answer"],
                     "ms": round(ms), "raw": raw}, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def export(self):
        txt = self.txt_out.get("1.0", "end").strip()
        if not txt:
            return
        p = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="九字解题_%s.txt" % datetime.datetime.now().strftime("%H%M%S"))
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self.txt_q.get("1.0", "end").strip() + "\n\n" + txt)
            messagebox.showinfo("AI学生核心", "已导出:\n%s" % p)

    def ask_key(self):
        from tkinter import simpledialog
        k = simpledialog.askstring("DeepSeek 密钥",
                                   "粘贴 API 密钥(保存在本地 deepseek_key.txt):", show="*")
        if k and k.strip():
            self.key = k.strip()
            try:
                with open(KEY_FILE, "w", encoding="utf-8") as f:
                    f.write(self.key)
            except Exception:
                pass
            self.key_src = "密钥文件"
            self.lab_model.configure(text="模型: deepseek-chat | 密钥: 已配置（密钥文件）")


def selftest():
    """诊断自检: 打包后可用 调试版.exe --selftest 打印环境情况。"""
    print("AI学生核心 自检")
    print("  打包运行(frozen):", bool(getattr(sys, "frozen", False)))
    print("  资源目录 HERE   :", HERE)
    print("  程序目录 APP_DIR:", APP_DIR)
    print("  内核 九字真言    :", "OK" if CORE else "缺失")
    qp = os.path.join(HERE, "十题输出", "十题九字_解题示范.json")
    print("  题库文件        :", qp, "->", os.path.exists(qp))
    k = ""
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                k = f.read().strip()
    except Exception:
        pass
    print("  密钥文件        :", KEY_FILE, "->", os.path.exists(KEY_FILE))
    print("  DeepSeek 密钥   : %s%s"
          % ("已配置 " if k else "未配置(点界面🔑输入) ",
             ("前缀 " + k[:8] + "…" if k else "")))
    try:
        r = tk.Tk()
        r.withdraw()
        r.destroy()
        print("  tkinter 图形库  : OK")
    except Exception as e:
        print("  tkinter 图形库  : 失败", e)
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:
        root = tk.Tk()
        CoreApp(root)
        root.mainloop()
        return 0
    except Exception as e:
        fatal("启动/运行异常: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
