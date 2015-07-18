class UGARouter(object):

    def db_for_read(self, model, **hints):
        database = getattr(model, "__database__", None)
        return database

    def db_for_write(self, model, **hints):
        database = getattr(model, "__database__", None)
        return database

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are only allowed if both objects are
        in the same database
        """
        if obj1._state.db == obj2._state.db:
            return True
        return None

    def allow_migrate(self, db, model):
        """
        All non-auth models end up in this pool.
        """
        return db=="default"
