# -*- coding: utf-8 -*-
import ipaddress
import sys
from socket import socket

import paramiko
import time

from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException



def sshcon(ip,port,username,password):
    sshcon = paramiko.SSHClient()
    sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        sshcon.connect(ip, port, username, password, compress=True)
        #print "ok"
        #print 'ipaddress %s,port %d,uername %s,password %s'%(ip,port,username,password)
        print(f"[ {ip} ] ssh secuees!")
        # cmds=['system-view\n','acl nu 2800\n','rule  permit source ip  0 \n', \
        #       'rule  permit source ip 0 \n','rule  permit source ip  0 \n', \
        #       'rule  permit source ip  0 \n', 'rule  permit ip  0 \n', \
        #       'rule  permit source ip  0 \n', \
        #       'quit\n','quit\n','save\n','\n','Y\n','\n','\n','Y\n','\n','quit\n',]

        # 锐捷
        #cmds=['conf t \n','snmp-server enable  version  v2c \n','\n', 'snmp-server host 10.113.14.38 traps version 2c ruijie \n', 
        #      'snmp-server host 10.113.14.3 traps version 2c ruijie \n','snmp-server enable traps \n', 
        #      'snmp-server community ruijie ro \n','\n','exit \n','\n','wr\n',]

        # H3C
        # lldp启用
        #cmds=['system-view \n','lldp global enable \n','save\n','\n','Y\n','\n','\n','Y\n','\n','quit\n',]

        cmds=['system-view \n','lldp global enable \n','snmp-agent \n','snmp-agent community read ruijie \n', \
            'snmp-agent sys-info version v2c \n','snmp-agent trap  enable \n', \
            'snmp-agent target-host trap address udp-domain 10.113.14.3 params securityname ruijie v2c \n', \
            'snmp-agent target-host trap address udp-domain 10.113.12.38 params securityname ruijie v2c \n', \
            'save\n','\n','Y\n','\n','\n','Y\n','\n','quit\n',]

        conn = sshcon.invoke_shell()
        for cmd in cmds:
            print("当前执行命令为: ",cmd)
            conn.send(cmd)
            time.sleep(3)
            print("命令执行结果: ")
            out = conn.recv(4096)
            print(out)
        # sshcon.close()
    except Exception as e:
        print(ip,"  connet error  ",e)
    sshcon.close()



def generate_ips(start_ip, end_ip, username, password):
    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)
    if start > end:
        raise ValueError("Start IP must be less than or equal to End IP")
    current_ip = start
    while current_ip <= end:
        # print(current_ip)
        # print(type(current_ip), type(username), type(password))
        sshcon(str(current_ip),"22",username,password)
        current_ip += 1


if __name__=="__main__":
    username = "admin"   # ruijie  admin
    password = "Password@123"   # ruijie@123   Password@123
    start_ip = "10.168.8.254"
    end_ip = "10.168.8.254"
    generate_ips(start_ip, end_ip, username, password)

