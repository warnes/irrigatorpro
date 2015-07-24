from django.db                       import connections
from django.db.models.aggregates     import Aggregate
from django.db.models.sql.aggregates import Aggregate as SQLAggregate
from uga.models                      import UGAProbeData

__initialized__ = False

class SimpleAggregate(Aggregate):
    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = SQLAggregate(col, source=source, is_summary=is_summary, **self.extra)
        aggregate.sql_function = self.sql_function
        aggregate.is_ordinal   = getattr(self, 'is_ordinal',  False)
        aggregate.is_computed  = getattr(self, 'is_computed', False)
        if hasattr(self, 'sql_template'):
            aggregate.sql_template = self.sql_template
        query.aggregates[alias] = aggregate


class Date(SimpleAggregate):
    sql_function = 'Date'
    name = 'Date'
