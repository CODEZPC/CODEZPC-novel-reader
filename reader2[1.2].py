from tkinter import *
from tkinter import filedialog, messagebox
import time, threading, math, os

tk = Tk()
CONFIG = {
    # 每页行数
    "LINES_PER_PAGE": 31,
    # 每行字数
    "CHARATERS_PER_LINE": 120,
    # 窗口宽
    "WINDOW_WIDTH": 1280,
    # 窗口高
    "WINDOW_HEIGHT": 720,
    # 跳转窗口宽
    "JUMP_WINDOW_WIDTH": 150,
    # 跳转窗口高
    "JUMP_WINDOW_HEIGHT": 20,
    # 字体A - JetBrains Mono
    "FONT_A": ".\\A.ttf",
    # 图标
    "ICON": "",
    # 识别编码
    "ENCODEINGS": ["gbk", "utf-8"],
    # 提示文本 - 正常
    "HINT_NORMAL": "[←][→] 上下页 | [T] 跳转 | [O] 打开 | [↑][↓] 调整预估阅读速度 | [H] 隐藏操作提示 | [Q] 退出",#待添加：W-Wiki库
    # 提示文本 - Shift
    "HINT_SHIFT": "[←][→] 上下十页 | [↑][↓] 调整预估阅读速度",
    # 提示文本 - 空
    "HINT_EMPTYL": "|",
    "HINT_EMPTYR": "|[H]",
    "HINT_EMPTYP": "█",
    # ===以下为用户设置获取=== #
    "TIME_PER_PAGE": 80,
    # ===以下为系统配置获取=== #
    # 屏幕宽
    "INFO_SCREEN_WIDTH": tk.winfo_screenwidth(),
    # 屏幕高
    "INFO_SCREEN_HEIGHT": tk.winfo_screenheight(),
}

showhint = True
lines = []
rip = []
backup = []
eng_char = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-={}[]|\\:\"';<>?,./`~ ·"
now = 1
full = 0


def loading():
    global text, status, title, hint
    tk.geometry(
        f"""{CONFIG["WINDOW_WIDTH"]}x{CONFIG["WINDOW_HEIGHT"]}+{int((CONFIG["INFO_SCREEN_WIDTH"] - CONFIG["WINDOW_WIDTH"]) / 2)}+{int((CONFIG["INFO_SCREEN_HEIGHT"] - CONFIG["WINDOW_HEIGHT"]) / 2)}"""
    )  # 居中
    tk.resizable(0, 0)  # 禁止缩放
    tk.title("")  # 空标题
    tk.iconbitmap(CONFIG["ICON"])  # 图标
    tk.configure(bg="#23272E")  # 背景颜色
    title = Label(
        text="CODEZPC's READER", fg="#767F89", bg="#23272E", font=("JetBrains Mono", 15)
    )  # 里标题
    title.place(x=10, y=10)
    text = Label(
        text="",
        fg="#C8C8C8",
        bg="#23272E",
        width=CONFIG["CHARATERS_PER_LINE"],
        height=CONFIG["LINES_PER_PAGE"],
        font=("黑体", 15),
        justify="left",
        anchor="nw",
    )  # 文本显示
    text.place(x=40, y=40)
    status = Label(
        text="---未打开文本---", fg="#767F89", bg="#23272E", font=("黑体", 12)
    )  # 状态栏
    status.place(x=10, y=665)
    hint = Label(
        text=CONFIG["HINT_NORMAL"],
        fg="#767F89",
        bg="#23272E",
        font=("黑体", 12),
    )  # 操作栏
    hint.place(x=10, y=690)
    version = Label(
        text="1.2", fg="#767F89", bg="#23272E", font=("JetBrains Mono", 5)
    )  # 版本号
    version.place(x=0, y=0)
    # 键盘监听
    tk.bind("<q>", qit)
    tk.bind("<Q>", qit)
    tk.bind("<o>", openfile_th)
    tk.bind("<O>", openfile_th)
    tk.bind("<t>", jump)
    tk.bind("<T>", jump)
    tk.bind("<Control-g>", genlist)
    tk.bind("<Control-G>", genlist)
    tk.bind("<h>", hide)
    tk.bind("<H>", hide)
    tk.bind("<w>",wiki)
    tk.bind("<W>",wiki)
    tk.bind("<Right>", nextpage)
    tk.bind("<Shift-Right>", nextpagex)
    tk.bind("<Left>", prevpage)
    tk.bind("<Shift-Left>", prevpagex)
    tk.bind("<Up>", addtime)
    tk.bind("<Shift-Up>", addtimex)
    tk.bind("<Down>", minustime)
    tk.bind("<Shift-Down>", minustimex)
    tk.bind("<KeyPress-Shift_L>", hintb)
    tk.bind("<KeyRelease-Shift_L>", hinta)


