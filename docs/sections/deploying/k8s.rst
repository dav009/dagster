Deploying on Kubernetes
-----------------------

Helm chart
^^^^^^^^^^

K8sRunLauncher
^^^^^^^^^^^^^^

Run launcher abstraction

Executing on the same node and launching execution somewhere else -- perhaps just on a remote Dagit
instance, or perhaps in another environment such as a Kubernetes Job. Layered so that you can use
different execution engines, etc., in the different launched runs.

Helm

Even if you don't use Helm, you may find the Helm charts useful as a reference for all the
components you will probably want as part of a Kubernetes-based deployment of Dagster.
