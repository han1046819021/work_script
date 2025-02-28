import os

def merge_txt_files(input_folder, output_file):
    # 获取文件夹内所有的txt文件
    txt_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for txt_file in txt_files:
            # 获取文件的完整路径
            file_path = os.path.join(input_folder, txt_file)
            
            # 写入文件标题作为分隔符
            outfile.write(f"----- {txt_file} -----\n")
            
            # 读取并写入文件内容
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write("\n\n")  # 文件之间增加空行作为分隔

# 使用示例
input_folder = r'E:\NAS转存文件\笔记本文件暂存\康复大学\康复大学\巡检脚本\锐捷交换机巡检记录\out-2024-12-18'  # 输入文件夹路径
output_file = r'E:\NAS转存文件\笔记本文件暂存\康复大学\康复大学\巡检脚本\锐捷交换机巡检记录\锐捷交换机巡检汇总\out-2024-12-18.txt'     # 输出合并后的文件路径

merge_txt_files(input_folder, output_file)
print("合并完成！")
