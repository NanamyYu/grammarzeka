import json
import jsonlines
import pandas


# Загрузка сообщений
with jsonlines.open('labs/jsonl/alisa_selezneva.jsonl') as f:
    sentences = pandas.DataFrame(f)

with open('stats.json', 'w') as f:
        json.dump({i: (0, 0) for i in range(sentences.shape[0])}, f)
with open('history.json', 'w') as f:
        json.dump({}, f)