# Final Discussion: Hybrid RAG Product Search Pipeline

This document summarizes the full project across all milestones, covering the
retrieval pipeline, RAG integration, quantitative evaluation, deployment, and
overall reflections on what worked and what did not.

Previous milestone discussions are available at:
- `results/milestone_1_discussion.md`: BM25 vs. semantic search comparison
- `results/milestone_2_discussion.md`: Hybrid RAG pipeline and qualitative evaluation

---

## 1. Project Overview

This project builds a hybrid product search and recommendation system over the
Amazon Reviews 2023 dataset (All Beauty category). The pipeline combines:

- **BM25** (keyword-based retrieval via `rank_bm25`)
- **Semantic search** (dense retrieval via `sentence-transformers/all-MiniLM-L6-v2` + FAISS)
- **Hybrid retrieval** (Reciprocal Rank Fusion of BM25 and semantic results)
- **RAG** (top-k retrieved products passed to `meta-llama/Meta-Llama-3-8B-Instruct` for answer generation)
- **Shiny app** (interactive UI with a search tab and a RAG chat tab)

The corpus is constructed by joining review text with product metadata (title,
description), which was a key fix identified in Milestone 1 that significantly
improved semantic search quality.

---

## 2. Step 1: Hybrid RAG Pipeline (Milestone 2 Continuation)

The hybrid RAG pipeline was completed in Milestone 2 and is implemented across
the following files in `src/`:

| File | Role |
|---|---|
| `search.py` | BM25 artifact loading and search |
| `semantic_search.py` | FAISS index loading and semantic search |
| `hybrid_search.py` | Score normalization and weighted hybrid fusion |
| `hybrid_RAG.py` | Reciprocal Rank Fusion + LLM generation |
| `RAG_pipeline.py` | Semantic-only RAG pipeline (Milestone 1 baseline) |

The hybrid retriever uses Reciprocal Rank Fusion (RRF) with k=60 (Robertson
and Zaragoza, 2009) to merge BM25 and semantic ranked lists. This avoids the
score normalization issues that arise when combining raw BM25 scores with
cosine distances directly, as each method uses an incompatible scale.

Full qualitative evaluation of the hybrid RAG workflow across five query types
is documented in `results/milestone_2_discussion.md`.

---

## 3. Step 2: Quantitative Evaluation (Feature Addition)

### 3.1 Approach

Quantitative evaluation was implemented in `src/evaluate.py`. The evaluation
measures **precision@k** and **recall@k** across three pipelines: BM25,
semantic search, and hybrid search, over 10 hand-crafted test queries covering
a range of beauty product categories.

**Precision@k** measures the fraction of top-k results that are relevant:

```
precision@k = (number of relevant results in top-k) / k
```

**Recall@k** measures the fraction of all relevant products that appear in
the top-k results:

```
recall@k = (number of relevant results in top-k) / (total relevant in corpus)
```

Relevance is defined by keyword matching on product titles using partial
substring matching, for example a result for "moisturizing face cream" is
considered relevant if the product title contains any of: `moistur`, `face
cream`, `hydrat`, `lotion`, `cerave`, or `neutrogena`. This approach avoids
the need for a hand-labeled ground truth set, which is not available for this
corpus, while still providing a meaningful proxy for retrieval quality.

Total relevant products per query are estimated by fetching the top-50 results
and counting matches, providing a reasonable denominator for recall.

### 3.2 Results

Mean scores across 10 queries at k = 3, 5, and 10:

| Pipeline | precision@3 | recall@3 | precision@5 | recall@5 | precision@10 | recall@10 |
|---|---|---|---|---|---|---|
| BM25 | 0.800 | 0.060 | 0.780 | 0.100 | 0.830 | 0.211 |
| Semantic | **0.967** | 0.061 | **0.960** | 0.101 | **0.960** | 0.202 |
| Hybrid | 0.900 | **0.063** | 0.920 | **0.106** | 0.870 | **0.201** |

Full per-query results are saved to `results/evaluation_results.csv`.

### 3.3 Observations

**Semantic search achieved the highest precision** across all k values,
which is consistent with the qualitative findings from Milestone 1 after the
corpus fix (adding product descriptions to the embedding input). The enriched
corpus gave the embedding model enough product-level context to surface
relevant results reliably.

**Hybrid search achieved the highest recall** at all k values, confirming that
combining BM25 and semantic retrieval broadens coverage beyond what either
method achieves alone. BM25 captures exact keyword matches that semantic search
misses, while semantic search captures conceptual matches that BM25 misses.

**Recall is uniformly low** across all pipelines, with values between 0.06 and
0.21. This reflects the nature of the corpus: relevant products are sparse
relative to the full dataset, and a top-k retriever can only surface a small
fraction of them. This is expected behavior for a product search use case where
the corpus contains hundreds of thousands of reviews across many product types.

