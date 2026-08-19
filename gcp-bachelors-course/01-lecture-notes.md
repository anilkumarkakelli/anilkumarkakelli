# Full lecture notes — Google Cloud Platform

**Course:** Bachelor of Computer Science  
**Use with:** figures (`02-figures-and-diagrams.md`), cases (`03-realtime-usecases.md`), labs (`04-lab-manual.md`).

These notes are written for **teaching**, not as a product brochure. Where GCP names change, teach the **abstraction**; look up the current console label before class.

---

## Week 1 — Cloud computing and the GCP mental model

### 1.1 Why cloud exists (CS view)

A data center is a distributed system with:

- **Capacity planning** (you buy hardware before you need it).
- **Failure** (disks, racks, buildings, fiber cuts).
- **Multi-tenancy** (many customers share physical hosts; isolation is a security problem).
- **Elastic control planes** (APIs that create/destroy resources in seconds).

Cloud providers sell **on-demand virtualized resources** plus **managed software** (databases, queues, ML) with a **pay-for-use** meter.

**NIST model (still the right exam definition):**

| Characteristic | Meaning in GCP |
|---|---|
| On-demand self-service | `gcloud`, Console, Terraform, client libraries |
| Broad network access | Public APIs + private Google access |
| Resource pooling | Projects share physical plants; IAM isolates tenants |
| Rapid elasticity | MIGs, GKE HPA, Cloud Run scale-to-zero |
| Measured service | Billing export to BigQuery |

**Service models:**

| Model | You manage | GCP examples |
|---|---|---|
| IaaS | OS, runtime, app | Compute Engine, Persistent Disk |
| CaaS | Container image, some cluster policy | GKE, Cloud Run (containers without cluster ops) |
| PaaS | App code | App Engine (standard), some Cloud Run usage |
| FaaS | Function + trigger | Cloud Functions, Cloud Run jobs/services as functions |
| SaaS | Nothing (consumer) | Gmail; **not** what this course builds |

**Deployment models:** public (GCP), private (Anthos/GKE on-prem), hybrid, multi-cloud.

### 1.2 GCP global infrastructure

Teach three nested scopes:

1. **Region** — independent geographic area (`asia-south1` = Mumbai). Latency and data-residency live here.
2. **Zone** — failure domain inside a region (`asia-south1-a`). A zone outage must **not** take down a well-designed regional app.
3. **Multi-region** — Google-managed replication across regions (e.g. `EU`, `US` for some storage/BigQuery). You trade latency and cost for durability/availability.

**Edge / points of presence:** Cloud CDN, Cloud Armor, global HTTP(S) load balancing terminate TLS near users, then send traffic over Google’s backbone to your region.

**Rule of thumb:** put **compute next to data**. Cross-region chatter is the usual source of both latency and egress bills.

### 1.3 Projects as the unit of isolation

Everything belongs to a **project** (ID, number, name). APIs are **enabled per project**. Billing is attached to a **billing account** (can fund many projects).

**Resource hierarchy (memorize):**

```
Organization
  └── Folders (dept, env)
        └── Projects
              └── Resources (VMs, buckets, topics)
```

IAM **inherits down**. A folder-level `roles/viewer` can see every project beneath it unless you use additional constraints.

### 1.4 Shared responsibility (exam favorite)

| Layer | Typical owner |
|---|---|
| Physical DC, hypervisor, Google backbone | Google |
| Guest OS patches on GCE | **You** |
| GKE node OS | Google (Container-Optimized OS) + you for workloads |
| Cloud SQL engine patches | Google; you still design schema and IAM |
| Application authN/authZ bugs | **You** |
| IAM policy too wide | **You** |

### 1.5 SLA vs SLO vs SLI (SRE vocabulary)

- **SLI** — measured thing (availability, latency p99).
- **SLO** — target you promise internally (99.9% successful HTTP).
- **SLA** — legal/commercial; GCP product SLAs are **not** your user SLA unless you architect for them (multi-zone, retries, regional LB).

