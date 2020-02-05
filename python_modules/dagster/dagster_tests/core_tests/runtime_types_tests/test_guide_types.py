from dagster import DagsterType, execute_solid, solid


def test_even_int():
    EvenDagsterType = DagsterType(
        name='EvenDagsterType',
        type_check_fn=lambda value: isinstance(value, int) and value % 2 is 0,
    )

    @solid
    def return_even_pass(_, num: int) -> EvenDagsterType:
        return num

    assert execute_solid(return_even_pass, input_values={'num': 2}).success

    assert not execute_solid(
        return_even_pass, input_values={'num': 1}, raise_on_error=False
    ).success
