import gzip
import json


arq = "200_0_1_w.json"
with gzip.open(arq+".gz", "rt", encoding="utf-8") as f:
    data = json.load(f)

print(data)

with open(arq, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)