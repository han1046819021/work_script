import threading
import paramiko
import time
import os
import datetime
import re

# 创建锁
lock = threading.Lock()
# 执行命令的函数
def sshcon(ip, port, username, password, result_queue):
    try:
        sshcon = paramiko.SSHClient()
        sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshcon.connect(ip, port, username, password, compress=True)
        conn = sshcon.invoke_shell()
        # 清除设备提示符
        conn.send("\r\n")
        time.sleep(1)
        conn.recv(4096)
        cmds = ['terminal length 0\r\n', 'show interfaces status\r\n']
        result = ""
        for cmd in cmds:
            conn.send(cmd)
            time.sleep(1)
            output = b""
            while conn.recv_ready():
                output += conn.recv(65535)
            result += output.decode('utf-8')

        # 加锁后更新共享结果
        with lock:
            result_queue.append((ip, result))  # 将结果传递到队列
        print(f"线程 {ip} 执行完毕.")
    except Exception as e:
        with lock:
            result_queue.append((ip, f"连接错误: {e}"))
        print(f"线程 {ip} 出现错误: {e}")
    finally:
        sshcon.close()


# 将筛选的结果写入输出文件
def save_to_file(ip, filtered_lines):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(r'E:\NAS转存文件\笔记本文件暂存\工作文件夹\康复大学\巡检脚本\锐捷交换机巡检记录', f'out-{now}')
    os.makedirs(folder_path, exist_ok=True)
    output_file = os.path.join(folder_path, f"{ip}_filtered_ports.txt")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in filtered_lines:
            outfile.write(line + '\n')
    print(f"筛选出的端口信息已保存到 {output_file}")


def read_hosts_from_file(filename):
    try:
        with open(filename, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]
        return hosts
    except FileNotFoundError:
        print(f"文件 {filename} 未找到")
        return []


# 筛选符合条件的行
def filter_ports(output):
    pattern = r'.*\b(?:10M|100M)\b.*'
    if output:
        filtered_lines = [line.strip() for line in output.splitlines() if re.search(pattern, line)]
        return filtered_lines
    else:
        return []
# 主函数
def main():
    ips = read_hosts_from_file(r'E:\NAS转存文件\笔记本文件暂存\工作文件夹\康复大学\巡检脚本源文件\巡检IP数据\锐捷POE交换机遍历巡检数据\IP—ALL.txt')
    username = "admin"
    password = "ruijie@123"

    if not ips:
        print("没有可用的IP地址，程序终止。")
    else:
        # 使用线程列表来处理多个IP
        result_queue = []  # 用于存储结果
        threads = []

        for host in ips:
            print(f"正在巡检 {host}...")
            thread = threading.Thread(target=sshcon, args=(host, 22, username, password, result_queue))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 获取结果并处理
        for ip, output in result_queue:
            if output:
                filtered_ports = filter_ports(output)
                if filtered_ports:
                    save_to_file(ip, filtered_ports)
                else:
                    print(f"交换机 {ip} 没有符合条件的端口。")
            else:
                print(f"无法获取交换机 {ip} 的信息。")


if __name__ == "__main__":
    main()
