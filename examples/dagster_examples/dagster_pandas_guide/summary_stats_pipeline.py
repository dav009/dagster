from datetime import datetime

from dagster_pandas import PandasColumn, create_dagster_pandas_dataframe_type
from pandas import DataFrame, read_csv

from dagster import EventMetadataEntry, OutputDefinition, pipeline, solid
from dagster.utils import script_relative_path


def compute_trip_dataframe_summary_statistics(dataframe):
    return [
        EventMetadataEntry.text(
            min(dataframe['start_time']).strftime('%Y-%m-%d'),
            'min_start_time',
            'Date data collection started',
        ),
        EventMetadataEntry.text(
            max(dataframe['end_time']).strftime('%Y-%m-%d'),
            'max_end_time',
            'Date data collection ended',
        ),
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


SummaryStatsTripDataFrame = create_dagster_pandas_dataframe_type(
    name='SummaryStatsTripDataFrame',
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
    event_metadata_fn=compute_trip_dataframe_summary_statistics,
)


@solid(
    output_defs=[
        OutputDefinition(
            name='summary_stats_trip_dataframe', dagster_type=SummaryStatsTripDataFrame
        )
    ],
)
def load_summary_stats_trip_dataframe(_) -> DataFrame:
    return read_csv(
        script_relative_path('./ebike_trips.csv'),
        parse_dates=['start_time', 'end_time'],
        date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'),
    )


@pipeline
def summary_stats_pipeline():
    load_summary_stats_trip_dataframe()
