import jsonlines
import pandas

with jsonlines.open('labs/jsonl/alisa_selezneva.jsonl') as f:
    test = pandas.DataFrame(f)
print(test['complex_words'][123][0]['word'])
