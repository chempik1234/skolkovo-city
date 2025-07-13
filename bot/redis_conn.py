from redis import Redis


def create_redis(host: str, port: int, db: int, password: str) -> Redis:
    return Redis(host, port, db, password=password)


def get_redis_url(user: str, password: str, host: str, port: int, db: int) -> str:
    return f"redis://{user}:{password}@{host}:{port}/{db}"