def openfile_th(event):
    th = threading.Thread(target=openfile)
    th.daemon = True
    th.start()


# 打开文件
def openfile(event=None):
    global lines, full, file, title, now, status, backup, rip
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    start = time.time()
    if file_path:
        for encoding in CONFIG["ENCODEINGS"]:
            try:
                lines = open(file_path, "r", encoding=encoding).readlines()
                backup = open(file_path, "r", encoding=encoding).readlines()
                break
            except UnicodeDecodeError:
                continue
        else:
            messagebox.showerror("错误", "无法识别文件编码")
            return
        idxl = 0
        for i in lines:
            length = CONFIG["CHARATERS_PER_LINE"]
            idx = 0
            for j in i:
                if j in eng_char:
                    length -= 1
                elif j == "\n":
                    lines[idxl] = i[0:idx] + length * " " + "\n"
                    break
                else:
                    length -= 2
                if length <= 1:
                    if (i[idx + 1] == "\n") or (i[idx + 1] in eng_char and length == 1):
                        idx += 1
                        continue
                    lines[idxl] = i[0:idx] + "\n"
                    lines.insert(idxl + 1, i[idx:])
                    break
                idx += 1
            idxl += 1
            full = idxl // CONFIG["LINES_PER_PAGE"]
            if idxl == CONFIG["LINES_PER_PAGE"] + 1:
                now = 1
                update(lines, 1)
            if idxl % 1000 == 0:
                updatestatus(now, full, load=True, i=idxl)
        full = int(math.ceil(idxl / CONFIG["LINES_PER_PAGE"]))
        updatestatus(now, full)
        file = file_path
        while "/" in file:
            file = file[file.index("/") + 1 :]
        title.configure(text=file[:-4], font=("黑体", 15))
        for i in lines:
            rip.append(i.rstrip())
        update(lines, now)
    end = time.time() - start
    print(end)


def update(txt, page):
    global full
    show = ""
    for i in range(
        (page - 1) * CONFIG["LINES_PER_PAGE"], page * CONFIG["LINES_PER_PAGE"]
    ):
        try:
            show += txt[i]
        except IndexError:
            show += "\n"
    text.configure(text=show)
    updatestatus(now, full)
    if not showhint:
        length = int(math.floor(75 * now / full))
        hint.configure(
            text=CONFIG["HINT_EMPTYL"]
            + length * CONFIG["HINT_EMPTYP"]
            + " " * (150 - 2 * length)
            + CONFIG["HINT_EMPTYR"]
        )


def loadtime(page, all):
    second = (all - page) * CONFIG["TIME_PER_PAGE"]
    minute = second // 60
    hour = minute // 60
    minute %= 60
    return (hour, minute)


