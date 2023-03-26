from factory import Factory


class BaseFactory(Factory):
    pass


class BaseDbFactory(Factory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        async def create_db():
            return await model_class(*args, **kwargs).insert()

        return create_db()
