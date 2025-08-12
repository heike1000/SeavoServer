create database devices0;
use devices0;
CREATE TABLE devices_info
(
    serial_number VARCHAR(128) NOT NULL PRIMARY KEY,
    fw_version    VARCHAR(256) NOT NULL,
    waked_at      TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
    last_update   TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
    longitude     VARCHAR(128) NOT NULL DEFAULT '0',
    latitude      VARCHAR(128) NOT NULL DEFAULT '0',
    limitation    VARCHAR(4)   NOT NULL DEFAULT '0',
    memory_usage  VARCHAR(128) NOT NULL DEFAULT '0/0'
);

CREATE TABLE apps_to_install
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128)  NOT NULL,
    download_url  VARCHAR(1024) NOT NULL,
    processed     INT           NOT NULL,
    INDEX idx_id_device_processed (serial_number, processed)
);

CREATE TABLE apps_to_uninstall
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128) NOT NULL,
    package_name  VARCHAR(128) NOT NULL,
    processed     INT          NOT NULL,
    INDEX idx_id_device_processed (serial_number, processed)
);

CREATE TABLE reboot
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128) NOT NULL,
    processed     INT          NOT NULL,
    INDEX idx_id_device_processed (serial_number, processed)
);

CREATE TABLE app_to_start_on_reboot
(
    serial_number VARCHAR(128) NOT NULL,
    kiosk         INT          NOT NULL,
    app_name      VARCHAR(128) NOT NULL,
    INDEX idx_id_device (serial_number)
);

CREATE TABLE messages
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128)  NOT NULL,
    message       VARCHAR(1024) NOT NULL,
    processed     INT           NOT NULL,
    INDEX idx_id_device_processed (serial_number, processed)
);

CREATE TABLE app_list
(
    serial_number VARCHAR(128) NOT NULL,
    app_name      VARCHAR(128) NOT NULL,
    INDEX idx_id_device (serial_number)
);

create database devices1;
use devices1;
CREATE TABLE devices_info
(
    serial_number VARCHAR(128) NOT NULL PRIMARY KEY,
    fw_version    VARCHAR(256) NOT NULL,
    waked_at      TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
    last_update   TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
    longitude     VARCHAR(128) NOT NULL DEFAULT '0',
    latitude      VARCHAR(128) NOT NULL DEFAULT '0',
    limitation    VARCHAR(4)   NOT NULL DEFAULT '0',
    memory_usage  VARCHAR(128) NOT NULL DEFAULT '0/0'
);

CREATE TABLE apps_to_install
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128)  NOT NULL,
    download_url  VARCHAR(1024) NOT NULL,
    processed     INT           NOT NULL,
    INDEX idx_id_device_processed (serial_number, processed)
);

CREATE TABLE apps_to_uninstall
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128) NOT NULL,
    package_name  VARCHAR(128) NOT NULL,
    processed     INT          NOT NULL,
    INDEX idx_id_device_processed (serial_number, processed)
);

CREATE TABLE reboot
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128) NOT NULL,
    processed     INT          NOT NULL,
    INDEX idx_id_device_processed (serial_number, processed)
);

CREATE TABLE app_to_start_on_reboot
(
    serial_number VARCHAR(128) NOT NULL,
    kiosk         INT          NOT NULL,
    app_name      VARCHAR(128) NOT NULL,
    INDEX idx_id_device (serial_number)
);

CREATE TABLE messages
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128)  NOT NULL,
    message       VARCHAR(1024) NOT NULL,
    processed     INT           NOT NULL,
    INDEX idx_id_device_processed (serial_number, processed)
);

CREATE TABLE app_list
(
    serial_number VARCHAR(128) NOT NULL,
    app_name      VARCHAR(128) NOT NULL,
    INDEX idx_id_device (serial_number)
);

CREATE USER 'proxy_user'@'localhost' IDENTIFIED BY '83929922Wr*';
GRANT ALL PRIVILEGES ON devices0.* TO 'proxy_user'@'localhost';
GRANT ALL PRIVILEGES ON devices1.* TO 'proxy_user'@'localhost';
FLUSH PRIVILEGES;

--https://downv6.qq.com/qqweb/QQ_1/android_apk/Android_9.2.0_64.apk
--https://dldir1.qq.com/weixin/android/weixin8061android2880_0x28003d34_arm64.apk

