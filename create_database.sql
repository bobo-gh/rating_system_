-- 创建数据库
CREATE DATABASE IF NOT EXISTS rating_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE rating_system;

-- 创建用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(500) NOT NULL,
    role VARCHAR(50) NOT NULL
);

-- 创建分组表
CREATE TABLE `groups` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- 创建用户-分组关联表
CREATE TABLE user_groups (
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES `groups`(id)
);

-- 创建成员表
CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_number VARCHAR(50) NOT NULL UNIQUE,
    school_stage VARCHAR(50) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    name VARCHAR(150) NOT NULL,
    group_id INT NOT NULL,
    notes TEXT,
    FOREIGN KEY (group_id) REFERENCES `groups`(id)
);

-- 创建评分表
CREATE TABLE scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    judge_id INT NOT NULL,
    member_id INT NOT NULL,
    score INT NOT NULL,
    UNIQUE KEY unique_judge_member (judge_id, member_id),
    FOREIGN KEY (judge_id) REFERENCES users(id),
    FOREIGN KEY (member_id) REFERENCES members(id)
);

-- 插入管理员账号
INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin'); 