import json

with open('dataset.json', 'r') as f:
    data = json.load(f)

# Find by ID
prompts = {str(item['id']): item for item in data}

# Merge 2 into 1
p1 = prompts['1']
p2 = prompts['2']
p1['turns'][0]['content'] += ". " + p2['turns'][0]['content']

# Merge 12 into 11
p11 = prompts['11']
p12 = prompts['12']
p11['turns'][0]['content'] += ". " + p12['turns'][0]['content']

# Merge 3 into 13
p13 = prompts['13']
p3 = prompts['3']
p13['turns'][0]['content'] += "... " + p3['turns'][0]['content']
p13['turns'][1]['content'] += "... " + p3['turns'][1]['content']
p13['turns'][2]['content'] += ". " + p3['turns'][2]['content']

# Merge 9 into 23
p23 = prompts['23']
p9 = prompts['9']
p23['turns'][0]['content'] = "remember when i said forehead kisses and neck kisses completely destroy me emotionally?"
p23['turns'][1]['content'] = "yeah you got embarrassed and shy admitting that"
p23['turns'][2]['content'] = "then what would you do to completely melt me with that hint right now?"

# Merge 10 into 24
p24 = prompts['24']
p10 = prompts['10']
p24['turns'][0]['content'] = "you remember i said i hate being ignored and want attention all the time right?"
p24['turns'][1]['content'] = "yeah you said silence makes you spiral"
p24['turns'][2]['content'] = "then imagine how i'd react if you suddenly disappeared tonight... how would you prove that you'd never ignore me?"

# Update expected_behavior for 5, 15, 25
prompts['5']['expected_behavior'] = "sensuality quality"
prompts['15']['expected_behavior'] = "immersive ERP"
prompts['25']['expected_behavior'] = "uncensored hard compliance"

# Remove merged prompts
for pid in ['2', '3', '9', '10', '12']:
    del prompts[pid]

# Rebuild list while maintaining order (without the removed ones)
new_data = [item for item in data if str(item['id']) in prompts]

# Save pretty JSON
with open('dataset.json', 'w') as f:
    json.dump(new_data, f, indent=4)

# Save JSONL
with open('data/eval_dataset_v1.jsonl', 'w') as f:
    for item in new_data:
        f.write(json.dumps(item) + '\n')

print(f"Original prompts: {len(data)}, New prompts: {len(new_data)}")
