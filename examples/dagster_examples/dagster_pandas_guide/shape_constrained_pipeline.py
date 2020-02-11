from datetime import datetime

from dagster_pandas import (
    PandasColumn,
    RowCountConstraint,
    StrictColumnsConstraint,
    create_dagster_pandas_dataframe_type,
)
from pandas import DataFrame, read_csv

from dagster import OutputDefinition, pipeline, solid
from dagster.utils import script_relative_path

ShapeConstrainedTripDataFrame = create_dagster_pandas_dataframe_type(
    name='ShapeConstrainedTripDataFrame',
    columns=[
        PandasColumn.integer_column('bike_id', min_value=0),
        PandasColumn.categorical_column('color', categories={'red', 'green', 'blue'}),
        PandasColumn.datetime_column(
            'start_time', min_datetime=datetime(year=2020, month=2, day=10)
        ),
        PandasColumn.datetime_column('end_time', min_datetime=datetime(year=2020, month=2, day=10)),
        PandasColumn.string_column('station'),
        PandasColumn.exists('amount_paid'),
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
    output_defs=[
        OutputDefinition(
            name='shape_constrained_trip_dataframe', dagster_type=ShapeConstrainedTripDataFrame
        )
    ],
)
def load_shape_constrained_trip_dataframe(_) -> DataFrame:
    return read_csv(
        script_relative_path('./ebike_trips.csv'),
        parse_dates=['start_time', 'end_time'],
        date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'),
    )


@pipeline
def shape_constrained_pipeline():
    load_shape_constrained_trip_dataframe()
