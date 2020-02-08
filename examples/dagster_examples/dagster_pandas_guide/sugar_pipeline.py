from datetime import datetime, timedelta

from dagster_pandas import PandasColumn, create_dagster_pandas_dataframe_type
from numpy import nan
from pandas import DataFrame

from dagster import OutputDefinition, pipeline, solid

NOW = datetime.now()


TripDataFrame = create_dagster_pandas_dataframe_type(
    name='TripDataFrame',
    columns=[
        PandasColumn.integer_column('bike_id', min_value=0),
        PandasColumn.categorical_column('color', categories={'red', 'green', 'blue'}),
        PandasColumn.datetime_column('start_time', min_datetime=NOW),
        PandasColumn.datetime_column('end_time', min_datetime=NOW),
        PandasColumn.string_column('station'),
        PandasColumn.exists('amount_paid'),
        PandasColumn.boolean_column('was_member'),
    ],
)


@solid(output_defs=[OutputDefinition(name='trip_dataframe', dagster_type=TripDataFrame)],)
def load_sugar_trip_dataframe(_) -> DataFrame:
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
            'amount_paid': [20, None, 0.0, nan],
            'was_member': [True, False, False, False],
        }
    )


@pipeline
def sugar_pipeline():
    load_sugar_trip_dataframe()
