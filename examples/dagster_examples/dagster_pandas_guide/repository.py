from dagster import RepositoryDefinition

from .custom_column_constraint_pipeline import custom_column_constraint_pipeline
from .shape_constrained_pipeline import shape_constrained_pipeline
from .sugar_pipeline import sugar_pipeline
from .summary_stats_pipeline import summary_stats_pipeline


def define_repo():
    return RepositoryDefinition(
        name='dagster_pandas_guide_examples',
        pipeline_dict={
            'custom_column_constraint_pipeline': lambda: custom_column_constraint_pipeline,
            'shape_constrained_pipeline': lambda: shape_constrained_pipeline,
            'summary_stats_pipeline': lambda: summary_stats_pipeline,
            'sugar_pipeline': lambda: sugar_pipeline,
        },
    )
