from telnetlib import Telnet
import re
import os
import datetime
import time

# 定义要匹配的正则表达式
pattern = r'.*\b(10M|100M)\b.*'
password = 'h3capadmin'

# 筛选符合条件的行
def filter_ports(output):
    if output:
        filtered_lines = [line.strip() for line in output.splitlines() if re.search(pattern, line)]
        return filtered_lines
    else:
        return []

# 将筛选的结果写入输出文件
def save_to_file(ip, filtered_lines):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(r'E:\NAS转存文件\笔记本文件暂存\康复大学\康复大学\巡检脚本\华三WT1024巡检记录', f'out-{now}')
    os.makedirs(folder_path, exist_ok=True)
    output_file = os.path.join(folder_path, f"{ip}_filtered_ports.txt")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in filtered_lines:
            outfile.write(line + '\n')
    print(f"筛选出的端口信息已保存到 {output_file}")


def do_telnet(host, password, commands):
    try:
        tn = Telnet(host, port=23, timeout=10)
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b'\n')
        time.sleep(1)
        tn.read_until(b'>')

        output_lines = []
        for command in commands:
            tn.write(command.encode('ascii') + b'\n')
            time.sleep(1)
            output = tn.read_until(b'>', timeout=5).decode('ascii').strip()
            output_lines.append(output)

        final_output = '\n'.join(line for line in output_lines if line.strip())
        return final_output

    except (ConnectionRefusedError, TimeoutError) as e:
        print(f"连接 {host} 时发生错误: {e}")
    except Exception as e:
        print(f"连接 {host} 时发生未知错误: {e}")
    finally:
        try:
            tn.close()
        except NameError:
            print(f"未能与 {host} 建立 Telnet 会话")

    return None


def read_hosts_from_file(filename):
    try:
        with open(filename, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]
        return hosts
    except FileNotFoundError:
        print(f"文件 {filename} 未找到")
        return []


def main():
    hosts = read_hosts_from_file(r'E:\NAS转存文件\笔记本文件暂存\康复大学\康复大学\巡检脚本源文件\巡检IP数据\WT1024遍历巡检数据\ip.txt')
    commands = ['screen-length disable', 'dis interface brief']

    if not hosts:
        print("没有可用的IP地址，程序终止。")
    else:
        for host in hosts:
            print(f"正在巡检 {host}...")
            output = do_telnet(host, password, commands)
            if output:
                filtered_ports = filter_ports(output)
                if filtered_ports:
                    save_to_file(host, filtered_ports)
                else:
                    print(f"交换机 {host} 没有符合条件的端口。")
            else:
                print(f"无法获取交换机 {host} 的信息。")

if __name__ == '__main__':
    main()
