```powershell
conda activate talentflow
```

```powershell
conda activate talentflow
```

```powershell
conda activate talentflow
```

```powershell
conda activate talentflow
```

```powershell
conda activate talentflow
```

```powershell
conda activate talent
```

# TalentFlow 环境配置指南

> 本文用于团队成员在 Windows PowerShell 中完成 TalentFlow 的首次环境配置和日常开发启动。
> 请将文中的路径占位符替换为自己电脑上的实际路径。
> 项目日常开发统一使用 `dev` 分支。

---

# 1. 目录与数据库约定

## 1.1 本地目录约定

```text
你的本地项目根目录
= workspace-core 所在目录

你的本地后端文件路径
= 你的本地项目根目录\backend

你的本地前端文件路径
= 你的本地项目根目录\frontend
```

例如，假设项目位于：

```text
D:\project\workspace-core
```

则对应关系为：

```text
你的本地项目根目录：
D:\project\workspace-core

你的本地后端文件路径：
D:\project\workspace-core\backend

你的本地前端文件路径：
D:\project\workspace-core\frontend
```

后续文档中的命令：

```powershell
cd "你的本地项目根目录"
cd "你的本地后端文件路径"
cd "你的本地前端文件路径"
```

都需要替换为你电脑中的真实项目路径。

---

## 1.2 PostgreSQL 数据库约定

```text
PostgreSQL 数据库名：talentflow
PostgreSQL 用户名：talentflow
PostgreSQL 默认端口：5432
```

根目录 `.env` 中应包含：

```dotenv
POSTGRES_DB=talentflow
POSTGRES_USER=talentflow
POSTGRES_PASSWORD=talentflow_dev_password_change_me
POSTGRES_PORT=5432
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

后端 `backend\.env` 中的数据库连接地址应类似：

```dotenv
DATABASE_URL=postgresql+psycopg://talentflow:talentflow_dev_password_change_me@localhost:5432/talentflow
```

其中最后一个：

```text
talentflow
```

就是 PostgreSQL 数据库名。

---

# 2. 首次配置环境

首次加入项目时，需要依次完成：

```text
创建 Conda 环境
安装后端依赖
安装前端依赖
创建本地配置文件
启动 PostgreSQL
执行数据库迁移
```

---

## 2.1 创建 Miniconda 环境

打开 PowerShell，进入项目根目录：

```powershell
cd "你的本地项目根目录"
```

根据团队统一环境文件创建 Conda 环境：

```powershell
conda env create -f backend/environment.yml
```

激活环境：

```powershell
conda activate talentflow
```

检查基础版本：

```powershell
python --version
node --version
npm --version
```

项目环境约定：

```text
Conda 环境名：talentflow
Python：3.12
Node.js：20
```

---

## 2.2 安装后端依赖

确认当前 PowerShell 已激活 `talentflow` 环境：

```powershell
conda activate talentflow
```

进入后端目录：

```powershell
cd "你的本地后端文件路径"
```

安装后端开发依赖：

```powershell
pip install -r requirements-dev.txt
```

`requirements-dev.txt` 用于安装后端运行、开发和测试所需的 Python 包。

---

## 2.3 安装前端依赖

进入前端目录：

```powershell
cd "你的本地前端文件路径"
```

安装 Vue 前端依赖：

```powershell
npm install
```

安装完成后会生成：

```text
frontend\node_modules\
```

该目录只存在于本地，不提交到 Git。

---

## 2.4 创建本地环境配置文件

进入项目根目录：

```powershell
cd "你的本地项目根目录"
```

复制根目录环境模板：

```powershell
Copy-Item ".env.example" ".env"
```

复制后端环境模板：

```powershell
Copy-Item "backend\.env.example" "backend\.env"
```

文件作用：

```text
.env
用于 Docker Compose 和 PostgreSQL 配置。

