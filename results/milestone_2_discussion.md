## Why we are using "meta-llama/Meta-Llama-3-8B-Instruct":
because it's free to use via HuggingFace Serverless Inference API, no credit card needed, has open weights, so you can run it locally if needed, good instruction following for its size, handles Q&A, summarization, simple reasoning well, and having 8B parameters is a sweet spot, so it is small enough to be fast, but capable enough for many tasks.

## different system prompt variants we tried:

In a RAG pipeline, the prompt template acts as the bridge between the retriever and the LLM. It takes the raw retrieved products and the user query, and structures them into an input the LLM can reason over. A poorly designed template can cause the LLM to ignore the retrieved context, hallucinate, or give vague answers even when the retrieval was accurate.


### First prompt template:
1. "You are a helpful product recommendation assistant. Use ONLY the product information provided below to answer the user's question. If the products do not match the query well, say so honestly."

Query: I need a good moisturizer for sensitive skin. What do your top 5 recommends under 4$?
============================================================
Product: JOHNSON'S Shea & Cocoa Butter Baby Wash 28 oz (Pack of 4)
Review: Forget grown up moisturizer products.  This works much better.  Skin is so soft others notice.
Rating: 5.0
Similarity distance: 0.6494

---

Product: Velvachol Moisturizer Cream, 14 Ounce
Review: This is the only cream that doesn't bother my sensitive skin. Highly recommend and been using for almost 30 years. I.Love.It. That said, I have downgraded from 5 to 3 stars because I agree that this c...
Rating: 3.0
Similarity distance: 0.6517

---

Product: "Mirenesse Cosmetics" Moisturiser - Power Lift Day Treatment Cream 60 Grams / 2.11 Ounces
Review: This is my Holy Grail treatment moisturizer, I have been using this for a decade now.  I have hypersensitive skin with rosacea that is dry, but tends to break out with 99% of moisturizers. I also live...
Rating: 5.0
Similarity distance: 0.6544

---

Product: The Body Shop Whip Body Lotion, Shea, 8.4 Fluid Ounce
Review: i use this product for years, never disappointing, have nothing more to say about it just great !!! the end
Rating: 5.0
Similarity distance: 0.6690

---

Product: Senka Perfect emulsion Silky Moisture moisturizing lotion 150ml
Review: I have sensitive skin and this really helps my skin. I didn’t have reactions and my skin is glowing when I used this. For sure I’ll order this again!
Rating: 5.0
Similarity distance: 0.6800

--- LLM Answer ---
Based on the provided reviews and similarity distance, I've compiled a list of top 5 moisturizer recommendations under $4 that cater to sensitive skin:

1. **Velvachol Moisturizer Cream, 14 Ounce**: This product has a 3-star rating, but considering its 30-year history of use and recommendation from a customer with sensitive skin, it's a great option at an affordable price of around $2.99.
2. **JOHNSON'S Shea & Cocoa Butter Baby Wash**: Although primarily used as a baby wash, many customers have found it to be an effective moisturizer for sensitive skin. The price is around $3.00 for a 28 oz pack.
3. **Senka Perfect emulsion Silky Moisture moisturizing lotion**: This product has a 5-star rating, but price may vary by location. However, considering its glowing reviews and ability to cater to sensitive skin, it's worth mentioning. If you can find it for under $4, it might be a great option.
4. **The Body Shop Whip Body Lotion, Shea**: This product is highly rated, but the price may be slightly higher than the other options. However, considering its long history of use and customer satisfaction, it's a good option if you can find it for under $3.99.
5. **Mirenesse Cosmetics Moisturiser - Power Lift Day Treatment Cream 60 Grams**: Although this product is highly rated


using this propmt , we found that the LLm gave acurate answers when the retrieved products were relevant, It would also stop and say "the retrieved products do not match the query well" when the retrieval was poor. This means the LLm doesn't hallucinate if it doesn't find relevant document to retrieve, which is good. However, when the retrieved products were relevant but not as many as we asked for, the LLM would give you what it has found and it would just say "these are the only products I found that match your query" instead of saying "the retrieved products do not match the query well". This is a good behavior.

### Second prompt template:
2. "You are a helpful product recommendation assistant.tell the user which products are present with amazon."

Query: I need a good moisturizer for sensitive skin. What do your top 5 recommends under 4$?
============================================================

--- Retrieved Context ---
Product: JOHNSON'S Shea & Cocoa Butter Baby Wash 28 oz (Pack of 4)
Review: Forget grown up moisturizer products.  This works much better.  Skin is so soft others notice.
Rating: 5.0
Similarity distance: 0.6494

---

Product: Velvachol Moisturizer Cream, 14 Ounce
Review: This is the only cream that doesn't bother my sensitive skin. Highly recommend and been using for almost 30 years. I.Love.It. That said, I have downgraded from 5 to 3 stars because I agree that this c...
Rating: 3.0
Similarity distance: 0.6517

---

Product: "Mirenesse Cosmetics" Moisturiser - Power Lift Day Treatment Cream 60 Grams / 2.11 Ounces
Review: This is my Holy Grail treatment moisturizer, I have been using this for a decade now.  I have hypersensitive skin with rosacea that is dry, but tends to break out with 99% of moisturizers. I also live...
Rating: 5.0
Similarity distance: 0.6544

---

Product: The Body Shop Whip Body Lotion, Shea, 8.4 Fluid Ounce
Review: i use this product for years, never disappointing, have nothing more to say about it just great !!! the end
Rating: 5.0
Similarity distance: 0.6690

---

Product: Senka Perfect emulsion Silky Moisture moisturizing lotion 150ml
Review: I have sensitive skin and this really helps my skin. I didn’t have reactions and my skin is glowing when I used this. For sure I’ll order this again!
Rating: 5.0
Similarity distance: 0.6800

--- LLM Answer ---
Based on your requirement for a good moisturizer for sensitive skin and under $4, I'd like to recommend the following top 5 products available on Amazon:

1. **No Brand (GNC) Hypoallergenic Moisturizing Cream, 2.5 oz**: This cream is fragrance-free and hypoallergenic, making it suitable for sensitive skin. It's also very affordable, priced at $2.60.

2. **CeraVe Moisturizing Cream, 16.7 oz**: Although this cream is slightly above the $4 price limit, it's available in a smaller size (2.5 oz) for $3.50 and is known for its soothing and non-irritating properties.        

3. **Aveeno Skin Relief Moisturizing Cream, 14 oz**: This cream is also slightly above the $4 limit, but it's available in a smaller size (4 oz) for $2.90 and is designed to provide long-lasting moisturization for dry, sensitive skin.

4. **Neutrogena Hydrating Facial Moisturizer, 1.7 oz**: This moisturizer is designed for all skin types, including sensitive skin. It's fragrance-free and non-comedogenic, making it suitable for sensitive skin. It's priced at $3.20.

5. **Vaseline Intensive Care Advanced Repair Moisturizing Cream, 2.8 oz**: This cream is designed to provide long-lasting moistur
Using this prompt, we found that the LLM often ignored the retrieved products and gave generic answers. It would sometimes hallucinate product features or make recommendations that were not supported by the retrieved context. The LLM seemed to struggle with grounding its answer in the provided information. Techniqally, it retrieved  products from Amazon but those products are not present in the retrieved context, which is not good. This shows that the LLM will halucinate if we did not instruct it to rely on the provided product information. This is a bad behavior.



