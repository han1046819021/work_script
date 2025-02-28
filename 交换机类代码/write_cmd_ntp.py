# -*- coding: utf-8 -*-
import paramiko
import time
from netmiko import ConnectHandler, platforms, ssh_dispatcher, NetMikoTimeoutException, NetMikoAuthenticationException
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
    try:
        with ConnectHandler(**device) as conn:
            flag = ""
            if conn.device_type == "ruijie_os":
                print(f"############# ruijie {str(host)} ################")
                test1 = conn.send_command("enable \n")
                print(test1)
                test2 = conn.send_command("ruijie@123 \n")
                print(test2)
                clock_information = conn.send_command("show ntp status")  # 显示时间信息
                print("当前NTP状态为:")
                print(clock_information)
                flag_1 = "Clock is synchronized"
                flag_2 = "reference is 10.170.10.252"
                if flag_1 in clock_information and flag_2 in clock_information:
                    flag = True
                    return flag
                else:
                    flag = False
                    return flag
            elif conn.device_type == "hp_comware":
                print(f"############# H3C {str(host)} ################")
                clock_information = conn.send_command("dis clock")  # 显示时间信息
                print("当前时间为： ", clock_information)
                real_day = "07/25/2024"
                if real_day in clock_information:
                    flag = True
                    return flag
                else:
                    flag = False
                    return flag
            elif conn.device_type == "huawei":
                print("############# Huawei ################")
            # print(conn)
        # 关闭连接
        conn.disconnect()
    except (NetMikoTimeoutException, NetMikoAuthenticationException) as e:
        print(f"捕获到SSH连接异常: {e}")


def generate_ips2(OS_type, start_ip, end_ip, username, password):
    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)
    shuaru_results = {}
    print("/n")
    print("/n")
    print("/n")
    print("【开始检测NTP配置是否刷入成功， 请等待.... ....】")
    if start > end:
        raise ValueError("Start IP must be less than or equal to End IP")
    current_ip = start
    while current_ip <= end:
        Flag = connect_info(OS_type, str(current_ip), username, password)
        if Flag:
            print("NTP配置刷入成功！")
            shuaru_results.update({str(current_ip): Flag})
            print({str(current_ip): Flag})
        else:
            print("NTP配置刷入异常！")
            shuaru_results.update({str(current_ip): Flag})
            print({str(current_ip): Flag})
        current_ip += 1
    return shuaru_results

def generate_ips(OS_type, start_ip, end_ip, username, password):
    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)
    device_infos = {}
    shuaru_results = {}
    ntp_infos = {}
    if start > end:
        raise ValueError("Start IP must be less than or equal to End IP")
    current_ip = start
    while current_ip <= end:
        Flag = connect_info(OS_type, str(current_ip), username, password)
        # 添加设备信息，以IP地址作为键值
        device_infos[str(current_ip)] = Flag
        # 刷命令
        if Flag == True:
            print(current_ip, "NTP已正常同步，不用刷了！")
            ntp_infos.update({'right_ntp': str(current_ip)})
        elif Flag == False:
            print(current_ip, "NTP未正常同步，请重新刷配置！")
            ntp_infos.update({'error_ntp': str(current_ip)})
            time.sleep(2)
            sshcon(str(current_ip), "22", username, password, OS_type)
            # device_infos.update(result)
            print("#########################")
        current_ip += 1
    # 延时3分钟，等待ntp配置生效，生效后进行检查配置是否已刷入成功
    time.sleep(180)
    shuaru_results = generate_ips2(OS_type, start_ip, end_ip, username, password)
    return device_infos, shuaru_results


## 刷入命令
def sshcon(ip,port,username,password, device_type):
    device = {
        'device_type': device_type,  # 填写适配过的type
        'host': ip,  # 你需要远程管理的设备IP地址
        'username': username,  # SSH名称
        'password': password,  # SSH密码
        'port': 22,  # optional, defaults to 22，SSH端口
        # 'timeout': 60,
        # 'fast_cli': True,
        # 'global_delay_factor': 0.01,  # 设备连接信息 开启fast_cli快速模式，全局global_delay_factor延迟因子调小（默认值为1）
        # 'secret': 'secret',  # optional, defaults to '' ##Cisco的特权密码，华为、华三不涉及
    }
    try:
        with ConnectHandler(**device) as conn:
            if conn.device_type == "ruijie_os":
                print("############# ruijie ################")
                # cmds = ['system-view \n', 'clock timezone beijing 8 \n', 'ntp server 10.170.10.252 \n', 'save\n', '\n', 'Y\n', '\n', '\n', 'Y\n', '\n', 'quit\n', ]
                cmds=['enable','\n', 'ruijie@123\n','conf t \n', 'clock timezone beijing 8 \n', 'ntp server 10.170.10.252 \n', '\n','exit \n','\n','wr\n',]
                write_command(ip, port, username, password, cmds)
                time.sleep(2)
            elif conn.device_type == "hp_comware":
                cmds = ['system-view \n', 'clock timezone UTC+8 add 08:00:00 \n', 'ntp-service enable \n',
                        'ntp-service unicast-server 10.170.10.252 \n', 'save\n', '\n', 'Y\n', '\n', '\n', 'Y\n', '\n',
                        'quit\n', ]
                write_command(ip, port, username, password, cmds)
                time.sleep(3)
        # 关闭连接
        conn.disconnect()
    except (NetMikoTimeoutException, NetMikoAuthenticationException) as e:
        print(f"捕获到SSH连接异常: {e}")
    # except paramiko.AuthenticationException:
    #     print(f"Authentication failed when connecting to {hostname}:{port}")
    # except netmiko.
    #     .SSHException as sshException:
    #     print(f"Unable to establish SSH connection to {hostname}:{port} : {sshException}")
    # except paramiko.BadHostKeyException as badHostKeyException:
    #     print(f"Unable to verify server's host key : {badHostKeyException}")
    # except Exception as e:
    #     print(f"An unexpected error occurred : {e}")


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
            time.sleep(2)
            print("命令执行结果: ")
            out = conn.recv(4096)
            print(out)
        # sshcon.close()
    except Exception as e:
        print("connet error",e)


if __name__ == '__main__':
    # connect_info("ruijie_os","10.168.0.3","root","ruijie@123")
    username = "admin"
    password = "ruijie@123"
    start_ip = "10.168.1.1"
    end_ip = "10.168.1.254"
    OS_type = "ruijie_os"   # ruijie_os

    # username = "admin"
    # password = "Password@123"
    # start_ip = "10.168.27.12"
    # end_ip = "10.168.27.12"
    # OS_type = "hp_comware"   # hp_comware
    device_infos, shuaru_results = generate_ips(OS_type, start_ip, end_ip, username, password)

    print("当前检测到的设备NTP配置情况：", device_infos)
    print("NTP配置刷入情况：", shuaru_results)

