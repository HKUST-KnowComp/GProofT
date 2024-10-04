import os
import json

folder_path = 'YOUR_FOLDER_PATH'

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path) and filename.endswith('.json'):
        with open(file_path, 'r') as f:
            data1 = json.load(f)
        
        if 'dev' in filename:
            with open('YOUR_FILE_PATH.json', 'r') as f:
                data2 = json.load(f)
            results = []
            for i, entry in enumerate(data1):
                claim_id = i
                claim = data2[i]['claim']
                # get the label from the predict:
                label = data1[i]['pred_label']
                qa_pairs = [(qa['question'], qa['answers'][0]['answer']) for qa in data2[i]['questions']]
                url = [qa['url'] for qa in data2[i]['questions']]
                scraped_text = [qa['scraped_text'] for qa in data2[i]['questions']]

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

            result_path = os.path.join('zs_evidence', filename)
            with open(result_path, 'w') as f:
                json.dump(results, f, indent=4)
        elif 'baseline_dev' in filename:
            with open('YOUR_FILE_PATH.json', 'r') as f:
                data2 = json.load(f)
            results = []
            for i, entry in enumerate(data1):
                claim_id = i
                claim = data2[i]['claim']
                # get the label from the predict:
                label = data1[i]['pred_label']
                qa_pairs = [(qa['question'], qa['answer']) for qa in data2[i]['evidence']]
                url = [qa['url'] for qa in data2[i]['evidence']]
                # scraped_text = [qa['scraped_text'] for qa in data2[i]['questions']]

                evidence = []
                for j, (question, answer) in enumerate(qa_pairs):
                    evidence.append({
                        "question": question,
                        "answer": answer,
                        "url": url[j],
                        # "scraped_text": scraped_text[j]
                    })

                results.append({
                    "claim_id": claim_id,
                    "claim": claim,
                    "pred_label": label,
                    # "justification": justification,
                    "evidence": evidence
                })

            result_path = os.path.join('zs_evidence', filename)
            with open(result_path, 'w') as f:
                json.dump(results, f, indent=4)
        else:
            with open('YOUR_FILE_PATH.json', 'r') as f:
                data2 = json.load(f)
            results = []
            for i, entry in enumerate(data1):
                claim_id = i
                claim = data2[i]['claim']
                # get the label from the predict:
                label = data1[i]['pred_label']
                qa_pairs = [(qa['question'], qa['answers'][0]['answer']) for qa in data2[i]['questions']]
                # url = [qa['url'] for qa in data2[i]['questions']]
                # scraped_text = [qa['scraped_text'] for qa in data2[i]['questions']]

                evidence = []
                for j, (question, answer) in enumerate(qa_pairs):
                    evidence.append({
                        "question": question,
                        "answer": answer,
                        # "url": url[j],
                        # "scraped_text": scraped_text[j]
                    })

                results.append({
                    "claim_id": claim_id,
                    "claim": claim,
                    "pred_label": label,
                    # "justification": justification,
                    "evidence": evidence
                })

            result_path = os.path.join('zs_evidence', filename)
            with open(result_path, 'w') as f:
                json.dump(results, f, indent=4)
