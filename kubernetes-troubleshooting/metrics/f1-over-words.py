# # F1 Over Words Metric

# # F1 over words evaluates semantic overlap between two texts by:

# # Comparing word-level matches (not character or sentence level)

# # Being order-agnostic ("CPU limits to 2 cores" vs "2 cores for CPU" get partial credit)

# # Ignoring case and punctuation (treats "DNS" and "dns" as identical)


# from collections import Counter
# import re

# def f1_over_words(actual, golden):
#     actual_words = re.findall(r'\w+', actual.lower())
#     golden_words = re.findall(r'\w+', golden.lower())

#     actual_counts = Counter(actual_words)
#     golden_counts = Counter(golden_words)

#     common = sum((actual_counts & golden_counts).values())
#     if common == 0:
#         return 0.0

#     precision = common / sum(actual_counts.values())
#     recall = common / sum(golden_counts.values())

#     if precision + recall == 0:
#         return 0.0

#     f1 = 2 * precision * recall / (precision + recall)
#     return f1
