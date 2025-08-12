drop database devices0;
drop database devices1;

INSERT INTO apps_to_install (id_device, download_url, processed)
VALUES (1,
        'https://downv6.qq.com/qqweb/QQ_1/android_apk/Android_9.2.0_64.apk', 0);
INSERT INTO apps_to_install (id_device, download_url, processed)
VALUES (1,
        'https://dldir1.qq.com/weixin/android/weixin8061android2880_0x28003d34_arm64.apk', 0);
INSERT INTO apps_to_uninstall (id_device, package_name, processed)
values (1, 'com.tencent.mm', 0);
INSERT INTO reboot (id_device, processed)
VALUES (1, 0)