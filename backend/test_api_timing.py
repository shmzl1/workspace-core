"""
API 响应时间测试工具
用法：
    python test_api_timing.py              # 测试所有接口
    python test_api_timing.py --rounds 5   # 每个接口测 5 轮取平均
    python test_api_timing.py --endpoint /api/v1/recruitment/jobs  # 单接口
"""
import time
import sys
import argparse
import httpx

# ═══════════════════════════════════════
# 配置：从登录接口获取你的 Token 填在这里
# ═══════════════════════════════════════
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ6aGFuZ3dlaSIsInVzZXJfaWQiOjEsInJvbGUiOiJFTVBMT1lFRSIsImV4cCI6MTc4NDAyMTU4MX0.iI6nQNJIzwM9cuxrAQo-LLOCz4igX5mlKqxGuZueL_E"
BASE_URL = "http://localhost:8000"

# 需要在请求体中带数据的接口
BODIED_ENDPOINTS: dict[str, tuple[str, dict]] = {
    "/api/v1/auth/login": ("POST", {
        "username": "zhangwei", "password": "password"
    }),
    "/api/v1/attendance/check-in": ("POST", {}),
    "/api/v1/attendance/check-out": ("POST", {}),
}

# ═══════════════════════════════════════
# 颜色输出（Windows 10+ 支持 ANSI）
# ═══════════════════════════════════════
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def time_request(
    client: httpx.Client,
    method: str,
    path: str,
    body: dict | None = None,
) -> tuple[int, float]:
    """执行一次请求，返回 (状态码, 毫秒数)"""
    headers = {}
    if TOKEN and "login" not in path:
        headers["Authorization"] = f"Bearer {TOKEN}"

    start = time.perf_counter()
    resp = client.request(
        method, f"{BASE_URL}{path}",
        json=body,
        headers=headers,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    return resp.status_code, elapsed_ms


def color_ms(ms: float) -> str:
    if ms < 100:
        return f"{GREEN}{ms:8.2f}ms{RESET}"
    elif ms < 500:
        return f"{YELLOW}{ms:8.2f}ms{RESET}"
    else:
        return f"{RED}{ms:8.2f}ms{RESET}"


def color_status(code: int) -> str:
    if 200 <= code < 300:
        return f"{GREEN}{code}{RESET}"
    elif 300 <= code < 500:
        return f"{YELLOW}{code}{RESET}"
    else:
        return f"{RED}{code}{RESET}"


def test_single(path: str, method: str = "GET", body: dict | None = None, rounds: int = 1):
    """测试单个接口"""
    times_ms: list[float] = []
    status = 0

    with httpx.Client(timeout=30) as client:
        for i in range(rounds):
            code, ms = time_request(client, method, path, body)
            status = code
            times_ms.append(ms)
            if rounds > 1:
                bar = "█" * (i + 1) + "░" * (rounds - i - 1)
                print(f"  [{bar}]  第 {i+1}/{rounds} 轮  {color_ms(ms)}  (HTTP {color_status(code)})", end="\r")
                sys.stdout.flush()

    avg = sum(times_ms) / len(times_ms)
    mn = min(times_ms)
    mx = max(times_ms)

    if rounds > 1:
        print(" " * 70, end="\r")  # 清除进度条

    status_str = color_status(status)
    avg_str = color_ms(avg)
    print(f"  {method:6s} {path:42s}  HTTP {status_str}  avg={avg_str}  min={mn:.2f}ms  max={mx:.2f}ms  (n={rounds})")

    return avg


def test_all_endpoints(rounds: int = 1):
    """测试一批接口"""
    # 无需认证的接口
    public_endpoints = [
        ("GET", "/api/v1/health"),
        ("GET", "/api/v1/policies"),
    ]

    # 需要认证的接口（基于 zhangwei/EMPLOYEE 的权限）
    auth_endpoints = [
        ("GET",  "/api/v1/employees/me"),
        ("GET",  "/api/v1/attendance/today"),
        ("GET",  "/api/v1/attendance/weekly"),
        ("GET",  "/api/v1/attendance/monthly-summary?year=2026&month=7"),
        ("GET",  "/api/v1/payroll/my"),
        ("GET",  "/api/v1/recruitment/jobs"),
        ("GET",  "/api/v1/recruitment/candidates"),
        ("GET",  "/api/v1/interviews"),
    ]

    print(f"\n{CYAN}{'═' * 80}{RESET}")
    print(f"{BOLD}  TalentFlow API 响应时间测试{RESET}")
    print(f"  服务地址: {BASE_URL}")
    print(f"  测试轮次: {rounds}")
    print(f"{CYAN}{'═' * 80}{RESET}\n")

    all_times: list[float] = []

    # 1. 公开接口
    print(f"{BOLD}  📡 公开接口{RESET}")
    for method, path in public_endpoints:
        avg = test_single(path, method, rounds=rounds)
        all_times.append(avg)

    # 2. 登录接口
    print(f"\n{BOLD}  🔐 认证接口（Token: zhangwei / EMPLOYEE）{RESET}")
    for path, (method, body) in BODIED_ENDPOINTS.items():
        if "login" in path:
            avg = test_single(path, method, body=body, rounds=rounds)
            all_times.append(avg)

    # 3. 业务接口
    for method, path in auth_endpoints:
        avg = test_single(path, method, rounds=rounds)
        all_times.append(avg)

    # 总结
    if all_times:
        avg_all = sum(all_times) / len(all_times)
        mn_all = min(all_times)
        mx_all = max(all_times)
        print(f"\n{CYAN}{'─' * 80}{RESET}")
        print(f"{BOLD}  📊 汇总统计{RESET}")
        print(f"  共测试 {len(all_times)} 个接口")
        print(f"  平均响应: {color_ms(avg_all)}")
        print(f"  最快: {color_ms(mn_all)}")
        print(f"  最慢: {color_ms(mx_all)}")
        print(f"{CYAN}{'─' * 80}{RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="TalentFlow API 响应时间测试")
    parser.add_argument("--rounds", "-n", type=int, default=1,
                        help="每个接口测试轮数（取平均值），默认 1")
    parser.add_argument("--endpoint", "-e", type=str, default=None,
                        help="仅测试指定接口，如: /api/v1/recruitment/jobs")
    parser.add_argument("--method", "-m", type=str, default="GET",
                        help="HTTP 方法，默认 GET")
    parser.add_argument("--token", "-t", type=str, default=None,
                        help="JWT Token（覆盖脚本内置的 TOKEN）")
    args = parser.parse_args()

    global TOKEN
    if args.token:
        TOKEN = args.token

    if args.endpoint:
        # 单接口模式
        body = None
        if args.endpoint in BODIED_ENDPOINTS:
            _, body = BODIED_ENDPOINTS[args.endpoint]
        print(f"\n{CYAN}🔍 单接口测试{RESET}\n")
        test_single(args.endpoint, args.method, body=body, rounds=args.rounds)
    else:
        # 全量测试模式
        test_all_endpoints(args.rounds)


if __name__ == "__main__":
    main()
