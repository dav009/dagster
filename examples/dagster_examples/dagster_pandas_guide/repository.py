from dagster import RepositoryDefinition

from .categorical_column_constraint_pipeline import categorical_pipeline
from .schema_validated_pipeline import schema_validated_pipeline
from .shape_constrained_pipeline import shape_constrained_pipeline
from .simple_pipeline import simple_pipeline
from .sugar_pipeline import sugar_pipeline


def define_repo():
    return RepositoryDefinition(
        name='dagster_pandas_guide_examples',
        pipeline_dict={
            'categorical_pipeline': lambda: categorical_pipeline,
            'schema_validated_pipeline': lambda: schema_validated_pipeline,
            'shape_constrained_pipeline': lambda: shape_constrained_pipeline,
            'simple_pipeline': lambda: simple_pipeline,
            'sugar_pipeline': lambda: sugar_pipeline,
        },
    )