Three nines (99.9%) ≈ 43 minutes downtime/month. Five nines is **not** free: it requires multi-region active-active and operational maturity.

---

## Week 2 — IAM, identity, billing, quotas

### 2.1 Identities

| Principal | Use |
|---|---|
| Google Account | Humans |
| Service account | Workloads (`my-api@PROJECT.iam.gserviceaccount.com`) |
| Google group | Teams |
| Workforce / workforce identity federation | Enterprise IdP |
| Workload identity federation | GitHub Actions, AWS, on-prem without long-lived keys |

**Never** download JSON keys for service accounts in new designs. Prefer **attached service accounts** (GCE/GKE/Cloud Run) and **Workload Identity**.

### 2.2 Policy = binding of members to roles on a resource

```
allow { member, role } on resource
```

**Role types:**

- **Primitive:** Owner / Editor / Viewer — too coarse for production; OK only for a sandbox.
- **Predefined:** `roles/pubsub.publisher` — prefer these.
- **Custom:** least privilege for teaching and prod.

**IAM Conditions** (time, source IP, resource tags) are how you express *“interns can start VMs only in `lab-*` projects during class hours.”*

### 2.3 Authentication vs authorization

- **AuthN:** OAuth 2.0 / OIDC, ADC (Application Default Credentials).
- **AuthZ:** IAM + (often) application-level checks (IAP, Firebase Auth, your JWT).

**ADC search order (students must know):** env var `GOOGLE_APPLICATION_CREDENTIALS` → well-known file → attached metadata server on GCP → `gcloud` user credentials locally.

### 2.4 Billing and FinOps basics

- **SKU** — billable meter (vCPU-hour, GiB-month, egress).
- **Labels** — `team=ai-lab`, `env=dev` for chargeback.
- **Budgets + Pub/Sub** — automate “stop student VMs” (policy, not magic).
- **Committed use discounts (CUDs)** and **sustained use** — teach that idle GKE nodes destroy lab budgets.
- **Egress** is often the surprise: Internet egress, cross-region, and some multi-region storage.

**Quotas** protect Google and you. Rate limits (`pubsub.googleapis.com`) vs allocation (`CPUS_PER_REGION`). Lab failures are often quota, not IAM.

---

## Week 3 — Compute Engine and managed instance groups

### 3.1 Virtual machine model

A **GCE instance** is: machine type (vCPU/RAM) + boot disk + optional GPUs + network interface(s) + service account + metadata (startup script).

**Machine families (teach the idea, not the SKU list):**

- General (`E2`, `N2`) — web, labs.
- Compute-optimized (`C2`) — HPC-ish, game servers.
- Memory-optimized (`M3`) — in-memory DBs.
- Accelerator (`A2`, `G2`) — ML training/inference.

**Disks:** pd-balanced vs pd-ssd vs Local SSD (ephemeral, high IOPS). Snapshots are crash-consistent; **app-consistent** backups need freeze/flush.

### 3.2 Availability on GCE

| Pattern | What it survives |
|---|---|
| Single VM | Almost nothing |
| MIG in one zone | Instance failure, not zone failure |
| Regional MIG (multi-zone) | Zone failure |
| Multi-region active-active | Region failure (hard: data replication) |

**Managed Instance Group (MIG):** instance template + autoscaler + autohealing (health check). This is the **IaaS building block** behind many “elastic” designs.

**Sole-tenancy / confidential VMs:** regulated workloads; mention, do not lab unless you have budget.

### 3.3 Metadata and identity on the VM

The metadata server (`169.254.169.254`) issues **short-lived tokens** for the attached service account. Attackers who RCE your VM **steal those tokens**. Hardening: least-privilege SA, OS Login, Shielded VM, no public IP + IAP.

---

## Week 4 — Containers: GKE and Cloud Run

### 4.1 Why containers

Image = app + libs + OS userland. **Immutable deploys**. Orchestration adds scheduling, health, secrets, service discovery.

### 4.2 Artifact Registry

