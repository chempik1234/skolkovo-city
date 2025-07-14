from db.models import UserDataModel


class UserRepositoryBase:
    async def get_object(self, **kwargs) -> UserDataModel | None:
        raise NotImplementedError()

    async def update_data(self, existing_object, data_dict) -> None:
        raise NotImplementedError()

    async def create_object(self, data_dict) -> UserDataModel:
        raise NotImplementedError()
