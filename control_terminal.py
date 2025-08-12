import sys
import pymysql
import requests

from consistent_hash import ConsistentHash

password = '83929922Wr*'

DB_spliter = ConsistentHash(["devices0", "devices1"],
                            [100, 100])
DB_CONFIGS = {
    'devices0': {
        'host': 'localhost',
        'user': 'proxy_user',
        'password': password,
        'database': 'devices0',
    },
    'devices1': {
        'host': 'localhost',
        'user': 'proxy_user',
        'password': password,
        'database': 'devices1',
    }
}


def reverse_geocode(lng, lat):
    url = f"https://restapi.amap.com/v3/geocode/regeo?key=17be3445fcdf6fedd3dcc394051c1bcf&location={lng},{lat}"
    response = requests.get(url).json()
    if response["status"] != "1":
        return {
            "country": "N/A",
            "province": "N/A",
            "city": "N/A",
            "district": "N/A",
            "township": "N/A",
            "street": "N/A",
            "number": "N/A",
            "formatted_address": "N/A"
        }
    regeocode = response["regeocode"]
    address_component = regeocode["addressComponent"]
    address_levels = {
        "country": address_component.get("country", ""),
        "province": address_component.get("province", ""),
        "city": address_component.get("city", ""),
        "district": address_component.get("district", ""),
        "township": address_component.get("township", ""),
        "street": address_component.get("streetNumber", {}).get("street", ""),
        "number": address_component.get("streetNumber", {}).get("number", ""),
        "formatted_address": regeocode.get("formatted_address", "")
    }
    return address_levels


def alter_results_to_dict(results, column_name):
    results_dict = []
    for i in range(len(results)):
        dict = {}
        for j in range(len(column_name)):
            dict[column_name[j]] = results[i][j]
        results_dict.append(dict)
    return results_dict


def show_devices_info():
    try:
        print("DevicesInfo")
        columnWidth = 25
        connection = pymysql.connect(**DB_CONFIGS['devices0'])
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


def show_devices_online():
    try:
        print("DevicesOnline")
        columnWidth = 20
        connection = pymysql.connect(**DB_CONFIGS['devices0'])
        cursor = connection.cursor()
        cursor.execute(
            "SELECT serial_number, TIMESTAMPDIFF(MINUTE, waked_at, last_update) as minutes_online, longitude, latitude, memory_usage FROM devices_info WHERE last_update >= DATE_SUB(NOW(), INTERVAL 30 SECOND)")
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        results_dict = alter_results_to_dict(results, column_names)
        for i in range(5):
            if (i != 4):
                print(column_names[i].ljust(columnWidth), end='')
            else:
                print(column_names[i].ljust(columnWidth))
        for i in range(len(results)):
            print(str(results_dict[i]['serial_number']).ljust(columnWidth), end='')
            print(str(results_dict[i]['minutes_online']).ljust(columnWidth), end='')
            print(str(results_dict[i]['longitude']).ljust(columnWidth), end='')
            print(str(results_dict[i]['latitude']).ljust(columnWidth), end='')
            print(str(results_dict[i]['memory_usage']).ljust(columnWidth))
        return results
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        connection.close()


def publish_app_to_install():
    device_serial_number = input("Device to download:\n")
    if (device_serial_number != "-1"):
        try:
            website = input("App's download_url:\n")
            connection = pymysql.connect(**DB_CONFIGS[DB_spliter.get_database(device_serial_number)])
            cursor = connection.cursor()
            cursor.execute("INSERT INTO apps_to_install (serial_number, download_url, processed) VALUES (%s, %s, 0)",
                           (device_serial_number, website))
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


def publish_app_to_uninstall():
    device_serial_number = input("Device to uninstall:\n")
    if (device_serial_number != "-1"):
        try:
            packageName = input("App's package name:\n")
            connection = pymysql.connect(**DB_CONFIGS[DB_spliter.get_database(device_serial_number)])
            cursor = connection.cursor()
            cursor.execute("INSERT INTO apps_to_uninstall (serial_number, package_name, processed) VALUES (%s, %s, 0)",
                           (device_serial_number, packageName))
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


