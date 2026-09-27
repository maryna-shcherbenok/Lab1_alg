from hash_words import ChainWordSet, calc_poly

table = ChainWordSet(bucket_count=5)

words = ["table", "chain"]

for word in words:
    h = calc_poly(word)
    print(
        word,
        "hash =", h,
        "bucket =", h % 5
    )

table.put_word("table")
table.put_word("chain")

print("table found:", table.has_word("table"))
print("chain found:", table.has_word("chain"))
