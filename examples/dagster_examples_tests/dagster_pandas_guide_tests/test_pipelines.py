import pytest
from dagster_examples.dagster_pandas_guide.categorical_column_constraint_pipeline import (
    categorical_pipeline,
)
from dagster_examples.dagster_pandas_guide.schema_validated_pipeline import (
    schema_validated_pipeline,
)
from dagster_examples.dagster_pandas_guide.shape_constrained_pipeline import (
    shape_constrained_pipeline,
)
from dagster_examples.dagster_pandas_guide.simple_pipeline import simple_pipeline
from dagster_examples.dagster_pandas_guide.sugar_pipeline import sugar_pipeline

from dagster import execute_pipeline


@pytest.mark.parametrize(
    'pipeline',
    [
        categorical_pipeline,
        schema_validated_pipeline,
        shape_constrained_pipeline,
        simple_pipeline,
        sugar_pipeline,
    ],
)
def test_guide_pipelines_success(pipeline):
    pipeline_result = execute_pipeline(pipeline)
    assert pipeline_result.success