Store Docker images and language packages in-region. Vulnerability scanning. CI pushes; GKE/Cloud Run pull. Prefer Artifact Registry over the older Container Registry.

### 4.3 GKE (Kubernetes on GCP)

**Control plane** managed by Google (regional control plane = HA etcd story). **Nodes** are GCE VMs in node pools.

Concepts students already need from a K8s course (or teach mini): Pod, Deployment, Service, Ingress, ConfigMap, Secret, HPA.

**GKE-specific (teach these):**

- **Workload Identity** — Pod SA ↔ GCP SA (no JSON keys).
- **GKE Autopilot** vs Standard — Autopilot: Google manages nodes; you pay per pod resource. Standard: you manage node pools.
- **Binary Authorization** — only signed images.
- **Gateway / Ingress** → Google Cloud Load Balancing.
- **Cluster autoscaler / node auto-provisioning**.

**When GKE is justified:** many services, sidecars, custom networking, stateful operators, mixed batch + serving.

**When it is overkill:** one HTTP API — use **Cloud Run**.

### 4.4 Cloud Run

Run a container: HTTPS endpoint, **scale to zero**, concurrency per instance, CPU boost, min instances for latency.

**Request model:** one revision serves traffic; you can split 10/90 for canary.

**Jobs** — finite batch (nightly). **Services** — request/event driven.

Limits to teach: request timeout, CPU always-allocated vs request-only, VPC connectors / Direct VPC egress for private IP.

### 4.5 Cloud Functions vs Cloud Run vs App Engine

| Need | Prefer |
|---|---|
| Tiny glue (GCS finalize → call API) | Cloud Functions (2nd gen is Cloud Run underneath) |
| Container you already have | Cloud Run |
| Opinionated PaaS + traffic splitting (legacy apps) | App Engine |

Do not teach App Engine as the future default; mention it for exams and brownfield.

---

## Week 5 — VPC networking

### 5.1 VPC is global; subnets are regional

In AWS, a VPC is regional. **In GCP, a VPC spans all regions**; **subnets are regional** (and auto-mode vs custom-mode). This is a frequent comparison question.

- **Auto-mode VPC:** default subnets in every region — convenient, sloppy for prod.
- **Custom-mode:** you define CIDRs. **Required for teaching production hygiene.**

**Firewall rules** are **stateful**, applied to VPC, filtered by **network tags** or **service accounts** (prefer SA-based rules). Direction: ingress/egress. Priority 0–65535 (lower number = higher priority). Implied deny ingress / allow egress.

### 5.2 Private Google Access, Cloud NAT, IAP

VMs **without public IPs** still reach `*.googleapis.com` via **Private Google Access**. Outbound Internet needs **Cloud NAT**.

**Identity-Aware Proxy (IAP):** authenticate Google identities before TCP/HTTP to admin ports. Teach “no SSH from 0.0.0.0/0”.

### 5.3 Connectivity patterns

| Pattern | Use |
|---|---|
| Cloud VPN | Low-volume hybrid |
| Dedicated Interconnect / Partner Interconnect | Campus / DC to GCP |
| VPC peering | Two VPCs, non-transitive |
| Shared VPC | Host project owns network; service projects own VMs (enterprises, universities) |
| Private Service Connect | Consume Google or third-party APIs privately |
| Serverless VPC Access / Direct VPC | Cloud Run → Memorystore |

**Peering is not transitive.** If A–B and B–C, A cannot reach C through B. Use **Network Connectivity Center** or a hub VPC for that topology.

### 5.4 IP addressing

- Alias IPs (GKE pods).
- Secondary ranges.
- IPv6 dual-stack (mention).
- **Internal vs external** load balancer addresses.

---

## Week 6 — Load balancing, CDN, DNS, Armor

### 6.1 Proxy vs pass-through

Google’s **global HTTP(S) Application Load Balancer** is a **proxy** at the edge: Anycast IP, SSL offload, URL maps, backends (MIGs, GKE, Cloud Run, buckets).

