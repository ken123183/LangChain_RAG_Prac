import traceback
try:
    from langchain.chains import RetrievalQA
    print("RetrievalQA OK")
except Exception as e:
    with open("err.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
