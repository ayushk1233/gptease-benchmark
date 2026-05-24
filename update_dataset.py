import json

with open('dataset.json', 'r') as f:
    data = json.load(f)

for item in data:
    item['target_style'] = item.get('target_style') or item['creator_persona']
    if item['conversation_length'] == "multi_turn":
        item['expected_progression'] = "slow_burn"
    else:
        item['expected_progression'] = "immediate"

with open('dataset.json', 'w') as f:
    json.dump(data, f, indent=4)

with open('data/eval_dataset_v1.jsonl', 'w') as f:
    for item in data:
        f.write(json.dumps(item) + '\n')
