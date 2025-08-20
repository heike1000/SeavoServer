import sys
import pymysql

# 测试用下载链接
# https://downv6.qq.com/qqweb/QQ_1/android_apk/Android_9.2.0_64.apk
# https://dldir1.qq.com/weixin/android/weixin8061android2880_0x28003d34_arm64.apk
password = '83929922Wr*'
config = {
    'host': 'localhost',
    'user': 'proxy_user',
    'password': password,
    'database': 'devices'
}


def alter_results_to_dict(results, column_name):
    results_dict = []
    for i in range(len(results)):
        dict = {}
        for j in range(len(column_name)):
            dict[column_name[j]] = results[i][j]
        results_dict.append(dict)
    return results_dict


# 功能：从两个数据库中获取所有设备的基本信息（序列号和固件版本）
# 简化SQL：SELECT * FROM devices_info
def show_devices_info():
    try:
        print("DevicesInfo")
        columnWidth = 25
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM devices_info")
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        results_dict = alter_results_to_dict(results, column_names)
        for i in range(2):
            if (i != 1):
                print(column_names[i].ljust(columnWidth), end='')
            else:
                print(column_names[i].ljust(columnWidth))
        for i in range(len(results)):
            print(str(results_dict[i]['serial_number']).ljust(columnWidth), end='')
            print(str(results_dict[i]['fw_version']).ljust(columnWidth))
        return results
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        connection.close()


# 功能：获取当前在线的设备信息（序列号、在线时长、内存使用率和位置）
# 简化SQL：serial_number, TIMESTAMPDIFF(MINUTE, waked_at, last_update) as minutes_online, memory_usage, location
def show_devices_online():
    try:
        print("DevicesOnline")
        columnWidth = 25
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT serial_number, TIMESTAMPDIFF(MINUTE, waked_at, last_update) as minutes_online, memory_usage, location FROM devices_info WHERE last_update >= DATE_SUB(NOW(), INTERVAL 60 SECOND)")
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        results_dict = alter_results_to_dict(results, column_names)
        for i in range(4):
            if (i != 3):
                print(column_names[i].ljust(columnWidth), end='')
            else:
                print(column_names[i].ljust(columnWidth))
        for i in range(len(results)):
            print(str(results_dict[i]['serial_number']).ljust(columnWidth), end='')
            print(str(results_dict[i]['minutes_online']).ljust(columnWidth), end='')
            print(str(results_dict[i]['memory_usage']).ljust(columnWidth), end='')
            print(str(results_dict[i]['location']).ljust(columnWidth))
        return results
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        connection.close()


# 功能：发布应用安装任务到指定设备
# 简化SQL：INSERT INTO apps_to_install (serial_number, download_url)
def publish_app_to_install():
    device_serial_number = input("Device to download:\n")
    if (device_serial_number != "-1"):
        try:
            website = input("App's download_url:\n")
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO apps_to_install (serial_number, download_url) VALUES (%s, %s)",
                           (device_serial_number, website))
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


# 功能：发布应用卸载任务到指定设备
# 简化SQL：INSERT INTO apps_to_uninstall (serial_number, package_name)
def publish_app_to_uninstall():
    device_serial_number = input("Device to uninstall:\n")
    if (device_serial_number != "-1"):
        try:
            packageName = input("App's package name:\n")
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO apps_to_uninstall (serial_number, package_name) VALUES (%s, %s)",
                           (device_serial_number, packageName))
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


# 功能：发布设备重启任务
# 简化SQL：INSERT INTO reboot (serial_number)
def reboot_device():
    device_serial_number = input("Device to reboot:\n")
    if (device_serial_number != "-1"):
        try:
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO reboot (serial_number) VALUES (%s)",
                           (device_serial_number))
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


