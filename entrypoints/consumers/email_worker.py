import asyncio
import logging

logger = logging.getLogger(__name__)


async def process_email_queue():
    logger.info("Email worker started")
    while True:
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(process_email_queue())
