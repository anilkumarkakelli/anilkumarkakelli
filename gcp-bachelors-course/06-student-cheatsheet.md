# Student one-pager (print before labs / exam)

## Hierarchy

Organization → Folders → **Projects** → resources. IAM inherits down. Enable APIs **per project**.

## Compute (default order)

Cloud Run → GKE (if cluster complexity) → GCE MIG (if you need the OS) → Functions (glue).

## Network

VPC **global**, subnet **regional**. No public VM IPs. Cloud NAT + Private Google Access. SSH via **IAP**. Firewalls: prefer **service accounts** over IP soup.

## Data

| If you need… | Use |
|---|---|
| Files/objects, signed upload | GCS |
| SQL one region | Cloud SQL |
| SQL global + external consistency | Spanner |
| Live client sync | Firestore |
| Huge keyed telemetry | Bigtable (design the row key) |
| Cache | Memorystore |
| Analytics SQL | BigQuery (partition!) |

## Real-time spine

Producer → **Pub/Sub topic** → many subscriptions (API worker, Dataflow, BigQuery).  
Delivery is **at-least-once** → **idempotent** consumers → **DLQ**.

Event time windows: **Dataflow / Beam** (watermarks, late data).

## Security

No JSON keys in git. Runtime **service account**. Secret Manager. Uniform bucket IAM. Cloud Armor on public HTTP. Organization policy: block public buckets.

## Ops

SLI → SLO → error budget. Logs, metrics, traces share a **trace id** across Pub/Sub. Budget alerts. Labels for chargeback.

## Cost landmines

Idle GKE, idle forwarding rules, BigQuery `SELECT *`, Internet **egress**, forgotten disks.

## Capstone skeleton

HTTPS LB → Cloud Run → Cloud SQL + GCS signed URLs; side effects on Pub/Sub → BigQuery.

## `gcloud` crumbs

```bash
gcloud config set project PROJECT_ID
gcloud run deploy SVC --source . --region REGION
gcloud pubsub topics publish TOPIC --message '{"ok":1}'
bq query --nouse_legacy_sql 'SELECT 1'
```
