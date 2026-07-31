"""
Health check script for Docker containers.
Usage: python healthcheck.py
"""

import asyncio
import os
import sys

import asyncpg


async def check_postgres() -> bool:
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://smartbcchopp:password@localhost:5432/smartbcchopp",
    )
    # Convert SQLAlchemy URL to asyncpg DSN
    dsn = url.replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncpg.connect(dsn, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


async def check_redis() -> bool:
    import asyncio

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("redis", 6379), timeout=2
        )
        writer.write(b"PING\r\n")
        data = await asyncio.wait_for(reader.read(1024), timeout=2)
        writer.close()
        return data.startswith(b"+PONG")
    except Exception:
        return False


async def main() -> None:
    check = sys.argv[1] if len(sys.argv) > 1 else "postgres"

    if check == "postgres":
        ok = await check_postgres()
    elif check == "redis":
        ok = await check_redis()
    else:
        print(f"Unknown check: {check}")
        sys.exit(1)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
