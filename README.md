# 评委评分系统功能介绍及部署指南

## 目录
- [系统概述](#系统概述)
- [技术架构](#技术架构)
- [部署步骤](#部署步骤)
  - [后端部署](#后端部署)
  - [数据库配置](#数据库配置)
  - [小程序部署](#小程序部署)
- [系统配置](#系统配置)
- [使用说明](#使用说明)
- [常见问题](#常见问题)

## 系统概述

评委评分系统是一个基于Python Flask后端和微信小程序前端的评分管理平台，使用MySQL数据库存储数据。系统支持多评委分组评分，实时统计分数，导出评分数据等功能。

### 主要功能
- 评委账号管理
- 分组管理
- 评分管理
- 数据导出
- 成绩统计

## 技术架构

### 后端技术栈
- Python 3.8+
- Flask 2.3.3
- MySQL 5.7+
- Flask-SQLAlchemy
- Flask-Login
- JWT认证

### 前端技术栈
- 微信小程序原生开发
- WeUI组件库

### 系统架构图
```
├── 后端服务 (Flask)
│   ├── 用户认证模块
│   ├── 数据管理模块
│   ├── API接口模块
│   └── 数据统计模块
├── 数据库服务 (MySQL)
│   ├── users (用户表)
│   ├── groups (分组表)
│   ├── members (成员表)
│   ├── scores (评分表)
│   └── user_groups (用户分组关联表)
└── 小程序端
    ├── 登录模块
    ├── 分组显示模块
    └── 评分模块
```

# 完整的部署步骤

1. **准备工作**
```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装必要的工具
sudo apt install python3 python3-pip python3-venv mysql-server nginx git -y
```

2. **配置 MySQL**
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
```

3. **部署项目**
```bash
# 创建项目目录
sudo mkdir -p /var/www/rating_system
sudo chown -R $USER:$USER /var/www/rating_system
cd /var/www/rating_system

# 克隆项目 克隆太慢，不如直接上传
sudo git clone https://github.com/bobo-gh/rating_system_.git .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn
```

4. **配置环境变量**
```bash
# 创建 .env 文件
cd /var/www/rating_system
vim .env

# 添加以下内容
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=rating_user
MYSQL_PASSWORD=你设置的密码
MYSQL_DATABASE=rating_system
JWT_SECRET=your_jwt_secret_key
SECRET_KEY=your_flask_secret_key

# 设置文件权限
chmod 600 .env
```

5. **配置 Gunicorn 服务**
```bash
# 创建服务文件
sudo vim /etc/systemd/system/rating_system.service

# 添加以下内容（替换 ubuntu 为你的用户名）
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

# 按ESC进入命令模式，:x
# 启动服务
sudo systemctl daemon-reload
sudo systemctl start rating_system
sudo systemctl enable rating_system
```

6. **配置 Nginx**
```bash
# 创建 Nginx 配置文件
sudo vim /etc/nginx/sites-available/rating_system

# 添加以下内容
server {
    listen 80;
    server_name 服务器IP;

    location / {
        proxy_pass http://127.0.0.1:4262;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/rating_system /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful


# 重启 Nginx
sudo systemctl restart nginx
```

7. **配置防火墙**
```bash
# 开放必要端口
sudo ufw allow 80
sudo ufw allow 4262 # 端口开放注意腾讯云上的允许
sudo ufw enable
```

8. **修改小程序配置**
```bash
# 修改小程序的服务器地址
# 编辑 miniprogram-1/utils/request.js 文件
vim miniprogram-1/utils/request.js

# 修改 BASE_URL 为
const BASE_URL = 'http://服务器IP:4262/api';
```

9. **初始化数据库**
```bash
# 在远程服务器上执行
mysql -u rating_user -p rating_system < rating_system.sql
```

10. **验证部署**
```bash
# 检查服务状态
sudo systemctl status rating_system
sudo systemctl status nginx

# 检查日志
sudo journalctl -u rating_system
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

11. **访问测试**
- 在浏览器访问 `http://服务器IP:4262` 应该能看到管理后台登录界面
- 默认管理员账号：
  - 用户名：admin
  - 密码：admin123

12. **小程序配置**
- 在微信开发者工具中：
  - 点击右上角【详情】
  - 在【本地设置】中勾选【不校验合法域名...】选项
  - 这样可以在开发阶段使用 IP 地址

13. **数据初始化**
- 登录管理后台
- 创建分组
- 上传评委和成员数据（使用 Excel 模板）

14. **常见问题处理**
- 如果访问出现 502 错误：
  ```bash
  # 检查 gunicorn 日志
  sudo journalctl -u rating_system
  
  # 检查应用权限
  sudo chown -R ubuntu:ubuntu /var/www/rating_system
  ```

- 如果数据库连接失败：
  ```bash
  # 检查 MySQL 状态
  sudo systemctl status mysql
  
  # 检查数据库连接
  mysql -u rating_user -p
  ```

15. **安全建议**
```bash
# 设置目录权限
sudo chown -R ubuntu:ubuntu /var/www/rating_system
sudo chmod -R 755 /var/www/rating_system
sudo chmod 600 /var/www/rating_system/.env

# 定期备份数据库
mysqldump -u rating_user -p rating_system > backup.sql
```

如果遇到任何问题，可以查看相应的日志文件进行排查。


## 使用说明

### 1. 管理员后台

#### 登录系统
- 访问 `http://您的服务器IP:4262`
- 默认管理员账号：admin
- 默认密码：admin123

#### 初始化数据
1. 准备Excel文件
   - 评委文件：包含 username, password, role, group_ids 列
   - 成员文件：包含 exam_number, school_stage, subject, name, group_id, notes 列

2. 上传文件
   - 登录后台
   - 进入数据初始化页面
   - 上传准备好的Excel文件

#### 数据导入说明

##### 1. 评委数据导入
评委数据Excel文件必须包含以下列：
```
username    - 用户名（必填）
password    - 密码（必填）
role        - 角色（必填，填写"judge"）
group_ids   - 分组ID（必填，多个分组用英文逗号分隔，如"1,2,3"）
```

注意事项：
- 所有必填字段不能为空
- 用户名不能重复
- role 字段必须填写 "judge"
- group_ids 中的分组ID必须是已存在的分组
- 如果某行数据不完整，该行将被跳过

##### 2. 成员数据导入
成员数据Excel文件必须包含以下列：
```
exam_number   - 考号（必填）
name          - 姓名（必填）
school_stage  - 学段（必填）
subject       - 学科（必填）
group_id      - 分组ID（必填）
notes         - 备注（选填）
```

注意事项：
- 除了notes外，其他字段都是必填的
- 考号不能重复
- group_id 必须是已存在的分组ID
- notes 字段可以为空
- 如果必填字段为空，该行将被跳过
- Excel中的空值(NaN)会被自动转换为空字符串

##### 3. 导入步骤
1. 下载模板
   - 点击"下载评委模板"或"下载成员模板"
   - 使用模板填写数据

2. 准备数据
   - 按照模板格式填写数据
   - 确保必填字段完整
   - 保存为Excel格式（.xlsx）

3. 上传文件
   - 登录管理员后台
   - ��入"数据初始化"页面
   - 选择评委文件和成员文件
   - 点击"开始初始化"

4. 确认结果
   - 系统会显示导入成功的记录数
   - 显示跳过的无效记录数
   - 如果有错误会显示具体原因

##### 4. 注意事项
1. 数据初始化会清除：
   - 所有评分记录
   - 所有成员数据
   - 所有评委用户（管理员账号保留）
   - 评委与分组的关联关系

2. 不会清除：
   - 管理员账号
   - 分组信息

3. 建议在初始化前：
   - 备份重要数据
   - 确认分组已创建
   - 仔细核对Excel文件内容

#### 日常管理
- 用户管理：添加/编辑评委账号
- 分组管理：创建/编辑评分分组
- 成员管理：添加/编辑待评分成员
- 数据导出：导出评分结果

### 2. 评委小程序

#### 登录
- 打开小程序
- 输入评委账号密码
- 登录系统

#### 评分操作
1. 查看分组
   - 登录后显示可评分的分组
   - 显示每个分组的评分进度

2. 评分
   - 选择分组进入成员列表
   - 点击成员进入评分界面
   - 输入分数（0-100）
   - 提交评分



```bash

```
