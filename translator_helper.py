import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import os
import webbrowser

# ==========================================
# 开启高 DPI 高清缩放支持
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


# ==========================================

class TranslationFormatter:
    def __init__(self, root):
        self.root = root
        self.root.title("ConPla txt - 极简工作台")
        self.root.geometry("900x750")

        self.version = "V1.2"
        self.author = "LeviCwiw"
        self.github_url = "https://github.com/LeviCwiw/ConPla_txt"

        icon_path = "app_icon.ico"
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.target_file = None
        self.font_family = "Microsoft YaHei"
        self.current_font_size = 12
        self._timer = None
        self.config_file = "app_config.txt"

        self.is_dark_mode = False
        self.search_start_index = "1.0"
        self.last_search_term = ""
        self.search_panel_visible = False  # 记录查找面板是否显示

        # 初始化界面
        self.setup_menu()  # 加载新版全局菜单栏
        self.setup_ui()
        self.load_last_save_path()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- 新版全局菜单栏 ---
    def setup_menu(self):
        self.menu_bar = tk.Menu(self.root)

        # 1. 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="📁 设置/修改保存的 TXT 文件", command=self.select_target_file)
        file_menu.add_separator()
        file_menu.add_command(label="❌ 退出", command=self.on_closing)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)

        # 2. 编辑菜单
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="✨ 智能首行缩进", command=self.format_indent)
        edit_menu.add_command(label="↩️ 撤销 (Ctrl+Z)", command=self.undo_action)
        edit_menu.add_separator()
        edit_menu.add_command(label="🧹 仅清空输入区", command=self.clear_text)
        self.menu_bar.add_cascade(label="编辑", menu=edit_menu)

        # 3. 查找菜单
        search_menu = tk.Menu(self.menu_bar, tearoff=0)
        search_menu.add_command(label="🔍 展开/收起 查找与替换 (Ctrl+F)", command=self.toggle_search_panel)
        self.menu_bar.add_cascade(label="查找", menu=search_menu)

        # 4. 视图菜单
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="➕ 放大视图字体 (A+)", command=lambda: self.change_font_size(2))
        self.view_menu.add_command(label="➖ 缩小视图字体 (A-)", command=lambda: self.change_font_size(-2))
        self.view_menu.add_separator()
        self.view_menu.add_command(label="🌙 切换夜间模式", command=self.toggle_theme)
        self.menu_bar.add_cascade(label="视图", menu=self.view_menu)

        # 5. 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="关于 ConPla txt", command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="访问 GitHub 主页", command=lambda: webbrowser.open(self.github_url))
        self.menu_bar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=self.menu_bar)

    def show_about(self):
        about_text = (
            f"ConPla txt - 轻小说/网文翻译专属工作台\n"
            f"-----------------------------------------\n\n"
            f"当前版本：{self.version}\n"
            f"软件作者：{self.author}\n\n"
            f"“将翻译排版与存储分离，专注每一段文字的精修。”\n\n"
            f"项目主页已开源至 GitHub，欢迎访问并获取最新更新。"
        )
        messagebox.showinfo("关于软件", about_text)

    # --- 核心 UI 设置 (极致精简版) ---
    def setup_ui(self):
        btn_style = {"relief": "flat", "font": (self.font_family, 10), "cursor": "hand2", "bd": 0, "pady": 5,
                     "padx": 10}

        # 顶部核心框架：只保留目标文件提示和保存按钮
        self.top_frame = tk.Frame(self.root, pady=12, padx=15)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        self.target_label = tk.Label(self.top_frame, text="⚠️ 未选择目标 TXT 文件 (请先在菜单栏[文件]中设置)",
                                     fg="#EF4444", font=(self.font_family, 10, "bold"))
        self.target_label.pack(side=tk.LEFT)

        self.btn_save = tk.Button(self.top_frame, text="💾 保存并清空 (Ctrl+Enter)", command=self.save_and_clear,
                                  font=(self.font_family, 10, "bold"), relief="flat", cursor="hand2", bd=0, pady=6,
                                  padx=20)
        self.btn_save.pack(side=tk.RIGHT)

        # 隐藏式的搜索替换框架 (默认不 pack 显示)
        self.search_frame = tk.Frame(self.root, pady=5)

        self.search_label1 = tk.Label(self.search_frame, text="查找:", font=(self.font_family, 10))
        self.search_label1.pack(side=tk.LEFT)
        self.search_entry = tk.Entry(self.search_frame, width=16, font=(self.font_family, 11), relief="flat",
                                     highlightthickness=1)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 10), ipady=3)

        self.btn_find = tk.Button(self.search_frame, text="🔍 查找下一个", command=self.find_next, **btn_style)
        self.btn_find.pack(side=tk.LEFT, padx=(0, 15))

        self.search_label2 = tk.Label(self.search_frame, text="替换为:", font=(self.font_family, 10))
        self.search_label2.pack(side=tk.LEFT)
        self.replace_entry = tk.Entry(self.search_frame, width=16, font=(self.font_family, 11), relief="flat",
                                      highlightthickness=1)
        self.replace_entry.pack(side=tk.LEFT, padx=(5, 10), ipady=3)

        self.btn_replace = tk.Button(self.search_frame, text="🔄 全部替换", command=self.replace_all_text, **btn_style)
        self.btn_replace.pack(side=tk.LEFT)

        # 底部状态栏框架
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=5)

        self.status_label = tk.Label(self.bottom_frame, text="", font=(self.font_family, 10, "bold"))
        self.status_label.pack(side=tk.LEFT)

        self.stats_label = tk.Label(self.bottom_frame, text="第 1 行, 第 0 列 | 共 0 字符", font=(self.font_family, 9))
        self.stats_label.pack(side=tk.RIGHT)

        # 中间编辑区
        self.mid_frame = tk.Frame(self.root)
        self.mid_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=15, pady=5)

        self.text_container = tk.Frame(self.mid_frame, highlightthickness=1)
        self.text_container.pack(expand=True, fill=tk.BOTH)

        scroll = tk.Scrollbar(self.text_container, bd=0, relief="flat")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_editor = tk.Text(self.text_container, font=(self.font_family, self.current_font_size), wrap=tk.CHAR,
                                   yscrollcommand=scroll.set, undo=True, maxundo=-1,
                                   relief="flat", bd=0, padx=15, pady=15, spacing1=6, spacing3=6)
        self.text_editor.pack(expand=True, fill=tk.BOTH)
        scroll.config(command=self.text_editor.yview)

        try:
            self.text_editor.tag_configure("search_highlight")
        except:
            pass

        # 事件绑定
        self.text_editor.bind("<KeyRelease>", self.update_editor_status)
        self.text_editor.bind("<ButtonRelease-1>", self.update_editor_status)
        self.text_editor.bind("<FocusIn>", self.update_editor_status)

        self.root.bind("<Control-Return>", lambda event: self.shortcut_save())
        self.root.bind("<Control-f>", lambda event: self.toggle_search_panel())  # 快捷键呼出查找替换

        self.apply_theme_colors()
        self.update_editor_status()

    # --- 搜索面板呼出逻辑 ---
    def toggle_search_panel(self):
        if self.search_panel_visible:
            self.search_frame.pack_forget()
            self.search_panel_visible = False
        else:
            self.search_frame.pack(after=self.top_frame, side=tk.TOP, fill=tk.X, padx=15, pady=(0, 5))
            self.search_panel_visible = True

    # --- 颜色与主题 ---
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme_colors()

    def apply_theme_colors(self):
        if self.is_dark_mode:
            bg_main, bg_sec, fg_text, bg_text, hl_line = "#1E1E1E", "#252526", "#D4D4D4", "#1E1E1E", "#2D2D30"
            btn_bg, btn_fg = "#333333", "#CCCCCC"
            entry_bg, entry_fg, entry_border = "#3F3F46", "#F4F4F5", "#71717A"
            sel_bg, sel_fg = "#0284C7", "#FFFFFF"

            self.view_menu.entryconfig(3, label="☀️ 切换日间模式")
            self.btn_find.config(bg="#065F46", fg="#D1FAE5", activebackground="#047857")
            self.btn_replace.config(bg="#312E81", fg="#E0E7FF", activebackground="#3730A3")
            self.btn_save.config(bg="#059669", fg="#FFFFFF", activebackground="#047857")
        else:
            bg_main, bg_sec, fg_text, bg_text, hl_line = "#F3F4F6", "#FFFFFF", "#4B5563", "#FFFFFF", "#F3F4F6"
            btn_bg, btn_fg = "#E5E7EB", "black"
            entry_bg, entry_fg, entry_border = "#FFFFFF", "#000000", "#D1D5DB"
            sel_bg, sel_fg = "#93C5FD", "#000000"

            self.view_menu.entryconfig(3, label="🌙 切换夜间模式")
            self.btn_find.config(bg="#D1FAE5", fg="#065F46", activebackground="#A7F3D0")
            self.btn_replace.config(bg="#E0E7FF", fg="#3730A3", activebackground="#C7D2FE")
            self.btn_save.config(bg="#10B981", fg="white", activebackground="#059669")

        self.root.configure(bg=bg_main)
        for frame in [self.top_frame, self.search_frame, self.mid_frame, self.bottom_frame]:
            frame.configure(bg=bg_main)

        self.top_frame.configure(bg=bg_sec)
        self.text_container.configure(bg=bg_text, highlightbackground=bg_sec)

        self.target_label.configure(bg=bg_sec)
        for label in [self.search_label1, self.search_label2, self.status_label, self.stats_label]:
            label.configure(bg=bg_main, fg=fg_text)

        self.search_entry.configure(bg=entry_bg, fg=entry_fg, insertbackground=entry_fg,
                                    highlightbackground=entry_border)
        self.replace_entry.configure(bg=entry_bg, fg=entry_fg, insertbackground=entry_fg,
                                     highlightbackground=entry_border)

        self.text_editor.configure(bg=bg_text, fg=fg_text, insertbackground=fg_text,
                                   selectbackground=sel_bg, selectforeground=sel_fg)
        self.text_editor.tag_configure("current_line", background=hl_line)

        try:
            self.text_editor.tag_raise("sel")
            self.text_editor.tag_raise("search_highlight")
        except tk.TclError:
            pass

    # --- 功能实现区 ---
    def find_next(self):
        search_term = self.search_entry.get()
        if not search_term:
            self.show_status_message("请输入要查找的内容！", "#EF4444" if not self.is_dark_mode else "#FCA5A5")
            return

        if search_term != self.last_search_term:
            self.search_start_index = "1.0"
            self.last_search_term = search_term

        self.text_editor.tag_remove("search_highlight", "1.0", tk.END)
        pos = self.text_editor.search(search_term, self.search_start_index, stopindex=tk.END)

        if pos:
            end_pos = f"{pos}+{len(search_term)}c"
            self.text_editor.tag_add("search_highlight", pos, end_pos)
            self.text_editor.tag_config("search_highlight", background="#FDE047", foreground="black")
            self.text_editor.see(pos)

            line_num = pos.split('.')[0]
            self.show_status_message(f"📍 已定位匹配项：第 {line_num} 行", "#10B981")
            self.search_start_index = end_pos
        else:
            self.show_status_message("⚠️ 已查找到文档末尾。", "#D97706" if not self.is_dark_mode else "#FBBF24")
            self.search_start_index = "1.0"

    def format_indent(self):
        text = self.text_editor.get("1.0", "end-1c")
        if not text: return

        scroll_pos = self.text_editor.yview()
        cursor_pos = self.text_editor.index(tk.INSERT)

        lines = text.split('\n')
        new_lines = []
        for line in lines:
            clean_line = line.strip(" \t　")
            if clean_line:
                if not clean_line.startswith(('「', '『', '（', '【', '《', '〈', '＜', '(', '<', '●', '■', '—', '-')):
                    clean_line = '　' + clean_line
                new_lines.append(clean_line)
            else:
                new_lines.append("")

        formatted_text = '\n'.join(new_lines)

        self.text_editor.config(autoseparators=False)
        self.text_editor.edit_separator()
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", formatted_text)
        self.text_editor.edit_separator()
        self.text_editor.config(autoseparators=True)

        self.text_editor.update_idletasks()
        self.text_editor.mark_set(tk.INSERT, cursor_pos)
        self.text_editor.yview_moveto(scroll_pos[0])
        self.text_editor.see(tk.INSERT)

        self.show_status_message("✨ 智能首行缩进完毕！", "#10B981")
        self.update_editor_status()

    def replace_all_text(self):
        find_str = self.search_entry.get()
        replace_str = self.replace_entry.get()
        if not find_str:
            self.show_status_message("请输入要查找的内容！", "#EF4444" if not self.is_dark_mode else "#FCA5A5")
            return

        current_text = self.text_editor.get("1.0", "end-1c")
        if find_str in current_text:
            scroll_pos = self.text_editor.yview()
            cursor_pos = self.text_editor.index(tk.INSERT)

            count = current_text.count(find_str)
            new_text = current_text.replace(find_str, replace_str)

            self.text_editor.config(autoseparators=False)
            self.text_editor.edit_separator()
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", new_text)
            self.text_editor.edit_separator()
            self.text_editor.config(autoseparators=True)

            self.text_editor.update_idletasks()
            self.text_editor.mark_set(tk.INSERT, cursor_pos)
            self.text_editor.yview_moveto(scroll_pos[0])
            self.text_editor.see(tk.INSERT)

            self.show_status_message(f"✅ 替换成功！共替换了 {count} 处。", "#10B981")
            self.update_editor_status()
        else:
            self.show_status_message(f"未找到包含 '{find_str}' 的内容。", "#6B7280")

    def undo_action(self):
        try:
            self.text_editor.edit_undo()
            self.show_status_message("已撤销上一步操作", "#D97706" if not self.is_dark_mode else "#FBBF24")
            self.update_editor_status()
            self.text_editor.see(tk.INSERT)
        except tk.TclError:
            self.show_status_message("没有可以撤销的操作了", "#6B7280")

    def update_editor_status(self, event=None):
        self.text_editor.tag_remove("current_line", "1.0", tk.END)
        self.text_editor.tag_add("current_line", "insert linestart", "insert lineend+1c")

        try:
            cursor_pos = self.text_editor.index(tk.INSERT)
            curr_line = cursor_pos.split('.')[0]
            curr_col = cursor_pos.split('.')[1]
            content = self.text_editor.get("1.0", "end-1c")
            self.stats_label.config(text=f"第 {curr_line} 行, 第 {curr_col} 列 | 共 {len(content)} 字符")
        except:
            pass

    def on_closing(self):
        content = self.text_editor.get("1.0", "end-1c").strip()
        if content:
            if not messagebox.askyesno("未保存警告",
                                       "您的编辑区还有未保存的译文！\n确定要直接退出吗？（未保存的内容将永久丢失）"):
                return
        self.root.destroy()

    def load_last_save_path(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved_path = f.read().strip()
                if saved_path and os.path.exists(os.path.dirname(saved_path)):
                    self.target_file = saved_path
                    self.target_label.config(text=f"当前目标: {saved_path}", fg="#10B981")
            except Exception:
                pass

    def save_path_to_config(self, path):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write(path)
        except Exception:
            pass

    def select_target_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")],
                                                 title="选择保存译文的文件")
        if file_path:
            self.target_file = file_path
            self.target_label.config(text=f"当前目标: {file_path}", fg="#10B981")
            self.save_path_to_config(file_path)

    def change_font_size(self, delta):
        self.current_font_size += delta
        if self.current_font_size < 8: self.current_font_size = 8
        if self.current_font_size > 40: self.current_font_size = 40
        self.text_editor.config(font=(self.font_family, self.current_font_size))
        self.show_status_message(f"字号已调整为 {self.current_font_size}", "#10B981")

    def clear_text(self):
        self.text_editor.delete("1.0", tk.END)
        self.update_editor_status()

    def shortcut_save(self):
        self.save_and_clear()
        return "break"

    def show_status_message(self, msg, color="#10B981"):
        self.status_label.config(text=msg, fg=color)
        if self._timer:
            self.root.after_cancel(self._timer)
        self._timer = self.root.after(2500, self.hide_status_message)

    def hide_status_message(self):
        self.status_label.config(text="")

    def save_and_clear(self):
        if not self.target_file:
            messagebox.showwarning("提示", "请先在上方菜单栏【文件】中设置保存的 TXT 文件！")
            return

        text_to_save = self.text_editor.get("1.0", "end-1c").rstrip('\n')
        if not text_to_save.strip():
            self.clear_text()
            return

        try:
            with open(self.target_file, "a", encoding="utf-8") as f:
                f.write(text_to_save + "\n\n")
                f.flush()
                os.fsync(f.fileno())

            self.clear_text()
            self.show_status_message("✅ 已成功保存并清空！", "#10B981")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法写入文件: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationFormatter(root)
    root.mainloop()