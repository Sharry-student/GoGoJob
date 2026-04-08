# 协作开发指南（CONTRIBUTING）

## 1. 分支策略
- `main`：稳定主分支，仅通过 Pull Request 合并。
- `feat/*`：新功能开发分支。
- `fix/*`：缺陷修复分支。
- `docs/*`：文档更新分支。

## 2. 基本流程
1. 从 `main` 拉取最新代码：
   ```bash
   git checkout main
   git pull origin main
   ```
2. 新建功能分支：
   ```bash
   git checkout -b feat/<feature-name>
   ```
3. 开发并本地自测（至少运行项目基础启动）。
4. 提交代码：
   ```bash
   git add .
   git commit -m "feat: xxx"
   git push -u origin feat/<feature-name>
   ```
5. 在 GitHub 发起 Pull Request 到 `main`，等待评审后合并。

## 3. 提交规范
- `feat:` 新功能
- `fix:` 修复
- `refactor:` 重构
- `docs:` 文档
- `style:` 样式调整

## 4. 避免覆盖他人修改
- 不要直接向 `main` push。
- 每次开发前先 `git pull origin main`。
- 出现冲突先在本地解决，再 push。
- 禁止对 `main` 执行 `push --force`。

## 5. 版本回滚与备份
- 每次稳定版本打标签：
  ```bash
  git tag -a vX.Y.Z -m "stable release"
  git push origin vX.Y.Z
  ```
- 需要回滚时优先使用 `git revert`，避免破坏历史。
- 重要里程碑建议额外备份数据库导出文件。

## 6. 本地运行要求
1. 安装依赖：`pip install -r requirements.txt`
2. 配置 MySQL 并创建 `gogojob` 数据库
3. 启动：`python run.py`
4. 首次同步数据：访问 `/bootstrap`

