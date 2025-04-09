import os
import sys
import json
import uuid
import hashlib
from colorama import Fore, Style, init

# 初始化colorama用于终端彩色输出
init()

# 定义emoji和颜色常量，用于美化输出
EMOJI = {
    "FILE": "📄",  # 文件相关操作
    "BACKUP": "💾",  # 备份相关操作
    "SUCCESS": "✅",  # 成功提示
    "ERROR": "❌",  # 错误提示
    "INFO": "ℹ️",  # 信息提示
    "RESET": "🔄",  # 重置操作
}


class MachineIDResetter:
    def __init__(self):
        # 判断操作系统，并设置对应操作系统下Cursor配置文件的路径
        if sys.platform == "win32":  # Windows操作系统
            appdata = os.getenv("APPDATA")
            if appdata is None:
                raise EnvironmentError("APPDATA 环境变量未设置")
            self.db_path = os.path.join(
                appdata, "Cursor", "User", "globalStorage", "storage.json"
            )
        elif sys.platform == "darwin":  # macOS操作系统
            self.db_path = os.path.abspath(
                os.path.expanduser(
                    "~/Library/Application Support/Cursor/User/globalStorage/storage.json"
                )
            )
        elif sys.platform == "linux":  # Linux和其他类Unix系统
            self.db_path = os.path.abspath(
                os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")
            )
        else:
            # 不支持的操作系统将抛出异常
            raise NotImplementedError(f"不支持的操作系统: {sys.platform}")

    def generate_new_ids(self):
        """
        生成新的机器标识ID
        包括设备ID、机器ID、MAC机器ID和SQM ID，这些ID用于Cursor的识别和统计
        """
        # 生成新的UUID作为设备ID
        dev_device_id = str(uuid.uuid4())

        # 生成新的machineId (64个字符的十六进制字符串)
        # 使用SHA-256哈希算法处理随机字节
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

        # 生成新的macMachineId (128个字符的十六进制字符串)
        # 使用SHA-512哈希算法处理随机字节，生成更长的哈希值
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

        # 生成新的sqmId (带花括号的UUID，通常用于Microsoft软件质量监控)
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        # 返回包含所有生成ID的字典
        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
        }

    def reset_machine_ids(self):
        """
        重置机器标识ID的主要方法
        检查配置文件、读取现有配置、生成新ID并保存
        """
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} 正在检查配置文件...{Style.RESET_ALL}")

            # 检查配置文件是否存在
            if not os.path.exists(self.db_path):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} 配置文件不存在: {self.db_path}{Style.RESET_ALL}"
                )
                return False

            # 检查是否有读写文件的权限
            if not os.access(self.db_path, os.R_OK | os.W_OK):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} 无法读写配置文件，请检查文件权限！{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} 如果你使用过 go-cursor-help 来修改 ID; 请修改文件只读权限 {self.db_path} {Style.RESET_ALL}"
                )
                return False

            # 读取当前的配置文件内容
            print(f"{Fore.CYAN}{EMOJI['FILE']} 读取当前配置...{Style.RESET_ALL}")
            with open(self.db_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 生成新的机器标识ID
            print(f"{Fore.CYAN}{EMOJI['RESET']} 生成新的机器标识...{Style.RESET_ALL}")
            new_ids = self.generate_new_ids()

            # 使用新生成的ID更新配置
            config.update(new_ids)

            # 将更新后的配置保存回文件
            print(f"{Fore.CYAN}{EMOJI['FILE']} 保存新配置...{Style.RESET_ALL}")
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

            # 显示成功消息
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 机器标识重置成功！{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}新的机器标识:{Style.RESET_ALL}")
            # 显示所有新生成的ID
            for key, value in new_ids.items():
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")

            return True

        except PermissionError as e:
            # 处理权限错误异常
            print(f"{Fore.RED}{EMOJI['ERROR']} 权限错误: {str(e)}{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}{EMOJI['INFO']} 请尝试以管理员身份运行此程序{Style.RESET_ALL}"
            )
            return False
        except Exception as e:
            # 处理其他所有异常
            print(f"{Fore.RED}{EMOJI['ERROR']} 重置过程出错: {str(e)}{Style.RESET_ALL}")
            return False


# 程序入口点
if __name__ == "__main__":
    # 打印程序标题和分隔线
    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} Cursor 机器标识重置工具{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

    # 创建重置器实例并执行重置操作
    resetter = MachineIDResetter()
    resetter.reset_machine_ids()

    # 打印结束分隔线并等待用户按键退出
    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} 按回车键退出...")
