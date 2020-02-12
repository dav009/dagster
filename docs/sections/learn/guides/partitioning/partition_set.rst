Creating a Simple Partition Set
==================================

If we're trying to calculate the total volume of trades for all stocks in January 2019, it might be difficult to get and process all the data in one query. Since we already have a pipeline that calculates total volume and takes a ticker symbol as config, we can create a partition set to help run the pipeline for each partition.

Let's assume there's only four stocks in the world: "AAPL", "GOOG", "MSFT", "TSLA"

.. code-block:: python

    def get_stock_ticker_partitions():
        return [
            Partition("AAPL"),
            Partition("GOOG"),
            Partition("MSFT"),
            Partition("TSLA"),
        ]

    def environment_dict_for_ticker_partition(partition):
        ticker_symbol = partition.value

        return {
            'solids': {
                'query_historical_stock_data' : { 'config' : { 'symbol': ticker_symbol}}
            }
        }

    stock_ticker_partition_sets = PartitionSetDefinition(
        name="stock_ticker_partition_sets",
        pipeline_name="compute_total_stock_volume",
        partition_fn=get_stock_ticker_partitions,
        environment_dict_fn_for_partition=environment_dict_for_ticker_partition,
    )

We can register these partitions decorating a function that returns a list of partition set definitions with the `@repository_partitions` and adding a reference to this function in `repository.yaml`, alongisde our repository reference.

.. code-block:: python

    @repository_partitions
    def define_partitions():
        return [stock_data_partitions_set]

.. code-block:: yaml

    repository:
        file: repository.py
        fn: define_partitions

Now, when we load dagit and playground, we can see all of our partitions and execute the configuration they generage.
