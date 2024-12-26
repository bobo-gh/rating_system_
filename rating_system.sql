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

 Date: 26/12/2024 12:49:06
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
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

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
) ENGINE = InnoDB AUTO_INCREMENT = 83 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of members
-- ----------------------------
INSERT INTO `members` VALUES (63, 'E003', '初中', '英语', '王五', 1, '优秀');
INSERT INTO `members` VALUES (64, 'E004', '高中', '物理', '李四', 2, '一般');
INSERT INTO `members` VALUES (65, 'E005', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (66, 'E006', '高中', '物理', '李四', 2, '');
INSERT INTO `members` VALUES (67, 'E007', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (68, 'E008', '高中', '物理', '李四', 2, '');
INSERT INTO `members` VALUES (69, 'E009', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (70, 'E010', '高中', '物理', '李四', 2, '');
INSERT INTO `members` VALUES (71, 'E011', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (72, 'E012', '高中', '物理', '李四', 2, '');
INSERT INTO `members` VALUES (73, 'E013', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (74, 'E014', '高中', '物理', '李四', 2, '');
INSERT INTO `members` VALUES (75, 'E015', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (76, 'E016', '高中', '物理', '李四', 2, '');
INSERT INTO `members` VALUES (77, 'E017', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (78, 'E018', '高中', '物理', '李四', 2, '');
INSERT INTO `members` VALUES (79, 'E019', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (80, 'E020', '高中', '物理', '李四', 2, '');
INSERT INTO `members` VALUES (81, 'E021', '初中', '英语', '王五', 1, '');
INSERT INTO `members` VALUES (82, 'E022', '高中', '物理', '李四', 2, '');

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
) ENGINE = InnoDB AUTO_INCREMENT = 81 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

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
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_groups
-- ----------------------------
INSERT INTO `user_groups` VALUES (15, 1);
INSERT INTO `user_groups` VALUES (16, 1);
INSERT INTO `user_groups` VALUES (18, 1);
INSERT INTO `user_groups` VALUES (21, 1);
INSERT INTO `user_groups` VALUES (15, 2);
INSERT INTO `user_groups` VALUES (17, 2);
INSERT INTO `user_groups` VALUES (19, 2);
INSERT INTO `user_groups` VALUES (20, 2);
INSERT INTO `user_groups` VALUES (21, 2);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 23 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'admin123', 'admin');
INSERT INTO `users` VALUES (15, 'j1', '123', 'judge');
INSERT INTO `users` VALUES (16, 'j2', '123', 'judge');
INSERT INTO `users` VALUES (17, 'j3', '123', 'judge');
INSERT INTO `users` VALUES (18, 'j4', '123', 'judge');
INSERT INTO `users` VALUES (19, 'j5', '123', 'judge');
INSERT INTO `users` VALUES (20, 'j6', '123', 'judge');
INSERT INTO `users` VALUES (21, 'j7', '123', 'judge');

SET FOREIGN_KEY_CHECKS = 1;
