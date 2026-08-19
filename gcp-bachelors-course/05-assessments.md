# Assessments — GCP bachelor course

## Weekly exit tickets (2 minutes)

1. Name one thing **you** still patch on GCE that Google patches on Cloud SQL.
2. Why is a GCP VPC “global” but a subnet “regional”?
3. Pub/Sub delivers **at-least-once**. What must your consumer do?
4. Why is BigQuery a bad checkout database?
5. Give one reason Cloud Run is a better default than GKE for a class project.

---

## Quiz bank (MCQ — mark *one* best answer)

**Q1.** The unit of IAM and API enablement is the:  
A. Zone B. Organization only C. **Project** D. Billing account  

**Q2.** A zonal MIG survives:  
A. Zone outage B. **VM crash in that zone** C. Region outage D. IAM lockout  

**Q3.** Prefer for a single HTTPS microservice, bursty, scale-to-zero:  
A. Bare GCE B. **Cloud Run** C. Bigtable D. Filestore  

**Q4.** Firestore is a poor fit for:  
A. Presence B. Chat metadata C. **Ad-hoc SUM over 5 years of orders** D. Session docs  

**Q5.** Private GCE reaching `storage.googleapis.com` without a public IP uses:  
A. Cloud Armor B. **Private Google Access** C. Cloud CDN D. BigQuery slots  

**Q6.** Cloud Armor primarily sits with:  
A. Cloud SQL B. **HTTP(S) load balancing** C. Pub/Sub D. Artifact Registry  

**Q7.** Hotspotting in Bigtable is usually caused by:  
A. Too many IAM roles B. **Monotonic / low-cardinality row keys** C. Cloud NAT D. CDN TTLs  

**Q8.** Dataflow watermarks exist because:  
A. IAM is eventual B. **Event time ≠ processing time** C. GCS is eventually consistent D. VMs reboot  

**Q9.** The identity of a Cloud Run service to Pub/Sub should be:  
A. A downloaded JSON user key B. **Attached / runtime service account** C. `allUsers` D. FTP password  

**Q10.** On-demand BigQuery cost is driven mainly by:  
A. Number of JOINs in the text B. **Bytes scanned** C. Number of comments in SQL D. Console theme  

*(Faculty: mix true/false and short design questions from lecture notes.)*

---

## Short answers (5 marks each)

1. Contrast **organization policy** “disable public buckets” with **IAM** on one bucket.
2. Explain **why** peering is non-transitive and what problem that creates for three departments.
3. Give **two** reasons to put analytics on a **subscription** rather than in the checkout HTTP handler.
4. TrueTime in one paragraph: what problem does waiting on the uncertainty interval solve?
5. Sketch IAM for GitHub Actions → Artifact Registry **without** JSON keys.

---

## Midterm (90 minutes) — design + concepts

**Part A (30).** 15 MCQs from weeks 1–6.

**Part B (30).** Label F10 (load balancers) and F8 (VPC) from the figures pack; 2–3 sentence captions.

**Part C (30).** *Campus lost-and-found app:* photos, search, spam. Choose compute, storage, DB, network. List **three** abuse cases and one GCP control each. No more than **one** paragraph of marketing language.

**Rubric:** correct service for requirement (40%), failure/abuse (30%), IAM/network hygiene (20%), cost awareness (10%).

---

## Final exam (3 hours)

**Closed book.** Figures provided as unlabeled sketches.

1. **(20)** Database decision tree: six workloads → six products + one sentence each.
2. **(25)** Real-time fraud: complete the sequence diagram; annotate a 40 ms budget; fail-open vs fail-closed.
3. **(20)** Pub/Sub redelivery + DLQ + idempotency SQL.
4. **(20)** Observability: four golden signals for Cloud Run + Pub/Sub worker; one log-based metric.
5. **(15)** Cost: idle GKE vs Cloud Run; BigQuery `SELECT *`; egress from multi-region GCS. Rank and explain.

---

## Capstone rubric (100)

| Criterion | Points |
|---|---|
| Real-time path exists and is justified | 20 |
| IAM least privilege (runtime SA) | 15 |
| Failure modes / DLQ / retries | 15 |
| Data model (hot vs SoR vs analytics) | 15 |
| Observability (dashboard or traces) | 10 |
| Cost model at 10× | 10 |
| Tear-down / IaC or documented delete | 5 |
| Demo clarity | 10 |

**Fail capstone** if: public bucket with PII, JSON key in Git, or BigQuery used as OLTP.

---

## Viva questions (oral)

- Walk me through **one** packet from phone to BigQuery in your demo.
- If `asia-south1-a` dies, what still works?
- Who can publish to your topic?
- Show me the **idempotency** key.
- What did you **not** use GKE for, and why was that correct?

---

## Honor code prompt (put on every assignment)

“I did not enable public access on data stores containing student or personal data. I deleted billable resources after the lab. I can explain every resource in my screenshot.”
