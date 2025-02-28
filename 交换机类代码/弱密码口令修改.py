from netmiko import ConnectHandler
import time

# 定义交换机连接的通用配置
device_config = {
    'device_type': 'h3c',  # H3C交换机类型
    'username': 'admin',    # 交换机的用户名
    'password': 'weakpassword',  # 现有的弱密码
    'secret': 'secret',     # enable模式的密码
    'timeout': 30,          # 超时设定
}

# 强密码，可以按需要修改
new_password = 'StrongP@ssw0rd'

# 读取设备IP表文件
def read_device_ips(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

# 修改设备密码
def change_password(ip):
    # 更新设备的 IP 地址
    device_config['host'] = ip

    try:
        # 连接交换机
        print(f"Connecting to device {ip}...")
        net_connect = ConnectHandler(**device_config)
        
        # 进入特权模式
        net_connect.enable()

        # 修改密码命令
        change_pass_command = f"""
            system-view
            local-user admin password irreversible-cipher {new_password}
            save
        """
        
        # 执行命令
        print(f"Changing password on {ip}...")
        net_connect.send_config_set(change_pass_command)
        time.sleep(1)

        # 保存配置
        net_connect.send_command('save')
        print(f"Password changed successfully on {ip}.")

        # 断开连接
        net_connect.disconnect()
    except Exception as e:
        print(f"Failed to connect or change password on {ip}: {str(e)}")

# 主程序
if __name__ == '__main__':
    device_ips = read_device_ips('设备ip表.txt')  # 提供设备ip表的路径

    # 对每个交换机进行密码修改
    for ip in device_ips:
        change_password(ip)
