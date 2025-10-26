"""
Bambu Lab 打印机 FTP 文件传输示例

演示如何通过 FTP 上传 .gcode.3mf 文件到拓竹打印机
"""

import os
import ftplib
import ssl
from typing import Optional


class BambuFTPClient:
    """
    Bambu Lab 打印机 FTP 客户端

    功能:
    - 连接到打印机 FTP 服务
    - 上传 .gcode.3mf 文件
    - 列出文件
    """

    def __init__(self, host: str, access_code: str):
        """
        初始化 FTP 客户端

        Args:
            host: 打印机 IP 地址
            access_code: 访问码
        """
        self.host = host
        self.port = 990  # FTPS 端口
        self.username = "bblp"
        self.password = access_code

        self.ftp: Optional[ftplib.FTP_TLS] = None

    def connect(self) -> bool:
        """
        连接到 FTP 服务器

        Returns:
            bool: 连接是否成功
        """
        try:
            print(f"Connecting to FTP server at {self.host}:{self.port}")

            # 创建 FTP_TLS 对象 (支持 SSL/TLS)
            self.ftp = ftplib.FTP_TLS()

            # 连接
            self.ftp.connect(self.host, self.port)

            # 登录
            self.ftp.login(self.username, self.password)

            # 切换到安全数据连接
            self.ftp.prot_p()

            print("FTP connection established")

            # 打印欢迎信息
            print(f"Welcome message: {self.ftp.getwelcome()}")

            return True

        except ftplib.all_errors as e:
            print(f"FTP connection failed: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.ftp:
            try:
                self.ftp.quit()
                print("FTP connection closed")
            except:
                self.ftp.close()
            self.ftp = None

    def upload_file(self, local_path: str, remote_name: Optional[str] = None) -> bool:
        """
        上传文件到打印机

        Args:
            local_path: 本地文件路径
            remote_name: 远程文件名 (None = 使用本地文件名)

        Returns:
            bool: 上传是否成功
        """
        if not self.ftp:
            print("Not connected to FTP server")
            return False

        if not os.path.exists(local_path):
            print(f"File not found: {local_path}")
            return False

        try:
            # 确定远程文件名
            if remote_name is None:
                remote_name = os.path.basename(local_path)

            # 确保文件名以 .gcode.3mf 结尾
            if not remote_name.endswith(".gcode.3mf"):
                print(f"Warning: File should have .gcode.3mf extension")

            print(f"Uploading {local_path} as {remote_name}...")

            # 打开本地文件
            with open(local_path, 'rb') as file:
                # 上传文件
                self.ftp.storbinary(f'STOR {remote_name}', file)

            print(f"Upload successful: {remote_name}")
            return True

        except ftplib.all_errors as e:
            print(f"Upload failed: {e}")
            return False

    def list_files(self) -> list:
        """
        列出远程目录中的文件

        Returns:
            list: 文件列表
        """
        if not self.ftp:
            print("Not connected to FTP server")
            return []

        try:
            files = []
            self.ftp.retrlines('LIST', files.append)
            return files
        except ftplib.all_errors as e:
            print(f"Failed to list files: {e}")
            return []

    def delete_file(self, remote_name: str) -> bool:
        """
        删除远程文件

        Args:
            remote_name: 远程文件名

        Returns:
            bool: 删除是否成功
        """
        if not self.ftp:
            print("Not connected to FTP server")
            return False

        try:
            self.ftp.delete(remote_name)
            print(f"Deleted: {remote_name}")
            return True
        except ftplib.all_errors as e:
            print(f"Failed to delete file: {e}")
            return False

    def get_file_size(self, local_path: str) -> int:
        """
        获取文件大小

        Args:
            local_path: 本地文件路径

        Returns:
            int: 文件大小(字节)
        """
        if os.path.exists(local_path):
            return os.path.getsize(local_path)
        return 0


# 使用示例
if __name__ == "__main__":
    # 创建 FTP 客户端
    ftp_client = BambuFTPClient(
        host="192.168.1.100",  # 替换为实际 IP
        access_code="12345678"  # 替换为实际访问码
    )

    # 连接
    if ftp_client.connect():
        try:
            # 列出文件
            print("\nFiles on printer:")
            files = ftp_client.list_files()
            for file in files:
                print(f"  {file}")

            # 上传文件示例
            # local_file = "/path/to/your/model.gcode.3mf"
            # if os.path.exists(local_file):
            #     ftp_client.upload_file(local_file)

        finally:
            ftp_client.disconnect()
