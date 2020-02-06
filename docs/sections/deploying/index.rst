Deploying Dagster
-----------------

Dagster supports a wide variety of deployment strategies.

Typically, you'll want to deploy Dagit somewhere, configure the way that it stores information and
launches runs, and make sure your pipelines are configured to run appropriately for your
environment.

In some environments, you'll want to run additional (engine-specific) workers on which to execute
runs.

And you may want to deploy Dagster pipelines into a completely different scheduling and execution
environment, like Apache Airflow.

No matter how you're planning to deploy Dagster, you should first understand its default behavior.

You should also be familiar with configuring the Dagster instance, which organizes all of the
information specific to a particular installation or deployment of Dagster, using ``dagster.yaml``.

And you should be aware of the per-pipeline run configuration you'll need for your pipeline runs to
take advantage of the environment in which they're deployed.

.. toctree::

  instance
  local
  aws
  gcp
  k8s
  dask
  scheduler
  airflow


Deploying on Kubernetes
~~~~~~~~~~~~~~~~~~~~~~~

Deploying on Dask
~~~~~~~~~~~~~~~~~

The `dagster-dask <https://github.com/dagster-io/dagster/tree/master/python_modules/dagster-dask>`__
module makes a :py:data:`~dagster_dask.dask_executor` available, which can target either a local
Dask cluster or a distributed cluster. Computation is distributed across the cluster at the
execution step level. This is a straightforward path to testable and scalable distributed
execution for heavier workloads.

Configuring a scheduler
~~~~~~~~~~~~~~~~~~~~~~~

Dagster's approach to scheduling pipelines for periodic execution is also oriented toward
extensibility. Schedules are defined in code using the :py:func:`@schedules <dagster.schedules>`
API and may be executed by multiple concrete schedulers.

The first scheduler we've built is in the
`dagster-cron <https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-cron>`__
package and is backed by system cron, the :py:class:`~dagster_cron.SystemCronScheduler`. (See the
`tutorial docs <scheduling-pipeline-runs>`_ for an example of how to schedule pipeline executions
using the cron-backed scheduler.)

Users can also write their own schedulers. If you're considering doing this, please reach out
through our Slack channel so that we can provide guidance and support.


Deploying to Airflow
~~~~~~~~~~~~~~~~~~~~

It's also possible to schedule pipelines for execution by compiling them to a format that can be
understood by a third-party scheduling system, and then defining schedules within that system.

This is the approach we use to deploy Dagster pipelines to Airflow (using the
`dagster-airflow <https://github.com/dagster-io/dagster/tree/master/python_modules/dagster-airflow>`__
package).

A Dagster pipeline is first compiled with a set of config options into an execution plan,
and then the individual execution steps are expressed as Airflow tasks using a set of custom wrapper
operators. The resulting DAG can be deployed to an existing Airflow install and scheduled and
monitored using all the tools being used to existing pipelines (See the
`Airflow guide <other/airflow.html>`_ for details.)

When using Airflow, your instance yaml shouldn't specify a scheduler. Airflow's own scheduler will...


.. include
  local
