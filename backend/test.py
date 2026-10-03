from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

content = """# CedarGate fee schedule (2025-01)

## Payout terms and worked example

Payout: percent 0.50%, fixed fee 2.00 USD, minimum fee 2.00 USD.
"""

encoded = model.tokenizer(
    content,
    truncation=False,
    add_special_tokens=True,
)

actual_count = len(encoded["input_ids"])

print("Whitespace count:", len(content.split()))
print("Model token count:", actual_count)
print("Model input limit:", model.max_seq_length)
print("Exceeds limit:", actual_count > model.max_seq_length if model.max_seq_length else False)