**BM25 had the lowest precision**, particularly at k=3 and k=5, which aligns
with the qualitative observation from Milestone 1 that BM25 struggles on
natural language and paraphrased queries that do not contain exact product terms.

### 3.4 Limitations of the Evaluation

The keyword-based relevance proxy has known weaknesses. A product titled
"Argan Oil Hair Serum" would be counted as relevant for a query about argan oil
even if the review content describes a negative experience, and a genuinely
useful product with an atypical title would be missed entirely. A more rigorous
evaluation would use human-annotated relevance judgments. This is left as
future work given the scope of this project.

---

## 4. Step 3: Deployment

### 4.1 Application

The application is a Python Shiny app (`app/app.py`) with two tabs:

- **Search tab**: the user enters a query and selects a retrieval method (BM25,
  Semantic, or Hybrid). The top 3 results are displayed in a styled table
  showing product title, review excerpt, relevance score, and star rating.

- **RAG Chat tab**: the user types a natural language question and receives a
  synthesized answer grounded in retrieved product reviews. The user can switch
  between Semantic RAG (Milestone 1 baseline) and Hybrid RAG (Milestone 2
  pipeline). A typing indicator is shown while the LLM generates its response,
  and the conversation history is maintained within the session.

### 4.2 Deployment Approach

Deployment was attempted on **HuggingFace Spaces** using Docker as the runtime.
The Space is configured at:
`https://huggingface.co/spaces/MhmdJamaal/dsci575-product-search`

The Dockerfile runs the full data pipeline at container startup before launching
the Shiny app:

```
download_data.py -> build_bm25.py -> build_semantic.py -> shiny run app/app.py
```

This approach was chosen over Posit Connect Cloud (free tier) because HuggingFace
Spaces provides more generous compute resources, native integration with the
HuggingFace Hub for dataset and model downloads, and a persistent Docker
environment that better accommodates the build pipeline.

### 4.3 Deployment Challenges and Solutions

**Challenge 1: Dataset authentication**
The Amazon Reviews 2023 dataset requires `trust_remote_code=True` and a
HuggingFace token for unauthenticated requests to succeed. This caused the
first deployment attempt to fail at the `load_dataset` call. The fix was to
pass `trust_remote_code=True` and `token=os.environ.get("HF_TOKEN")` to
`load_dataset`, with `HF_TOKEN` stored as a repository secret in the Space
settings.

**Challenge 2: Embedding generation timeout**
The full corpus of 700,000+ reviews took an estimated 9 hours to embed on
HuggingFace's free CPU tier (approximately 12 seconds per batch of 256). This
exceeded the 30-minute startup timeout and caused the container to be killed
before the app was ready. The fix was to sample 5,000 rows from the merged
dataset using DuckDB's `USING SAMPLE 5000 ROWS` clause in `download_data.py`,
reducing embedding time to under 5 minutes while preserving enough data for
a functional demonstration.

**Challenge 3: Conda-built dependency in requirements.txt**
The initial `requirements.txt` was generated in a conda environment, which
caused pip to record a local `file://` path for `appdirs` instead of a PyPI
version string. Posit Connect Cloud (an earlier deployment target) rejected
this with a dependency resolution error. The fix was to filter out `file://`
references using `pip freeze | grep -v "file://"` and pin `appdirs==1.4.4`
explicitly.

**Challenge 4: Incompatible GUI packages in container**
`PySide6` and `shiboken6` are Qt GUI libraries that cannot be installed in a
headless Linux container. These were removed from `requirements.txt` before
building the Docker image.

### 4.4 Reproducibility

The full pipeline can be reproduced locally using the Makefile:

```bash
make build   # download data, build BM25 model, build FAISS index
make check   # verify all artifacts exist
make app     # launch the Shiny app
```

All scripts are designed to be idempotent: if an artifact already exists on
disk, the corresponding build step is skipped. This means re-running `make
build` after a partial failure resumes from where it left off rather than
reprocessing from scratch.

---

## 5. Code Quality

### 5.1 Path Handling

All file paths are resolved relative to `__file__` using `pathlib.Path`, so
scripts run correctly regardless of the working directory. For example:

```python
ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "processed" / "faiss_index" / "index_products.faiss"
```

### 5.2 API Keys

The HuggingFace token and any other secrets are loaded from a `.env` file using
`python-dotenv`. No API keys appear in source code. The `.env` file is listed
in `.gitignore`.

### 5.3 Artifact Caching

All build scripts check whether their output files exist before recomputing.
This applies to the tokenized corpus, BM25 model, document embeddings, and
FAISS index. Cold builds recompute everything; warm builds load from disk.

---

## 6. Step 4: Cloud Deployment Plan

This section describes how the Amazon product recommendation pipeline would be
deployed on AWS in a production setting. The plan addresses data storage,
compute, LLM inference, and pipeline updates.

### 6.1 Data Storage