backend\.env
用于 FastAPI、数据库连接、JWT、CORS、LLM 和本地数据目录配置。
```

以下文件只保留在本地，不能提交到 Git：

```text
.env
backend\.env
```

---

## 2.5 启动 PostgreSQL 数据库

先手动打开 Docker Desktop，并确认 Docker Desktop 已正常运行。

进入项目根目录：

```powershell
cd "你的本地项目根目录"
```

启动 PostgreSQL：

```powershell
docker compose up -d postgres
```

查看数据库服务状态：

```powershell
docker compose ps
```

正常情况下，`postgres` 服务应处于运行状态。

---

## 2.6 创建或更新数据库表结构

进入后端目录：

```powershell
cd "你的本地后端文件路径"
```

执行数据库迁移：

```powershell
alembic upgrade head
```

该命令会执行项目已有的 Alembic 迁移，使本地数据库表结构更新到当前最新版本。

当前首次迁移文件为：

```text
backend\alembic\versions\0001_initial_schema.py
```

本次基线建设没有执行迁移。团队成员在本地数据库、依赖和环境确认完成后，再手动执行：

```powershell
cd "你的本地后端文件路径"
alembic upgrade head
```

---

# 3. 日常开发

团队日常开发统一使用：

```text
dev 分支
```

每次开发通常只需要完成：

```text
切换并更新 dev
启动数据库
启动后端
启动前端
```

以下操作不是每次开发都要做：

```text
pip install
npm install
conda env update
alembic upgrade head
```

只有依赖文件、Conda 环境文件或数据库迁移文件发生变化时，才需要执行这些更新命令。

---

## 3.1 终端 1：更新代码并启动数据库

打开 PowerShell，进入项目根目录：

```powershell
cd "你的本地项目根目录"
```

切换到日常开发分支：

```powershell
git switch dev
```

拉取远程最新代码：

```powershell
git pull origin dev
```

启动 PostgreSQL：

```powershell
docker compose up -d postgres
```

分支说明：

```text
dev：
日常开发、提交和联调分支。

main：
稳定、可验收、可答辩分支。
```

日常开发中：

```text
统一在 dev 分支修改和提交代码。
不要直接在 main 分支开发功能。
```

---

## 3.2 终端 2：启动后端 FastAPI

打开新的 PowerShell 终端。

激活 Conda 环境：

```powershell
conda activate talentflow
```

进入后端目录：

```powershell
cd "你的本地后端文件路径"
pip install -r requirements-dev.txt
```

启动 FastAPI：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

命令含义：

```text
uvicorn
启动 FastAPI 开发服务器。

app.main:app
加载 backend\app\main.py 中名为 app 的 FastAPI 应用对象。

--reload
开发模式。
修改 Python 文件后，后端会自动重启。

--host 0.0.0.0
监听电脑全部网络接口。
本机可通过 localhost 访问；
后续小程序局域网调试时，也可以通过笔记本局域网 IP 访问。

--port 8000
后端运行在 8000 端口。
```

后端启动后，常用地址为：

```text
后端地址：
http://localhost:8000

API 前缀：
http://localhost:8000/api/v1

Swagger 接口文档：
http://localhost:8000/docs
```

---

## 3.3 终端 3：启动前端 Vue

打开新的 PowerShell 终端。

进入前端目录：

```powershell
cd "你的本地前端文件路径"
npm install
```

启动 Vue 前端：

```powershell
npm run dev
```

通常可在浏览器中访问：

```text
http://localhost:5173
```

实际地址以终端输出为准。

---

# 4. 仅在相关文件变化时执行的更新命令

以下命令不是每天都要执行。

---

## 4.1 后端依赖文件变化时

当队友修改了：

```text
backend\requirements.txt
backend\requirements-dev.txt
```

执行：

```powershell
conda activate talentflow

cd "你的本地后端文件路径"

