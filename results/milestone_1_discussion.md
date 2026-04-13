# Retrieval Evaluation: BM25 vs Semantic Search
more details about query comparison found in `notebooks/queries_comparison.ipynb`
## Dataset
Amazon product reviews (hair care category).
Corpus: review title + review text, joined with product metadata.
Embedding model: all-MiniLM-L6-v2
BM25 implementation: rank_bm25 (BM25Okapi)
## Query Results and Observations
Will show one result example here for each method, teh rest can be found in  `notebooks/queries_comparison.ipynb`

### Q1 [KEYWORD]: "argan oil hair spray"

- **BM25 Top Result:** 
Product title:- Nadira Organics Virgin Argan Oil for Skin, Fac...	
Review:- Love this Argan oil, on my second bottle. Use ...	
Rating:- 5.0 
score:- 20.852335
- **Semantic Search Top Result:**
Product title:- Cuticle Nippers
Review:- The cuticle nipper kept getting stuck. It does...
Rating:- 1.0
Score:- 0.827

**Observation:** BM25 performs well here because the query contains exact product
terms. BM25 returns relevant results mentioning "argan oil" and "hair spray". Semantic search returns a less relevant result, likely because the query is very specific and the embedding model may not capture the exact product match as well as BM25.

### Q3 [KEYWORD] "sulfate free shampoo"
- **BM25 Top Result:**
Product title:- GK HAIR Global Keratin Moisturizing Shampoo an...
Review:- This is a great sulfate free shampoo and condi...
Rating:- 5.0
score:- 27.81
	
- **Semantic Search Top Result:**
Product title:- Chapfix Lip Balm for Men, SPF 15, with Beeswax...
Review:- I first saw these at Walmart. They charged 2 d...
Rating:- 5.0
Score:- 0.811089


**Observation:** BM25 performs well here because the query contains exact product
terms. BM25 returns relevant results mentioning ("sulfate free", "shampoo") Semantic search returns a less relevant result, likely because the query is very specific and the embedding model may not capture the exact product match as well as BM25.

### Q4 [SEMANTIC]: "something to make frizzy hair smooth"
- **BM25 Top Result:**
		
Product title:- Living Proof Full Shampoo
Review:- Makes my curly frizzy hair  beautiful and smooth
Rating:- 5.0
score:- 19.724033

