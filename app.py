import uvicorn
from fastapi import FastAPI, HTTPException, Query
from consistent_hash import ConsistentHash
import aiomysql
from pydantic import BaseModel

# 测试用下载链接
# https://downv6.qq.com/qqweb/QQ_1/android_apk/Android_9.2.0_64.apk
# https://dldir1.qq.com/weixin/android/weixin8061android2880_0x28003d34_arm64.apk

# 配置服务器环境
# apt install mysql-server
# sudo mysql_secure_installation
# apt install python3.12-venv
# python3 -m venv/home/python3
# source /home/python3/bin/activate

# 启动/关闭服务器
# nohup uvicorn app:app --host 0.0.0.0 --port 5000 --workers=6 --loop uvloop --http httptools > /dev/null 2>&1 &
# pkill -f "uvicorn app:app"

# 运行压力测试
# python -m locust -f stress_test.py
app = FastAPI()
DB_spliter = ConsistentHash(["devices0", "devices1"],
                            [100, 100])
password = 'YOUR PASSWORD'
DB_CONFIGS = {
    'devices0': {
        'host': 'localhost',
        'user': 'proxy_user',
        'password': password,
        # 'port': 6033 需配置Proxysql
        'db': 'devices0'
    },
    'devices1': {
        'host': 'localhost',
        'user': 'proxy_user',
        'password': password,
        # 'port': 6033 需配置Proxysql
        'db': 'devices1'
    }
}


async def create_pool(config):
    return await aiomysql.create_pool(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        db=config['db'],
        minsize=12,
        maxsize=30,
        pool_recycle=1800,
        connect_timeout=10,
        autocommit=False
    )


pools = {}


@app.on_event("startup")
async def startup():
    # 初始化所有连接池
    for db_name, config in DB_CONFIGS.items():
        pools[db_name] = await create_pool(config)


@app.on_event("shutdown")
async def shutdown():
    # 关闭所有连接池
    for pool in pools.values():
        pool.close()
        await pool.wait_closed()


def get_db_pool(serial_number: str) -> aiomysql.Pool:
    db_name = DB_spliter.get_database(serial_number)
    return pools[db_name]


# 失败情况统一返回格式（所有接口）：
# HTTP 500 错误，返回 {"status": "failure", "error": str(e)}

# 功能：检查设备是否需要重启
# 参数：serial_number - 设备序列号
# 返回值：{"status": "success", "reboot": True/False}，True表示需要重启
@app.get("/api/reboot")
async def get_reboot_command(serial_number: str = Query(...)):
    pool = get_db_pool(serial_number)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await conn.begin()
                await cursor.execute("""
                                     SELECT id
                                     FROM reboot
                                     WHERE serial_number = %s
                                       AND processed = '0'
                                     """, (serial_number))
                result = await cursor.fetchone()
                if result:
                    await cursor.execute(
                        "UPDATE reboot SET processed = '1' WHERE id = %s",
                        (result[0]))
                    await conn.commit()
                    return {"status": "success",
                            "reboot": True}
                else:
                    await conn.commit()
                    return {"status": "success",
                            "reboot": False}
            except Exception as e:
                await conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={"status": "failure",
                            "error": str(e)}
                )


# 功能：获取设备需要安装的应用下载链接
# 参数：serial_number - 设备序列号
# 返回值：{"status": "success", "download_url": url}，url为None表示没有需要安装的应用
@app.get("/api/install")
async def get_apps_to_install(serial_number: str = Query(...)):
    pool = get_db_pool(serial_number)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await conn.begin()
                await cursor.execute("""
                                     SELECT id, download_url
                                     FROM apps_to_install
                                     WHERE serial_number = %s
                                       AND processed = '0'
                                     """, (serial_number))
                app_info = await cursor.fetchone()
                if app_info:
                    await cursor.execute(
                        "UPDATE apps_to_install SET processed = '1' WHERE id = %s",
                        (app_info[0]))
                    await conn.commit()
                    return {
                        "status": "success",
                        "download_url": app_info[1]
                    }
                else:
                    await conn.commit()
                    return {
                        "status": "success",
                        "download_url": None
                    }
            except Exception as e:
                await conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={"status": "failure",
                            "error": str(e)}
                )


# 功能：获取设备需要卸载的应用包名
# 参数：serial_number - 设备序列号
# 返回值：{"status": "success", "package_name": name}，name为None表示没有需要卸载的应用
@app.get("/api/uninstall")
async def get_apps_to_uninstall(serial_number: str = Query(...)):
    pool = get_db_pool(serial_number)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await conn.begin()
                await cursor.execute("""
                                     SELECT id, package_name
                                     FROM apps_to_uninstall
                                     WHERE serial_number = %s
                                       AND processed = '0'
                                     """, (serial_number))
                app_info = await cursor.fetchone()
                if app_info:
                    await cursor.execute(
                        "UPDATE apps_to_uninstall SET processed = '1' WHERE id = %s",
                        (app_info[0]))
                    await conn.commit()
                    return {
                        "status": "success",
                        "package_name": app_info[1]
                    }
                else:
                    await conn.commit()
                    return {
                        "status": "success",
                        "package_name": None
                    }
            except Exception as e:
                await conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={"status": "failure",
                            "error": str(e)}
                )


