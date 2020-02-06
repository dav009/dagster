from datetime import datetime

from dagster_pandas import PandasColumn, create_dagster_pandas_dataframe_type
from dagster_pandas.constraints import (
    ColumnConstraint,
    ColumnConstraintViolationException,
    ColumnTypeConstraint,
    RowCountConstraint,
    StrictColumnsConstraint,
)
from pandas import DataFrame

from dagster import EventMetadataEntry, OutputDefinition, pipeline, solid


class CategoricalColumnConstraint(ColumnConstraint):
    def __init__(self, categories):
        self.categories = categories
        super(CategoricalColumnConstraint, self).__init__(
            error_description="Expected Categories are {}".format(self.categories),
            markdown_description="Category examples are {}...".format(self.categories),
        )

    def validate(self, dataframe, column_name):
        rows_with_unexpected_buckets = dataframe[~dataframe[column_name].isin(self.categories)]
        if not rows_with_unexpected_buckets.empty:
            raise ColumnConstraintViolationException(
                constraint_name=self.name,
                constraint_description=self.error_description,
                column_name=column_name,
                offending_rows=rows_with_unexpected_buckets,
            )


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


CategoricalTripDataFrame = create_dagster_pandas_dataframe_type(
    name='CategoricalTripDataFrame',
    columns=[
        PandasColumn('bike_id', constraints=[ColumnTypeConstraint('int64')]),
        PandasColumn(
            'color',
            constraints=[
                ColumnTypeConstraint('object'),
                CategoricalColumnConstraint({'red', 'green', 'blue'}),
            ],
        ),
        PandasColumn('start_time', constraints=[ColumnTypeConstraint('int64')]),
        PandasColumn('end_time', constraints=[ColumnTypeConstraint('int64')]),
    ],
    dataframe_constraints=[
        RowCountConstraint(4),
        StrictColumnsConstraint(['bike_id', 'color', 'start_time', 'end_time']),
    ],
    event_metadata_fn=compute_trip_dataframe_summary_statistics,
)


@solid(
    output_defs=[
        OutputDefinition(name='categorical_trip_dataframe', dagster_type=CategoricalTripDataFrame)
    ],
)
def load_categorical_trip_dataframe(_) -> DataFrame:
    return DataFrame(
        {
            'bike_id': [1, 2, 3, 1],
            'color': ['red', 'green', 'blue', 'red'],
            'start_time': [1580926118, 1580929718, 1580933318, 1580936918],
            'end_time': [1580933318, 1580936918, 1580940518, 1580944118],
        }
    )


@pipeline
def categorical_pipeline():
    load_categorical_trip_dataframe()
