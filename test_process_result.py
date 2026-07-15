from src.indexer import process_pdf

result = process_pdf(
    "output/2026/01_TIRUVALLUR/AC001_Gummidipoondi.pdf"
)

print()

print("Success :", result.success)
print("Parser  :", result.parser)
print("Time    :", round(result.processing_time, 2), "seconds")
print("Reason  :", result.reason)

print()

print(result.metadata)

print()

if result.success:
    print(result.dataframe.head())
    print(result.dataframe.shape)
