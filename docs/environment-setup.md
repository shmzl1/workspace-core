 #TalentFlow 智聘中枢：环境配置指南

## 一、首次配置

### 1. 创建 Conda 环境

在项目根目录执行：

```powershell
conda env create -f backend/environment.yml
conda activate talentflow
```

检查环境是否正确：

```powershell
python --version
node --version
npm --version
```

安装后端依赖：

```powershell
pip install -r backend/requirements-dev.txt
```

---

### 2. 配置前端环境

在项目根目录执行：

```powershell
cd frontend
npm install
cd ..
```

> `node_modules` 是本地依赖目录，不提交到 Git。

---

### 3. 使用 Docker Desktop 创建数据库环境

先打开 Docker Desktop，确认其处于运行状态。

在项目根目录创建本地配置文件：

```powershell
Copy-Item .env.example .env
Copy-Item backend\.env.example backend\.env
```

启动 PostgreSQL：

```powershell
docker compose up -d postgres
```

首次创建数据库表，或后续数据库迁移文件更新后，执行：

```powershell
cd backend
alembic upgrade head
cd ..
```

检查数据库容器状态：

```powershell
docker compose ps
```

---

## 二、之后每天开发

### 1. 拉取最新代码

开始开发前，先确认当前没有未提交的修改：

```powershell
git status
```

然后切换到开发分支并拉取最新代码：

```powershell
git switch dev
git pull origin dev
```

> 所有成员日常开发都在 `dev` 分支进行。
> 如果 `git status` 显示有未提交修改，先提交或暂存后再拉取，避免冲突。

临时保存当前未完成修改：

```powershell
git stash
git pull origin dev
git stash pop
```

---

### 2. 启动前更新前端、后端和数据库环境

先激活 Conda 环境：

```powershell
conda activate talentflow
```

更新后端依赖：

```powershell
pip install -r backend/requirements-dev.txt
```

更新前端依赖：

```powershell
cd frontend
npm install
cd ..
```

启动数据库并更新表结构：

```powershell
docker compose up -d postgres

cd backend
alembic upgrade head
cd ..
```

如果 `backend/environment.yml` 被更新，再额外执行：

```powershell
conda env update -f backend/environment.yml --prune
conda activate talentflow
```

---

### 3. 启动数据库、后端和前端

建议打开三个 PowerShell 终端。

#### 终端 1：数据库

在项目根目录执行：

```powershell
docker compose up -d postgres
```

#### 终端 2：后端

```powershell
conda activate talentflow
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端地址：

```text
http://localhost:8000
```

接口文档：

```text
http://localhost:8000/docs
```

#### 终端 3：前端

```powershell
conda activate talentflow
cd frontend
npm run dev
```

前端地址：

```text
http://localhost:5173
```

---

### 4. 推送代码到 dev

先确认当前分支：

```powershell
git branch --show-current
```

正常情况下应显示：

```text
dev
```

查看本次修改：

```powershell
git status
```

提交并推送：

```powershell
git add .
git commit -m "feat: 简述本次修改内容"
git push origin dev
```

示例：

```powershell
git add .
git commit -m "feat: 完成候选人评分权重沙盘"
git push origin dev
```

如果同时需要同步到 GitHub 远端：

```powershell
git push origin dev
git push github dev
```

---

## 三、发布稳定版本到 main

只有准备阶段验收、Sprint 验收或答辩时，再将 `dev` 合并到 `main`。

```powershell
git switch main
git pull origin main
git merge dev
git push origin main
```

如果同时同步 GitHub：

```powershell
git push github main
```

> 不要直接在 `main` 分支开发或提交功能代码。
> `main` 只保存稳定、可演示的版本。

---

## 四、禁止提交的本地文件

以下文件不能提交：

```text
.env
backend/.env
frontend/.env.local
node_modules
__pycache__
data/runtime/chroma
真实上传文件
真实简历
真实薪资数据
模型 API Key
数据库密码
JWT 密钥
```
