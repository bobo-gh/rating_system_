# 评委评分系统使用指南

## 目录
- [系统简介](#系统简介)
- [功能特点](#功能特点)
- [系统架构](#系统架构)
- [部署指南](#部署指南)
  - [环境要求](#环境要求)
  - [后端部署](#后端部署)
  - [小程序部署](#小程序部署)
- [使用指南](#使用指南)
  - [管理员后台](#管理员后台)
  - [评委小程序](#评委小程序)
- [常见问题](#常见问题)

## 系统简介

评委评分系统是一个专门为各类评分场景设计的综合性评分管理平台，包含Web管理后台和微信小程序两个部分。系统支持多评委分组评分，成绩实时统计，数据导出等功能。

### 主要用户角色
- 管理员：负责系统管理、评委管理、分组管理等
- 评委：通过小程序进行评分操作

## 功能特点

### Web管理后台
1. 用户管理
   - 评委账号管理
   - 评委分组分配
   - 密码重置

2. 分组管理
   - 创建/编辑/删除分组
   - 分组成员管理
   - 评委分配

3. 成员管理
   - 成员信息管理
   - 批量导入成员
   - 成员分组分配

4. 数据管理
   - Excel���入导出
   - 评分数据统计
   - 成绩汇总导出

### 微信小程序
1. 评委功能
   - 账号登录
   - 查看分配分组
   - 成员评分
   - 评分记录查看

2. 评分功能
   - 实时评分
   - 分数验证
   - 评分状态显示
   - 成绩修改

## 系统架构

### 技术栈
- 后端：Python + Flask + MySQL
- 前端：微信小程序
- 数据库：MySQL 5.7+

### 系统结构
```
├── 后端服务 (Flask)
│   ├── 用户认证模块
│   ├── 数据管理模块
│   ├── API接口模块
│   └── 数据统计模块
├── 数据库服务 (MySQL)
│   ├── 用户表
│   ├── 分组表
│   ├── 成员表
│   └── 评分表
└── 小程序端
    ├── 登录模块
    ├── 分组显示模块
    └── 评分模块
```

## 部署指南

### 环境要求
- Python 3.8+
- pip包管理器
- MySQL 5.7+
- 微信开发者工具
- Windows/Linux服务器

### 后端部署

1. **安装Python环境**
```bash
# Windows
# 访问 https://www.python.org/downloads/ 下载并安装Python 3.8+

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip
```

2. **安装MySQL**
```bash
# Windows
# 访问 https://dev.mysql.com/downloads/mysql/ 下载并安装MySQL

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql

# 设置MySQL root密码
sudo mysql_secure_installation
```

3. **创建数据库和用户**
```sql
# 登录MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE rating_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rating_user'@'localhost' IDENTIFIED BY '您的密码';
GRANT ALL PRIVILEGES ON rating_system.* TO 'rating_user'@'localhost';
FLUSH PRIVILEGES;
```

4. **下载项目代码**
```bash
# 创建项目目录
mkdir rating_system
cd rating_system

# 下载项目文件
# 将项目文件复制到此目录
```

5. **配置数据库连接**
```bash
# 创建配置文件 .env
echo "DATABASE_URL=mysql://rating_user:您的密码@localhost/rating_system" > .env
```

6. **安装依赖包**
```bash
pip install -r requirements.txt
```

7. **初始化数据库**
```bash
# 进入Python交互环境
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
...     exit()
```

8. **启动服务**
```bash
# 开发环境
python app.py

# 生产环境
# 安装gunicorn（Linux）
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:4262 app:app
```

9. **配置防火墙**
```bash
# Windows：在防火墙设置中开放4262端口

# Linux
sudo ufw allow 4262
```

### 小程序部署

1. **安装微信开发者工具**
- 访问[微信开发者工具下载页面](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
- 下载并安装适合您操作系统的版本

2. **导入项目**
- 打开微信开发者工具
- 点击"导入项目"
- 选择项目目录中的 `miniprogram-1` 文件夹
- 填写小程序的 AppID（需要在微信公众平台注册）

3. **修改配置**
- 打开 `miniprogram-1/utils/request.js`
- 修改 `BASE_URL` 为您的服务器地址：
```javascript
const BASE_URL = 'http://您的服务器IP:4262/api';
```

4. **项目配置**
- 在"详情"面板中
- 勾选"不校验合法域名..."（开发环境）
- 生产环境需要在微信公众平台配置服务器域名

## 使用指南

### 管理员后台

1. **登录系统**
- 访问 `http://服务器IP:4262`
- 默认管理员账号：admin
- 默认密码：admin123

2. **用户管理**
- 点击"用户管理"
- 可以添加、编辑、删除评委账号
- 为评委分配评分分组

3. **分组管理**
- 创建评分分组
- 管理分组成员
- 分配评委权限

4. **成员管理**
- 手动添加/编辑成员
- 通过Excel批量导入
- 分配成员到分组

5. **数据导出**
- 导出评分数据
- 查看统计报表
- 导出成绩汇总

### 评委小程序

1. **登录**
- 打开小程序
- 输入评委账号和密码
- 登录系统

2. **查看分组**
- 登录后自动显示分配的分组
- 显示每个分组的评分进度

3. **评分操作**
- 点击分组进入成员列表
- 点击成员进入评分界面
- 输入分数（0-100）
- 提交评分

4. **查看记录**
- 已评分的成员显示分数
- 未评分的成员显示"未评分"
- 可以查看评分进度

## 常见问题

1. **无法连接数据库？**
- 检查MySQL服务是否正常运行
- 确认数据库用户名和密码是否正确
- 检查数据库连接字符串格式

2. **数据库性能问题？**
- 检查MySQL配置参数
- 优化数据库索引
- 检查慢查询日志

3. **无法登录系统？**
- 检查用户名密码是否正确
- 确认账号是否为评委角色
- 检查网络连接是否正常

4. **看不到分组？**
- 确认管理员是否已分配分组
- 检查账号权限是否正确
- 尝试退出重新登录

5. **无法提交评分？**
- 检查分数是否在0-100范围内
- 确认该成员是否已被评分
- 检查网络连接

6. **系统显示异常？**
- 清除小程序缓存
- 重新编译小程序
- 检查服务器连接

## 生产环境优化建议

1. **数据库优化**
- 配置MySQL主从复制
- 定期备份数据库
- 优化MySQL配置参数
- 添加必要的索引

2. **服务器配置**
- 使用nginx反向代理
- 配置SSL证书
- 启用数据库连接池
- 配置服务器监控

3. **安全措施**
- 定期更新MySQL密码
- 限制数据库远程访问
- 配置防火墙规则
- 启用MySQL审计日志

## 技术支持

如遇到问题，请联系系统管理员或技术支持人员。 
