# 评分系统（Rating System）

## 项目介绍

这是一个基于Flask和微信小程序的评分系统，主要用于组织评委对参评人员进行打分评估。系统分为Web管理端和微信小程序评委端两部分。

### 主要功能

#### Web管理端
- 用户管理：管理员可以添加、编辑、删除评委账号
- 分组管理：创建和管理不同的评分分组
- 成员管理：添加、编辑、删除待评分成员
- 数据导入：支持Excel批量导入评委和待评分成员数据
- 评分统计：查看所有评分数据，支持按学段、学科筛选
- 数据导出：支持导出评分统计数据到Excel

#### 小程序评委端
- 评委登录：评委使用账号密码登录
- 分组查看：查看自己所在的评分分组
- 评分功能：对分组内的成员进行打分
- 评分进度：实时显示评分进度

## 部署指南

### 1. 服务器环境准备

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装必要的系统包
sudo apt install -y python3-pip python3-venv nginx mysql-server mysql-client libmysqlclient-dev

# 安装SSL所需的包
sudo apt install -y certbot python3-certbot-nginx
```

### 2. 创建项目目录和虚拟环境

```bash
# 创建项目目录
sudo mkdir -p /var/www/rating_system
cd /var/www/rating_system

# 创建并激活Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 创建项目所需目录
#这里直接上传项目整个目录压缩文件
```

### 3. 项目文件部署

项目文件压缩之前导出所用模块，可参考

```python
# 这里注意项目打包时，导出完整的模块： 激活本地项目的虚拟环境，在项目目录下导出模块， 虽然这样有时程序运行好似还缺模块，根据错误提示再pip一下
E:\rating_system\.venv\Scripts>activate.bat
pip freeze > requirements.txt
```

将项目压缩

```bash
# 上传项目文件压缩包，将项目文件压缩文件解压到指定目录
sudo apt-get install p7zip-full
7z x rating_system.7z
# 安装项目依赖
pip install -r requirements.txt
pip install gunicorn
```



### 4. 配置`MySQL`数据库

```bash
# 启动 MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# 设置 root 密码
sudo mysql_secure_installation

# 登录 MySQL
sudo mysql -u root -p

# 在 MySQL 中执行以下命令
CREATE DATABASE rating_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rating_user'@'localhost' IDENTIFIED BY '你设置的密码';
GRANT ALL PRIVILEGES ON rating_system.* TO 'rating_user'@'localhost';
FLUSH PRIVILEGES;
exit;

# 数据库进行初始化在mysql shell下运行项目目录下的create_database.sql
# 切换到项目目录
cd /var/www/rating_system

# 使用MySQL命令执行SQL文件
sudo mysql -u root -p rating_system < create_database.sql
# 验证数据库是否创建成功
# 登录MySQL
mysql -u rating_user -p

# 在MySQL中执行以下命令
use rating_system;
show tables;  # 查看是否创建了所有表
select * from user;  # 检查管理员用户是否创建成功
exit;

```

### 5. 配置环境变量

```bash
# 项目根目录下创建.env文件
cd /var/www/rating_system
vim .env

# 添加以下内容
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=rating_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=rating_system
JWT_SECRET=your_jwt_secret_key
SECRET_KEY=your_flask_secret_key

# 设置文件权限
chmod 600 .env
```

### 6. 配置`Gunicorn`

创建`Gunicorn`服务文件：
```bash
sudo vim /etc/systemd/system/rating_system.service
```

服务文件内容：
```ini
[Unit]
Description=Rating System Gunicorn Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/rating_system
Environment="PATH=/var/www/rating_system/venv/bin"
ExecStart=/var/www/rating_system/venv/bin/gunicorn -w 4 -b 0.0.0.0:4262 app:app
Restart=always

[Install]
WantedBy=multi-user.target
                              
```

启动服务：
```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload
sudo systemctl start rating_system
sudo systemctl enable rating_system
```

### 7. 配置`Nginx`

创建`Nginx`配置文件：
```bash
sudo vim /etc/nginx/sites-available/rating_system
```

配置文件内容：
```nginx
# HTTP - 重定向到HTTPS
server {
    listen 80;                                    # 监听80端口（HTTP）
    server_name www.aibobo.tech aibobo.tech;     # 指定域名，支持带www和不带www的访问
    return 301 https://$server_name$request_uri;  # 301永久重定向到HTTPS
}

