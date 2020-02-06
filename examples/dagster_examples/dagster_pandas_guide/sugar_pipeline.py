from datetime import datetime, timedelta

from dagster_pandas import PandasColumn, create_dagster_pandas_dataframe_type
from dagster_pandas.constraints import RowCountConstraint, StrictColumnsConstraint
from pandas import DataFrame

from dagster import EventMetadataEntry, OutputDefinition, pipeline, solid

NOW = datetime.now()


def compute_trip_dataframe_summary_statistics(dataframe):
    return [
        EventMetadataEntry.text(
            str(dataframe['bike_id'].nunique()),
            'num_unique_bikes',
            'Number of unique bikes that took trips',
        ),
        EventMetadataEntry.text(
            str(len(dataframe)), 'n_rows', 'Number of rows seen in the dataframe'
        ),
        EventMetadataEntry.text(
            str(dataframe.columns), 'columns', 'Keys of columns seen in the dataframe'
        ),
    ]


SugarTripDataFrame = create_dagster_pandas_dataframe_type(
    name='SugarTripDataFrame',
    columns=[
        PandasColumn.integer_column('bike_id', min_value=0),
        PandasColumn.categorical_column('color', categories={'red', 'green', 'blue'}),
        PandasColumn.datetime_column('start_time', min_datetime=NOW),
        PandasColumn.datetime_column('end_time', min_datetime=NOW),
    ],
    dataframe_constraints=[
        RowCountConstraint(4),
        StrictColumnsConstraint(['bike_id', 'color', 'start_time', 'end_time']),
    ],
    event_metadata_fn=compute_trip_dataframe_summary_statistics,
)


@solid(
    output_defs=[OutputDefinition(name='sugar_trip_dataframe', dagster_type=SugarTripDataFrame)],
)
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
        }
    )


@pipeline
def sugar_pipeline():
    load_sugar_trip_dataframe()
