from typing import cast

from redis.asyncio import Redis


class RedisCacheService:
    def __init__(self, redis_url: str) -> None:
        self._redis: Redis | None = None
        self._redis_url = redis_url

    async def get(self, key: str) -> str | None:
        if not self._redis:
            return None
        return cast(str | None, await self._redis.get(key))

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        if not self._redis:
            return None
        await self._redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        if not self._redis:
            return None
        await self._redis.delete(key)

    async def connect(self) -> None:
        self._redis = await Redis.from_url(self._redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None
