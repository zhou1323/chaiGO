import sys

from app.core.config import settings
from redis.asyncio.client import Redis
from redis.exceptions import AuthenticationError, TimeoutError


class RedisClient(Redis):
    def __init__(self):
        super(RedisClient, self).__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            decode_responses=True,  # decode utf-8
        )

    async def open(self):
        try:
            await self.ping()
        except TimeoutError:
            sys.exit()
        except AuthenticationError:
            sys.exit()
        except Exception as e:
            sys.exit()

    async def delete_prefix(self, prefix: str, exclude: str | list = None):
        """
        remove all keys with same prefix

        :param prefix:
        :param exclude:
        :return:
        """
        keys = []
        async for key in self.scan_iter(match=f"{prefix}*"):
            if isinstance(exclude, str):
                if key != exclude:
                    keys.append(key)
            elif isinstance(exclude, list):
                if key not in exclude:
                    keys.append(key)
            else:
                keys.append(key)
        for key in keys:
            await self.delete(key)


redis_client = RedisClient()
