from db.models import UserDataModel


class UserCacheRepositoryBase:
    def get_object(self, telegram_id: int | str) -> UserDataModel | None:
        raise NotImplementedError()

    def invalidate_object(self, telegram_id: int | str) -> None:
        raise NotImplementedError()

    def cache_object(self, user: UserDataModel) -> None:
        raise NotImplementedError()
