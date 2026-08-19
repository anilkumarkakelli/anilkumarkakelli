# Figures and diagrams (lecture-ready)

All diagrams are **Mermaid**. Paste into slides or [mermaid.live](https://mermaid.live). Suggested spoken script is under each figure.

Color convention: **blue** = project/control, **green** = network, **orange** = data, **red** = untrusted.

---

## F1 — Cloud service models

```mermaid
flowchart TB
  subgraph You["You manage"]
    App[Application]
    Data[Data]
    RT[Runtime]
    OS[OS]
    HW[Hardware]
  end
  IaaS["IaaS — GCE"]
  PaaS["PaaS — App Engine / Cloud Run"]
  FaaS["FaaS — Cloud Functions"]
  SaaS["SaaS — Gmail"]
```

**Better teaching version (stacked responsibility):**

```mermaid
block-beta
  columns 4
  block:IaaS:1
    columns 1
    A1["App"]
    A2["Runtime"]
    A3["OS"]
    A4["You"]
    A5["Google: hypervisor+DC"]
  end
  block:PaaS:1
    columns 1
    B1["App"]
    B2["You"]
    B3["Google: runtime+OS"]
    B4["Google"]
    B5["Google"]
  end
  block:FaaS:1
    columns 1
    C1["Function"]
    C2["You"]
    C3["Google"]
    C4["Google"]
    C5["Google"]
  end
  block:SaaS:1
    columns 1
    D1["Google"]
    D2["Google"]
    D3["Google"]
    D4["Google"]
    D5["Google"]
  end
```

**Say:** “Moving right, you trade control for undifferentiated heavy lifting. You never outsource **your** authorization bugs.”

---

## F2 — Regions, zones, edge

```mermaid
flowchart LR
  User((User)) --> Edge[Google edge<br/>CDN / global LB]
  Edge -->|backbone| R1
  subgraph R1["Region asia-south1"]
    Z1[Zone a]
    Z2[Zone b]
    Z3[Zone c]
  end
  R1 -.->|optional replica| R2["Region asia-south2"]
```

**Say:** “A zone is a failure domain. A region is a latency and residency domain. The edge is where TLS dies and caches live.”

---

## F3 — Resource hierarchy and IAM inheritance

```mermaid
flowchart TD
  Org[Organization example.edu]
  F1[Folder: faculty]
  F2[Folder: students]
  P1[Project: research-nlp]
  P2[Project: stu-2026-042]
  VM[GCE instance]
  Bkt[GCS bucket]
  Org --> F1 --> P1 --> VM
  Org --> F2 --> P2 --> Bkt
```

```mermaid
flowchart LR
  Policy["IAM: group:tas@edu<br/>role: viewer on Folder students"]
  Policy --> Inherit[Inherits to all student projects]
```

**Say:** “Grant at the highest correct node. A Viewer on the student folder sees every lab project — that may be intended for TAs, never for the public.”

---

## F4 — Shared responsibility

```mermaid
flowchart TB
  subgraph Google["Google"]
    DC[Buildings, power, fiber]
    Hyp[Hypervisor, GKE control plane]
    API[Cloud SQL patches, GCS durability]
  end
  subgraph You["You"]
    IAM[IAM bindings]
    App[App logic, SQL injection]
    OS[GCE OS patches]
    Schema[Data classification]
  end
```

---

## F5 — Compute decision tree

```mermaid
flowchart TD
  Q1{Need a full OS<br/>or GPU you manage?}
  Q1 -->|yes| GCE[Compute Engine / MIG]
  Q1 -->|no| Q2{Many services,<br/>sidecars, operators?}
  Q2 -->|yes| GKE[GKE]
  Q2 -->|no| Q3{HTTP/events,<br/>scale to zero OK?}
  Q3 -->|yes| CR[Cloud Run]
  Q3 -->|no| Q4{Tiny glue?}
  Q4 -->|yes| CF[Cloud Functions]
  Q4 -->|no| Batch[Cloud Run Jobs / Batch / Dataflow]
```

**Say:** “Start at Cloud Run. Move left only when a constraint appears.”

---

## F6 — GCE managed instance group + LB

```mermaid
flowchart TB
  U[Users] --> GLB[Global HTTP S LB]
  GLB --> HC[Health checks]
  subgraph RegionalMIG["Regional MIG"]
    VMa[VM zone-a]
    VMb[VM zone-b]
  end
  GLB --> VMa
  GLB --> VMb
  T[Instance template] --> RegionalMIG
  AS[Autoscaler CPU 60%] --> RegionalMIG
```

---

## F7 — GKE vs Cloud Run (data plane)

```mermaid
flowchart LR
  subgraph GKE["GKE cluster"]
    CP[Regional control plane]
    NP[Node pool VMs]
    Pods[Pods]
    CP --- NP --> Pods
  end
  subgraph CR["Cloud Run"]
    Rev[Revision]
    Inst[Instances 0..N]
    Rev --> Inst
  end
```

**Say:** “GKE: you still have nodes. Cloud Run: Google maps requests to containers; you do not SSH anywhere.”

---

## F8 — VPC: global VPC, regional subnets

```mermaid
flowchart TB
  subgraph VPC["VPC production-custom"]
    subgraph SA["Subnet asia-south1 10.1.0.0/20"]
      API[Cloud Run egress / GCE]
    end
    subgraph SB["Subnet us-central1 10.2.0.0/20"]
      Batch[Batch workers]
    end
  end
  FW[Firewall: allow 443 from LB<br/>deny 22 from Internet]
  FW -.-> VPC
```

**Say:** “Unlike AWS, this VPC is global. Subnets stay regional. Firewalls are VPC-wide with tags or service accounts.”

---

## F9 — Private VM, NAT, Private Google Access

```mermaid
sequenceDiagram
  participant VM as GCE no public IP
  participant PGA as Private Google Access
  participant API as pubsub.googleapis.com
  participant NAT as Cloud NAT
  participant WWW as Internet
  VM->>PGA: GCS / Pub/Sub APIs
  PGA->>API: private path
  VM->>NAT: apt update / third-party
  NAT->>WWW: SNAT
```

---

## F10 — Load balancer taxonomy

```mermaid
flowchart TD
  In[Incoming traffic]
  In --> L7{HTTP/HTTPS?}
  L7 -->|yes, global Anycast| ALB[Application LB<br/>URL map, SSL, CDN, Armor]
  L7 -->|TCP/UDP, preserve IP| NLB[Passthrough NLB<br/>games, SIP]
  L7 -->|internal only| ILB[Internal LB]
  ALB --> BE[Backends: MIG / GKE / Cloud Run / GCS]
```

---

## F11 — Storage decision

```mermaid
flowchart TD
  S{Access pattern?}
  S -->|POSIX many writers| FS[Filestore]
  S -->|Block for one DB VM| PD[Persistent Disk]
  S -->|Unbounded objects, HTTP| GCS[Cloud Storage]
  S -->|Structured OLTP| DB[See database tree]
```

---

## F12 — Database decision tree (core exam figure)

```mermaid
flowchart TD
  W{Workload?}
  W -->|SQL transactions, one region| SQL[Cloud SQL]
  W -->|SQL, global, horizontal| SP[Spanner]
  W -->|Documents + live clients| FS[Firestore]
  W -->|Huge key-value / time series| BT[Bigtable]
  W -->|Sub-ms cache| RD[Memorystore]
  W -->|Analytics SQL| BQ[BigQuery]
```

---

## F13 — Spanner TrueTime (intuition, not a clock paper)

```mermaid
sequenceDiagram
  participant App
  participant L as Leader replica
  participant TT as TrueTime
  App->>L: Commit
  L->>TT: TT.now interval
  Note over L,TT: Wait until uncertainty elapsed
  L->>App: Commit timestamp
```

**Say:** “Spanner does not violate physics. It **waits out clock uncertainty** so commit order is globally meaningful.”

---

## F14 — Pub/Sub fan-out (the real-time backbone)

```mermaid
flowchart LR
  Prod[Producers<br/>API / IoT / GCE] --> T[Topic orders]
  T --> S1[Push sub → Cloud Run]
  T --> S2[Pull sub → Dataflow]
  T --> S3[BigQuery subscription]
  T --> DLQ[Dead letter topic]
  S1 -.->|nacks / max delivery| DLQ
```

**Say:** “One topic, many independent subscribers. Analytics must not block checkout.”

---

## F15 — At-least-once and idempotency

```mermaid
sequenceDiagram
  participant P as Publisher
  participant T as Topic
  participant C as Consumer
  participant DB as System of record
  P->>T: msg id=abc
  T->>C: deliver abc
  C->>DB: upsert order abc
  Note over C: Crash before ack
  T->>C: redeliver abc
  C->>DB: upsert order abc again
```

**Say:** “Redelivery is normal. Use idempotency keys in Cloud SQL/Spanner, not ‘hope for exactly once.’”

---

## F16 — Dataflow windows and watermarks

```mermaid
flowchart LR
  E[Unbounded events] --> W[Tumbling window 1 min]
  W --> WM[Watermark]
  WM --> L[Allowed lateness]
  L --> Pane[Triggered pane → BigQuery]
```

**Say:** “Event time ≠ processing time. Watermarks guess completeness; late data still happens — design for it.”

---

## F17 — BigQuery storage vs compute

```mermaid
flowchart TB
  GCS[Colossus / GCS-backed table files]
  Slot[Slot workers]
  User[SQL]
  User --> Slot --> GCS
```

**Say:** “You pay for **bytes scanned** (on-demand) or **slots**. Partition and cluster or you scan the lake.”

---

## F18 — Real-time ML scoring

```mermaid
flowchart LR
  Ev[Event] --> Feat[Feature lookup<br/>Feature Store / Redis]
  Feat --> EP[Vertex AI endpoint]
  EP --> Dec{Score}
  Dec -->|block| Risk[Risk path]
  Dec -->|allow| App[Continue]
  Dec --> Log[BigQuery training log]
```

---

## F19 — Observability of a request

```mermaid
flowchart LR
  LB[LB] --> CR[Cloud Run]
  CR --> SQL[Cloud SQL]
  CR --> PS[Publish Pub/Sub]
  PS --> WK[Worker]
  WK --> BQ[BigQuery]
```

```mermaid
sequenceDiagram
  participant U as User
  participant CR as Cloud Run
  participant PS as Pub/Sub
  participant W as Worker
  U->>CR: HTTP trace id=T
  CR->>PS: publish attrs trace=T
  PS->>W: push
  Note over CR,W: One trace in Cloud Trace
```

---

## F20 — CI/CD with federation (no JSON keys)

```mermaid
sequenceDiagram
  participant GH as GitHub Actions
  participant WIF as Workload Identity Federation
  participant AR as Artifact Registry
  participant Run as Cloud Run
  GH->>WIF: OIDC token
  WIF->>GH: short-lived GCP token
  GH->>AR: docker push
  GH->>Run: deploy revision
```

---

## F21 — Threat / trust boundaries

```mermaid
flowchart TB
  Inet[Internet] -->|Armor + IAP + HTTPS| LB
  LB --> Run[Cloud Run]
  Run --> SQL[(Cloud SQL private IP)]
  Run --> SA[Runtime SA]
  SA --> GCS[Bucket private]
  SA --> KMS[KMS decrypt]
```

**Say:** “The service account **is** the identity of the app. If it can `storage.objects.get` on `*`, so can an RCE.”

---

## F22 — Cost heatmap (whiteboard)

Draw a 2×2:

| | Low surprise | High surprise |
|---|---|---|
| **Low $** | Cloud Run scale-to-zero, Pub/Sub | BigQuery `SELECT *`, GCS egress |
| **High $** | Spanner, GPUs (expected) | Idle GKE nodes, unattended MIG |

---

## F23 — Student SaaS reference architecture

```mermaid
flowchart TB
  U[Browser] --> CDN[Cloud CDN]
  CDN --> LB[HTTPS LB + Armor]
  LB --> API[Cloud Run API]
  API --> SQL[(Cloud SQL)]
  API --> GCS[GCS signed URLs]
  API --> PS[Pub/Sub]
  PS --> IDX[Search indexer Cloud Run]
  PS --> ST[Dataflow]
  ST --> BQ[(BigQuery)]
  BI[Looker Studio] --> BQ
```

Use this as the **capstone skeleton**. Every extra box needs a sentence of justification.

---

## F24 — Consistency spectrum (place products)

```mermaid
flowchart LR
  Strong[Strong / external] --> Eventual[Eventual]
  Strong --> SP[Spanner]
  Strong --> SQL[Cloud SQL primary]
  Strong --> FS[Firestore document]
  Eventual --> Cache[Memorystore]
  Eventual --> CDN[Cloud CDN]
  Eventual --> BQ[BigQuery streaming buffer]
```

---

## Slide hygiene

- One figure per slide; font ≥ 18 pt after export.
- Never screenshot the live Console as a “figure” — it dates in months.
- When a product is renamed, keep the **arrows** (who talks to whom); update labels.
