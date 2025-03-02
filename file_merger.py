import os
import shutil
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading

# 定义支持的文件类型
SUPPORTED_EXCEL = ('.xlsx', '.xls')
SUPPORTED_TEXT = ('.txt', '.log', '.csv')
SUPPORTED_IMAGES = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')

# ====================== 文件处理功能 ======================

def get_files_from_folder(folder_path, extensions):
    """获取文件夹中指定扩展名的文件路径"""
    files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(extensions):
            files.append(os.path.join(folder_path, file))
    return files

def get_files_from_folders(folder_paths, extensions):
    """从多个文件夹获取指定扩展名的文件路径"""
    all_files = []
    for folder in folder_paths:
        files = get_files_from_folder(folder, extensions)
        all_files.extend(files)
    return all_files

# ====================== Excel文件合并功能 ======================

def merge_excel_files_to_sheets(input_folders, output_file, status_callback=None):
    """将多个文件夹中的Excel文件合并到一个Excel文件的不同工作表中"""
    # 获取所有文件夹中的Excel文件
    input_files = get_files_from_folders(input_folders, SUPPORTED_EXCEL)
    
    if not input_files:
        if status_callback:
            status_callback("未找到Excel文件。")
        return False
    
    try:
        # 创建一个ExcelWriter对象，用于写入多个工作表
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            total_files = len(input_files)
            for i, file in enumerate(input_files):
                # 更新进度
                if status_callback:
                    status_callback(f"正在处理 {i+1}/{total_files}: {os.path.basename(file)}")
                
                # 读取Excel文件
                df = pd.read_excel(file)
                # 获取文件名（不带扩展名）作为工作表名称
                sheet_name = os.path.splitext(os.path.basename(file))[0]
                # 如果工作表名称过长，进行截断
                if len(sheet_name) > 31:  # Excel工作表名称最大长度为31个字符
                    sheet_name = sheet_name[:31]
                # 将DataFrame写入Excel文件中的新工作表
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        if status_callback:
            status_callback(f"所有Excel文件已成功整合到 {output_file} 中。")
        return True
    except Exception as e:
        if status_callback:
            status_callback(f"合并Excel文件时出错: {str(e)}")
        return False

# ====================== TXT文件合并功能 ======================

def merge_txt_files(input_folders, output_file, status_callback=None):
    """将多个文件夹中的文本文件合并到一个文本文件中"""
    # 获取所有文件夹中的文本文件
    txt_files = get_files_from_folders(input_folders, SUPPORTED_TEXT)
    
    if not txt_files:
        if status_callback:
            status_callback("未找到文本文件。")
        return False
    
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            total_files = len(txt_files)
            for i, txt_file in enumerate(txt_files):
                # 更新进度
                if status_callback:
                    status_callback(f"正在处理 {i+1}/{total_files}: {os.path.basename(txt_file)}")
                
                # 写入文件标题作为分隔符
                outfile.write(f"\n----- {os.path.basename(txt_file)} -----\n\n")
                
                # 读取并写入文件内容
                try:
                    with open(txt_file, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except UnicodeDecodeError:
                    # 如果UTF-8解码失败，尝试使用GBK编码
                    with open(txt_file, 'r', encoding='gbk') as infile:
                        outfile.write(infile.read())
                outfile.write("\n\n")  # 文件之间增加空行作为分隔
        
        if status_callback:
            status_callback(f"所有文本文件已成功整合到 {output_file} 中。")
        return True
    except Exception as e:
        if status_callback:
            status_callback(f"合并文本文件时出错: {str(e)}")
        return False

# ====================== 图片文件合并功能 ======================

def copy_images(input_folders, destination_folder, status_callback=None):
    """将多个文件夹中的图片文件复制到目标文件夹中"""
    # 如果目标文件夹不存在，则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # 获取所有图片文件
    all_images = []
    for folder in input_folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(SUPPORTED_IMAGES):
                    all_images.append(os.path.join(root, file))
    
    if not all_images:
        if status_callback:
            status_callback("未找到图片文件。")
        return False
    
    try:
        total_files = len(all_images)
        copied_count = 0
        
        for i, source_file in enumerate(all_images):
            # 更新进度
            if status_callback:
                status_callback(f"正在处理 {i+1}/{total_files}: {os.path.basename(source_file)}")
            
            # 构建目标文件路径
            destination_file = os.path.join(destination_folder, os.path.basename(source_file))
            
            # 如果目标文件夹中已经存在同名文件，则修改文件名
            if os.path.exists(destination_file):
                base_name, ext = os.path.splitext(os.path.basename(source_file))
                counter = 1
                # 如果同名文件存在，则添加数字后缀
                while os.path.exists(destination_file):
                    destination_file = os.path.join(destination_folder, f"{base_name}_{counter}{ext}")
                    counter += 1
            
            # 复制图片到目标文件夹
            shutil.copy(source_file, destination_file)
            copied_count += 1
        
        if status_callback:
            status_callback(f"已成功复制 {copied_count} 个图片文件到 {destination_folder} 中。")
        return True
    except Exception as e:
        if status_callback:
            status_callback(f"复制图片文件时出错: {str(e)}")
        return False

# ====================== 多文件夹合并功能 ======================

def merge_folders(input_folders, output_folder, file_types, status_callback=None):
    """根据选择的文件类型合并多个文件夹的内容"""
    results = []
    
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 处理Excel文件
    if 'excel' in file_types:
        excel_output = os.path.join(output_folder, "合并Excel.xlsx")
        excel_result = merge_excel_files_to_sheets(input_folders, excel_output, status_callback)
        results.append(("Excel", excel_result))
    
    # 处理文本文件
    if 'text' in file_types:
        text_output = os.path.join(output_folder, "合并文本.txt")
        text_result = merge_txt_files(input_folders, text_output, status_callback)
        results.append(("文本", text_result))
    
    # 处理图片文件
    if 'image' in file_types:
        image_output = os.path.join(output_folder, "合并图片")
        image_result = copy_images(input_folders, image_output, status_callback)
        results.append(("图片", image_result))
    
    return results

# 如果直接运行此脚本，则显示使用说明
if __name__ == "__main__":
    print("这是文件合并工具的后端模块。请运行 file_merger_gui.py 来启动图形界面。")