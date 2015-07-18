from django.test.runner import DiscoverRunner
from django.conf import settings
from uga.models import UGAProbeData


class ManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run, so that one doesn't need
    to execute the SQL manually to create them.
    """
    def setup_test_environment(self, *args, **kwargs):
        from django.db.models.loading import get_models

        ## Make all Models managed, so they'll be created in the test
        ## database 
        self.unmanaged_models = [m for m in get_models()
                                 if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True

        ## Change the table name for UGAProbeData to something django
        ## can create, storing the old value
        UGAProbeData._meta.__db_table_stored = UGAProbeData._meta.db_table
        del UGAProbeData._meta.db_table

        ## Go do the tests...
        super(DiscoverRunner, self).setup_test_environment(*args,
                                                            **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(DiscoverRunner, self).teardown_test_environment(*args,
                                                               **kwargs)


        UGAProbeData._meta.db_table = UGAProbeData._meta.__db_table_stored
        del UGAProbeData._meta.db_table_stored

        ## Reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False
