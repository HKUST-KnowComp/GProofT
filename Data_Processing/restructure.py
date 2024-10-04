import json

with open('YOUR_FILE_PATH.json', 'r') as file:
    data = json.load(file)

results = []
instruction = 'Based on the given questions and answers, provide a verdict to the claim(can only be one of Supported, Refuted, Conflicting Evidence/Cherrypicking or Not Enough Evidence) and a one sentence justification.'

# for i, entry in enumerate(data):
#     claim_id = i
#     claim = entry['claim']
#     # label = entry['label']
#     # justification = entry['justification']

#     # combine the claim and question-answer pairs into a single string
#     input_text = f"Claim: {claim}\n"
#     for i, QA_pair in enumerate(entry['questions']):
#         input_text += f"Question {i+1}: {QA_pair['question']}\nAnswer {i+1}: {QA_pair['answers'][0]['answer']}\n"
#     input_text += "The verdict and justification for the claim is:"
    
#     ouput_text = "" #f"{label}. Justification: {justification}"

#     results.append({"claim_id": claim_id, "instruction": instruction, "input": input_text, "output": ouput_text})

# with open('otherdata/0~499_dev_restructured.json', 'w') as file:
#     json.dump(results, file, indent=4)


for i, entry in enumerate(data):
    claim_id = i
    claim = entry['claim']
    # label = entry['label']
    # justification = entry['justification']

    # combine the claim and question-answer pairs into a single string
    input_text = f"Claim: {claim}\n"
    for i, QA_pair in enumerate(entry['evidence']):
        input_text += f"Question {i+1}: {QA_pair['question']}\nAnswer {i+1}: {QA_pair['answers'][0]['answer']}\n"
    input_text += "The verdict and justification for the claim is:"
    
    ouput_text = "" #f"{label}. Justification: {justification}"

    results.append({"claim_id": claim_id, "instruction": instruction, "input": input_text, "output": ouput_text})

with open('YOUR_FILE_PATH.json', 'w') as file:
    json.dump(results, file, indent=4)
