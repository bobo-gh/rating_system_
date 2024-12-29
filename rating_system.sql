/*
 Navicat Premium Dump SQL

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80040 (8.0.40)
 Source Host           : localhost:3306
 Source Schema         : rating_system

 Target Server Type    : MySQL
 Target Server Version : 80040 (8.0.40)
 File Encoding         : 65001

 Date: 29/12/2024 10:53:33
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for groups
-- ----------------------------
DROP TABLE IF EXISTS `groups`;
CREATE TABLE `groups`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of groups
-- ----------------------------
INSERT INTO `groups` VALUES (4, '初中数学组');
INSERT INTO `groups` VALUES (3, '初中语文组');
INSERT INTO `groups` VALUES (2, '小学数学组');
INSERT INTO `groups` VALUES (1, '小学语文组');
INSERT INTO `groups` VALUES (6, '高中数学组');
INSERT INTO `groups` VALUES (5, '高中语文组');

-- ----------------------------
-- Table structure for members
-- ----------------------------
DROP TABLE IF EXISTS `members`;
CREATE TABLE `members`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `school_stage` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `group_id` int NOT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `exam_number`(`exam_number` ASC) USING BTREE,
  INDEX `group_id`(`group_id` ASC) USING BTREE,
  CONSTRAINT `members_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 163 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of members
-- ----------------------------
INSERT INTO `members` VALUES (143, 'E001', '小学', '语文', '张三', 1, '语文课代表');
INSERT INTO `members` VALUES (144, 'E002', '小学', '语文', '李四', 1, '朗读比赛第一');
INSERT INTO `members` VALUES (145, 'E003', '小学', '语文', '王五', 1, '作文优秀');
INSERT INTO `members` VALUES (146, 'E004', '小学', '语文', '赵六', 1, '写字比赛第一');
INSERT INTO `members` VALUES (147, 'E005', '小学', '数学', '钱七', 2, '数学课代表');
INSERT INTO `members` VALUES (148, 'E006', '小学', '数学', '孙八', 2, '奥数成绩优异');
INSERT INTO `members` VALUES (149, 'E007', '小学', '数学', '周九', 2, '心算能手');
INSERT INTO `members` VALUES (150, 'E008', '小学', '数学', '吴十', 2, '解题能手');
INSERT INTO `members` VALUES (151, 'E009', '初中', '语文', '郑一', 3, '语文竞赛一等奖');
INSERT INTO `members` VALUES (152, 'E010', '初中', '语文', '王二', 3, '作文竞赛优胜');
INSERT INTO `members` VALUES (153, 'E011', '初中', '语文', '陈三', 3, '辩论赛优胜');
INSERT INTO `members` VALUES (154, 'E012', '初中', '数学', '刘四', 4, '数学竞赛一等奖');
INSERT INTO `members` VALUES (155, 'E013', '初中', '数学', '林五', 4, '数学建模优胜');
INSERT INTO `members` VALUES (156, 'E014', '初中', '数学', '黄六', 4, '数学思维优秀');
INSERT INTO `members` VALUES (157, 'E015', '高中', '语文', '杨七', 5, '语文学科带头人');
INSERT INTO `members` VALUES (158, 'E016', '高中', '语文', '朱八', 5, '写作特长生');
INSERT INTO `members` VALUES (159, 'E017', '高中', '语文', '徐九', 5, '古文功底扎实');
INSERT INTO `members` VALUES (160, 'E018', '高中', '数学', '何十', 6, '数学竞赛省一等奖');
INSERT INTO `members` VALUES (161, 'E019', '高中', '数学', '高一', 6, '数学奥赛优胜');
INSERT INTO `members` VALUES (162, 'E020', '高中', '数学', '马二', 6, '理科实验小组组长');

-- ----------------------------
-- Table structure for scores
-- ----------------------------
DROP TABLE IF EXISTS `scores`;
CREATE TABLE `scores`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `judge_id` int NOT NULL,
  `member_id` int NOT NULL,
  `score` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_judge_member`(`judge_id` ASC, `member_id` ASC) USING BTREE,
  INDEX `member_id`(`member_id` ASC) USING BTREE,
  CONSTRAINT `scores_ibfk_1` FOREIGN KEY (`judge_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `scores_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 114 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of scores
-- ----------------------------

-- ----------------------------
-- Table structure for user_groups
-- ----------------------------
DROP TABLE IF EXISTS `user_groups`;
CREATE TABLE `user_groups`  (
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`user_id`, `group_id`) USING BTREE,
  INDEX `group_id`(`group_id` ASC) USING BTREE,
  CONSTRAINT `user_groups_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `user_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user_groups
-- ----------------------------
INSERT INTO `user_groups` VALUES (54, 1);
INSERT INTO `user_groups` VALUES (57, 1);
INSERT INTO `user_groups` VALUES (59, 1);
INSERT INTO `user_groups` VALUES (62, 1);
INSERT INTO `user_groups` VALUES (54, 2);
INSERT INTO `user_groups` VALUES (58, 2);
INSERT INTO `user_groups` VALUES (59, 2);
INSERT INTO `user_groups` VALUES (63, 2);
INSERT INTO `user_groups` VALUES (55, 3);
INSERT INTO `user_groups` VALUES (57, 3);
INSERT INTO `user_groups` VALUES (60, 3);
INSERT INTO `user_groups` VALUES (62, 3);
INSERT INTO `user_groups` VALUES (55, 4);
INSERT INTO `user_groups` VALUES (58, 4);
INSERT INTO `user_groups` VALUES (60, 4);
INSERT INTO `user_groups` VALUES (63, 4);
INSERT INTO `user_groups` VALUES (56, 5);
INSERT INTO `user_groups` VALUES (57, 5);
INSERT INTO `user_groups` VALUES (61, 5);
INSERT INTO `user_groups` VALUES (56, 6);
INSERT INTO `user_groups` VALUES (58, 6);
INSERT INTO `user_groups` VALUES (61, 6);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 64 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'admin123', 'admin', '2024-12-28 11:21:10');
INSERT INTO `users` VALUES (54, 'judge1', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (55, 'judge2', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (56, 'judge3', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (57, 'judge4', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (58, 'judge5', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (59, 'judge6', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (60, 'judge7', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (61, 'judge8', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (62, 'judge9', 'judge123', 'judge', '2024-12-29 02:41:52');
INSERT INTO `users` VALUES (63, 'judge10', 'judge123', 'judge', '2024-12-29 02:41:52');

SET FOREIGN_KEY_CHECKS = 1;
