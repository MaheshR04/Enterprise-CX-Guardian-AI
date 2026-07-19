"""
Enterprise CX Guardian AI — In-Memory Metrics Engine.

Tracks application telemetry without external dependencies:
  - Request counts (total, per route, per status code)
  - Error counts (4xx, 5xx, by error_code)
  - Latency histogram (p50, p90, p99, avg, max)
  - Active connections gauge
  - System information (CPU, memory, uptime)

Thread-safe using asyncio.Lock for concurrent async access.
Cleared on application restart (stateless — use Prometheus/InfluxDB
for persistent metrics in production).
"""

import time
import platform
import statistics
import asyncio
from collections import defaultdict, deque
from typing import Dict, Any, List, Optional

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

# ── Boot timestamp ─────────────────────────────────────────────────
_BOOT_TIME: float = time.time()


def _uptime_seconds() -> float:
    return time.time() - _BOOT_TIME


def _format_uptime(seconds: float) -> str:
    s = int(seconds)
    days, rem   = divmod(s, 86400)
    hours, rem  = divmod(rem, 3600)
    mins, secs  = divmod(rem, 60)
    parts = []
    if days:  parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if mins:  parts.append(f"{mins}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


# ══════════════════════════════════════════════════════════════════
# MetricsCollector
# ══════════════════════════════════════════════════════════════════

class MetricsCollector:
    """
    In-process telemetry store.

    Designed to be updated from FastAPI middleware on every request
    and read from the /metrics and /health endpoints.
    """

    def __init__(self, latency_window: int = 1000):
        self._lock = asyncio.Lock()

        # ── Request counters ───────────────────────────────────────
        self.total_requests:   int = 0
        self.active_requests:  int = 0          # gauge: in-flight
        self.total_errors:     int = 0          # 4xx + 5xx

        self.requests_by_method: Dict[str, int] = defaultdict(int)
        self.requests_by_status: Dict[int, int]  = defaultdict(int)
        self.requests_by_route:  Dict[str, int]  = defaultdict(int)

        self.errors_by_code:     Dict[str, int]  = defaultdict(int)
        self.errors_4xx:         int = 0
        self.errors_5xx:         int = 0

        # ── Latency ring-buffer (rolling window) ───────────────────
        self._latency_window: int = latency_window
        self._latencies: deque = deque(maxlen=latency_window)  # ms floats

        self.total_latency_ms:   float = 0.0
        self.max_latency_ms:     float = 0.0
        self.min_latency_ms:     float = float("inf")

        # ── Route-level latency ────────────────────────────────────
        self._route_latencies: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )

    # ── Write API ──────────────────────────────────────────────────

    async def record_request_start(self) -> None:
        async with self._lock:
            self.total_requests  += 1
            self.active_requests += 1

    async def record_request_end(
        self,
        method: str,
        route: str,
        status_code: int,
        latency_ms: float
    ) -> None:
        async with self._lock:
            self.active_requests = max(0, self.active_requests - 1)

            # Counters
            self.requests_by_method[method.upper()] += 1
            self.requests_by_status[status_code]    += 1
            self.requests_by_route[route]           += 1

            # Errors
            if status_code >= 400:
                self.total_errors += 1
            if 400 <= status_code < 500:
                self.errors_4xx += 1
            if status_code >= 500:
                self.errors_5xx += 1

            # Latency
            self._latencies.append(latency_ms)
            self._route_latencies[route].append(latency_ms)
            self.total_latency_ms += latency_ms
            if latency_ms > self.max_latency_ms:
                self.max_latency_ms = latency_ms
            if latency_ms < self.min_latency_ms:
                self.min_latency_ms = latency_ms

    async def record_error(self, error_code: str) -> None:
        async with self._lock:
            self.errors_by_code[error_code] += 1

    # ── Read API ───────────────────────────────────────────────────

    def _percentile(self, data: List[float], p: float) -> float:
        if not data:
            return 0.0
        sorted_data = sorted(data)
        idx = max(0, int(len(sorted_data) * p / 100) - 1)
        return round(sorted_data[idx], 2)

    def _latency_stats(self, samples: List[float]) -> Dict[str, float]:
        if not samples:
            return {"p50": 0, "p90": 0, "p99": 0, "avg": 0, "max": 0, "min": 0}
        return {
            "p50": self._percentile(samples, 50),
            "p90": self._percentile(samples, 90),
            "p99": self._percentile(samples, 99),
            "avg": round(statistics.mean(samples), 2),
            "max": round(max(samples), 2),
            "min": round(min(samples), 2),
        }

    async def get_request_metrics(self) -> Dict[str, Any]:
        async with self._lock:
            latency_samples = list(self._latencies)
            avg = (
                self.total_latency_ms / self.total_requests
                if self.total_requests else 0
            )
            return {
                "total_requests":       self.total_requests,
                "active_requests":      self.active_requests,
                "total_errors":         self.total_errors,
                "error_rate_pct":       round(
                    (self.total_errors / self.total_requests * 100)
                    if self.total_requests else 0, 2
                ),
                "errors_4xx":           self.errors_4xx,
                "errors_5xx":           self.errors_5xx,
                "requests_by_method":   dict(self.requests_by_method),
                "requests_by_status":   {
                    str(k): v for k, v in self.requests_by_status.items()
                },
                "top_routes":           dict(
                    sorted(self.requests_by_route.items(),
                           key=lambda x: x[1], reverse=True)[:10]
                ),
                "errors_by_code":       dict(self.errors_by_code),
            }

    async def get_latency_metrics(self) -> Dict[str, Any]:
        async with self._lock:
            samples = list(self._latencies)
            stats   = self._latency_stats(samples)
            route_stats = {}
            for route, deq in self._route_latencies.items():
                route_stats[route] = self._latency_stats(list(deq))
            return {
                "sample_count":   len(samples),
                "window_size":    self._latency_window,
                "global_ms":      stats,
                "by_route_ms":    dict(
                    sorted(route_stats.items(),
                           key=lambda x: x[1].get("avg", 0), reverse=True)[:10]
                ),
            }

    async def get_system_info(self) -> Dict[str, Any]:
        """Returns host system telemetry (requires psutil for full data)."""
        info: Dict[str, Any] = {
            "platform":        platform.system(),
            "platform_release": platform.release(),
            "architecture":    platform.machine(),
            "python_version":  platform.python_version(),
            "uptime_seconds":  round(_uptime_seconds(), 1),
            "uptime_human":    _format_uptime(_uptime_seconds()),
        }

        if _PSUTIL_AVAILABLE:
            try:
                proc = psutil.Process()
                mem  = psutil.virtual_memory()
                info.update({
                    "cpu_count":           psutil.cpu_count(logical=True),
                    "cpu_percent":         psutil.cpu_percent(interval=0.1),
                    "memory_total_mb":     round(mem.total / 1024 / 1024, 1),
                    "memory_used_mb":      round(mem.used  / 1024 / 1024, 1),
                    "memory_percent":      mem.percent,
                    "process_rss_mb":      round(proc.memory_info().rss / 1024 / 1024, 1),
                    "process_threads":     proc.num_threads(),
                    "process_open_files":  len(proc.open_files()),
                })
            except Exception:
                info["psutil_error"] = "Could not read process info"
        else:
            info["psutil_available"] = False

        return info


# ── Global singleton ───────────────────────────────────────────────
metrics = MetricsCollector()
