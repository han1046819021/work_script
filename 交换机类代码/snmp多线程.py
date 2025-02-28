# -*- coding: utf-8 -*-
import ipaddress
import sys
from socket import socket
import paramiko
import time
from concurrent.futures import ThreadPoolExecutor
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException

# 设备默认账户配置
DEVICE_CREDENTIALS = {
    'h3c': {
        'username': 'admin',
        'password': 'Password@123'
    },
    'ruijie': {
        'username': 'admin',
        'password': 'ruijie@123'
    }
}

# 设备配置命令模板
DEVICE_COMMANDS = {
    'h3c': {
        'lldp_only': [
            'system-view \n',
            'lldp global enable \n',
            'save\n','\n','Y\n','\n','\n','Y\n','\n','quit\n',
        ],
        'snmp_full': [
            'system-view \n',
            'lldp global enable \n',
            'snmp-agent \n',
            'snmp-agent community read ruijie \n',
            'snmp-agent sys-info version v2c \n',
            'snmp-agent trap enable \n',
            'snmp-agent target-host trap address udp-domain 10.113.14.3 params securityname ruijie v2c \n',
            'snmp-agent target-host trap address udp-domain 10.113.14.38 params securityname ruijie v2c \n',
            'save\n','\n','Y\n','\n','\n','Y\n','\n','quit\n',
        ]
    },
    'ruijie': {
        'snmp_full': [
            'conf t \n',
            'snmp-server enable version v2c \n','\n',
            'snmp-server host 10.113.14.38 traps version 2c ruijie \n',
            'snmp-server host 10.113.14.3 traps version 2c ruijie \n',
            'snmp-server enable traps \n',
            'snmp-server community ruijie ro \n','\n',
            'exit \n','\n','wr\n',
        ]
    }
}

def ssh_execute(ip, port, device_type='h3c', config_type='snmp_full'):
    """执行SSH连接和命令配置"""
    # 获取设备对应的账户信息
    credentials = DEVICE_CREDENTIALS.get(device_type)
    if not credentials:
        print(f"[{ip}] 错误: 未找到设备类型 {device_type} 的账户配置")
        return
        
    username = credentials['username']
    password = credentials['password']
    
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(ip, port, username, password, compress=True)
        print(f"[{ip}] SSH连接成功! (设备类型: {device_type})")

        # 获取设备对应的命令列表
        cmds = DEVICE_COMMANDS.get(device_type, {}).get(config_type, [])
        if not cmds:
            print(f"[{ip}] 错误: 未找到设备类型{device_type}的{config_type}配置")
            return

        conn = ssh_client.invoke_shell()
        for cmd in cmds:
            print(f"[{ip}] 执行命令: {cmd.strip()}")
            conn.send(cmd)
            time.sleep(2)
            output = conn.recv(4096).decode('utf-8')
            print(f"[{ip}] 执行结果: {output}")

    except AuthenticationException:
        print(f"[{ip}] 认证失败: 用户名或密码错误 (用户名: {username})")
    except Exception as e:
        print(f"[{ip}] 连接错误: {str(e)}")
    finally:
        ssh_client.close()

def process_ip_range(start_ip, end_ip, device_type, config_type, max_threads=10):
    """使用线程池处理IP范围"""
    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)
    
    if start > end:
        raise ValueError("起始IP必须小于或等于结束IP")

    # 创建线程池
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        current_ip = start
        while current_ip <= end:
            executor.submit(
                ssh_execute,
                str(current_ip),
                22,
                device_type,
                config_type
            )
            current_ip += 1

if __name__ == "__main__":
    # 配置参数
    start_ip = "172.26.140.254"
    end_ip = "172.26.140.254"
    device_type = "h3c"  # 可选: 'h3c' 或 'ruijie'
    config_type = "snmp_full"  # 根据device_type选择对应的配置类型
    
    # 执行配置
    process_ip_range(
        start_ip,
        end_ip,
        device_type,
        config_type,
        max_threads=10
    )

