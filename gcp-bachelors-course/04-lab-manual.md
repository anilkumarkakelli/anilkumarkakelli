# Lab manual — GCP (free-tier / low-cost)

**Rules:** enable only listed APIs; set a **budget alert** on day 1; delete GKE clusters before you leave; never upload PII; never make buckets public.

**Tooling:** Cloud Console + Cloud Shell. Optional: local `gcloud`.

Each lab: **goal → steps → evidence → reflection (5 sentences).**

---

## Lab 0 — Hygiene (week 1)

**Goal:** project, APIs, budget, `gcloud`.

1. Create project `cs-gcp-<roll>`.
2. Link billing (faculty billing account).
3. Budget: 100% of faculty cap → email.
4. Enable: `cloudresourcemanager`, `serviceusage`, `iam`, `logging`.
5. `gcloud config set project ...`

**Evidence:** screenshot of budget + `gcloud config list`.

**Reflection:** What is a project number vs ID?

---

## Lab 1 — IAM least privilege (week 2)

**Goal:** a service account that can only list GCS objects in **one** bucket.

1. Create bucket `cs-gcp-<roll>-lab1` (regional).
2. Create SA `lab1-reader`.
3. Grant `roles/storage.objectViewer` **on the bucket**, not the project.
4. Create a second bucket; show the SA **cannot** list it (`403`).
5. (Optional) IAM Condition: expire binding at end of lab day.

**Evidence:** two command outputs (allow + deny).

---

## Lab 2 — GCE + firewall + IAP (week 3)

**Goal:** VM without `0.0.0.0/0` SSH.

1. Custom VPC + subnet.
2. e2-micro VM, **no external IP**.
3. Cloud NAT + Private Google Access.
4. IAP tunnel SSH (`gcloud compute ssh --tunnel-through-iap`).
5. Startup script installs nginx; firewall allows 80 **only from** a health-check / LB range **or** skip public HTTP and curl via IAP.

If IAP is too heavy for your campus, use a **bastion** in a management subnet — still no SSH from the world.

**Evidence:** `curl` to nginx via approved path; firewall rule dump.

---

## Lab 3 — Cloud Run deploy (week 4)

**Goal:** container from source.

1. Enable Cloud Run + Artifact Registry.
2. Tiny Python/Go/Node HTTP server returning `{"ok": true, "ts": ...}`.
3. `gcloud run deploy --allow-unauthenticated` **only if** faculty permits; otherwise `--no-allow-unauthenticated` + `roles/run.invoker` for student accounts.
4. Show revision; change env var; new revision.
5. Load: `hey` or `ab` 200 requests; screenshot Cloud Monitoring request count.

**Evidence:** service URL + revision list.

---

## Lab 4 — VPC two-tier (week 5)

**Goal:** “frontend” and “backend” tags.

1. Two instance groups or two Cloud Run services.
2. Firewall: frontend SA may reach backend on 8080; **you** may not reach backend from your laptop.
3. Demonstrate deny.

**Evidence:** tcpdump or `curl` from frontend vs laptop.

---

## Lab 5 — HTTPS LB + Cloud Armor (week 6)

**Goal:** one Anycast IP, two backends (or one MIG), Armor deny of a test User-Agent.

1. Serverless NEG to Cloud Run **or** MIG.
2. URL map `/` → service.
3. Armor rule: deny `User-Agent: evil-scanner`.
4. `curl -A evil-scanner` → 403; normal curl → 200.

**Evidence:** Armor policy + both curls.

**Cost note:** idle LBs cost money — delete after demo.

---

## Lab 6 — GCS signed URL + lifecycle (week 7)

**Goal:** browser-class upload without public bucket.

1. Uniform IAM; no `allUsers`.
2. SA (or user) generates **V4 signed URL** PUT, 10-minute expiry.
3. Upload with `curl -X PUT`.
4. Lifecycle: delete `uploads/` after 1 day (or 7).
5. Show object is not world-readable.

**Evidence:** signed URL command + 403 on anonymous GET.

---

## Lab 7 — Cloud SQL vs Firestore (week 8)

**Goal:** feel OLTP vs document realtime.

**A. Cloud SQL Postgres** (smallest HA off if budget tight): schema `orders(id, amount)`; insert; select.

**B. Firestore:** collection `presence/{studentId}` with timestamp; enable a **listener** in a 20-line web page (Firebase SDK) **or** `gcloud` snapshots.

**Reflection:** which query is painful in each? (SQL: “notify all clients of one document change”; Firestore: “sum all orders this month”.)

---

## Lab 8 — Real-time spine: Pub/Sub → Cloud Run → BigQuery (week 9) **[core]**

**Goal:** the course’s distinctive lab.

1. Dataset `lab8`, table `events(ts TIMESTAMP, student STRING, payload STRING)` partitioned by `ts`.
2. Topic `lab8-events`.
3. Cloud Run consumer: verify OIDC (push) or pull; **idempotent** insert using `insertId` or payload hash.
4. Publish 100 messages.
5. Query BigQuery: `COUNT(*)`.
6. Publish a **poison** JSON; show dead-letter topic after N nacks (configure DLQ).

**Evidence:** BQ query result + DLQ message.

**Extension:** Dataflow template Pub/Sub → BigQuery instead of Cloud Run.

---

## Lab 9 — BigQuery public data (week 10)

**Goal:** scan discipline.

1. Query `bigquery-public-data.samples.shakespeare` or `chicago_taxi_trips` with **partition filter**.
2. Job details: **bytes billed**.
3. Rewrite a bad `SELECT *` into a partitioned, column-pruned query; compare bytes.

**Evidence:** two job statistics screenshots.

**Optional:** `CREATE MODEL` logistic regression on a tiny public dataset (BigQuery ML).

---

## Lab 10 — Logs, metrics, SLO (week 11)

**Goal:** golden signals on the Lab 3 or 8 service.

1. Log-based metric: count HTTP 5xx.
2. Alerting policy: 5xx > 5 in 1 minute (email).
3. Force an error; show incident.
4. Trace: add OpenTelemetry **or** Cloud Trace capture on Cloud Run (default) and open one trace.

**Evidence:** incident screenshot + trace waterfall.

---

## Capstone lab (weeks 11–12)

Build **one** of: IoT alert, fraud stub, live score board, chat room — using **Case figures** from `03-realtime-usecases.md`.

**Must include:**

- Custom VPC or serverless egress story.
- IAM: no Editor on project for the runtime SA.
- Pub/Sub or Firestore listeners.
- Cost estimate for 10× traffic (spreadsheet is enough).
- Runbook: how to drain subscriptions and delete resources.

**Demo:** 8 minutes + 4 minutes questions.

---

## Tear-down checklist (every session)

```text
[ ] GKE clusters deleted
[ ] Cloud Run min instances = 0
[ ] LBs / Armor / static IPs deleted
[ ] Cloud SQL instances stopped or deleted
[ ] Bigtable / Spanner (if any) deleted
[ ] Unneeded disks / snapshots
[ ] Budget still green
```

Faculty: a nightly Cloud Scheduler + Cloud Function that lists `gcloud compute instances list` across student projects is worth the setup time.
