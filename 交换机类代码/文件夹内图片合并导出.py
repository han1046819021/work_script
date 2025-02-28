import os
import shutil

# 定义支持的图片文件格式
supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')

# 遍历文件夹，复制图片文件
def copy_images(source_folder, destination_folder):
    # 如果目标文件夹不存在，则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # 遍历源文件夹及其子文件夹
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            # 判断文件是否为图片
            if file.lower().endswith(supported_extensions):
                # 构建源文件路径
                source_file = os.path.join(root, file)
                # 构建目标文件路径
                destination_file = os.path.join(destination_folder, file)
                
                # 如果目标文件夹中已经存在同名文件，则修改文件名
                if os.path.exists(destination_file):
                    base_name, ext = os.path.splitext(file)
                    counter = 1
                    # 如果同名文件存在，则添加数字后缀
                    while os.path.exists(destination_file):
                        destination_file = os.path.join(destination_folder, f"{base_name}_{counter}{ext}")
                        counter += 1
                
                # 复制图片到目标文件夹
                shutil.copy(source_file, destination_file)
                print(f"已复制: {source_file} -> {destination_file}")

# 主程序
def main():
    # 输入源文件夹和目标文件夹路径
    source_folder = r"C:\Users\10468\Desktop\QAQ"  # 替换为你的源文件夹路径
    destination_folder = r"C:\Users\10468\Desktop\QAQ\合并图片"  # 替换为你的目标文件夹路径
    
    # 调用复制函数
    copy_images(source_folder, destination_folder)
    print("图片复制完成！")

if __name__ == '__main__':
    main()