def updatestatus(page, all, load=False, i=0):
    global status
    hour, minute = loadtime(page, all)
    status.configure(
        text=f"第{now}/{full}页 {round((now/full)*100,3):.3f}% 预计剩余{hour if 0 < hour <= 1200 else ("" if hour == 0 else "1200+")}{"小时" if hour != 0 else ""}{f"{minute:02d}分钟" if hour < 20 else ""} 速度设置为{CONFIG["TIME_PER_PAGE"]}秒/页"
        + (f" 加载中……({int(round(i/len(lines)*100,0))}%)" if load else "")
    )


def nextpage(event):
    global now, full
    if full == 0:
        return
    if now < full:
        now += 1
    else:
        now = 1
    update(lines, now)


def prevpage(event):
    global now, full
    if full == 0:
        return
    if now > 1:
        now -= 1
    else:
        now = full
    update(lines, now)


def nextpagex(event):
    global now, full
    if full == 0:
        return
    if now + 9 < full:
        now += 10
    elif now < full:
        now = full
    else:
        now = 1
    update(lines, now)


def prevpagex(event):
    global now, full
    if full == 0:
        return
    if now - 9 > 1:
        now -= 10
    elif now > 1:
        now = 1
    else:
        now = full
    update(lines, now)


def addtime(event):
    if CONFIG["TIME_PER_PAGE"] < 600:
        CONFIG["TIME_PER_PAGE"] += 1
    if full != 0:
        update(lines, now)


def minustime(event):
    if CONFIG["TIME_PER_PAGE"] > 1:
        CONFIG["TIME_PER_PAGE"] -= 1
    if full != 0:
        update(lines, now)


def addtimex(event):
    if CONFIG["TIME_PER_PAGE"] + 10 <= 600:
        CONFIG["TIME_PER_PAGE"] += 10
    else:
        CONFIG["TIME_PER_PAGE"] = 600
    if full != 0:
        update(lines, now)


def minustimex(event):
    if CONFIG["TIME_PER_PAGE"] - 10 >= 1:
        CONFIG["TIME_PER_PAGE"] -= 10
    else:
        CONFIG["TIME_PER_PAGE"] = 1
    if full != 0:
        update(lines, now)


def hinta(event):
    global hint
    if showhint:
        hint.configure(text=CONFIG["HINT_NORMAL"])


def hintb(event):
    global hint
    if showhint:
        hint.configure(text=CONFIG["HINT_SHIFT"])


def hide(event):
    global showhint
    if showhint:
        showhint = False
        if full != 0:
            length = int(math.floor(75 * now / full))
            hint.configure(
                text=CONFIG["HINT_EMPTYL"]
                + length * CONFIG["HINT_EMPTYP"]
                + " " * (150 - 2 * length)
                + CONFIG["HINT_EMPTYR"]
            )
        else:
            hint.configure(text="")
    else:
        showhint = True
        hint.configure(text=CONFIG["HINT_NORMAL"])


def jump(event):
    def save(event):
        global now, full
        if 1 <= int(entry.get()) <= full:
            now = int(entry.get())
            jumping.destroy()
            update(lines, now)

    jumping = Toplevel(tk)
    jumping.geometry(
        f"""{CONFIG["JUMP_WINDOW_WIDTH"]}x{CONFIG["JUMP_WINDOW_HEIGHT"]}+{int((CONFIG["INFO_SCREEN_WIDTH"] - CONFIG["JUMP_WINDOW_WIDTH"]) / 2)}+{int((CONFIG["INFO_SCREEN_HEIGHT"] - CONFIG["JUMP_WINDOW_HEIGHT"]) / 2)}"""
    )  # 居中
    entry = Entry(jumping)
    entry.pack()
    jumping.bind("<Return>", save)


def genlist(event):
    with open("./cont" + file, "w", encoding="utf-8") as f:
        for i in backup:
            if i[0] != " " and i[0] != "\n":
                f.write(f"{i[:-1]} --- {(rip.index(i[:-1])+1)//31+1}\n")


def wiki(event):
    os.startfile(r"./wiki")


# 退出
def qit(event):
    exit()


if __name__ == "__main__":
    loading()

mainloop()
