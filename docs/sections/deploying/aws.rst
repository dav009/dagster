.. _deployment-aws:

Deploying to AWS
----------------

Depending on your organization's deployment and infrastructure management tools, deployments to
cloud services can be accomplished in a wide variety of ways. Internally, we strongly favor
infrastructure-as-code tools like `Pulumi <https://www.pulumi.com/>`_.


Quick start with dagster-aws
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``dagster_aws`` package includes a CLI tool intended to help you get a demo Dagster
deployment up and running as quickly as possible.

**NOTE: The dagster-aws CLI is not intended to provide a secure configuration, and the instance
it sets up will be launched into an existing VPC and publicly accessible. In production settings,
you will want to launch Dagit into an appropriately configured VPC, using an appropriate security
group, etc.**

Ensure you have AWS credentials on your local machine, and run:

.. code-block:: shell

    mkdir -p ~/dagster_aws
    export DAGSTER_HOME=~/dagster_aws
    pip install dagster dagit dagster-aws
    dagster-aws init

This script will walk you through the set up of an EC2 instance to host Dagit. You can also choose
to launch an RDS instance; if you do so, the remote EC2 instance will automatically be configured
to talk to RDS via a ``dagster.yaml`` file in the remote ``$DAGSTER_HOME``.

This script will output a configuration file at ``$DAGSTER_HOME/dagit-aws-config.yaml``, which will
look something like this:

.. code-block:: YAML

    ec2:
      ami_id: ami-08fd8ae3806f09a08
      instance_id: i-07330e77c4dd1bc81
      key_file_path: /path/to/dagster-keypair-test-20200205T222824.pem
      key_pair_name: dagster-keypair-test-20200205T222824
      local_path: null
      region: us-west-1
      remote_host: ec2-54-67-22-239.us-west-1.compute.amazonaws.com
      security_group_id: sg-02cd3b76c352c2098
    rds:
      db_engine: postgres
      db_engine_version: '11.5'
      db_name: dagster
      instance_name: dagster-rds-test
      instance_type: db.t3.small
      instance_uri: dagster-rds-test.cldkwizddrkj.us-west-1.rds.amazonaws.com
      password: dWz9gDZWo2RQL7Dm
      storage_size_gb: 20
      username: dagster

Subsequent usage of the ``dagster-aws`` CLI tool on the same machine will use this configuration to
connect to your running EC2 instance.

FIXME

Once the EC2 instance is launched and ready, you can synchronize your Dagster code to it using:

.. code-block:: shell

    cd /path/to/your/dagster/code
    dagster-aws up

This will copy over your Dagster client code to the EC2 instance, launch Dagit as `systemd` service,
and finally print a URL for you to connect to Dagit. You can look at
`init.sh <https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-aws/dagster_aws/cli/shell/init.sh>`_
for details on how we initialize the VM for running Dagit and the specification of the ``systemd``
service.

The ``dagster-aws`` CLI saves its state to ``$DAGSTER_HOME/dagster-aws-config.yaml``, so you can inspect
that file to understand what's going on and/or debug any issues.

.. rubric:: EC2 or ECS hosted Dagit

To host dagit on a bare VM or in Docker on ECS, see the `Local or Standalone Dagit <local.html>`_
guide.

.. rubric:: Execution

Out of the box, Dagit runs single-process execution. To enable multi-process execution, add the
following to your pipeline configuration YAML:

.. code-block:: yaml

    :caption: execution_config.yaml

    execution:
      multiprocess:
        max_concurrent: 0
    storage:
      filesystem:

**NOTE:** This YAML fragment should be put in your pipeline-specific configuration, not in
``$DAGSTER_HOME/dagster.yaml``. This is designed to permit configuration of execution on a
per-pipeline. Future versions of Dagster may add support for globally configuring execution.

.. rubric:: RDS Run / Events Storage

On AWS you can use a hosted RDS PostgreSQL database for your Dagster run/events data. As
noted previously, this can be accomplished by adding the following to ``$DAGSTER_HOME/dagster.yaml``:

.. code-block:: yaml

   :caption: dagster.yaml

    run_storage:
        module: dagster_postgres.run_storage
        class: PostgresRunStorage
        config:
            postgres_url: "postgresql://{username}:{password}@{host}:5432/{database}"

    event_log_storage:
        module: dagster_postgres.event_log
        class: PostgresEventLogStorage
        config:
            postgres_url: "postgresql://{username}:{password}@{host}:5432/{database}"

In this case, you'll want to ensure you provide the right connection strings for your RDS instance,
and ensure that the node or container hosting Dagit is able to connect to RDS.

.. rubric:: S3 Intermediates Storage

You'll probably also want to configure an S3 bucket to use for Dagster intermediates (see the
`intermediates tutorial guide <../tutorial/intermediates.html>`_ for more info). Dagster supports
serializing data passed between solids to S3; to enable this, you need to add S3 storage to your
:py:class:`ModeDefinition`:

.. code-block:: python

    from dagster_aws.s3.system_storage import s3_plus_default_storage_defs
    from dagster import ModeDefinition

    prod_mode = ModeDefinition(name='prod', system_storage_defs=s3_plus_default_storage_defs)


Then, just add the following YAML to your pipeline config:

.. code-block:: yaml

    :caption: execution_config.yaml

    storage:
      s3:
        config:
          s3_bucket: your-s3-bucket-name

With this in place, your pipeline runs will store intermediates on S3 in the location
``s3://<bucket>/dagster/storage/<pipeline run id>/intermediates/<solid name>.compute``
