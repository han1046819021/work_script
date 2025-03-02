import pandas as pd
import os

def get_excel_files_from_folder(folder_path):
    """获取文件夹中所有的Excel文件路径"""
    excel_files = []
    for file in os.listdir(folder_path):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            excel_files.append(os.path.join(folder_path, file))
    return excel_files

def merge_excel_files_to_sheets(input_folder, output_file):
    # 获取文件夹中的所有Excel文件
    input_files = get_excel_files_from_folder(input_folder)
    
    if not input_files:
        print("文件夹中没有找到Excel文件。")
        return

    # 创建一个ExcelWriter对象，用于写入多个工作表
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for file in input_files:
            # 读取Excel文件
            df = pd.read_excel(file)
            # 获取文件名（不带扩展名）作为工作表名称
            sheet_name = os.path.splitext(os.path.basename(file))[0]
            # 将DataFrame写入Excel文件中的新工作表
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"所有文件已成功整合到 {output_file} 中。")

if __name__ == "__main__":
    # 输入文件夹路径
    input_folder = r'E:\NAS转存文件\笔记本文件暂存\工作文件夹\康复大学\新建文件夹'  # 替换为你的文件夹路径
    
    # 输出文件路径
    output_file = r'E:\NAS转存文件\笔记本文件暂存\工作文件夹\康复大学\新建文件夹\1.xlsx'
    
    # 调用函数进行整合
    merge_excel_files_to_sheets(input_folder, output_file)