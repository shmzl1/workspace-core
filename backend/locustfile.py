"""
TalentFlow API 压力测试脚本 (Locust)

用法:
    cd backend
    locust -f locustfile.py --host=http://localhost:8000

然后打开浏览器访问 http://localhost:8089 配置并发参数并启动测试。

快速无 UI 模式 (100并发, 60秒):
    locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 60s --csv=locust_report
"""

import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 确保能导入 app 模块 (locust 从 backend/ 目录运行时自动生效)
BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from jose import jwt
from locust import HttpUser, between, task

# ---------------------------------------------------------------------------
# JWT 配置 (与 backend/.env 保持一致)
# ---------------------------------------------------------------------------
JWT_SECRET_KEY = "talentflow_local_dev_jwt_secret_not_for_production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 120

# ---------------------------------------------------------------------------
# 压测专用用户 — 统一使用 HR_SPECIALIST (linyuqing)
#
# 权限从数据库查询, 不是从 JWT 取的。HR_SPECIALIST 拥有最全的权限集:
#   recruitment.read / candidate.read / interview.read / interview.manage
#   policy.read / audit.read / attendance.self.read / payroll.* / employee.*
#
# 这样可以避免 403, 纯粹压测 API 性能。
# ---------------------------------------------------------------------------
TEST_USER = {
    "user_id": 3,
    "username": "linyuqing",
    "role": "HR_SPECIALIST",
}

# ---------------------------------------------------------------------------
# 要压测的端点列表 — (权重, HTTP方法, 路径)
#
# 权重越高被选中的概率越大, 用于模拟真实流量分布。
# 所有端点均确保 HR_SPECIALIST 有权限访问。
# ---------------------------------------------------------------------------
ENDPOINTS = [
    # 高频查询类 — 每个用户登录后最先访问的
    (25, "GET", "/api/v1/auth/me"),
    (20, "GET", "/api/v1/recruitment/jobs"),
    (15, "GET", "/api/v1/recruitment/dashboard"),
    # 中频业务类
    (10, "GET", "/api/v1/recruitment/candidates"),
    (10, "GET", "/api/v1/interviews"),
    # 低频查询类
    (5,  "GET", "/api/v1/policies"),
    (5,  "GET", "/api/v1/audit/logs"),
    (5,  "GET", "/api/v1/employees"),
    (5,  "GET", "/api/v1/recruitment/applications"),
]


def make_token(user: dict) -> str:
    """直接生成 JWT token, 绕过登录接口, 只压测 API 本身。"""
    payload = {
        "sub": user["username"],
        "user_id": user["user_id"],
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


class TalentFlowUser(HttpUser):
    """模拟 HR 用户, 对 TalentFlow API 发起请求。

    所有并发用户共用同一个 HR 身份 (linyuqing),
    避免因权限不足产生 403 噪声, 纯粹测量 API 响应性能。
    """

    # 每个用户请求之间的等待时间 (秒)
    wait_time = between(0.5, 2.0)

    def on_start(self) -> None:
        """用户上线时生成 JWT token(不经过数据库, 无额外开销)。"""
        self.token = make_token(TEST_USER)
        self.client.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "X-Trace-Id": f"locust-linyuqing-{time.monotonic_ns()}",
            }
        )

    @task(50)
    def call_api_endpoint(self):
        """按权重随机选取一个 API 端点进行请求。"""
        total_weight = sum(w for w, _, _ in ENDPOINTS)
        r = random.uniform(0, total_weight)
        cumulative = 0
        for weight, method, path in ENDPOINTS:
            cumulative += weight
            if r <= cumulative:
                break

        with self.client.get(
            path, name=path, catch_response=True
        ) as resp:
            if resp.status_code >= 500:
                resp.failure(f"500: {resp.text[:200]}")
            elif resp.status_code == 403:
                resp.failure(f"403 权限不足 (请确认 {TEST_USER['username']} 拥有此端点权限): {resp.text[:200]}")
            elif resp.status_code == 401:
                resp.failure(f"401 认证失败: {resp.text[:200]}")

    @task(5)
    def health_check(self):
        """健康检查。"""
        with self.client.get("/health", name="/health", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Health check 失败: {resp.status_code}")


# ---------------------------------------------------------------------------
# 单端点极限压测模板 (取消注释后使用, 把上面的 TalentFlowUser 注释掉):
# ---------------------------------------------------------------------------
# class TalentFlowUser(HttpUser):
#     wait_time = between(0.1, 0.3)  # 极短等待, 打满吞吐
#
#     def on_start(self):
#         self.token = make_token(TEST_USER)
#         self.client.headers["Authorization"] = f"Bearer {self.token}"
#
#     @task
#     def get_jobs(self):
#         self.client.get("/api/v1/recruitment/jobs")