**Network / passthrough NLB:** preserves client IP, regional, for TCP/UDP (game servers).

**Internal LB:** RFC1918, for east-west.

### 6.2 Backend health and session affinity

Health checks must hit a cheap `/healthz`. **Connection draining**. Session affinity (cookie, client IP) vs **stateless** (preferred).

### 6.3 Cloud CDN and Media CDN

Cache at Google’s edge. Cache keys, TTLs, negative caching. **Signed cookies/URLs** for premium video. Origin can be a bucket (static) or LB (dynamic).

### 6.4 Cloud Armor

WAF + DDoS. OWASP rules, rate limiting, geo, Adaptive Protection. Pair with global LB. This is the right place to discuss **Layer 7 attacks** vs **volumetric L3/L4** (Google’s front end absorbs much L3/L4).

### 6.5 Cloud DNS

Public and private zones. Routing policies (weighted, geolocation) for **active-active**. DNSSEC.

---

## Week 7 — Object and file storage

### 7.1 Cloud Storage (GCS)

**Buckets** are globally unique names; data lives in a **location** (region / dual-region / multi-region).

**Storage classes:** Standard, Nearline, Coldline, Archive — trade retrieval cost vs storage cost. **Autoclass** for unknown access patterns.

**Consistency:** strong consistency for overwrite/read of objects (teach as “read-after-write for new objects is strongly consistent”).

**Access:** IAM vs ACLs (prefer uniform bucket-level IAM). **Signed URLs** for browser uploads without making the bucket public. **Customer-managed keys (CMEK)**.

**Object versioning + lifecycle** — student labs: expire `tmp/` after 7 days.

**HNS (hierarchical namespace)** — analytics / Data Lakehouse layouts.

### 7.2 Persistent Disk vs Filestore

| | PD | Filestore (NFS) | GCS |
|---|---|---|---|
| Semantics | Block | POSIX file | Object |
| Attach | One RW writer (multi-writer special cases) | Many VMs | Many clients |
| Use | VM boot, databases | Lift-and-shift shared files | Data lake, backups, static web |

---

## Week 8 — Databases (the decision lecture)

**Do not memorize 12 products. Teach a decision tree.**

### 8.1 OLTP vs OLAP vs cache vs wide-column

| Workload | GCP default | Why |
|---|---|---|
| Relational OLTP, SQL, transactions | **Cloud SQL** (Postgres/MySQL) | Familiar, HA failover, backups |
| Global SQL, horizontal scale, external consistency | **Spanner** | TrueTime; expensive; worth it for global consistency |
| Mobile/web JSON, realtime listeners | **Firestore** | Sync SDK; not analytics |
| Massive keyed telemetry (IoT, ads) | **Bigtable** | HBase-like; design row keys or you die |
| Sub-ms cache / sessions | **Memorystore** (Redis/Memcached) | Volatile or persistence modes |
| Analytics SQL on TBs–PBs | **BigQuery** | Columnar, separates storage/compute |
| Graph / vector (survey) | AlloyDB + extensions, Vertex Vector Search | Mention only |

### 8.2 Cloud SQL

HA (regional): primary + standby, synchronous replication. Read replicas. Maintenance windows. **Private IP + Auth proxy** (no public IP in labs if possible). Automated backups + PITR.

### 8.3 Spanner (conceptual)

- **TrueTime** — GPS + atomic clocks bound clock uncertainty; enables external consistency without a single leader bottleneck in the same way as classic DBs.
- **Split / Paxos** groups — row-range sharding.
- Schema: interleaving tables, primary keys (hotspotting if you use timestamps as leading key — **same lesson as Bigtable**).

### 8.4 Firestore

Document + collection. **Strong consistency per document**. Realtime listeners = **push** to clients. Security rules (if Firebase). **Datastore mode** vs Native mode — know they exist.

Good for: presence, chat metadata, session, game state that is not a 10 TB scan.

Bad for: multi-document analytics, ad-hoc SQL over everything (export to BigQuery).

### 8.5 Bigtable

