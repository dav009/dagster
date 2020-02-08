from datetime import datetime, timedelta

from dagster_pandas import PandasColumn, create_dagster_pandas_dataframe_type
from dagster_pandas.constraints import (
    ColumnConstraint,
    ColumnConstraintViolationException,
    ColumnTypeConstraint,
    RowCountConstraint,
    StrictColumnsConstraint,
)
from pandas import DataFrame

from dagster import OutputDefinition, pipeline, solid

NOW = datetime.now()


class DivisibleByFiveConstraint(ColumnConstraint):
    def __init__(self):
        message = "Value must be divisible by 5"
        super(DivisibleByFiveConstraint, self).__init__(
            error_description=message, markdown_description=message
        )

    def validate(self, dataframe, column_name):
        rows_with_unexpected_buckets = dataframe[dataframe[column_name].apply(lambda x: x % 5 != 0)]
        if not rows_with_unexpected_buckets.empty:
            raise ColumnConstraintViolationException(
                constraint_name=self.name,
                constraint_description=self.error_description,
                column_name=column_name,
                offending_rows=rows_with_unexpected_buckets,
            )


CustomTripDataFrame = create_dagster_pandas_dataframe_type(
    name='CustomTripDataFrame',
    columns=[
        PandasColumn.integer_column('bike_id', min_value=0),
        PandasColumn.categorical_column('color', categories={'red', 'green', 'blue'}),
        PandasColumn.datetime_column('start_time', min_datetime=NOW),
        PandasColumn.datetime_column('end_time', min_datetime=NOW),
        PandasColumn.string_column('station'),
        PandasColumn(
            'amount_paid', constraints=[ColumnTypeConstraint('int64'), DivisibleByFiveConstraint()]
        ),
        PandasColumn.boolean_column('was_member'),
    ],
    dataframe_constraints=[
        RowCountConstraint(4),
        StrictColumnsConstraint(
            ['bike_id', 'color', 'start_time', 'end_time', 'station', 'amount_paid', 'was_member']
        ),
    ],
)


@solid(
    output_defs=[OutputDefinition(name='custom_trip_dataframe', dagster_type=CustomTripDataFrame)],
)
def load_custom_trip_dataframe(_) -> DataFrame:
    return DataFrame(
        {
            'bike_id': [1, 2, 3, 1],
            'color': ['red', 'green', 'blue', 'red'],
            'start_time': [
                NOW,
                NOW + timedelta(hours=1),
                NOW + timedelta(hours=5, days=2),
                NOW + timedelta(hours=3),
            ],
            'end_time': [
                NOW + timedelta(hours=1),
                NOW + timedelta(hours=2),
                NOW + timedelta(hours=7, days=2),
                NOW + timedelta(hours=4),
            ],
            'station': ['civic center', 'montgomery', 'civic center', 'mission'],
            'amount_paid': [20, 10, 5, 0],
            'was_member': [True, False, False, False],
        }
    )


@pipeline
def custom_column_constraint_pipeline():
    load_custom_trip_dataframe()
