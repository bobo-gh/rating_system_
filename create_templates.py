import pandas as pd
import os

# 确保目录存在
os.makedirs('static/templates_files', exist_ok=True)

# 定义分组信息（用于后续引用）
groups = {
    '1': '小学语文组',
    '2': '小学数学组',
    '3': '初中语文组',
    '4': '初中数学组',
    '5': '高中语文组',
    '6': '高中数学组'
}

# 创建评委模板（10组数据）
judge_data = {
    'username': [f'judge{i}' for i in range(1, 11)],
    'password': ['judge123'] * 10,
    'role': ['judge'] * 10,
    'group_ids': [
        '1,2',       # judge1 评小学语文和数学
        '3,4',       # judge2 评初中语文和数学
        '5,6',       # judge3 评高中语文和数学
        '1,3,5',     # judge4 评语文组（小初高）
        '2,4,6',     # judge5 评数学组（小初高）
        '1,2',       # judge6 评小学组
        '3,4',       # judge7 评初中组
        '5,6',       # judge8 评高中组
        '1,3',       # judge9 评小学初中语文
        '2,4'        # judge10 评小学初中数学
    ]
}

# 创建评委DataFrame并保存
judge_df = pd.DataFrame(judge_data)
judge_df.to_excel('static/templates_files/judges_template.xlsx', index=False)

# 创建成员模板（20组数据）
member_data = {
    'exam_number': [f'E{str(i).zfill(3)}' for i in range(1, 21)],  # E001-E020
    'name': [
        '张三', '李四', '王五', '赵六',         # 小学语文组
        '钱七', '孙八', '周九', '吴十',         # 小学数学组
        '郑一', '王二', '陈三',                 # 初中语文组
        '刘四', '林五', '黄六',                 # 初中数学组
        '杨七', '朱八', '徐九',                 # 高中语文组
        '何十', '高一', '马二'                  # 高中数学组
    ],
    'school_stage': [
        '小学', '小学', '小学', '小学',         # 1组
        '小学', '小学', '小学', '小学',         # 2组
        '初中', '初中', '初中',                 # 3组
        '初中', '初中', '初中',                 # 4组
        '高中', '高中', '高中',                 # 5组
        '高中', '高中', '高中'                  # 6组
    ],
    'subject': [
        '语文', '语文', '语文', '语文',         # 1组
        '数学', '数学', '数学', '数学',         # 2组
        '语文', '语文', '语文',                 # 3组
        '数学', '数学', '数学',                 # 4组
        '语文', '语文', '语文',                 # 5组
        '数学', '数学', '数学'                  # 6组
    ],
    'group_id': [
        '1', '1', '1', '1',                    # 小学语文组
        '2', '2', '2', '2',                    # 小学数学组
        '3', '3', '3',                         # 初中语文组
        '4', '4', '4',                         # 初中数学组
        '5', '5', '5',                         # 高中语文组
        '6', '6', '6'                          # 高中数学组
    ],
    'notes': [
        '语文课代表', '朗读比赛第一', '作文优秀', '写字比赛第一',      # 小学语文组
        '数学课代表', '奥数成绩优异', '心算能手', '解题能手',         # 小学数学组
        '语文竞赛一等奖', '作文竞赛优胜', '辩论赛优胜',              # 初中语文组
        '数学竞赛一等奖', '数学建模优胜', '数学思维优秀',            # 初中数学组
        '语文学科带头人', '写作特长生', '古文功底扎实',              # 高中语文组
        '数学竞赛省一等奖', '数学奥赛优胜', '理科实验小组组长'        # 高中数学组
    ]
}

# 创建成员DataFrame并保存
member_df = pd.DataFrame(member_data)
member_df.to_excel('static/templates_files/members_template.xlsx', index=False)

print("模板文件已创建：")
print("1. static/templates_files/judges_template.xlsx")
print("2. static/templates_files/members_template.xlsx") 