# HTTPS
server {
    listen 443 ssl;                              # 监听443端口，启用SSL
    server_name www.aibobo.tech aibobo.tech;     # 指定域名

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/www.aibobo.tech/fullchain.pem;      # SSL证书文件
    ssl_certificate_key /etc/letsencrypt/live/www.aibobo.tech/privkey.pem;    # SSL私钥文件

    # SSL安全参数
    ssl_protocols TLSv1.2 TLSv1.3;               # 只允许TLS 1.2和1.3
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;  # 加密算法
    ssl_prefer_server_ciphers on;                # 优先使用服务器的加密算法
    ssl_session_cache shared:SSL:10m;            # SSL会话缓存
    ssl_session_timeout 10m;                     # SSL会话超时时间

    # API 路由
   location / {
        # 反向代理设置
        proxy_pass http://127.0.0.1:4262;        # 转发到Flask应用
        proxy_http_version 1.1;                  # 使用HTTP 1.1
        proxy_set_header Upgrade $http_upgrade;  # WebSocket支持
        proxy_set_header Connection 'upgrade';   # WebSocket支持
        
        # 请求头设置
        proxy_set_header Host $host;             # 传递原始主机名
        proxy_set_header X-Real-IP $remote_addr; # 传递真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # 传递代理链路
        proxy_set_header X-Forwarded-Proto $scheme;  # 传递协议类型

        # CORS头部设置
        add_header 'Access-Control-Allow-Origin' '*' always;          # 允许所有来源
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;  # 允许的HTTP方法
        add_header 'Access-Control-Allow-Headers' 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization' always;  # 允许的请求头

               # OPTIONS请求特殊处理
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization';
            add_header 'Access-Control-Max-Age' 1728000;  # 预检请求缓存时间
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;  # 返回无内容状态码
        }
    }
}                                                                                                                                                                                              
```

创建符号链接：
```bash
sudo ln -s /etc/nginx/sites-available/rating_system /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 8. 配置SSL证书

```bash
# 安装SSL证书
sudo certbot --nginx -d your_domain.com

# 自动续期证书
sudo certbot renew --dry-run
```

### 9. 文件权限设置

```bash
# 设置目录权限
sudo chown -R www-data:www-data /var/www/rating_system
sudo chmod -R 755 /var/www/rating_system
```

### 10、访问测试

- 在浏览器访问 `http://服务器IP:4262` 应该能看到管理后台登录界面
- 默认管理员账号：
  - 用户名：`admin`
  - 密码：`admin123`

### 11、小程序配置

- 在微信开发者工具中：
  - 点击右上角【详情】
  - 在【本地设置】中勾选【不校验合法域名...】选项
  - 这样可以在开发阶段使用 IP 地址

## 问题总结与解决方案

### 1. 跨域问题
- 问题：小程序端无法访问后端API
- 解决：使用Flask-CORS处理跨域请求，并正确配置允许的域名和方法

### 2. 并发评分问题
- 问题：多个评委同时评分可能导致数据不一致
- 解决：使用数据库事务和唯一约束确保评分数据的一致性

### 3. Excel导入导出问题
- 问题：大量数据导入导出时内存占用过高
- 解决：使用pandas的chunk功能分批处理数据，并使用BytesIO处理文件流

### 4. 用户认证问题
- 问题：Web端和小程序端需要不同的认证机制
- 解决：Web端使用Flask-Login，小程序端使用JWT令牌

### 5. 数据统计性能问题
- 问题：评分数据统计查询较慢
- 解决：优化数据库索引，使用缓存机制

### 6. 文件上传安全问题
- 问题：文件上传可能带来安全隐患
- 解决：严格限制文件类型，使用安全的文件名生成方式
- 6. 文件上传安全问题

### 7. 常用的操作命令

```bash
# 赋予权限
sudo chmod -R 777 /var/www/rating_system/*
# 删除
rm /var/www/rating_system/rating_system.tar
# 更改路径写的权限 为所有者添加写权限
chmod u+w /var/www/rating_system
# 为所有者、组用户和其他用户添加写权限
chmod a+w /var/www/rating_system
# 打包/var/www/rating_system 将此目录下的venv目录除外
tar --exclude=venv -cvf rating_system.tar /var/www/rating_system
# 强制删除目录
rm -rf /var/www/rating_system
# 将压缩文件解压到指定目录
sudo apt-get install p7zip-full
7z x rating_system.7z
```

## 维护建议

1. 定期备份数据库
```bash
# 创建备份脚本
#!/bin/bash
backup_dir="/var/backups/rating_system"
date_format=$(date +%Y%m%d_%H%M%S)
mysqldump -u rating_user -p rating_system > "$backup_dir/backup_$date_format.sql"
```

2. 监控系统日志
```bash
# 检查应用日志
tail -f /var/www/rating_system/logs/flask_app.log

# 检查Nginx日志
tail -f /var/log/nginx/error.log
```

3. 定期更新依赖包
```bash
pip install --upgrade -r requirements.txt
```

## 技术栈

- 后端：Python Flask

- 数据库：MySQL

- 前端：微信小程序

- Web端：Bootstrap + jQuery

- 服务器：Nginx + Gunicorn

  

## 贡献者

- 后端开发：[o1]
- 前端开发：[Cursor]
- 项目管理：[Bobo]

## 许可证

MIT License



```bash

```
