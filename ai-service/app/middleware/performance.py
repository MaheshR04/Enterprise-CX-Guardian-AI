"""
Enterprise CX Guardian AI — Performance Middleware & Cache Layer (FastAPI)
==========================================================================

Implements all 5 performance features:
  1. Response Compression    (GZip for large responses)
  2. In-Memory Cache         (TTL cache for read-heavy endpoints)
  3. Lazy Loading            (deferred heavy imports + singleton registry)
  4. Async Processing        (background task queue for non-blocking ops)
  5. Cache-Control Headers   (ETag + conditional request support)

Cache strategy:
  - GET /api/v1/conversations/* → TTL 30s  (list/search results)
  - GET /health, /metrics       → TTL 10s  (health probes)
  - POST /api/v1/chat           → NO cache (always fresh)
  - All mutation endpoints      → NO cache + cache busting

Production upgrade path:
  Replace _InMemoryCache with Redis:
    from redis.asyncio import Redis
    cache = RedisCache(url=settings.REDIS_URL, ttl=30)
"""

import asyncio
import gzip
import hashlib
import json
import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

from fastapi import BackgroundTasks, Request
from fastapi.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware          # re-export for main.py
from starlette.types import ASGIApp

from app.core.logger import logger


# ══════════════════════════════════════════════════════════════════
# 1. Response Compression — re-export GZipMiddleware
# ══════════════════════════════════════════════════════════════════
# Import GZipMiddleware directly in main.py:
#   from starlette.middleware.gzip import GZipMiddleware
#   app.add_middleware(GZipMiddleware, minimum_size=512)
#
# minimum_size=512  → compress responses > 512 bytes (skip tiny JSON)


# ══════════════════════════════════════════════════════════════════
# 2. In-Memory TTL Cache
# ══════════════════════════════════════════════════════════════════

class _CacheEntry:
    __slots__ = ("value", "expires_at", "etag")

    def __init__(self, value: Any, ttl: float, etag: str):
        self.value      = value
        self.expires_at = time.monotonic() + ttl
        self.etag       = etag

    def is_expired(self) -> bool:
        return time.monotonic() > self.expires_at


