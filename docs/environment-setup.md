# TalentFlow 智聘中枢：团队环境配置指南

本文面向 Windows + PowerShell + Miniconda 成员。以下命令是团队约定的计划使用方式，不代表当前所有脚手架、Docker、迁移或服务已验证完成。

## 首次配置

### 1. 创建 Conda 环境

```powershell
conda env create -f backend/environment.yml
conda activate talentflow
```

### 2. 配置前端

```powershell
cd frontend
npm install
cd ..
```

### 3. Docker Desktop 创建数据库

先打开 Docker Desktop。

复制示例配置：

```powershell
Copy-Item .env.example .env
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env.local
```

计划使用：

```powershell
docker compose up -d postgres

cd backend
alembic upgrade head
cd ..
```

## 之后开发

### 1. 拉取最新代码

```powershell
git switch dev
git pull origin dev
```

只使用 `dev` 和 `main`。不要直接向 `main` 提交。

### 2. 启动前更新环境

```powershell
conda activate talentflow
pip install -r backend/requirements-dev.txt

cd frontend
npm install
cd ..

docker compose up -d postgres

cd backend
alembic upgrade head
cd ..
```

如果 `backend/environment.yml` 更新，再执行：

```powershell
conda env update -f backend/environment.yml --prune
conda activate talentflow
```

### 3. 启动数据库、后端、前端

数据库：

```powershell
docker compose up -d postgres
```

后端：

```powershell
conda activate talentflow
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```powershell
conda activate talentflow
cd frontend
npm run dev
```

### 4. 推送代码

```powershell
git add .
git commit -m "feat: 简述本次修改"
git push origin dev
```

## 禁止提交

- `.env`
- `backend/.env`
- `frontend/.env.local`
- `node_modules`
- `__pycache__`
- 真实密钥
- 真实数据
- 本地 Chroma 数据
- 真实上传文件和真实报告
