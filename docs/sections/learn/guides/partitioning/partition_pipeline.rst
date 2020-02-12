Writing a partition ready pipeline
==================================

We use solid configuration as the mechanism to easily write pipelines that operate on partitions. If you haven't explored the dagster config system, take a look at `intro tutorial <../../tutorial/config>`_.

To get a clearer understanding of partitioning, we can work through an example pipeline that calculates the total volume traded for a given stock. Volume ris defined as the number of shares traded in a given time period.

We'll use the `Financial Modeling Prep API <https://financialmodelingprep.com/developer/docs//>` as our data source. The API has an endpoint that can give us historical price data for a given stock over a time range:

.. code-block:: console

    https://financialmodelingprep.com/api/v3/historical-price-full/AAPL?from=2019-01-01&to=2019-01-31

If we query this URL, we see that we get a json response containing an an array with the volume (number of shares) traded on each day.

.. code-block:: JSON

    {
    "symbol" : "AAPL",
    "historical" : [ {
        "date" : "2019-01-02",
        "open" : 154.89,
        "high" : 158.85,
        "low" : 154.23,
        "close" : 157.92,
        "adjClose" : 156.05,
        "volume" : 3.70397E7,
        "unadjustedVolume" : 3.70397E7,
        "change" : -3.03,
        "changePercent" : -1.956,
        "vwap" : 157.0,
        "label" : "January 02, 19",
        "changeOverTime" : -0.01956
    }, {
        "date" : "2019-01-03",
        "open" : 143.98,
        "high" : 145.72,
        "low" : 142.0,
        "close" : 142.19,
        "adjClose" : 140.51,
        "volume" : 9.13122E7,
        "unadjustedVolume" : 9.13122E7,
        "change" : 1.79,
        ...

Let's write our first pipeline to query this URL and calculate the total volume traded for January 2019.

Before we begin, let's set up a project structure to organize our code:

.. code-block:: console

    partition-tutorial
    ├── repository.py
    ├── repository.yaml

And point our `repository.yaml` to our repository:

repository.yaml:

.. code-block:: YAML

    repository:
        file: repository.py
        fn: define_repo

Our first solid will take the stock ticker symbol as config, and query the API to return the volume traded from Jan 01 - Jan 31 2019. We pass the json response to the downstream solid.

.. code-block:: python

    from dagster import solid
    import requests

    API_URL = "https://financialmodelingprep.com/api/v3/historical-price-full"

    @solid(config={'symbol': str})
    def query_historical_stock_data(context):
        symbol = context.solid_config['symbol']
        ds_start = "2019-01-01"
        ds_end = "2019-01-31"

        request_url = "{API_URL}/{symbol}?from={ds_start}&to={ds_end}".format(
            api_url=stock_data_api_url, symbol=symbol, ds_start=ds_start, ds_end=ds_end
        )

        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()

Our second solid will take the json response and sum up the volume amounts:

.. code-block:: python

    from dagster import solid, InputDefinition

    @solid(input_defs=[InputDefinition('json_response', dict)])
    def sum_volume(context, json_response):
        historical_data = json_response['historical']
        total_volume = 0
        for date in historical_data:
            total_volume += date['volume']

        context.log.info('Total volume: {total_volume}'.format(total_volume=str(total_volume)))

        return total_volume

Great! Now we can wrap this up in a pipeline and repository and try executing it in dagit.

.. code-block:: python

    from dagster import pipeline, RepositoryDefinition

    @pipeline
    def compute_total_stock_volume():
        sum_volume(query_historical_stock_data())

    def define_repo():
        return RepositoryDefinition(
            name='partitioning-tutorial', pipeline_defs=[compute_total_stock_volume]
        )

We can try configuring the pipeline run to calculate the total volume for Apple shares:

.. code-block:: YAML

    solids:
        query_historical_stock_data:
            config:
                symbol: "AAPL"

Now if we wanted to calculate the total volume for several different stocks, it's easy to simply change our configuration to run for a different ticker:

.. code-block:: YAML

    solids:
        query_historical_stock_data:
            config:
                symbol: "GOOG"