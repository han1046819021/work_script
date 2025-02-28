#我来帮你编写一个Python脚本，用于修改锐捷交换机的弱口令。这个脚本将：
#1. 读取IP地址表
#2. 连接每个锐捷交换机
#3. 修改密码为强密码
#4. 导出新的密码对照表

#以下是建议的代码：

#```python:交换机弱口令修改.py
import pandas as pd
import paramiko
import random
import string
from datetime import datetime

def generate_strong_password(length=12):
    """生成强密码：包含大小写字母、数字和特殊字符"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = []
    # 确保密码包含至少一个大写字母、小写字母、数字和特殊字符
    password.append(random.choice(string.ascii_uppercase))
    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.digits))
    password.append(random.choice("!@#$%^&*"))
    
    # 填充剩余长度
    for i in range(length - 4):
        password.append(random.choice(characters))
    
    # 打乱密码顺序
    random.shuffle(password)
    return ''.join(password)

def change_switch_password(ip, username, old_password, new_password):
    """修改交换机密码"""
    try:
        # 建立SSH连接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=old_password)
        
        # 进入配置模式并修改密码
        commands = [
            'enable',
            'configure terminal',
            f'username {username} password {new_password}',
            'exit',
            'write',
            'exit'
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()
        
        ssh.close()
        return True
    except Exception as e:
        print(f"修改密码失败 {ip}: {str(e)}")
        return False

def main():
    # 读取IP地址表（假设是CSV格式）
    try:
        df = pd.read_csv('ip_list.csv')
    except:
        print("无法读取IP地址表文件")
        return

    # 创建结果DataFrame
    results = []
    
    # 处理每个IP地址
    for index, row in df.iterrows():
        ip = row['ip']  # 假设CSV文件中有'ip'列
        new_password = generate_strong_password()
        
        success = change_switch_password(
            ip=ip,
            username='admin',
            old_password='ruijie@123',
            new_password=new_password
        )
        
        results.append({
            'IP': ip,
            'New_Password': new_password if success else '修改失败',
            'Status': '成功' if success else '失败'
        })
    
    # 创建结果DataFrame并导
