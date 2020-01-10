#!/bin/bash
# TODO setup grive; https://www.fossmint.com/grive2-google-drive-client-for-linux/
mysqldump -uroot -proot123 Twitter > ~/data_partition/database_backups/`date +%Y%m%d`.Twitter.sql