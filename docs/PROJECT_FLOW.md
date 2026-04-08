# 业务链路与项目层次

## 1. 数据层
- 原始数据：`raw_data/*.csv`
- 一次清洗：`clean_recruitment_data.py`
- 标准结果：`clean_data/all_jobs_cleaned.csv`
- 入库动作：`app/services/data_loader.py -> jobs`

## 2. 模型层
- 薪资预测模型：`app/services/analytics.py::predict_salary`
- 岗位匹配模型：`app/services/analytics.py::match_jobs`
- 模型缓存与刷新：`refresh_ml_cache` + `/api/ml/refresh`

## 3. 接口层
- 页面路由：`app/routes/main.py`
- 认证与用户管理：`app/routes/auth.py`
- 数据 API：`/api/dashboard`、`/api/map`、`/api/predict`、`/api/match`

## 4. 展示层
- 模板层：`app/templates/*.html`
- 交互层：`app/static/js/*.js`
- 样式层：`app/static/css/main.css`
- 资源层：`app/static/img/lanyangyang.png`（登录背景图）
- 顶部统一信息条：`content-head-bg` 内承载管理员标签、头像与菜单

## 5. 系统管理层
- 初始化引导：`/setup`
- 手动导入：`/bootstrap`
- 用户管理：`/admin/users`
- 认证权限：`app/services/security.py`

## 6. 关键约束
- 网页展示数据来源必须是 SQL，不直接读取 CSV。
- 预测与匹配必须受“岗位类别”约束。
- 城市省份由清洗层统一后再用于统计与可视化。
- 导航分组：首页单独；岗位组、热力图组、分析组分族群展示。
- 系统管理入口位于右上角头像菜单，避免侧栏拥挤。
- 导航栏为 sticky 布局，页面滚动时保持完整可见。
