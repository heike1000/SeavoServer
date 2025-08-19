create database devices;
use devices;
CREATE TABLE devices_info
(
    serial_number VARCHAR(128) NOT NULL PRIMARY KEY,
    fw_version    VARCHAR(256) NOT NULL,
    waked_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_update   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    location      VARCHAR(128) NOT NULL DEFAULT '0',
    geo_fence     VARCHAR(128) NOT NULL DEFAULT '0',
    limitation    VARCHAR(4)   NOT NULL DEFAULT '0',
    memory_usage  VARCHAR(128) NOT NULL DEFAULT '0/0'
);

CREATE TABLE apps_to_install
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128)  NOT NULL,
    download_url  VARCHAR(1024) NOT NULL,
    processed     VARCHAR(4)    NOT NULL DEFAULT '0',
    INDEX         idx_id_device_processed (serial_number, processed)
);

CREATE TABLE apps_to_uninstall
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128) NOT NULL,
    package_name  VARCHAR(128) NOT NULL,
    processed     VARCHAR(4)   NOT NULL DEFAULT '0',
    INDEX         idx_id_device_processed (serial_number, processed)
);

CREATE TABLE reboot
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128) NOT NULL,
    processed     VARCHAR(4)   NOT NULL DEFAULT '0',
    INDEX         idx_id_device_processed (serial_number, processed)
);

CREATE TABLE app_to_start_on_reboot
(
    serial_number VARCHAR(128) NOT NULL,
    kiosk         VARCHAR(4)   NOT NULL,
    app_name      VARCHAR(128) NOT NULL,
    INDEX         idx_id_device (serial_number)
);

CREATE TABLE messages
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(128)  NOT NULL,
    message       VARCHAR(1024) NOT NULL,
    processed     VARCHAR(4)    NOT NULL DEFAULT '0',
    INDEX         idx_id_device_processed (serial_number, processed)
);

CREATE TABLE app_list
(
    serial_number VARCHAR(128) NOT NULL,
    app_name      VARCHAR(128) NOT NULL,
    INDEX         idx_id_device (serial_number)
);

CREATE USER 'proxy_user'@'localhost' IDENTIFIED BY '83929922Wr*';
GRANT ALL PRIVILEGES ON devices.* TO 'proxy_user'@'localhost';
FLUSH PRIVILEGES;