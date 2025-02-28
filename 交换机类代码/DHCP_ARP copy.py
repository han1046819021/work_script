# -*- coding: utf-8 -*-
import paramiko
import time
import re
import time
from netmiko import ConnectHandler, platforms, ssh_dispatcher
import ipaddress

def connect_info(device_type, host, username, password):
    device = {
        'device_type': device_type,  # 填写适配过的type
        'host': host,  # 你需要远程管理的设备IP地址
        'username': username,  # SSH名称
        'password': password,  # SSH密码
        'port': 22,  # optional, defaults to 22，SSH端口
        # 'secret': 'secret',  # optional, defaults to '' ##Cisco的特权密码，华为、华三不涉及
    }
    with ConnectHandler(**device) as conn:
        flag = ""
        if conn.device_type == "ruijie_os":
            print("############# ruijie ################")
            Dhcp_information = conn.send_command('dis dhcp snooping trust')  # 显示DHCP配置信息
            if "DHCP snooping is enabled" in Dhcp_information and "Tunnel trusted" in Dhcp_information:
                print(Dhcp_information)
                flag = True
                return flag
            else:
                flag = False
                return flag
        elif conn.device_type == "hp_comware":
            print("############# H3C ################")
            Dhcp_information = conn.send_command('dis dhcp snooping trust')  # 显示DHCP配置信息
            if "DHCP snooping is enabled" in Dhcp_information:
                flag = True
                # 使用正则表达式提取符合格式的部分
                matches = re.findall(r"(Ten-GigabitEthernet\d+/\d+/\d+\s+Trusted)", Dhcp_information)
                matches2 = re.findall(r"^XGE\d+/\d+/\d+\s+Trusted\s+-$", Dhcp_information, re.MULTILINE)
                # 处理并输出结果
                if len(matches) == 0:
                    if len(matches2) == 0:
                        print("没匹配到端口啊！！！！！！！！！！！")
                    else:
                        for match2 in matches2:
                            if "Trusted" in match2.strip():
                                print(match2.strip())
                            else:
                                flag = False   # 只要有一个端口状态不是Trusted就需要重新刷
                else:
                    for match in matches:
                        if "Trusted" in match.strip():
                            print(match.strip())
                        else:
                            flag = False   # 只要有一个端口状态不是Trusted就需要重新刷

                print("##########################################")
                print(Dhcp_information)
                return flag
            else:
                print(Dhcp_information)
                flag = False
                return flag
        elif conn.device_type == "huawei":
            print("############# Huawei ################")
        # print(conn)
    # 关闭连接
    conn.disconnect()


def generate_ips(OS_type, start_ip, end_ip, username, password):
    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)
    device_infos = {}
    if start > end:
        raise ValueError("Start IP must be less than or equal to End IP")
    current_ip = start
    while current_ip <= end:
        Flag = connect_info(OS_type, str(current_ip), username, password)
        # 添加设备信息，以IP地址作为键值
        device_infos[str(current_ip)] = Flag
        # 刷命令
        if Flag == True:
            print(current_ip, "  配置已存在，不用刷了！")
        elif Flag == False:
            print("@@@@@@@@@@@@@@@@@@@@@@@@@")
            result = sshcon(str(current_ip), "22", username, password, OS_type)
            device_infos.update(result)
            print("#########################")
        current_ip += 1
    return device_infos


## 刷入命令
def sshcon(ip,port,username,password, device_type):
    result = {}
    device = {
        'device_type': device_type,  # 填写适配过的type
        'host': ip,  # 你需要远程管理的设备IP地址
        'username': username,  # SSH名称
        'password': password,  # SSH密码
        'port': 22,  # optional, defaults to 22，SSH端口
        # 'secret': 'secret',  # optional, defaults to '' ##Cisco的特权密码，华为、华三不涉及
    }
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    with ConnectHandler(**device) as conn:
        if conn.device_type == "ruijie_os":
            print("############# ruijie ################")
            Dhcp_information = conn.send_command('dis dhcp snooping trust')  # 显示DHCP配置信息
            if "DHCP snooping is enabled" in Dhcp_information and "Tunnel trusted" in Dhcp_information:
                print(Dhcp_information)
                flag = True
                return flag
            else:
                flag = False
                return flag
        elif conn.device_type == "hp_comware":
            interfaces_information = conn.send_command("dis int brief")  # 显示interfaces配置信息
            print(interfaces_information)

            # 定义正则表达式模式
            pattern = r'(XGE\d/\d/\d+.*)'
            # 使用正则表达式匹配
            matches = re.findall(pattern, interfaces_information)
            # 打印匹配结果
            for match in matches:
                # print("222222222222222222222222")
                # print(match)
                if "UP" in match:
                    int = match.split(" ")[0]
                    print(int)
                    result[int] = "UP"
                elif "DOWN" in match:
                    int = match.split(" ")[0]
                    print(int)
                    result[int] = "DOWN"
            cmds = ['system-view \n', 'dhcp snooping enable \n']
            for ints in result:
                print(ints[3:])
                cmds.append(f"interface ten {ints[3:]} \n")
                cmds.append(f"dhcp snooping trust \n")
            cmds = cmds + ['save\n', '\n', 'Y\n', '\n', '\n', 'Y\n', '\n', 'quit\n', 'quit\n', ]
            print("cmds:  ",cmds)
            write_command(ip, port, username, password, cmds)
            time.sleep(2)
            Flag = connect_info(device_type, ip, username, password)
            if Flag == True:
                print("刷入成功！")
                result["status"] = "刷入成功！"
            else:
                print("刷入失败！")
                result["status"] = "刷入失败！"
        elif conn.device_type == "huawei":
            print("############# Huawei ################")
        # print(conn)
    print(result)
    # 关闭连接
    # conn.disconnect()
    return result


def write_command(ip,port,username,password,cmds):
    try:
        sshcon=paramiko.SSHClient()
        sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshcon.connect(ip,port,username,password,compress=True)
        print("ssh secuees")
        conn = sshcon.invoke_shell()
        for cmd in cmds:
            conn.send(cmd)
            print("当前执行命令为: ", cmd)
            if "dhcp snooping enable" in cmd:
                time.sleep(5)
            time.sleep(3)
            print("命令执行结果: ")
            out = conn.recv(4096)
            print(out)
        sshcon.close()
    except Exception as e:
        print("connet error",e)


if __name__ == '__main__':
    connect_info("ruijie_os","10.168.0.3","root","ruijie@123")
    username = "root"
    password = "ruijie@123"
    start_ip = "10.168.0.2"
    end_ip = "10.168.0.2"
    OS_type = "ruijie_os"   # hp_comware,ruijie_os

    # username = "admin"
    # password = "Password@123"
    # start_ip = "10.168.29.1"
    # end_ip = "10.168.29.4"
    # OS_type = "hp_comware"   # hp_comware,ruijie_os

    result = generate_ips(OS_type, start_ip, end_ip, username, password)
    print(result)


