# 评委评分系统部署指南

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

## 部署步骤

### 1. 环境准备

#### 系统要求
- Windows/Linux服务器
- Python 3.8+
- MySQL 5.7+
- 微信开发者工具

#### 安装Python环境
```bash
# Windows
# 访问 https://www.python.org/downloads/ 下载并安装Python 3.8+

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. MySQL数据库配置

#### 安装MySQL
```bash
# Windows
# 访问 https://dev.mysql.com/downloads/mysql/ 下载并安装MySQL 5.7+

# Linux (Ubuntu/Debian)
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### 创建数据库和用户
```sql
# 登录MySQL sudo mysql -u root
mysql -u root -p
#修改mysql的root密码
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Gb@720715'; 
# 创建数据库
CREATE DATABASE rating_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户并授权
CREATE USER 'rating_user'@'localhost' IDENTIFIED BY 'Gb@720715';
GRANT ALL PRIVILEGES ON rating_system.* TO 'rating_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 后端部署

#### 获取代码
```bash
# 创建项目目录
sudo mkdir -p /var/www/rating_system

# 修改目录所有者为当前用户（替换 your_username 为你的用户名）无需替换
sudo chown -R $USER:$USER /var/www/rating_system

# 设置适当的权限
sudo chmod -R 755 /var/www/rating_system
cd /var/www/rating_system

# 克隆代码或解压项目文件
# 将项目文件复制到此目录
```

#### 创建虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 配置环境变量和安全密钥

##### 方法一：使用 .env 文件（开发环境推荐）
1. 在项目根目录创建 `.env` 文件：
```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=rating_user
MYSQL_PASSWORD=您的数据库密码
MYSQL_DATABASE=rating_system

# 安全密钥（使用 Python 生成安全的随机密钥）
JWT_SECRET=您的JWT密钥
SECRET_KEY=您的Flask密钥
```

2. 生成安全的随机密钥：
```python
# 在 Python 交互环境中执行
import secrets
print("JWT_SECRET=" + secrets.token_hex(32))
print("SECRET_KEY=" + secrets.token_hex(32))
```

##### 方法二：使用系统环境变量（生产环境推荐）
1. Linux/Mac 系统：
```bash
# 设置数据库配置
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=rating_user
export MYSQL_PASSWORD=您的数据库密码
export MYSQL_DATABASE=rating_system

# 设置安全密钥
export JWT_SECRET=您的JWT密钥
export SECRET_KEY=您的Flask密钥
```

2. Windows 系统：
```powershell
# 设置数据库配置
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_USER=rating_user
set MYSQL_PASSWORD=您的数据库密码
set MYSQL_DATABASE=rating_system

# 设置安全密钥
set JWT_SECRET=您的JWT密钥
set SECRET_KEY=您的Flask密钥
```

##### 密钥说明
- `JWT_SECRET`：用于生成和验证 JWT（JSON Web Token）的密钥，小程序用户登录时使用
- `SECRET_KEY`：Flask 应用的密钥，用于会话管理和 CSRF 保护等

##### 安全建议
1. 使用足够复杂的随机字符串作为密钥
2. 不要将实际使用的密钥提交到代码仓库
3. 在生产环境中使用环境变量而不是 `.env` 文件
4. 定期更换密钥
5. 不同环境（开发、测试、生产）使用不同的密钥

#### 初始化数据库
```bash
# 进入Python交互环境
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
...     exit()
```

#### 启动服务
```bash
# 开发环境
python app.py

# 生产环境（Linux）
gunicorn -w 4 -b 0.0.0.0:4262 app:app
```

### 4. 小程序部署

#### 准备工作
1. 注册微信小程序账号
2. 下载微信开发者工具
3. 获取小程序 AppID

#### 导入项目
1. 打开微信开发者工具
2. 导入项目，选择 `miniprogram-1` 目录
3. 填入 AppID

#### 修改配置
1. 修改服务器地址
```javascript
// miniprogram-1/utils/request.js
const BASE_URL = 'http://您的服务器IP:4262/api';
```

2. 配置服务器域名
- 登录微信公众平台
- 设置 -> 开发设置 -> 服务器域名
- 添加后端服务器域名

## 系统配置

### 1. 防火墙配置
```bash
# Windows
# 在Windows防火墙中开放4262端口

# Linux
sudo ufw allow 4262
```

### 2. Nginx配置（可选）
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:4262;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. SSL配置（推荐）
建议使用SSL证书确保数据传输安全。

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

## 常见问题

### 1. 数据库连接问题
- 检查MySQL服务状态
- 验证数据库用户名密码
- 确认数据库连接字符串格式

### 2. 小程序连接问题
- 检查服务��IP和端口
- 确认域名是否已配置
- 验证网络连接状态

### 3. 评分相关问题
- 确认评委权限是否正确
- 检查分组分配是否完成
- 验证评分规则是否符合要求

## 安全建议

### 1. 数据库安全
- 定期备份数据
- 更新数据库密码
- 限制数据库远程访问

### 2. 服务器安全
- 启用防火墙
- 配置SSL证书
- 定期更新系统

### 3. 应用安全
- 使用强密码
- 启用JWT认证
- 实施访问控制
- 使用安全的随机密钥
- 定期更换应用密钥
- 避免在代码中硬编码敏感信息
- 使用环境变量管理敏感配置

## 技术支持

如遇到问题，请联系系统管理员和技术支持人员。 

## CentOS 部署指南

### 1. 系统准备
```bash
# 更新系统
sudo yum update -y

