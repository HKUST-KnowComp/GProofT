
import json

data1 = []
data2 = []
# open the prediction jsonl file and read the data
with open('YOUR_FILE_PATH.jsonl', 'r') as f:
    for line in f:
        line_data = json.loads(line)
        data1.append(line_data)

# open the evidence json file and read the data
with open('YOUR_FILE_PATH.json', 'r') as f:
    data2 = json.load(f)


results = []
for i, entry in enumerate(data1):
    claim_id = i
    claim = data2[i]['claim']
    # get the label from the predict:
    label = entry['predict'].split('.')[0]
    justification = entry['predict'].split(': ')[1]
    qa_pairs = [(qa['question'], qa['answers'][0]['answer']) for qa in data2[i]['evidence']]
    url = [qa['url'] for qa in data2[i]['evidence']]
    scraped_text = [qa['scraped_text'] for qa in data2[i]['evidence']]

    evidence = []
    for j, (question, answer) in enumerate(qa_pairs):
        evidence.append({
            "question": question,
            "answer": answer,
            "url": url[j],
            "scraped_text": scraped_text[j]
        })

    results.append({
        "claim_id": claim_id,
        "claim": claim,
        "pred_label": label,
        # "justification": justification,
        "evidence": evidence
    })

with open('YOUR_RESULTS_FILE.json', 'w') as f:
    json.dump(results, f, indent=4)
