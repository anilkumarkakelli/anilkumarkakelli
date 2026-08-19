# Instructor guide — GCP for bachelor CS

## Pedagogy

Teach **decision-making**, not product catalogs. Every lecture should end with: *“If the requirement is X, which GCP service and why not Y?”*

Recommended pattern (50-minute lecture):

| Minutes | Activity |
|---|---|
| 0–8 | Recap + one production failure story (outage, bill shock, IAM leak) |
| 8–28 | Concepts + 2–3 figures from `02-figures-and-diagrams.md` |
| 28–42 | Walk a real-time use case from `03-realtime-usecases.md` |
| 42–50 | Exit ticket: 2 MCQs or a 3-line architecture sketch |

Labs: students **build one vertical slice** (API → Pub/Sub → worker → BigQuery) rather than clicking every console page.

## 12-week plan

| Week | Lecture topics | Lab | Case |
|---|---|---|---|
| 1 | Cloud models, GCP global fabric, projects | Create project, enable APIs, gcloud init | Why Pokémon GO needed elastic regions |
| 2 | IAM, resource hierarchy, billing, quotas | Custom role + budget alert | Bill-shock postmortem |
| 3 | Compute: GCE, MIG, instance templates | NGINX on GCE + MIG + health check | Seasonal retail traffic |
| 4 | Containers: Artifact Registry, GKE, Cloud Run | Cloud Run hello + GKE cluster (small) | Snapchat story upload path |
| 5 | Networking: VPC, subnet, firewall, Cloud NAT | Two-tier VPC, private GCE, IAP tunnel | Zero-trust campus app |
| 6 | Load balancing, CDN, Cloud Armor, Cloud DNS | HTTP(S) LB + Cloud Armor policy | Live sports CDN |
| 7 | Storage: GCS classes, PD, Filestore | Lifecycle + signed URL upload | Media ingest |
| 8 | Databases: SQL, Spanner, Firestore, Bigtable, Memorystore | Cloud SQL + Firestore contrast lab | Global user profile |
| 9 | Real-time: Pub/Sub, Dataflow, Eventarc | Pub/Sub → Cloud Run → BigQuery | Fraud / IoT telemetry |
| 10 | Analytics: BigQuery, Looker Studio; intro Vertex AI | SQL on public dataset + streaming insert | Spotify-style analytics |
| 11 | Security + SRE: KMS, Secret Manager, Logging, SLOs | Log-based metric + alert | Payment PCI-style isolation |
| 12 | Architectures, cost, exam revision | Capstone demo | Student presentations |

## Demo environment (faculty)

Keep spend low:

- One **folder** `teaching-gcp` with student projects `stu-<id>`.
- **Budget alerts** at 50% / 90% / 100% of a hard monthly cap.
- Prefer **Cloud Run + Pub/Sub + BigQuery sandbox** over GKE for most labs.
- Delete GKE clusters after each lab (largest cost driver).
- Use **public BigQuery datasets** (`bigquery-public-data`) so students need no ETL.

Suggested student IAM: `roles/editor` is too wide for teaching. Prefer:

- `roles/run.admin`, `roles/pubsub.editor`, `roles/bigquery.jobUser`, `roles/bigquery.dataEditor` on a dataset, `roles/storage.objectAdmin` on one bucket, `roles/logging.viewer`, `roles/monitoring.viewer`.

## Assessment weights (suggested)

| Component | Weight | Notes |
|---|---|---|
| Lab portfolio (8 labs) | 30% | Screenshots + `gcloud` history + short reflection |
| Midterm (weeks 1–6) | 20% | Conceptual + small design |
| Capstone architecture + demo | 30% | Must include a **real-time** path |
| Final exam | 20% | Closed book, figures to label |

Capstone constraint: **must** use at least one of Pub/Sub, Dataflow, or Firestore real-time listeners, plus IAM least privilege and a cost estimate.

## Common student misconceptions

1. “Cloud = someone else’s computer” — incomplete: also **control plane APIs**, **shared responsibility**, **multi-tenant isolation**.
2. “More zones = always more availability” — only if the **app is multi-zone** and **data is replicated**.
3. “GKE is always better than Cloud Run” — GKE wins for complex networking/sidecars/state; Cloud Run wins for request-scoped HTTP services.
4. “BigQuery is a MySQL replacement” — OLAP vs OLTP; do not put checkout transactions in BigQuery.
5. “Pub/Sub is a database” — it is a **durable log / queue**, not a system of record.
6. “Free tier means free forever” — quotas, egress, and forgotten GKE nodes cause surprise bills.

## Academic integrity

Require **architecture decision records** (one page): alternatives considered, why GCP product X, cost and threat notes. Penalize console-click recipes with no reasoning.

## Accessibility of figures

All diagrams are Mermaid (text). Recolor in slides; keep **region / zone / project** colors consistent:

- Project = blue, VPC = green, data plane = orange, control plane = grey, untrusted Internet = red.