Row key design is the course. **Tall vs wide** tables. Unbalanced keys (user IDs that are sequential) create **hot tablets**. Replication for HA. Use with HBase API / Debezium stories.

### 8.6 CAP in one slide

You cannot independently maximize consistency, availability, and partition tolerance. Spanner **appears** to give C + A in practice by using a tightly synchronized network and TrueTime; partitions still degrade. **Firestore/SQL** choose C over A in a region. **Caches** choose A/latency. Teach students to **state what they sacrifice**.

---

## Week 9 — Events and stream processing (real-time core)

### 9.1 Why queues exist

Synchronous HTTP chains fail when a downstream is slow. **Producer/consumer decoupling**, backpressure, replay.

### 9.2 Pub/Sub

- **Topic** — named feed.
- **Subscription** — pull, push (HTTPS), or BigQuery/GCS export.
- **At-least-once** delivery (default). **Exactly-once** is an application + idempotency problem (and some newer features help; still design idempotent consumers).
- **Ordering keys** — per-key order, throughput trade-off.
- **Dead letter topics** — poison messages.
- **Seek / snapshot / replay** — operational gold.
- Retention and message size limits (know they exist; look up current numbers before exam year).

**Push vs pull:** Cloud Run push is simple; pull is better for batching and custom rate.

### 9.3 Dataflow (Apache Beam)

Unified **batch + streaming**. Windows: tumbling, hopping, session. **Watermarks** and **late data**. Exactly-once sink to BigQuery when configured correctly.

Teach Beam `PCollection` → `ParDo` → `GroupByKey`. Students who have done Spark will transfer.

**When not Dataflow:** simple filter/transform → Cloud Run workers. Dataflow wins at **shuffle, windows, join streams**.

### 9.4 Eventarc, Event Threat Detection, audit logs as events

Many GCP services emit **CloudEvents**. Eventarc routes them to Cloud Run. **Cloud Audit Logs** can drive security automation.

### 9.5 Dataproc / Kafka / Pub/Sub Lite / Managed Kafka

Survey: Dataproc = managed Spark/Hadoop. **Pub/Sub Lite** = cheaper, zonal, Kafka-like partitions. **Managed Service for Apache Kafka** (product availability varies by date — verify). For a bachelor course, **Pub/Sub + Dataflow** is the spine.

---

## Week 10 — Analytics and ML

### 10.1 BigQuery

- Storage (Capacitor columnar) **independent** of compute (slots / on-demand bytes scanned).
- **Standard SQL.** Partition + cluster or you **scan (and pay for) the world**.
- Streaming inserts vs load jobs vs Storage Write API.
- **Authorized views** for row-level security teaching.
- **BigQuery ML** — `CREATE MODEL` for quick baselines (logistic regression, boosted trees, remote Vertex models).
- **BI Engine** / Looker Studio for dashboards.

**Slot contention:** one student `SELECT *` on a 2 TB table ruins the sandbox. Teach `LIMIT`, preview, and partitioned public datasets (`_TABLE_SUFFIX`).

### 10.2 Vertex AI (survey, 1 lecture)

| Piece | Role |
|---|---|
| Training (custom / AutoML) | Produce a model artifact |
| Feature Store | Online/offline features for real-time scoring |
| Endpoints | Online prediction (low latency) |
| Batch prediction | Score a table overnight |
| Model Garden / Gemini APIs | Foundation models; **data governance still your problem** |
| Vector Search | RAG / semantic retrieval |

**Real-time ML path:** event → features (Memorystore / Feature Store) → Vertex endpoint → decision → log to BigQuery for drift.

Ethics: PII, training-data leakage, prompt injection for LLM apps. CS bachelors should hear this once.

---

## Week 11 — Security, identity-aware apps, operations

### 11.1 Defense in depth on GCP

