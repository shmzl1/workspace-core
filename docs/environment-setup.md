# TalentFlow 环境配置

以下命令是规划中的团队开发流程，不表示本次已执行或验证。

## 首次

```powershell
conda env create -f backend/environment.yml
conda activate talentflow
```

```powershell
cd frontend
npm install
cd ..
```

打开 Docker Desktop 后：

```powershell
docker compose up -d postgres
```

```powershell
cd backend
alembic upgrade head
cd ..
```

## 日常开发

```powershell
git switch dev
git pull origin dev
```

```powershell
conda activate talentflow
pip install -r backend/requirements-dev.txt
```

```powershell
cd frontend
npm install
cd ..
```

```powershell
docker compose up -d postgres
```

```powershell
cd backend
alembic upgrade head
cd ..
```

## 后端

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 前端

```powershell
npm run dev
```

## 推送

```powershell
git add .
git commit -m "feat: 简述本次修改"
git push origin dev
```

## 强调

- 只有 `dev` 与 `main`。
- 不直接向 `main` 提交。
- 不提交 `.env`、`node_modules`、`__pycache__`、真实密钥和真实数据。
