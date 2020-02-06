Validating Pandas DataFrames with Dagster Types
------------------------------------------------

   * :ref:`Dagster DataFrame Level Validation <dataframe_level_validation>`
   * :ref:`Dagster DataFrame Schema Validation <schema_validation>`
   * :ref:`Dagster DataFrame Bespoke Validation <bespoke_validation>`
   * :ref:`Validation Sugar <validation_synctactic_sugar>`

The dagster type system can be extended to support a ton of validation needs. Since many pipelines perform 
transformations on pandas dataframes, we built a pandas integration that extends the dagster type system to
easily express constraints on your dataframes so that your pipelines are robust to data changes and transformation 
errors.

Our dagster-pandas integration provides an API for creating custom dataframe types that perform schema validation, 
data quality checks, emit summary statistics, and enable safe/reliable IO for dataframe serialization/deserialization.

To create a custom dagster pandas type, use ``create_dagster_pandas_dataframe_type``. Aside from optional
``name`` and ``description`` fields for documentation in dagit, you can provide a summary statistics function that emits
``EventMetadataEntry`` objects. To further illustrate this idea, take a look at the next example which creates a custom
dagster dataframe that details e-bike trips. Given this, we can construct our dagster pandas type and hook it into 
our solids in the following way:

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/simple_pipeline.py
   :caption: simple_pipeline.py

If you execute this pipeline in the dagit playground, you should get the following:

.. thumbnail:: tutorial1.png

Notice the summary statistics being surfaced as your pipeline executes. Since data systems can seldom control the
quality of the data they receive, it becomes important to monitor data as it flows through your systems.
In complex pipelines, this can help debug and monitor data drift over time.

.. _dataframe_level_validation:

Dagster DataFrame Level Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we have a custom dataframe type that emits summary statistics during a pipeline run, we can start to 
express dataframe level shape constraints (e.g number of rows, or columns). 

You can do this by providing a list of dataframe constraints to ``create_dagster_pandas_dataframe_type``. These
constraint objects live in ``dagster_pandas/constraints.py``. Two such constraints are
the ``RowCountConstraint`` and ``StrictColumnsConstraint``.

Let's extend the example above to illustrate this:

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/shape_constrained_pipeline.py
   :lines: 39-46
   :caption: shape_constrained_pipeline.py

So if we rerun the above example with this dataframe, nothing should change. However, if you pass in 100 to the row
count constraint, you can watch your pipeline fail that type check. 

.. _schema_validation:

Dagster DataFrame Schema Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Aside from shape validation, ``create_dagster_pandas_dataframe_type`` also provides schema validation. You can do this
by providing a list of ``PandasColumn`` objects which are containers for columns and their constraints. Right now, all
of our columns contain integer types. It is then possible to construct the following schema for the ``TripDataFrame``
dataframe.

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/schema_validated_pipeline.py
   :lines: 41-53
   :caption: schema_validated_pipeline.py

On top of the shape constraints, the ``TripDataFrame`` will also apply type constraints to your columns allowing
you to get schema level validation for your dataframes. In fact, this schema will also be documented for you and
will be accessible via the solid viewer in dagit in the following way:

.. thumbnail:: tutorial2.png

.. _bespoke_validation:

Dagster DataFrame Bespoke Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to add many constraints to your list to get a bunch of validation for your columns. However, 
there will inevitably be cases where you want some bespoke validation. To do this, simply create a constraint
that adheres to the ``ColumnConstraint`` interface and insert it into the ``constraints`` list for your
``PandasColumn``.

Let's reimplement ``CategoricalColumnConstraint``. To do this, all it needs is a ``markdown_description``
for dagit which accepts and renders markdown syntax, a ``error_description``
for error logs, and a validation method which throws a ``ColumnConstraintViolationException`` if
a row fails validation. This would look like the following:

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/categorical_column_constraint_pipeline.py
   :caption: categorical_column_constraint_pipeline.py


.. _validation_synctactic_sugar:

Validation Sugar
^^^^^^^^^^^^^^^^

You are probably noticing that adding a bunch of constraints to a ``PandasColumn`` can get quite cumbersome.
To fix this, the ``PandasColumn`` class defines a higher level API for common use cases. Let's go back to
the ``TripDataFrame``. Let's assume that instead of seconds since epoch, our timestamps were represented as
datetime objects. Our ``TripDataFrame`` can also be expressed in the following way:

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/sugar_pipeline.py
   :lines: 28-41
   :caption: sugar_pipeline.py

These are just convenience methods that compose the right PandasColumns for you for the most common use cases. Feel free
to explore them in the ``PandasColumn`` class to see all of the different convenience functions available to you.

Hopefully this gives a decent picture of how dataframes ought to be used in dagster and the syntactic sugar
available to maximize workflow development.
