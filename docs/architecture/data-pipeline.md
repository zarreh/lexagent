# Data pipeline

1. `data/seed_statutes.py` extracts statute sections from public-domain TX and
   CA landlord–tenant law.
2. `data/seed_precedents.py` generates synthetic case summaries and outcomes.
3. `data/build_vector_store.py` embeds both corpora into Qdrant collections
   for retrieval.
