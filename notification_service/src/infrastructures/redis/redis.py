from redis.asyncio import Redis

decoded_connection = Redis(decode_responses=True)