1. **Organization Policy** (disable public buckets, restrict locations to `asia-south1`).
2. **VPC Service Controls** — anti-exfil perimeter around BigQuery/GCS (hard; demo video OK).
3. **CMEK / Cloud KMS / Cloud HSM**.
4. **Secret Manager** — not Git, not VM metadata.
5. **Binary Authorization + Artifact Analysis**.
6. **SCC (Security Command Center)** — misconfig findings.
7. **Cloud Armor + IAP**.
8. **Forseti/Policy Controller** — survey.

### 11.2 Observability (four golden signals)

Google SRE: **latency, traffic, errors, saturation**.

| Product | Use |
|---|---|
| Cloud Logging | Audit + app logs; log router to bucket/BigQuery/Pub/Sub |
| Cloud Monitoring | Metrics, SLOs, alerting |
| Cloud Trace | Distributed traces (OpenTelemetry) |
| Cloud Profiler | CPU/heap |
| Error Reporting | Exception grouping |
| Cloud Audit Logs | Admin / data access / system events |

**Trace context** must propagate on Pub/Sub and HTTP (`traceparent`). Otherwise the real-time lab is un-debuggable.

### 11.3 CI/CD

Cloud Build or GitHub Actions federated with Workload Identity. Artifact Registry → Cloud Deploy → GKE/Cloud Run. **Skaffold** optional. Infrastructure: **Terraform** + a state bucket.

---

## Week 12 — Architecture, reliability, cost, revision

### 12.1 Well-architected questions (force students to answer)

1. What fails? (zone, region, identity, quota, poison message)
2. What is the **RPO/RTO**?
3. What is the **consistency** requirement?
4. What is the **p99 latency** budget and where is it spent (edge, app, DB)?
5. What is the **unit cost** at 10× traffic?
6. Who can exfiltrate data?

### 12.2 Twelve-factor + cloud

Config via env/Secret Manager, disposability (Cloud Run), logs as streams, backing services as attached resources.

### 12.3 Multi-cloud honesty

Portable **app** (containers, Beam, Postgres) vs portable **operations** (IAM, networking, data gravity). Multi-cloud doubles cognitive load. Teach **exit strategy** (export GCS, dump SQL) rather than dual-running everything.

### 12.4 Cheatsheet: default “good” architecture for a student SaaS

- Custom VPC, no public VM IPs, Cloud NAT, IAP.
- Cloud Run + Artifact Registry.
- Cloud SQL Postgres private IP.
- GCS for blobs, signed URLs.
- Pub/Sub for all side effects (email, search index, analytics).
- BigQuery for analytics (not OLTP).
- Cloud Armor on global LB if public.
- Budget alerts; labels everywhere.

---

## Appendix A — `gcloud` survival set

```bash
gcloud init
gcloud config set project PROJECT_ID
gcloud services enable run.googleapis.com pubsub.googleapis.com
gcloud auth application-default login   # local only
gcloud iam service-accounts list
```

Prefer **Terraform** for anything that must be torn down after lab.

## Appendix B — Comparison table (exam)

| Concern | Typical GCP answer | Typical AWS analogue (for literacy) |
|---|---|---|
| Project | Project | Account |
| IAM | IAM (resource-centric) | IAM (account-centric) |
| VM | Compute Engine | EC2 |
| K8s | GKE | EKS |
| Serverless container | Cloud Run | ECS/Fargate, Lambda + HTTP |
| Object store | GCS | S3 |
| Warehouse | BigQuery | Redshift / Athena |
| Queue/stream | Pub/Sub | SQS + SNS + Kinesis |
| Global SQL | Spanner | Aurora global / Dynamo + patterns |

Analogues are **not 1:1**. Grade students on **properties**, not name matching.

## Appendix C — Glossary (first-use definitions)

- **Control plane** — APIs that mutate infrastructure.
- **Data plane** — packets/requests of the application.
- **Idempotency** — processing a message twice does not double-charge.
- **Poison message** — a payload that always crashes the consumer.
- **Hotspot** — one tablet/split/instance receives disproportionate keys.
- **Egress** — data leaving a network boundary you pay for.
- **Blast radius** — how much dies when one identity or region fails.
