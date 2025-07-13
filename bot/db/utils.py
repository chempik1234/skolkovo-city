def get_asyncpg_url(user: str, password: str, host: str, port: int, db: str) -> str:
    return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(user, password, host, port, db)
