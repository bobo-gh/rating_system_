# create_db.sql - SQL script to create the database schema
 -- 创建用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

-- 创建分组表
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- 创建成员表
CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    group_id INTEGER,
    FOREIGN KEY(group_id) REFERENCES groups(id)
);

-- 创建评分表
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judge_id INTEGER,
    member_id INTEGER,
    score INTEGER,
    UNIQUE(judge_id, member_id),
    FOREIGN KEY(judge_id) REFERENCES users(id),
    FOREIGN KEY(member_id) REFERENCES members(id)
);


