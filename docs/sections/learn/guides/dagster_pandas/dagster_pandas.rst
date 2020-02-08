Validating Pandas DataFrames with Dagster Types
------------------------------------------------
   * :ref:`Creating Dagster DataFrame Types <creating_dagster_dataframes>`
   * :ref:`Dagster DataFrame Level Validation <dataframe_level_validation>`
   * :ref:`Dagster DataFrame Custom Validation <custom_validation>`

Pandas is a broadly adopted library for data transformations, so we built a pandas integration that extends the
dagster type system to easily express custom dataframe types that perform data validation, emit summary statistics,
and enable reliable dataframe serialization/deserialization. On top of this, the dagster type system generates
documentation of your dataframe constraints and makes it accessible via Dagit.

.. _creating_dagster_dataframes:

Creating Dagster DataFrame Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a custom dagster pandas type use ``create_dagster_pandas_dataframe_type`` and provide a list of
``PandasColumn`` objects which act as containers for your columns and their constraints. However, we provide a
ton of convenience constructors. To further illustrate this idea, take a look at
the next example which creates a custom dagster dataframe that details e-bike trips. Given this, we can construct
our dagster pandas type and hook it into our solids in the following way:

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/sugar_pipeline.py
   :caption: sugar_pipeline.py

By passing in these `PandasColumn` objects, you are expressing the schema and constraints you expect your dataframe
to folow and when dagster performs type checks for your solids. Moreover, if you go to the solid viewer, you can
see your schema documented for you in dagit:

.. thumbnail:: tutorial2.png

These are just convenience methods that compose the right PandasColumns for you for the most common use cases. Feel
free to explore them in the ``PandasColumn`` class to see all of the different convenience functions available
to you.

.. _dataframe_level_validation:

Dagster DataFrame Level Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we have a custom dataframe type that performs schema validation during a pipeline run, we can start to
express dataframe level shape constraints (e.g number of rows, or columns). 

You can do this by providing a list of dataframe constraints to ``create_dagster_pandas_dataframe_type``. These
constraint objects live in ``dagster_pandas/constraints.py``. Two such constraints are
the ``RowCountConstraint`` and ``StrictColumnsConstraint``.

Let's extend the example above to illustrate this:

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/shape_constrained_pipeline.py
   :lines: 16-33
   :caption: shape_constrained_pipeline.py

So if we rerun the above example with this dataframe, nothing should change. However, if you pass in 100 to the row
count constraint, you can watch your pipeline fail that type check.

.. _dataframe_summary_statistics:

Dagster DataFrame Summary Statistics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Aside from constraint validation, ``create_dagster_pandas_dataframe_type`` also takes in a summary statistics function
that emits ``EventMetadataEntry`` objects which are surfaced during pipeline runs. Since data systems seldom control
the quality of the data they receive, it becomes important to monitor data as it flows through your systems. In complex
pipelines, this can help debug and monitor data drift over time. Let's illustrate how this works in our example:

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/summary_stats_pipeline.py
   :lines: 12-50
   :caption: summary_stats_pipeline.py

Now if you run this pipeline in the dagit playground, you should see the following:

.. thumbnail:: tutorial1.png

.. _custom_validation:

Dagster DataFrame Custom Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As you start to express more and more complex column schema models, you are going to inevitably need to start
performing more custom validation. Luckily, this lets you dive into the lower level ``PandasColumn``
and ``ColumnLevelConstraint`` API's. Under the hood, ``PandasColumn`` objects take in a column name and a arbitrary
list of ``ColumnConstraint`` objects. To tie this back to our example, let's say that we want to validate that the
amount paid for a e-bike must be in 5 dollar increments because that is the price per mile rounded up
(These e-bikes are made of solid gold). As a result, let's implement a ``DivisibleByFiveConstraint``. To do this,
all it needs is a ``markdown_description`` for dagit which accepts and renders markdown syntax, a
``error_description`` for error logs, and a validation method which throws a ``ColumnConstraintViolationException``
if a row fails validation. This would look like the following:

.. literalinclude:: ../../../../../examples/dagster_examples/dagster_pandas_guide/custom_column_constraint_pipeline.py
   :lines: 36-55
   :caption: custom_column_constraint_pipeline.py

Hopefully this gives a decent picture of how dataframes ought to be used in dagster and the syntactic sugar
available to maximize workflow development.
