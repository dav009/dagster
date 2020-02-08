from datetime import datetime, timedelta

from dagster_pandas import (
    PandasColumn,
    RowCountConstraint,
    StrictColumnsConstraint,
    create_dagster_pandas_dataframe_type,
)
from pandas import DataFrame

from dagster import OutputDefinition, pipeline, solid

NOW = datetime.now()


ShapeConstrainedTripDataFrame = create_dagster_pandas_dataframe_type(
    name='ShapeConstrainedTripDataFrame',
    columns=[
        PandasColumn.integer_column('bike_id', min_value=0),
        PandasColumn.categorical_column('color', categories={'red', 'green', 'blue'}),
        PandasColumn.datetime_column('start_time', min_datetime=NOW),
        PandasColumn.datetime_column('end_time', min_datetime=NOW),
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
def shape_constrained_pipeline():
    load_shape_constrained_trip_dataframe()
