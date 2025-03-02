import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from file_merger import merge_folders

class FileMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件合并工具")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TCheckbutton", font=("微软雅黑", 10))
        self.style.configure("TFrame", background="#f0f0f0")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建界面元素
        self.create_widgets()
        
        # 初始化变量
        self.input_folders = []
        self.output_folder = ""
        self.merge_thread = None
        
    def create_widgets(self):
        # 创建标题
        title_label = ttk.Label(self.main_frame, text="文件合并工具", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=10)
        
        # 创建文件类型选择框架
        file_types_frame = ttk.LabelFrame(self.main_frame, text="选择要合并的文件类型", padding="10")
        file_types_frame.pack(fill=tk.X, pady=10)
        
        # 文件类型选择
        self.excel_var = tk.BooleanVar(value=True)
        self.text_var = tk.BooleanVar(value=False)
        self.image_var = tk.BooleanVar(value=False)
        
        excel_cb = ttk.Checkbutton(file_types_frame, text="Excel文件(.xlsx, .xls)", variable=self.excel_var)
        text_cb = ttk.Checkbutton(file_types_frame, text="文本文件(.txt, .log, .csv)", variable=self.text_var)
        image_cb = ttk.Checkbutton(file_types_frame, text="图片文件(.jpg, .jpeg, .png, .gif, .bmp, .tiff)", variable=self.image_var)
        
        excel_cb.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        text_cb.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        image_cb.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # 创建源文件夹选择框架
        source_frame = ttk.LabelFrame(self.main_frame, text="选择源文件夹", padding="10")
        source_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 添加源文件夹按钮
        add_folder_btn = ttk.Button(source_frame, text="添加文件夹", command=self.add_folder)
        add_folder_btn.pack(side=tk.TOP, anchor="w", pady=5)
        
        # 源文件夹列表框架
        folders_frame = ttk.Frame(source_frame)
        folders_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(folders_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建列表框
        self.folders_listbox = tk.Listbox(folders_frame, selectmode=tk.EXTENDED, font=("微软雅黑", 10))
        self.folders_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        self.folders_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.folders_listbox.yview)
        
        # 删除选中文件夹按钮
        remove_folder_btn = ttk.Button(source_frame, text="删除选中文件夹", command=self.remove_folder)
        remove_folder_btn.pack(side=tk.TOP, anchor="w", pady=5)
        
        # 创建目标文件夹选择框架
        target_frame = ttk.LabelFrame(self.main_frame, text="选择目标文件夹", padding="10")
        target_frame.pack(fill=tk.X, pady=10)
        
        # 目标文件夹选择
        self.output_folder_var = tk.StringVar()
        output_entry = ttk.Entry(target_frame, textvariable=self.output_folder_var, width=60)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        output_btn = ttk.Button(target_frame, text="浏览...", command=self.select_output_folder)
        output_btn.pack(side=tk.RIGHT, padx=5)
        
        # 创建状态框架
        status_frame = ttk.LabelFrame(self.main_frame, text="处理状态", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        # 状态文本框
        self.status_text = tk.Text(status_frame, height=5, wrap=tk.WORD, font=("微软雅黑", 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # 操作按钮框架
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # 开始合并按钮
        self.merge_btn = ttk.Button(buttons_frame, text="开始合并", command=self.start_merge)
        self.merge_btn.pack(side=tk.RIGHT, padx=5)
        
        # 退出按钮
        exit_btn = ttk.Button(buttons_frame, text="退出", command=self.root.quit)
        exit_btn.pack(side=tk.RIGHT, padx=5)
    
    def add_folder(self):
        folder = filedialog.askdirectory(title="选择源文件夹")
        if folder:
            if folder not in self.input_folders:
                self.input_folders.append(folder)
                self.folders_listbox.insert(tk.END, folder)
                self.update_status(f"已添加文件夹: {folder}")
            else:
                messagebox.showinfo("提示", "该文件夹已添加")
    
    def remove_folder(self):
        selected_indices = self.folders_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "请先选择要删除的文件夹")
            return
        
        # 从后往前删除，避免索引变化
        for i in sorted(selected_indices, reverse=True):
            folder = self.folders_listbox.get(i)
            self.folders_listbox.delete(i)
            self.input_folders.remove(folder)
            self.update_status(f"已移除文件夹: {folder}")
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="选择目标文件夹")
        if folder:
            self.output_folder = folder
            self.output_folder_var.set(folder)
            self.update_status(f"已选择目标文件夹: {folder}")
    
    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def start_merge(self):
        # 检查是否选择了文件类型
        file_types = []
        if self.excel_var.get():
            file_types.append('excel')
        if self.text_var.get():
            file_types.append('text')
        if self.image_var.get():
            file_types.append('image')
        
        if not file_types:
            messagebox.showerror("错误", "请至少选择一种文件类型")
            return
        
        # 检查是否选择了源文件夹
        if not self.input_folders:
            messagebox.showerror("错误", "请至少添加一个源文件夹")
            return
        
        # 检查是否选择了目标文件夹
        if not self.output_folder:
            messagebox.showerror("错误", "请选择目标文件夹")
            return
        
        # 禁用开始按钮，避免重复点击
        self.merge_btn.config(state=tk.DISABLED)
        
        # 清空状态文本框
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        
        # 重置进度条
        self.progress_var.set(0)
        
        # 在新线程中执行合并操作
        self.merge_thread = threading.Thread(target=self.run_merge, args=(file_types,))
        self.merge_thread.daemon = True
        self.merge_thread.start()
    
    def run_merge(self, file_types):
        try:
            self.update_status("开始合并文件...")
            
            # 调用合并函数
            results = merge_folders(self.input_folders, self.output_folder, file_types, self.update_status)
            
            # 处理结果
            success_count = sum(1 for _, success in results if success)
            total_count = len(results)
            
            if success_count == total_count:
                messagebox.showinfo("成功", "所有文件合并成功！")
            elif success_count > 0:
                messagebox.showwarning("部分成功", f"合并完成，但有 {total_count - success_count} 种文件类型合并失败。")
            else:
                messagebox.showerror("失败", "所有文件合并失败，请检查日志。")
            
            # 设置进度条为100%
            self.progress_var.set(100)
            
        except Exception as e:
            self.update_status(f"合并过程中出错: {str(e)}")
            messagebox.showerror("错误", f"合并过程中出错: {str(e)}")
        finally:
            # 恢复开始按钮
            self.merge_btn.config(state=tk.NORMAL)

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = FileMergerApp(root)
    root.mainloop()