def reboot_device():
    device_serial_number = input("Device to reboot:\n")
    if (device_serial_number != "-1"):
        try:
            connection = pymysql.connect(**DB_CONFIGS[DB_spliter.get_database(device_serial_number)])
            cursor = connection.cursor()
            cursor.execute("INSERT INTO reboot (serial_number, processed) VALUES (%s, 0)",
                           (device_serial_number))
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


def publish_app_to_start_on_reboot():
    device_serial_number = input("Device to set:\n")
    if (device_serial_number != "-1"):
        mode = input("1 to able start on reboot, 2 to disable:\n")
        if (mode == "1"):
            appName = input("App to start on reboot:\n")
            kiosk = input("1 to kiosk, 0 not to:\n")
        try:
            connection = pymysql.connect(**DB_CONFIGS[DB_spliter.get_database(device_serial_number)])
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


def get_app_list():
    columnWidth = 25
    device_serial_number = input("Device to get App list:\n")
    if (device_serial_number != "-1"):
        try:
            connection = pymysql.connect(**DB_CONFIGS[DB_spliter.get_database(device_serial_number)])
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


def send_message():
    device_serial_number = input("Device to send:\n")
    if (device_serial_number != "-1"):
        content = input("Message to send:\n")
        try:
            connection = pymysql.connect(**DB_CONFIGS[DB_spliter.get_database(device_serial_number)])
            cursor = connection.cursor()
            cursor.execute("INSERT INTO messages (serial_number, message, processed) VALUES (%s, %s, 0)",
                           (device_serial_number, content))
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


def set_limitation():
    device_serial_number = input("Device to set limitation:\n")
    mode = input("0 - no limitation, 1 - close limitation, 2 - lock:\n")
    if (device_serial_number != "-1" and (mode == "0" or mode == "1" or mode == "2")):
        try:
            connection = pymysql.connect(**DB_CONFIGS[DB_spliter.get_database(device_serial_number)])
            cursor = connection.cursor()
            cursor.execute("UPDATE devices_info SET limitation = %s WHERE serial_number = %s"
                           , (mode, device_serial_number));
            connection.commit()
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            connection.close()


fence = ["district", "福田区"]


def geographic_fence():
    device_serial_number = input("Device to set geographic fence:\n")
    if (device_serial_number != "-1"):
        try:
            connection = pymysql.connect(**DB_CONFIGS[DB_spliter.get_database(device_serial_number)])
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM devices_info WHERE serial_number = %s",
                           (device_serial_number))
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            results_dict = alter_results_to_dict(results, column_names)
            location = reverse_geocode(float(results_dict[0]['longitude']),
                                       float(results_dict[0]['latitude']))
            print("Current location: " + str(location))
            print("Fence: " + str(fence))
            process = "n"
            if location[fence[0]] != fence[1]:
                print("Device isn't in designated area")
                process = input("Process? (y/n)")
                if (process == "y"):
                    if location[fence[0]] != fence[1]:
                        cursor.execute("INSERT INTO reboot (serial_number, processed) VALUES (%s, 0)",
                                       (device_serial_number))
                        connection.commit()
                        cursor.execute("UPDATE devices_info SET limitation = %s WHERE serial_number = %s"
                                       , ("3", device_serial_number));
                        connection.commit()
            else:
                print("Device already in designated area")
                if results_dict[0]['limitation'] == "3":
                    cursor.execute("INSERT INTO reboot (serial_number, processed) VALUES (%s, 0)",
                                   (device_serial_number))
                    connection.commit()
                    cursor.execute("UPDATE devices_info SET limitation = %s WHERE serial_number = %s"
                                   , ("0", device_serial_number));
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