# Production

## Read this when

- builds, pipelines or deployments come up
- containers, Kubernetes or infrastructure configuration are involved
- something must be monitored, logged or traced
- choosing cloud services

## Automation and CI/CD

```
commit -> build -> test -> package -> deploy     (automated, not by hand)
```

- **Continuous integration:** every commit builds and runs all tests; feedback in minutes, a
  broken build is cheap to fix.
- **Continuous delivery:** every green build can be released; a human picks when.
- **Continuous deployment:** every green build goes to production on its own.
- Releasing should be routine and boring. Small changes, often.

## Containers

- A **VM** runs a full guest OS on a hypervisor; a **container** shares the host kernel and
  carries only the app and its dependencies: lighter, and the same image runs the same everywhere.
- **Image:** read-only layers with what the app needs; a running container adds a writable layer.
- Docker: the `docker` client talks to the `dockerd` daemon, which builds images and runs
  containers.

## Orchestration (Kubernetes)

Runs containers across many machines from a declared desired state: restarts, scales, spreads.

- **Pod:** the smallest unit, one or more containers sharing network and storage.
- **Worker node:** runs pods (`kubelet`, `kube-proxy`, a container runtime).
- **Control plane:** `kube-apiserver` (front door), `etcd` (cluster state), `kube-scheduler`
  (places pods), `kube-controller-manager` (fixes drift from the desired state).
- Daily commands: `kubectl get pods`, `describe pod`, `logs`, `apply -f`.

## Infrastructure as configuration (Terraform)

Declare the infrastructure; the tool keeps a state file of what it created and changes only the
difference. `terraform init`, `fmt`, `plan` (preview), `apply`, `destroy`. State files and
variable files hold secrets: never commit or print them.

## Observability

The three pillars: **metrics** (numbers over time: latency, error rate), **logs** (collected in
one searchable place), **traces** (one request followed across services by a trace id).
Monitoring watches them and alerts on thresholds. Prometheus pulls and stores metrics (PromQL);
Grafana shows dashboards and alerts. Health and metrics endpoints (e.g. Spring Actuator) catch a
regression before it is an incident.

## Cloud

- **IaaS** (VMs, storage, network; you run the OS), **PaaS** (a managed runtime), **FaaS** (one
  function, run and scaled on demand), **SaaS** (a finished application).
- Cloud-native properties: scalability, loose coupling, high cohesion, fault tolerance,
  observability, manageability (update while running).
- A firewall per instance (e.g. AWS security groups): allow only what is needed; everything else
  is denied.
