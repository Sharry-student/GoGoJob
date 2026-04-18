# 传媒行业招聘数据分析平台（GoGoJob）

## 1. 项目概述
本项目针对传媒与泛运营岗位招聘数据，构建“数据清洗—数据库治理—模型分析—可视化决策”一体化应用。系统聚焦以下业务目标：
- 对多来源招聘数据进行标准化处理，保证统计口径一致；
- 在 MySQL 中建立可维护的数据资产，避免前端直接读取文件；
- 提供面向求职者的薪资预测与岗位匹配能力；
- 通过可视化页面输出地区、学历、经验、公司规模等维度洞察。

## 2. 核心功能
- 一次清洗脚本：省市区标准化、薪资解析、职位标准化、福利提取、岗位描述结构化拆分；
- SQL 数据服务化：前端图表与模型仅基于 MySQL 数据查询；
- 薪资预测：支持规则统计回退 + 机器学习模型融合输出；
- 岗位匹配：岗位类别强约束 + 地域/薪资/资历多维评分；
- 薪资热力图：省级热力 + 省份点击联动城市与岗位明细；
- 岗位分类页增强：每个岗位类别页面增加 Top10 岗位列表展示，降低页面留白；
- 岗位交叉对比：组合两个不同的“岗位类别+工作城市”，直观对比两者的薪资极值与平均水平。
- 导航分组增强：POPULAR JOBS / VISUAL MAP / DATA ANALYSIS 分族群导航；
- 顶部头像菜单：系统管理与退出登录迁移至右上角管理员头像菜单，并增加“管理员”提示标签；
- 管理员信息条：头像、文字与菜单统一放置在顶部浅色背景块内，保证全页面一致；
- 后台管理：用户管理、初始化引导、手动数据重载。

## 3. 技术栈
### 前端
- HTML5 + Jinja2
- CSS3 + Bootstrap
- JavaScript + Axios + ECharts

### 后端
- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Login

### 数据与建模
- MySQL 8
- Pandas / NumPy
- scikit-learn（回归、特征向量化、相似度）
- pypinyin（拼音排序）

## 4. 数据流程
1. 原始招聘文件落盘至 `raw_data/`；
2. 执行 `clean_recruitment_data.py` 生成 `clean_data/all_jobs_cleaned.csv`；
3. 访问 `/bootstrap` 将清洗后 CSV 全量入库至 MySQL `jobs` 表；
4. 后端 API 基于 SQL 查询提供图表统计与模型输入；
5. 前端页面通过 API 进行交互与渲染。

## 5. 项目结构（含模板细分）
```text
GoGoJob/
├─ app/
│  ├─ routes/
│  │  ├─ auth.py                    # 登录、登出、用户管理
│  │  └─ main.py                    # 页面路由 + 数据API
│  ├─ services/
│  │  ├─ analytics.py               # 统计、预测、匹配核心逻辑
│  │  ├─ data_loader.py             # CSV -> SQL 导入
│  │  ├─ job_title.py               # 职位标准化规则
│  │  └─ security.py                # 权限与密码策略
│  ├─ templates/
│  │  ├─ base.html                  # 全站布局与导航
│  │  ├─ login.html                 # 登录页
│  │  ├─ dashboard.html             # 首页看板
│  │  ├─ category.html              # 分类分析页
│  │  ├─ map.html                   # 薪资热力图页
│  │  ├─ predict.html               # 薪资预测页
│  │  ├─ match.html                 # 岗位匹配页
│  │  ├─ job_detail.html            # 岗位详情页
│  │  ├─ compare.html               # 岗位对比页
│  │  ├─ users.html                 # 用户管理页
│  │  └─ setup.html                 # 初始化引导页
│  ├─ static/
│  │  ├─ css/main.css               # 全局样式
│  │  ├─ js/*.js                    # 页面交互脚本
│  │  └─ img/lanyangyang.png        # 登录背景图
│  ├─ models.py                     # ORM 模型
│  ├─ config.py                     # 配置与数据库连接
│  └─ __init__.py                   # 应用工厂与初始化
├─ raw_data/                        # 原始数据
├─ clean_data/                      # 清洗结果
├─ clean_recruitment_data.py        # 一次清洗主脚本
├─ run.py                           # 服务入口
├─ requirements.txt                 # 依赖清单
└─ docs/                            # 项目链路与步骤说明
```