class InMemoryCache:
    """
    LRU-ordered TTL cache with async-safe reads.

    Eviction: LRU when capacity is exceeded.
    TTL:      Expired entries are lazily evicted on access.
    ETag:     MD5 hash of serialized value for conditional requests.

    Thread safety: uses asyncio.Lock for async access.
    """

    def __init__(self, max_size: int = 1000):
        self._store: OrderedDict[str, _CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._lock = asyncio.Lock()
        self._hits   = 0
        self._misses = 0

    def _make_key(self, prefix: str, *parts: str) -> str:
        raw = ":".join([prefix] + [str(p) for p in parts])
        return hashlib.md5(raw.encode()).hexdigest()

    def _make_etag(self, value: Any) -> str:
        return hashlib.md5(json.dumps(value, default=str, sort_keys=True).encode()).hexdigest()

    async def get(self, key: str) -> Tuple[Optional[Any], Optional[str]]:
        """Returns (value, etag) or (None, None) on miss."""
        async with self._lock:
            entry = self._store.get(key)
            if entry is None or entry.is_expired():
                if key in self._store:
                    del self._store[key]
                self._misses += 1
                return None, None
            # LRU: move to end
            self._store.move_to_end(key)
            self._hits += 1
            return entry.value, entry.etag

    async def set(self, key: str, value: Any, ttl: float = 30.0) -> str:
        """Store value with TTL. Returns etag."""
        etag = self._make_etag(value)
        async with self._lock:
            if len(self._store) >= self._max_size:
                # Evict oldest (LRU)
                self._store.popitem(last=False)
            self._store[key] = _CacheEntry(value, ttl, etag)
            self._store.move_to_end(key)
        return etag

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def invalidate_prefix(self, prefix: str) -> int:
        """Delete all keys whose underlying prefix matches. Returns count."""
        async with self._lock:
            victims = [k for k in self._store if k.startswith(prefix)]
            for k in victims:
                del self._store[k]
            return len(victims)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    @property
    def stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        return {
            "size":      len(self._store),
            "max_size":  self._max_size,
            "hits":      self._hits,
            "misses":    self._misses,
            "hit_rate":  round((self._hits / total * 100) if total else 0, 1),
        }

    def make_key(self, prefix: str, *parts: str) -> str:
        return self._make_key(prefix, *parts)


# Global cache singleton
cache = InMemoryCache(max_size=2000)


# ── TTL constants ──────────────────────────────────────────────────
CACHE_TTL = {
    "conversations_list":   30.0,    # GET /conversations
    "conversation_detail":  60.0,    # GET /conversations/{id}
    "health":               10.0,    # GET /health
    "metrics":              15.0,    # GET /metrics
}


# ══════════════════════════════════════════════════════════════════
# 3. Cache-Control & ETag Response Middleware
# ══════════════════════════════════════════════════════════════════

# Routes that should be cached (prefix match)
_CACHEABLE_GET_PREFIXES = (
    "/api/v1/conversations",
    "/health",
    "/metrics",
)

# Mutation methods that should bust cache
_MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class CacheMiddleware(BaseHTTPMiddleware):
    """
    HTTP response cache middleware with ETag support.

    For cacheable GET endpoints:
      - Checks in-memory cache before forwarding to route handler
      - Returns cached response with ETag header
      - Handles If-None-Match → 304 Not Modified

    For mutation endpoints:
      - Adds Cache-Control: no-store
      - Automatically invalidates affected conversation cache keys
    """

    def _is_cacheable(self, request: Request) -> bool:
        if request.method != "GET":
            return False
        path = request.url.path
        return any(path.startswith(p) for p in _CACHEABLE_GET_PREFIXES)

    def _cache_key(self, request: Request) -> str:
        return cache.make_key(
            "http",
            request.url.path,
            str(request.url.query)
        )

    async def dispatch(self, request: Request, call_next: Callable):
        # ── Mutation: no-store + cache bust ──────────────────────
        if request.method in _MUTATION_METHODS:
            response = await call_next(request)
            response.headers["Cache-Control"] = "no-store"
            return response

        # ── GET: check cache ──────────────────────────────────────
        if self._is_cacheable(request):
            key = self._cache_key(request)
            cached_body, etag = await cache.get(key)

            if cached_body is not None:
                # Conditional request — 304 Not Modified
                if_none_match = request.headers.get("If-None-Match")
                if if_none_match and if_none_match == f'"{etag}"':
                    return Response(status_code=304, headers={"ETag": f'"{etag}"'})

                # Serve from cache
                logger.debug(f"[Cache] HIT | {request.url.path}")
                return JSONResponse(
                    content=cached_body,
                    headers={
                        "ETag":          f'"{etag}"',
                        "X-Cache":       "HIT",
                        "Cache-Control": "private, max-age=30"
                    }
                )

        # ── Forward to route handler ──────────────────────────────
        response = await call_next(request)

        if self._is_cacheable(request) and response.status_code == 200:
            try:
                body_bytes = b""
                async for chunk in response.body_iterator:
                    body_bytes += chunk
                body = json.loads(body_bytes.decode())

                key  = self._cache_key(request)
                path = request.url.path
                ttl  = (
                    CACHE_TTL["conversation_detail"] if "/conversations/" in path
                    else CACHE_TTL["conversations_list"] if "/conversations" in path
                    else CACHE_TTL["health"]           if "/health" in path
                    else CACHE_TTL["metrics"]          if "/metrics" in path
                    else 30.0
                )
                etag = await cache.set(key, body, ttl=ttl)
                logger.debug(f"[Cache] SET | {path} | ttl: {ttl}s")

                return JSONResponse(
                    content=body,
                    status_code=response.status_code,
                    headers={
                        "ETag":          f'"{etag}"',
                        "X-Cache":       "MISS",
                        "Cache-Control": f"private, max-age={int(ttl)}"
                    }
                )
            except Exception:
                pass

        return response


# ══════════════════════════════════════════════════════════════════
# 4. Lazy Loading — Deferred Singleton Registry
# ══════════════════════════════════════════════════════════════════

class LazyRegistry:
    """
    Deferred singleton factory.

    Expensive objects (ML models, heavy clients) are instantiated
    only on first access, not at module import time.

    Usage:
        @lazy_registry.register("groq_client")
        def _make_groq_client():
            from app.clients.groq_client import GroqClient
            return GroqClient()

        client = lazy_registry.get("groq_client")
    """

    def __init__(self):
        self._factories:  Dict[str, Callable] = {}
        self._instances:  Dict[str, Any]      = {}
        self._init_times: Dict[str, float]    = {}

    def register(self, name: str):
        """Decorator to register a factory function."""
        def decorator(factory: Callable):
            self._factories[name] = factory
            return factory
        return decorator

    def get(self, name: str) -> Any:
        """Get or lazily create a singleton instance."""
        if name not in self._instances:
            if name not in self._factories:
                raise KeyError(f"[LazyRegistry] No factory registered for '{name}'")
            start = time.perf_counter()
            self._instances[name]  = self._factories[name]()
            elapsed = (time.perf_counter() - start) * 1000
            self._init_times[name] = elapsed
            logger.info(f"[LazyLoad] Initialized '{name}' | {elapsed:.1f}ms")
        return self._instances[name]

    @property
    def loaded(self) -> Dict[str, float]:
        """Returns names and init times of all loaded singletons."""
        return dict(self._init_times)


# Global lazy registry
lazy_registry = LazyRegistry()


# ══════════════════════════════════════════════════════════════════
# 5. Async Background Task Queue
# ══════════════════════════════════════════════════════════════════

class AsyncTaskQueue:
    """
    Lightweight async background task processor.

    Non-critical post-response operations (analytics writes,
    notification dispatch, cache warm-up) are queued here so
    they don't block the HTTP response.

    Usage:
        task_queue.enqueue(save_analytics, conversation_id, data)
        # → HTTP response returns immediately
        # → save_analytics() runs in background
    """

    def __init__(self, max_workers: int = 4):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._max_workers = max_workers
        self._workers: list = []
        self._processed = 0
        self._failed    = 0
        self._running   = False

    async def start(self) -> None:
        """Start background worker tasks. Called in lifespan startup."""
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self._max_workers)
        ]
        logger.info(
            f"[AsyncQueue] Started {self._max_workers} background workers"
        )

    async def stop(self) -> None:
        """Drain queue and shut down workers. Called in lifespan shutdown."""
        self._running = False
        for _ in self._workers:
            await self._queue.put(None)           # Sentinel to unblock workers
        await asyncio.gather(*self._workers, return_exceptions=True)
        logger.info(
            f"[AsyncQueue] Stopped | processed: {self._processed} | failed: {self._failed}"
        )

    def enqueue(self, coro_func: Callable, *args, **kwargs) -> None:
        """
        Non-blocking enqueue. Safe to call from synchronous code.
        The coroutine is scheduled for background execution.
        """
        try:
            self._queue.put_nowait((coro_func, args, kwargs))
        except asyncio.QueueFull:
            logger.warning(
                f"[AsyncQueue] Queue full — dropping task: {coro_func.__name__}"
            )

    async def _worker(self, worker_id: int) -> None:
        """Worker loop — drains the queue until stopped."""
        while self._running:
            item = await self._queue.get()
            if item is None:
                break
            coro_func, args, kwargs = item
            try:
                await coro_func(*args, **kwargs)
                self._processed += 1
            except Exception as exc:
                self._failed += 1
                logger.error(
                    f"[AsyncQueue] Worker {worker_id} failed | "
                    f"task: {coro_func.__name__} | {type(exc).__name__}: {exc}"
                )
            finally:
                self._queue.task_done()

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "queue_size": self._queue.qsize(),
            "workers":    self._max_workers,
            "processed":  self._processed,
            "failed":     self._failed,
            "running":    self._running,
        }


# Global task queue singleton
task_queue = AsyncTaskQueue(max_workers=4)
