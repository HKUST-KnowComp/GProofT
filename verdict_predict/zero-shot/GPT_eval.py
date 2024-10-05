from openai import AzureOpenAI
import time
import json
import pandas as pd
from tqdm import tqdm
import os

#setup OpenAI API
client = AzureOpenAI(
  azure_endpoint = "YOUR_ENDPOINT",
  api_version = "YOUR_API_VERSION",
  api_key = "YOUR_API_KEY"
)
model_name="gpt-35-turbo"
#get response from LLM
def dispatch_openai_requests(
        messages_list,
        model=model_name,
        max_tokens=256,
):
    responses = []
    for x in messages_list:
        response = client.chat.completions.create(
            model=model,
            messages=x,
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
        )
        responses.append(response)
        time.sleep(1)
    return responses
#Read the dataset
input="$DATASET_PATH/FILE"#filename here
df = pd.read_json(input)
claim=df["claim"]
qa=df["questions"]

templates_verdict = "Supported,Refuted,Conflicting Evidence/Cherrypicking,Not Enough Evidence"
total=len(claim)
timeout_succeed = 1  # @param
timeout_failure = 10  # @param
retry_limit=5
out_filename = f'output/{model_name}_verdict_{input}_zeroshot.json'
out_directory = "output"
os.makedirs(out_directory, exist_ok=True)
prompt_template="Determine one most possible verdict for the claim \"{}\" from {}, based on the given question and answer pairs \"{}\", respond ONLY the verdict WITH NOTHING ELSE. "
def concatenation(qa_pair):
    return "\n".join(qa_pair)


with open(out_filename, 'w') as output_file:
    output_file.write("[\n")

total_usage=0
for i in tqdm(range(total)):
    retry =0
    while True:
        try:
            qa_pair=[f"Q: {qa[i][qca]['question']} A: {qa[i][qca]['answers'][0]['answer']}"for qca in range(len(qa[i]))]
            prompt_list = [[
                {"role": "user", "content": prompt_template.format(claim[i],templates_verdict,concatenation(qa_pair))},
            ]]
            if len(prompt_list) == 0:
                pred = []
                break

            pred = dispatch_openai_requests(
                messages_list=prompt_list,
                max_tokens=256,
            )
            for iteration in pred:
                total_usage +=iteration.usage.total_tokens
            #time.sleep(timeout_succeed)
            
            
            final_verdict = [x.choices[0].message.content for x in pred]
    
            evidence=[{"question":qa[i][qca]['question'],"answer":qa[i][qca]['answers'][0]['answer']} for qca in range(len(qa[i]))]
            results={
                "claim_id": i,
                "claim": claim[i],
                "pred_label": final_verdict[0],
                "evidence": evidence,
            }
            output = open(out_filename, mode='a+')
            json.dump(results, output, indent=4)
            if i!=total-1:
                output.write(",\n")
            output.close()
            break
        except Exception as e:
            error_message = str(e)
            if "Internal server error" in error_message:
                print("Internal server error, implementing retry...")
                retry = retry+1
                if retry < retry_limit:
                    time.sleep(2)
                else:
                    print("Internal server error, retry attempts exceeded the maximum limit.")
                    break
            if "Rate limit is exceeded" in error_message:
                print("Rate limit is exceeded, implementing retry...")
                retry = retry + 1
                if retry < retry_limit:
                    time.sleep(2)
                else :
                    print("Rate limit is exceeded, retry attempts exceeded the maximum limit.")
                    break
            if "Remote end closed connection without response" in error_message:
                print("Remote end closed connection without response. Retrying...")
                time.sleep(15)
                retry = retry + 1
                if retry < retry_limit:
                    time.sleep(1)
                else:
                    print("Remote and closed connection without response. Retry attempts exceeded the maximum limit.")
                    break
            if "content management policy" in error_message:
                print("The prompt triggered Azure OpenAI's content management policy. Please modify your prompt and retry.")
                evidence=[{"question":qa[i][qca]['question'],"answer":qa[i][qca]['answers'][0]['answer']} for qca in range(len(qa[i]))]
                results={
                    "claim": claim[i],
                    "pred_label": "Not Answerable",
                    "evidence": evidence,
                }
                output = open(out_filename,encoding="utf-8", mode='a+')
                json.dump(results, output, indent=4)
                if i!=total-1:
                    output.write(",\n")
                output.close()
                break
            else:
                if retry < retry_limit:
                    time.sleep(2)
                else:
                    print(error_message)
                    break
    
with open(out_filename, 'a+') as output_file:
    output_file.write("\n]")

print("The prediction has completed, the total token uasge is",total_usage, "the average usage of each claim is",total_usage/total)
