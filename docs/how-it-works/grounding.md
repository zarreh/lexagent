# Grounding

LexAgent's answers must be traceable to a statute section or a synthetic
precedent. Before an answer is returned, a citation verifier checks that every
cited source was actually retrieved. If a citation is missing or malformed, the
loop reroutes back to retrieval rather than publishing an ungrounded answer.