pip install -r requirements-dev.txt
```

---

## 4.2 前端依赖文件变化时

当队友修改了：

```text
frontend\package.json
frontend\package-lock.json
```

执行：

```powershell
cd "你的本地前端文件路径"

npm install
```

---

## 4.3 Conda 环境文件变化时

当队友修改了：

```text
backend\environment.yml
```

执行：

```powershell
cd "你的本地项目根目录"

conda env update -f backend/environment.yml --prune
conda activate talentflow
```

---

## 4.4 数据库迁移文件变化时

当队友新增或修改了 Alembic 迁移文件时，执行：

```powershell
cd "你的本地后端文件路径"

alembic upgrade head
```

通常迁移文件位于：

```text
backend\alembic\versions\
```

---

# 5. 日常提交代码

开发完成后，进入项目根目录：

```powershell
cd "你的本地项目根目录"
```

先查看本次修改：

```powershell
git status
```

确认无误后，加入暂存区：

```powershell
git add .
```

创建提交：

```powershell
git commit -m "feat: 简述本次修改"
```

推送到远程 `dev` 分支：

```powershell
git push origin dev
```

提交信息格式：

```text
feat: 新增功能
fix: 修复问题
docs: 修改文档
refactor: 重构代码
```

示例：

```powershell
git commit -m "feat: 新增员工签到签退接口"
git commit -m "fix: 修复候选人评分排序错误"
git commit -m "docs: 更新环境配置说明"
git commit -m "refactor: 调整招聘模块目录结构"
```

---

# 6. 不允许提交的内容

以下内容不允许提交到 Git：

```text
.env
backend\.env
frontend\.env.local

node_modules\
__pycache__\
*.pyc

data\runtime\uploads\
data\runtime\reports\
data\runtime\chroma\

真实 API Key
真实 JWT 密钥
真实员工数据
真实薪资数据
真实简历文件
```

每次提交前，都应先执行：

```powershell
git status
```

确认暂存区中没有敏感配置、临时文件和运行时文件。

---

# 7. 最常用命令速查

## 每次开发

```powershell
# 终端 1：更新 dev 并启动数据库
cd "你的本地项目根目录"

git switch dev
git pull origin dev

docker compose up -d postgres
```

```powershell
# 终端 2：启动后端
conda activate talentflow

cd "你的本地后端文件路径"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```powershell
# 终端 3：启动前端
cd "你的本地前端文件路径"

npm run dev
```

## 开发完成后

```powershell
cd "你的本地项目根目录"

git status
git add .
git commit -m "feat: 本次完成的功能"
git push origin dev
```
# 本地数据库与开发身份

本地 PostgreSQL 容器对宿主机统一暴露 `5433`，后端、Alembic 与
`scripts/seed_dev_data.py` 都读取同一个 `DATABASE_URL`：

```env
DATABASE_URL=postgresql+psycopg://talentflow:talentflow_dev_password_change_me@localhost:5433/talentflow
POSTGRES_PORT=5433
```

未设置 `DATABASE_URL` 时，后端使用 `POSTGRES_HOST`、`POSTGRES_PORT`、
`POSTGRES_USER`、`POSTGRES_PASSWORD`、`POSTGRES_DB` 拼接连接地址。

Vue 开发环境由统一 API 客户端注入当前开发身份。员工工作台默认使用
`zhangwei / EMPLOYEE`，HR 工作台默认使用 `linyuqing / HR_SPECIALIST`；
请求头为 `X-Mock-User-Id` 与 `X-Mock-Role`，服务端会校验 ID 和角色是否匹配。

前端开发服务器默认将 `/api` 和 `/health` 代理到 `http://localhost:8000`，
因此未创建 `frontend/.env.local` 时，`/api/v1` 请求仍可到达 FastAPI。
如设置 `VITE_API_BASE_URL=http://localhost:8000/api/v1`，则浏览器直接访问该地址。
候选人池和面试日历会先检查 `/health`，后端不可用时退出加载状态并提供重新加载入口。
