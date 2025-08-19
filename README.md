文件结构：
config
    -deploy_database.sql  数据库、表单、用户创建
    -mysqld.cnf  mysql配置文件
    -nginx.conf  nginx配置文件
app.py  FastAPI实例
consistent_hash.py  一致性哈希算法
control_terminal.py  控制终端
stress_test.py  压力测试

备注：
注意修改app.py、deploy_database.sql、control_terminal.py中的数据库密码

