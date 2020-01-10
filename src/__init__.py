"""
CREATE USER 'ankur'@'127.0.0.1' IDENTIFIED BY 'ankur123';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
CREATE USER 'ankur'@'%' IDENTIFIED BY 'ankur123';
GRANT SELECT ON *.* TO 'ankur'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

GRANT ALL ON Twitter.* TO 'root'@'127.0.0.1' IDENTIFIED BY 'root123';
Copy


UPDATE mysql.user SET host = {newhost} WHERE user = {youruser}

"""