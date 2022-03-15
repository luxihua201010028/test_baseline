# coding:utf-8
# @author:sjl
# @created:2019/01/14
# @updated:2019/01/25
# @des: 实现文件的上传、下载等功能


import paramiko
import os
import time
import datetime

host = "192.168.202.2"  # 远程服务器ip
user = "luxihua"  # 远程服务器用户名
password = "cc86c854"  # 远程服务器密码
port = 22
local_put_path = "/Users/luxihua/Documents/github/pythonProject/test/local.jpg"  # 需要上传的文件放在此目录
local_get_path = "/Users/luxihua/Documents/github/pythonProject/test"  # 从远程服务器下载的文件放在此目录
remote_put_path = "/home/luxihua/Desktop/test"  # 上传的文件放在远程服务器的此目录
remote_get_path = "/home/luxihua/Desktop/test/remote.jpg"  # 从远程服务器的此目录下载文件


class Pysftp(object):
    """
    python3 自动上传、下载文件
    """
    global local_put_path, local_get_path, remote_put_path, remote_get_path

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def connect(self):
        """
        建立ssh连接
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, self.port, self.user, self.password)
        print("连接已建立")

    def cmd(self, cmd):
        """
        需要执行的命令
        """
        # cmd = "date"
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        print(stdout.read().decode("utf8"))

    def mkdir(self):
        """
        创建本地文件夹，存放上传、下载的文件
        """
        for lp in [local_put_path, local_get_path]:
            if not os.path.exists(lp):
                os.makedirs(lp, 666)
                print("创建本地文件夹:{}".format(lp))
            else:
                print("本地文件夹:{}已存在".format(lp))

    def put(self):
        """
        上传文件
        """
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        # sftp = self.ssh.open_sftp()
        for root, dirs, files in os.walk(local_put_path):
            for fname in files:
                local_full_name = os.path.join(root, fname)
                self.local_done_write(local_full_name)  # 本地文件已写入完成，可以上传了
                sftp.put(local_full_name, os.path.join(remote_put_path, fname))
                os.remove(local_full_name)
                print("{}\n上传成功：本地文件:{}====>远程{}:{},已删除该本地文件\n".format(datetime.datetime.now(), local_full_name,
                                                                       self.host, remote_put_path))

    def get(self):
        """
        下载文件
        """
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        # sftp = self.ssh.open_sftp() #  在ssh服务器上开启一个sftp会话
        for fname in sftp.listdir(remote_get_path):
            try:
                # if fname[:7] == 'result-': # 文件名以'result-'开头才下载，但是不够优雅
                if fname.startwith('result-'):  # 贼拉优雅了
                    remote_full_name = os.path.join(remote_get_path, fname)
                    self.remote_done_transffer(remote_full_name)
                    sftp.get(remote_full_name, os.path.join(local_get_path, fname))
                    sftp.remove(remote_full_name)
                    print("[{}]下载成功：远程文件{}:{}====>本地{},已删除该远程文件\n".format(datetime.datetime.now(), self.host,
                                                                          remote_full_name, local_get_path))
            except Exception as e:
                print(e)

    def stat(self, fpath):
        """
        检查远程服务器文件状态
        :param fpath:文件绝对路径
        """
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        # sftp = self.ssh.open_sftp()
        return sftp.stat(fpath)

    def remote_done_transffer(self, fpath):
        """
        检查文件是否传输完成
        :param fpath:远程服务器上待下载文件绝对路径
        """
        while True:
            old_size = self.stat(fpath).st_size
            time.sleep(3)
            new_size = self.stat(fpath).st_size
            if new_size <= old_size:  # 传输已完成
                return

    def close(self):
        """
        关闭ssh连接
        """
        self.ssh.close()
        print("连接关闭")

    def local_done_write(self, fpath):
        """
        检查本地文件是否已写入完成
        :param fpath:本地待上传文件绝对路径
        """
        while True:
            old_size = os.stat(fpath).st_size
            time.sleep(3)
            new_size = os.stat(fpath).st_size
            if new_size <= old_size:  # 写入已完成
                return


def transffer():
    """传输函数
    """
    global host, port, user, password
    obj = Pysftp(host, port, user, password)
    obj.connect()
    obj.mkdir()
    while True:
        # obj.cmd()
        obj.put()
        obj.get()
        time.sleep(5)


if __name__ == '__main__':
    transffer()
