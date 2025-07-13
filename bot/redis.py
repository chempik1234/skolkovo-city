from redis import Redis


def create_redis(host: str, port: int, db: int, password: str):
    return Redis(host, port, db, password=password)