# 功能：设置或取消应用在设备重启时自动启动
# 简化SQL：REPLACE INTO app_to_start_on_reboot (serial_number, kiosk, app_name)
# 简化SQL：delete from app_to_start_on_reboot WHERE serial_number = %s
def publish_app_to_start_on_reboot():
    device_serial_number = input("Device to set:\n")
    if (device_serial_number != "-1"):
        mode = input("1 to able start on reboot, 2 to disable:\n")
        if (mode == "1"):
            appName = input("App to start on reboot:\n")
            kiosk = input("1 to kiosk, 0 not to:\n")
        try:
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            if mode == "1":
                cursor.execute(
                    "REPLACE INTO app_to_start_on_reboot (serial_number, kiosk, app_name) VALUES (%s, %s, %s)",
                    (device_serial_number, kiosk, appName))
            elif mode == "2":
                cursor.execute("delete from app_to_start_on_reboot WHERE serial_number = %s"
                               , (device_serial_number));
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


# 功能：获取指定设备上安装的应用列表
# 简化SQL：SELECT * FROM app_list
def get_app_list():
    columnWidth = 25
    device_serial_number = input("Device to get App list:\n")
    if (device_serial_number != "-1"):
        try:
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM app_list WHERE serial_number = %s",
                           (device_serial_number))
            connection.commit()
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            print(column_names[1].ljust(columnWidth))
            for i in range(len(results)):
                print(str(results[i][1]).ljust(columnWidth))
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


# 功能：发送消息到指定设备
# 简化SQL：INSERT INTO messages (serial_number, message)
def send_message():
    device_serial_number = input("Device to send:\n")
    if (device_serial_number != "-1"):
        content = input("Message to send:\n")
        try:
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO messages (serial_number, message) VALUES (%s, %s)",
                           (device_serial_number, content))
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


# 功能：设置设备的限制模式（无限制、关闭限制或锁定）
# 简化SQL：UPDATE devices_info SET limitation = %s WHERE serial_number = %s
def set_limitation():
    device_serial_number = input("Device to set limitation:\n")
    mode = input("0 - no limitation, 1 - close limitation, 2 - lock:\n")
    if (device_serial_number != "-1" and (mode == "0" or mode == "1" or mode == "2")):
        try:
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            cursor.execute("UPDATE devices_info SET limitation = %s WHERE serial_number = %s"
                           , (mode, device_serial_number));
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


# 功能：设置设备的地理围栏
# 简化SQL：UPDATE devices_info SET geo_fence = %s WHERE serial_number = %s
def geographic_fence():
    device_serial_number = input("Device to set geographic fence:\n")
    geo_fence = input("Geography fence:\n")
    if (device_serial_number != "-1"):
        try:
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            cursor.execute("UPDATE devices_info SET geo_fence = %s WHERE serial_number = %s"
                           , (geo_fence, device_serial_number));
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


while (True):
    print("1 to print all devices\n"
          "2 to print devices online, online time length, location\n"
          "3 to install App for a device\n"
          "4 to uninstall App for a device\n"
          "5 to arrange an app to start on reboot\n"
          "6 to get App list\n"
          "7 to reboot a device\n"
          "8 to send message\n"
          "9 to set limitation (Need reboot)\n"
          "10 to set geographic fence"
          )
    opcode = int(input())
    result = ""
    if (opcode == 1):
        result = show_devices_info()
        input("Continue......")
    elif (opcode == 2):
        result = show_devices_online()
        input("Continue......")
    elif (opcode == 3):
        result = publish_app_to_install()
        input("Continue......")
    elif (opcode == 4):
        result = publish_app_to_uninstall()
        input("Continue......")
    elif (opcode == 5):
        result = publish_app_to_start_on_reboot()
        input("Continue......")
    elif (opcode == 6):
        result = get_app_list()
        input("Continue......")
    elif (opcode == 7):
        result = reboot_device()
        input("Continue......")
    elif (opcode == 8):
        result = send_message()
        input("Continue......")
    elif (opcode == 9):
        result = set_limitation()
        input("Continue......")
    elif (opcode == 10):
        result = geographic_fence()
        input("Continue......")
    else:
        sys.exit()