# 安装基础开发工具
sudo yum groupinstall "Development Tools" -y
sudo yum install wget git vim -y
```

### 2. 安装 Python 环境

#### 方法一：使用 SCL（推荐）
```bash
# 安装 SCL 源
sudo yum install centos-release-scl -y

# 安装 Python 3.8
sudo yum install rh-python38 -y

# 启用 Python 3.8
scl enable rh-python38 bash

# 验证 Python 版本
python --version
```

#### 方法二：从源码编译（如果方法一不可用）
```bash
# 安装编译所需的依赖
sudo yum groupinstall "Development Tools" -y
sudo yum install openssl-devel bzip2-devel libffi-devel -y

# 下载 Python 3.8.12 源码
cd /opt
sudo wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
sudo tar xzf Python-3.8.12.tgz
cd Python-3.8.12

# 配置和编译
sudo ./configure --enable-optimizations
sudo make altinstall

# 创建软链接（可选，如果想设为默认 Python）
sudo ln -sf /usr/local/bin/python3.8 /usr/bin/python3
sudo ln -sf /usr/local/bin/pip3.8 /usr/bin/pip3

# 验证安装
python3.8 --version
pip3.8 --version
```

#### 安装后配置
```bash
# 升级 pip
python3.8 -m pip install --upgrade pip

# 安装虚拟环境工具
python3.8 -m pip install virtualenv
```

### 3. 安装 MySQL
```bash
# 添加 MySQL 仓库
sudo rpm -Uvh https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm

# 安装 MySQL 服务器
sudo yum install mysql-community-server -y

# 启动 MySQL 服务
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 获取临时密码
sudo grep 'temporary password' /var/log/mysqld.log

# 运行安全配置脚本
sudo mysql_secure_installation
```

### 4. 配置 MySQL
```sql
# 使用临时密码登录 MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE rating_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rating_user'@'localhost' IDENTIFIED BY '您的密码';
GRANT ALL PRIVILEGES ON rating_system.* TO 'rating_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. 项目部署

#### 创建项目目录
```bash
# 创建项目目录
sudo mkdir -p /var/www/rating_system
sudo chown -R $USER:$USER /var/www/rating_system
cd /var/www/rating_system

# 复制项目文件到此目录
# ... 复制你的项目文件 ...
```

#### 配置 Python 虚拟环境
```bash
# 创建虚拟环境
python3.8 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 gunicorn
pip install gunicorn
```

#### 配置环境变量
```bash
# 创建并编辑 .env 文件
vim .env

# 添加以下内容
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=rating_user
MYSQL_PASSWORD=您的数据库密码
MYSQL_DATABASE=rating_system
JWT_SECRET=您的JWT密钥
SECRET_KEY=您的Flask密钥
```

### 6. 配置 Systemd 服务

#### 创建服务文件
```bash
sudo vim /etc/systemd/system/rating_system.service
```

添加以下内容：
```ini
[Unit]
Description=Rating System Gunicorn Service
After=network.target

[Service]
User=your_username
Group=your_username
WorkingDirectory=/var/www/rating_system
Environment="PATH=/var/www/rating_system/venv/bin"
ExecStart=/var/www/rating_system/venv/bin/gunicorn -w 4 -b 0.0.0.0:4262 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start rating_system

# 设置开机自启
sudo systemctl enable rating_system

# 查看服务状态
sudo systemctl status rating_system
```

### 7. 配置防火墙
```bash
# 开放必要端口
sudo firewall-cmd --permanent --add-port=4262/tcp
sudo firewall-cmd --reload

# 查看开放的端口
sudo firewall-cmd --list-all
```

### 8. 配置 Nginx（推荐）

#### 安装 Nginx
```bash
# 安装 Nginx
sudo yum install nginx -y

# 启动 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 配置 Nginx
```bash
# 创建配置文件
sudo vim /etc/nginx/conf.d/rating_system.conf
```

添加以下内容：
```nginx
server {
    listen 80;
    server_name your_domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:4262;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### 重启 Nginx
```bash
# 测试配置文件
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 9. 配置 SSL（推荐）

#### 安装 Certbot
```bash
# 安装 EPEL 仓库（如果还没安装）
sudo yum install epel-release -y

# 安装 Certbot
sudo yum install certbot python3-certbot-nginx -y

# 获取证书并自动配置 Nginx
sudo certbot --nginx -d your_domain.com
```

### 10. 日志管理
```bash
# 查看应用日志
sudo journalctl -u rating_system

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```