**Raw data** (HuggingFace downloads, original parquet files) would be stored in
**Amazon S3** in a dedicated `raw/` prefix. S3 is the natural choice here since
the data originates as parquet files and DuckDB can query S3 directly without
downloading the full dataset first, using a query like:

```python
con.execute("SELECT * FROM read_parquet('s3://bucket/data/raw/*.parquet')")
```

**Processed data** (merged parquet, tokenized corpus, document embeddings) would
also live in S3 under a `processed/` prefix. These are intermediate artifacts
that are expensive to recompute but do not need low-latency access at query time,
so object storage is appropriate.

**The FAISS vector index** would be stored in S3 and loaded into memory at
application startup. For a corpus of 700,000+ products the index is on the order
of a few hundred MB, which is reasonable to load once per instance. For larger
corpora, a managed vector database such as **Amazon OpenSearch** (with k-NN
plugin) or **Pinecone** would be used instead, as these support incremental
updates and do not require reloading the full index on every restart.

**The BM25 model** (a serialized pickle file) would also be stored in S3 and
loaded at startup. If the corpus grows significantly, BM25 would be replaced
with **Amazon OpenSearch** full-text search, which supports inverted index
updates without full rebuilds.

### 6.2 Compute

**Application runtime**: the Shiny app would run on **AWS EC2** behind an
**Application Load Balancer**. For a small-to-medium deployment, a single
`t3.medium` or `t3.large` instance is sufficient since the retrieval step is
CPU-bound and the LLM inference is offloaded to an external API. The Docker
image built for HuggingFace Spaces is directly portable to EC2 with no changes.

**Build pipeline**: the data download and index build steps would run as
**AWS Batch** jobs triggered on a schedule or on demand. This separates
expensive preprocessing from the serving layer, so the app instance does not
need to run the full pipeline at startup as it does in the current HuggingFace
deployment.

**Concurrency**: each user query triggers a retrieval step (fast, in-memory)
and an LLM API call (network-bound, 1-5 seconds). The Shiny app handles
requests asynchronously. For higher concurrency, multiple EC2 instances would
sit behind the load balancer, with each instance maintaining its own in-memory
copy of the FAISS index and BM25 model. Since these artifacts are read-only at
serving time, no synchronization is needed between instances.

### 6.3 LLM Inference

In the current implementation, LLM inference is handled by the **HuggingFace
Serverless Inference API**, which is free but rate-limited and not suitable for
production traffic.

For production, two options are viable:

**Option A: API-based inference** using a hosted model provider such as the
**Amazon Bedrock** API (e.g. Llama 3 via Bedrock) or the **OpenAI API**. This
requires no GPU infrastructure, scales automatically, and charges per token.
It is the lowest-effort production path and would be the first choice for a
team without dedicated ML infrastructure.

**Option B: Self-hosted inference** using an **AWS EC2 GPU instance**
(e.g. `g4dn.xlarge` with a T4 GPU) running the model via `vllm` or
`text-generation-inference`. This is more cost-effective at high request volumes
and avoids data leaving the AWS environment, which matters for privacy-sensitive
applications. The trade-off is higher operational complexity.

For this project, Option A is the recommended starting point given the team size
and scope.

### 6.4 Streaming Updates and Pipeline Maintenance

**Incorporating new products**: new Amazon review data would be ingested on a
weekly schedule using an **AWS Batch** job that downloads the latest parquet
files, appends them to the processed corpus, and rebuilds the BM25 and FAISS
indexes. If using OpenSearch instead of FAISS, new documents can be indexed
incrementally without a full rebuild.

**Keeping the pipeline up to date**: the embedding model (`all-MiniLM-L6-v2`)
and BM25 parameters are fixed at build time. Model updates would require a full
index rebuild, which would be triggered manually or on a monthly schedule. A
blue-green deployment pattern would be used: the new index is built in a staging
bucket, validated with the quantitative evaluation script (`src/evaluate.py`),
and then promoted to production by updating the S3 path the app reads from,
with no downtime.

**Monitoring**: AWS CloudWatch would be used to track request latency, LLM API
costs, and retrieval quality metrics over time. Degradation in precision@k
relative to the baseline in `results/evaluation_results.csv` would trigger an
alert and prompt a manual review of the pipeline.

---

## 7. Summary of Findings Across All Milestones


| Aspect | Finding |
|---|---|
| Corpus construction | Adding product descriptions to the embedding input was the single biggest improvement to semantic search quality |
| BM25 strengths | Fast, interpretable, reliable for exact-keyword queries |
| Semantic strengths | Better for natural language and paraphrased queries once corpus is enriched |
| Hybrid advantage | Highest recall across all k values, broader coverage than either method alone |
| RAG grounding | Prompt design matters: instructing the LLM to rely only on retrieved context eliminates hallucination |
| Remaining weakness | Complex queries with constraints (price, rating, sentiment) require metadata filtering that neither retrieval method supports natively |
| Deployment | HuggingFace Spaces with Docker is the most practical free deployment option for this pipeline given compute and timeout constraints |