# 功能：注册新设备或检查设备是否已注册
# 参数：serial_number - 设备序列号, fw_version - 固件版本
# 返回值：{"status": "success", "is_registered": True/False, "limitation": "0"/"1"/"2"}，limitation为三种限制等级
class RegisterDeviceRequest(BaseModel):
    serial_number: str
    fw_version: str


@app.post("/api/register")
async def register_device(data: RegisterDeviceRequest):
    pool = get_db_pool(data.serial_number)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await conn.begin()
                await cursor.execute(
                    "SELECT limitation FROM devices_info WHERE serial_number = %s",
                    (data.serial_number)
                )
                device_exists = await cursor.fetchone()
                if not device_exists:
                    await cursor.execute(
                        "INSERT INTO devices_info (serial_number, fw_version) VALUES (%s, %s)",
                        (data.serial_number, data.fw_version)
                    )
                await conn.commit()
                return {
                    "status": "success",
                    "is_registered": bool(device_exists),
                    "limitation": device_exists[0] if device_exists else "0"
                }
            except Exception as e:
                await conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={"status": "failure",
                            "error": str(e)}
                )


# 功能：更新设备状态信息（位置、内存使用等）
# 参数：serial_number - 设备序列号, waked - 是否唤醒("1"/"0"), location - 位置信息, memory_usage - 内存使用情况
# 返回值：{"status": "success", "geo_fence": str}，返回设备的电子围栏信息
class UpdateStateRequest(BaseModel):
    serial_number: str
    waked: str
    location: str
    memory_usage: str


@app.post("/api/update_state")
async def update_state(data: UpdateStateRequest):
    pool = get_db_pool(data.serial_number)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await conn.begin()
                # waked为"1"时会更新waked_at字段
                if data.waked == "1":
                    sql = """
                          UPDATE devices_info
                          SET waked_at     = CURRENT_TIMESTAMP,
                              last_update  = CURRENT_TIMESTAMP,
                              location     = %s,
                              memory_usage = %s
                          WHERE serial_number = %s \
                          """
                else:
                    sql = """
                          UPDATE devices_info
                          SET last_update  = CURRENT_TIMESTAMP,
                              location     = %s,
                              memory_usage = %s
                          WHERE serial_number = %s \
                          """
                await cursor.execute(sql, (
                    data.location,
                    data.memory_usage,
                    data.serial_number
                ))
                await conn.commit()
                await cursor.execute(
                    "SELECT geo_fence FROM devices_info WHERE serial_number = %s",
                    (data.serial_number)
                )
                geo_fence = await cursor.fetchone()
                return {"status": "success",
                        "geo_fence": geo_fence[0] if geo_fence else "0"}
            except Exception as e:
                await conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={"status": "failure",
                            "error": str(e)}
                )


# 功能：获取设备待处理的消息
# 参数：serial_number - 设备序列号
# 返回值：{"status": "success", "messages": [{"id": id, "content": msg},...]}
@app.get("/api/messages")
async def get_messages(serial_number: str = Query(...)):
    pool = get_db_pool(serial_number)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await conn.begin()
                await cursor.execute("""
                                     SELECT id, message
                                     FROM messages
                                     WHERE serial_number = %s
                                       AND processed = '0'
                                     """, (serial_number))
                messages = await cursor.fetchall()
                result = []
                message_ids = []
                for msg in messages:
                    result.append({
                        "id": msg[0],
                        "content": msg[1]
                    })
                    message_ids.append(msg[0])
                if message_ids:
                    await cursor.execute("""
                                         UPDATE messages
                                         SET processed = '1'
                                         WHERE id IN %s
                                         """, (message_ids,))
                await conn.commit()
                return {
                    "status": "success",
                    "messages": result
                }
            except Exception as e:
                await conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={"status": "failure",
                            "error": str(e)}
                )


# 功能：更新设备上安装的应用列表
# 参数：serial_number - 设备序列号, apps - 应用名称列表
# 返回值：{"status": "success"}
class UpdateAppListRequest(BaseModel):
    serial_number: str
    apps: list[str]


@app.post("/api/update_app_list")
async def update_app_list(data: UpdateAppListRequest):
    pool = get_db_pool(data.serial_number)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await conn.begin()
                await cursor.execute("""
                                     DELETE
                                     FROM app_list
                                     WHERE serial_number = %s
                                     """, (data.serial_number))
                insert_sql = """
                             INSERT INTO app_list (serial_number, app_name)
                             VALUES (%s, %s) \
                             """
                await cursor.executemany(
                    insert_sql,
                    [(data.serial_number, app) for app in data.apps]
                )
                await conn.commit()
                return {"status": "success"}
            except Exception as e:
                await conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={"status": "failure",
                            "error": str(e)}
                )


# 功能：获取设备启动时需要自动启动的应用
# 参数：serial_number - 设备序列号
# 返回值：{"status": "success", "app_name": None/name, "kiosk": None/"1"/"0"}
@app.get("/api/app_on_start")
async def get_app_to_start_on_reboot(serial_number: str = Query(...)):
    pool = get_db_pool(serial_number)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await conn.begin()
                await cursor.execute("""
                                     SELECT app_name, kiosk
                                     FROM app_to_start_on_reboot
                                     WHERE serial_number = %s
                                     """, (serial_number))
                result = await cursor.fetchone()
                await conn.commit()
                return {
                    "status": "success",
                    "app_name": result[0] if result else None,
                    "kiosk": result[1] if result else None
                }
            except Exception as e:
                await conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={"status": "failure",
                            "error": str(e)}
                )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        workers=1
    )
