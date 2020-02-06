from datetime import datetime

from dagster_pandas import (
    RowCountConstraint,
    StrictColumnsConstraint,
    create_dagster_pandas_dataframe_type,
)
from pandas import DataFrame

from dagster import EventMetadataEntry, OutputDefinition, pipeline, solid


def compute_trip_dataframe_summary_statistics(dataframe):
    return [
        EventMetadataEntry.text(
            datetime.fromtimestamp(min(dataframe['start_time'])).strftime('%Y-%m-%d'),
            'min_start_time',
            'Date data collection started',
        ),
        EventMetadataEntry.text(
            datetime.fromtimestamp(max(dataframe['end_time'])).strftime('%Y-%m-%d'),
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


ShapeConstrainedTripDataFrame = create_dagster_pandas_dataframe_type(
    name='ShapeConstrainedTripDataFrame',
    event_metadata_fn=compute_trip_dataframe_summary_statistics,
    dataframe_constraints=[
        RowCountConstraint(4),
        StrictColumnsConstraint(['bike_id', 'start_time', 'end_time']),
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
            'start_time': [1580926118, 1580929718, 1580933318, 1580936918],
            'end_time': [1580933318, 1580936918, 1580940518, 1580944118],
        }
    )


@pipeline
def shape_constrained_pipeline():
    load_shape_constrained_trip_dataframe()
