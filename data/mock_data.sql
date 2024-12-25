# mock_data.sql - SQL script to insert mock data 
-- 插入管理员
INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');

-- 插入评委
INSERT INTO users (username, password, role) VALUES ('judge1', 'judge123', 'judge');
INSERT INTO users (username, password, role) VALUES ('judge2', 'judge123', 'judge');

-- 插入分组
INSERT INTO groups (name) VALUES ('组A');
INSERT INTO groups (name) VALUES ('组B');

-- 插入成员
INSERT INTO members (name, group_id) VALUES ('成员1', 1);
INSERT INTO members (name, group_id) VALUES ('成员2', 1);
INSERT INTO members (name, group_id) VALUES ('成员3', 2);
INSERT INTO members (name, group_id) VALUES ('成员4', 2);