- **Semantic Search Top Result:**
Product title:- Thinksport Safe Sunscreen SPF 50+ (6 ounce) (2...
Review:- Needed reef safe sunscreen for our upcoming tr...
Rating:- 5.0
Score:- 0.722

**Observation:** BM25 suppose to perform poorly here because the query is more about a concept (frizz control) rather than specific keywords. Semantic search should excel here by understanding the intent and retrieving reviews about products that help with frizzy hair, even if they don't contain the exact words "frizzy" or "smooth".
We had some issues with the semantic search results , still trying to debug and understand why the results were not as expected. We will update this section once we have more insights.


### Q9 [COMPLEX]: what do people say about this product causing hair loss
- **BM25 Top Result:**

Product title:- Roux Fermodyl Extra Strength Conditioner Vials
Review:- My hair is beautiful after using Fermodyl cond...
Rating:- 5.0
score:- 27.68

- **Semantic Search Top Result:**
Product title:- Brazilian Body Wave Bundles With Closure Virgi...
Review:- This hair is absolutely beautiful! Texture is ...
Rating:- 5.0
Score:- 0.782

**Observation:** BM25 may struggle here because the query is complex and may not contain specific keywords that match the reviews. Semantic search should perform better by understanding the intent behind the query and retrieving reviews that discuss hair loss in relation to the product, even if they don't use the exact phrase "causing hair loss". However, in our case, BM25 returned a relevant result mentioning hair condition after using the product, while semantic search returned a less relevant result, likely because the query is complex and the embedding model may not capture the nuances of the question as well as BM25 in this case.


### Q10 [COMPLEX]: "highly rated hair product that works for both men and women"
- **BM25 Top Result:**

Product title:- JOOYHOOM Professional Hair Cutting Scissors Se...	
Review:- Great price for a set of hair cutting kit! Wor...
Rating:- 5.0
score:- 36.37

- **Semantic Search Top Result:**
Product title:- Gel Toe Separators,XUZOU Toe Straighteners for...
Review:- They arrived very quickly and I used them righ...
Rating:- 5.0
Score:- 0.785

**Observation:** Similar to Q9, BM25 may struggle with the complexity of the query, while semantic search should ideally perform better by understanding the intent. However, in our case, BM25 returned a relevant result haur scissors, while semantic search returned a less relevant result, likely because the query is complex and the embedding model may not capture the nuances of the question as well as BM25 in this case.

### Overall, BM25 performed well for keyword-based queries, while semantic search had some issues with relevance, especially for more specific or complex queries. We will continue to investigate the semantic search results to understand why they were not as expected and see if there are ways to improve them.

## 4.4 Summary of Findings

### Strengths and Weaknesses

#### BM25
**Strengths:**
- Performs reliably on keyword-heavy queries where the user uses product-specific 
  terms that appear verbatim in reviews or product titles (e.g. "sulfate free shampoo", 
  "argan oil hair spray"). 
- Fast, lightweight, and requires no GPU or embedding model.
- Scores are interpretable: higher scores directly reflect term frequency and 
  document length normalization.
- Robust when the corpus is domain-specific and users know the terminology.

**Weaknesses:**
- Fails completely on paraphrased or conceptual queries. A query like 
  "something to make frizzy hair smooth" returns poor results because none 
  of those words appear in reviews that mention "frizz control" or "smoothing serum".
- No understanding of synonyms, intent, or context.
- Cannot handle multi-constraint queries (e.g. price range + hair type + product type).

#### Semantic Search
**Strengths:**
- Handles natural language and paraphrased queries well once the corpus is 
  correctly constructed with product title + review text.
- Captures conceptual similarity: queries about "heat protection" surface 
  reviews mentioning "flat iron damage" or "thermal shield" without exact matches.
- More robust to spelling variation and informal language.

**Weaknesses:**
- Highly sensitive to corpus construction. Embedding only review text (without 
  product title) caused completely irrelevant results, e.g. returning lip balm 
  and fake blood for "sulfate free shampoo".
- Sensitive to the similarity metric used. Using L2 distance instead of cosine 
  similarity on sentence transformer embeddings produced near-random rankings 
  with suspiciously similar distances across all results.
- Cannot filter by structured attributes like price, rating, or verified purchase 
  without additional post-processing.
- Slower and more resource-intensive than BM25, especially at 700k+ documents.

---

### Query Types That Are Challenging for Both Methods

- **Constraint-based queries:** Queries like "best leave-in conditioner for thick 
  curly hair under $20" require both semantic understanding and structured filtering. 
  Neither BM25 nor semantic search can enforce a price constraint natively. Both 
  methods may return highly relevant products that are outside the budget.

- **Opinion aggregation queries:** Queries like "what do people say about this 
  product causing hair loss" expect a synthesized answer across many reviews, not 
  a single retrieved document. Both methods return individual reviews, leaving the 
  user to read and aggregate themselves.

- **Negation queries:** Queries containing "without", "no", or "not" 
  (e.g. "shampoo with no sulfates and no parabens") are poorly handled by both 
  methods. BM25 ignores negation entirely and semantic search may not reliably 
  distinguish "contains sulfates" from "sulfate free" at the embedding level.

- **Comparative queries:** "Which is better, argan oil or coconut oil for dry hair" 
  requires reasoning across multiple documents and product types, which neither 
  method supports.

---

### Where Advanced Methods Would Help

- **Reranking:** A cross-encoder reranker (e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`) 
  applied on top of the top-20 BM25 or semantic candidates would significantly 
  improve precision for complex queries. Cross-encoders jointly encode the query 
  and document together, capturing relevance more accurately than bi-encoders.

- **Hybrid Retrieval (BM25 + Semantic):** Combining both methods via Reciprocal 
  Rank Fusion (RRF) would leverage the strengths of each: BM25 for exact keyword 
  recall and semantic search for conceptual coverage. This is especially useful 
  for medium-difficulty queries where neither method alone is sufficient.

- **Metadata Filtering:** Pre-filtering the corpus by structured fields (price range, 
  average rating, verified purchase) before retrieval would directly address 
  constraint-based queries. This is straightforward to implement with FAISS using 
  a filtered index or by post-filtering results.

- **RAG (Retrieval Augmented Generation):** For opinion aggregation and comparative 
  queries, retrieving the top-k documents and passing them to an LLM to synthesize 
  a coherent answer would dramatically improve usefulness. For example, retrieving 
  the top 10 reviews mentioning "hair loss" and asking an LLM to summarize 
  sentiment would directly serve the user's intent in a way that neither BM25 
  nor semantic search alone can.
