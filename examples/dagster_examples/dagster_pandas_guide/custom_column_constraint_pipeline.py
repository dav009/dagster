from datetime import datetime

from dagster_pandas import PandasColumn, create_dagster_pandas_dataframe_type
from dagster_pandas.constraints import (
    ColumnConstraint,
    ColumnConstraintViolationException,
    ColumnTypeConstraint,
    RowCountConstraint,
    StrictColumnsConstraint,
)
from pandas import DataFrame, read_csv

from dagster import OutputDefinition, pipeline, solid
from dagster.utils import script_relative_path


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
        PandasColumn.datetime_column(
            'start_time', min_datetime=datetime(year=2020, month=2, day=10)
        ),
        PandasColumn.datetime_column('end_time', min_datetime=datetime(year=2020, month=2, day=10)),
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
    return read_csv(
        script_relative_path('./ebike_trips.csv'),
        parse_dates=['start_time', 'end_time'],
        date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'),
    )


@pipeline
def custom_column_constraint_pipeline():
    load_custom_trip_dataframe()
