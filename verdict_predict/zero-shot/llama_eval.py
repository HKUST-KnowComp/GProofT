import json
import torch
import transformers
from huggingface_hub import login


# log in to the Hugging Face model hub
login('YOUR_ACCESS_TOKEN')

# set the device to GPU if available, otherwise use CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# set the cache directory and model ID
cache_dir = "YOUR_CACHE_DIR"
model_id = "YOUR_MODEL_ID"

# load the model and tokenizer
tokenizer = transformers.AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
model = transformers.AutoModelForCausalLM.from_pretrained(model_id, cache_dir=cache_dir)
model.to(device)

with open('dev.json', 'r') as file:
    data = json.load(file)

results = []

def generate_verdict(claim, question, answer):
    input_text = f"Claim: {claim} Question: {question} Answer: {answer} Based on the above question and answer, provide a verdict to the claim(can only be supported, refuted, irrelevant to the claim), remember to add a punct like format 'supported.' The verdict is:"

    tokenized_text = tokenizer(input_text, return_tensors='pt', truncation=True, max_length=1024)
    tokenized_text = {key: value.to(device) for key, value in tokenized_text.items()}
    generated_token = model.generate(**tokenized_text, max_new_tokens=200, output_scores=True, return_dict_in_generate=True)
    
    # get the generated token IDs
    generated_token_ids = generated_token['sequences'][0]

    # decode the generated token IDs into text
    input_length = tokenized_text['input_ids'].shape[1]
    generated_text = tokenizer.decode(generated_token_ids[input_length:], skip_special_tokens=True)
    return generated_text

def generate_justification(claim, final_verdict, qa_pairs):
    input_text = f"Claim: {claim}"
    for i, (question, answer) in enumerate(qa_pairs):
        input_text += f"Question {i+1}: {question} Answer {i+1}: {answer} "
    input_text += f"Based on the above questions and answers, we provide a final verdict to the claim: {final_verdict}. Justify this verdict with a one sentence explanation. The justification is:"

    tokenized_text = tokenizer(input_text, return_tensors='pt', truncation=True, max_length=1024)
    tokenized_text = {key: value.to(device) for key, value in tokenized_text.items()}
    generated_token = model.generate(**tokenized_text, max_new_tokens=200, output_scores=True, return_dict_in_generate=True)
    generated_token_ids = generated_token['sequences'][0]
    input_length = tokenized_text['input_ids'].shape[1]
    generated_text = tokenizer.decode(generated_token_ids[input_length:], skip_special_tokens=True)
    return generated_text

# process each entry in the data
for i, entry in enumerate(data[0]):
    claim = entry['claim']
    claim_id = i
    qa_pairs = [(q['question'], q['answers'][0]['answer']) for q in entry['questions']]
    urls = [q['answers'][0]['source_url'] for q in entry['questions']]
    
    # generate verdicts and evidence for each QA pair
    verdicts = []
    evidence = []

    for i, (question, answer) in enumerate(qa_pairs):
        # generate verdict
        response = generate_verdict(claim, question, answer)
        
        # process the response to extract the verdict
        def extract_first_sentence(response):
            # find the position of the first period
            end_pos = response.find('.')
            if end_pos != -1:
                # extract the first sentence
                if 'supported' in response[:end_pos]:
                    return 'supported'
                elif 'refuted' in response[:end_pos]:
                    return 'refuted'
                else:
                    return 'irrelevant to the claim'
            else:
                return 'irrelevant to the claim'  # if no period is found, return 'irrelevant to the claim'

        verdict = extract_first_sentence(response)

        verdicts.append(verdict)
        evidence.append({
            "question": question,
            "answer": answer,
            "url": urls[i],
            "label": verdict
        })

    # generate the final verdict
    if "supported" in verdicts and "refuted" in verdicts:
        final_verdict = "Conflicting Evidence/Cherrypicking"
    # if verdicts are all supported, then the final verdict is supported
    elif all([v == "supported" for v in verdicts]):
        final_verdict = "supported"
    # if verdicts are all refuted, then the final verdict is refuted
    elif all([v == "refuted" for v in verdicts]):
        final_verdict = "refuted"
    else:
        final_verdict = "not enough evidence"

    # generate justification
    justification = generate_justification(claim, final_verdict, qa_pairs)
    # extract the first sentence of the justification
    justification = justification[:justification.find('.')+1]

    # append the results to the list
    results.append({
        "claim_id": claim_id,
        "claim": claim,
        "evidence": evidence,
        "pred_label": final_verdict,
        "justification": justification
    })

# save the results to a JSON file
with open('YOUR_RESULTS_FILE.json', 'w') as file:
    json.dump(results, file, indent=4)

print("Processing complete. Results saved to 'results.json'.")