## 6. 数据库设计
### jobs（核心业务表）
- 主键：`id`
- 源数据标识：`csv_id`
- 岗位信息：`category`, `title`, `normalized_title`
- 地区信息：`province`, `city`, `region`
- 公司信息：`company_name`, `company_size`, `company_type`, `company_industry`
- 薪资信息：`min_salary`, `max_salary`, `avg_salary`
- 任职条件：`education`, `experience`
- 描述信息：`description`

### users（权限表）
- `id`, `username`, `password_hash`, `role`

## 7. 核心算法
### 7.1 薪资预测
- **统计优先策略**：在同岗位类别约束下，按“省份/城市/学历/经验/规模”逐层回退，优先使用同分组样本的分位区间；
- **模型回退策略**：样本不足时，使用文本化结构特征输入回归模型；
- **模型选择**：在 RandomForest、ExtraTrees、GradientBoosting 中进行验证集 MAE 对比，选取误差更低模型；
- **输出项**：最小值、最大值、均值、置信度、样本量、模型指标。

### 7.2 岗位匹配
- **硬约束**：匹配候选仅来自用户选择的岗位类别；
- **多维评分**：城市/省份匹配、薪资区间匹配、学历经验匹配、规模匹配；
- **相似度增强**：对结构化特征向量计算余弦相似度，增强分数区分；
- **结果输出**：Top10 结果与分项评分。

## 8. 大数据技术应用
- 多文件批处理清洗与字段归一化；
- 高维特征向量化与模型缓存；
- 分层回退保障小样本可解释性；
- SQL 作为统一数据服务层，支持持续增量更新。

## 9. 安装与运行
### 9.1 环境要求
- Python 3.10+
- MySQL 8.0+

### 9.2 安装步骤
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 创建数据库：
   ```sql
   CREATE DATABASE gogojob CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   ```
   - Open the app/config.py file in your project, find the "MySQL Configuration" section, and modify the following parameters to your local MySQL information:
     - MYSQL_PORT：你的 MySQL 端口号（默认 3306）
     - MYSQL_PASSWORD：你的 MySQL root 用户密码
     - 其他参数如无特殊修改，保持默认即可
   
3. 启动服务：
   ```bash
   python run.py
   ```
4. 首次导入数据：
   - 登录后访问：`http://127.0.0.1:5000/bootstrap`

## 10. 项目特色
- 以 SQL 为唯一服务数据源，避免前端“直读文件”导致口径漂移；
- 清洗规则与业务约束前置，预测与匹配结果可追溯；
- 管理端支持初始化与用户治理，适用于协作开发环境。
- UI采用中文业务语义与深色侧栏 + 浅色内容区布局，强调稳重、专业与可读性。
- 预测/匹配输入区采用悬浮面板，便于长页面滚动时持续可操作。
- 首页图表使用分区配色策略，避免同色图造成识别困难。
- 登录页支持自定义背景图与遮罩增强，保证信息可读性。
- 页面标题区域增加浅色块背景，缓解页面顶部留白，提升层次。
- 左侧导航栏随页面滚动保持完整可见，长页面操作不中断。
- 薪资热力图“全国热力图”和“TOP10 排名”容器高度统一，页面视觉更协调。

## 11. 未来发展方向
- 加入增量清洗任务与调度编排；
- 增加模型漂移监控、数据质量告警；
- 引入更强语义模型提升岗位匹配精度；
- 提供多租户与权限细粒度控制。

## 12. 文档阅读指引
- 文档按阅读人群分类索引见：`docs/DOC_INDEX.md`
