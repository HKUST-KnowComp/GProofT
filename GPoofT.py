import spacy
import os
import time
import json
import pandas as pd
from datetime import datetime
from openai import AzureOpenAI
from transformers import T5Tokenizer, T5ForConditionalGeneration
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

LOAD_DATA_PATH = "INPUT_PATH"
OUTPUT_FILE_PATH = "OUTPUT_PATH"

AZURE_ENDPOINT = "YOUR_ENDPOINT"
API_VERSION = "YOUR_API_VERSION"
AZURE_API_KEY = "YOUR_API_KEY"
GPT_VERSION = "gpt-35-turbo"
GENERAL_INSTRUCTION = f'''You are a helpful assistant.'''

SPACY_MODEL = "en_core_web_sm"  
SPLIT_MODEL_NAME = "valhalla/t5-base-qg-hl"

SEARCH_SCOPE = ['https://www.googleapis.com/auth/cse']

SERVICE_ACCOUNT_FILE = "YOUR_SERVICE_ACCOUNT_PATH"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE"
API_KEY = "YOUR_API_KEY"

search_empty = 0
search_empty_list = []  
subclaim_invalid = 0
Internal_server_error = 0
Rate_limit_exceeded = 0
timeout = 0
connection_loss = 0
prompt_violence = 0
Unexpected = 0
request_Google_API = 0
# In the workshop, we load data from json files
# This is the starting and ending index that the user would like to process
index_start = 0
index_end = 1
all_missions = index_end - index_start
valid_state = True
valid_index = index_end
GPT_tokens = 0

def get_response(message, instruction, retry_attempt):
    global prompt_violence, Internal_server_error, Rate_limit_exceeded, timeout, connection_loss, Unexpected, GPT_tokens
    max_retry_attempt = 5
    try:
        client = AzureOpenAI(
            azure_endpoint = AZURE_ENDPOINT,
            api_version = API_VERSION,
            api_key = AZURE_API_KEY
        )
        response = client.chat.completions.create(
            model = GPT_VERSION,
            temperature = 0,
            messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": message}
            ]
        )
        GPT_tokens += response.usage.total_tokens
        return response.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        print(f"Exception occurred: {error_message}")
        if "Internal server error" in error_message:
            print("Internal server error, implementing retry...")
            Internal_server_error = Internal_server_error+1
            if retry_attempt < max_retry_attempt:
                time.sleep(2)
                return get_response(message,instruction,retry_attempt+1)
            else :
                print("Internal server error, retry attempts exceeded the maximum limit.")
                return None
        elif "Rate limit is exceeded" in error_message:
            print("Rate limit is exceeded, implementing retry...")
            Rate_limit_exceeded = Rate_limit_exceeded + 1
            time.sleep(2)
            if retry_attempt < max_retry_attempt:
                time.sleep(2)
                return get_response(message,instruction,retry_attempt+1)
            else :
                print("Rate limit is exceeded, retry attempts exceeded the maximum limit.")
                return None
        elif ("Remote end closed connection" in error_message) or ('Connection aborted' in error_message):
            print("Remote end closed connection without response. Retrying...")
            time.sleep(15)
            connection_loss = connection_loss + 1
            if retry_attempt < max_retry_attempt:
                return get_response(message,instruction,retry_attempt+1)
            else:
                print("Remote and closed connection without response. Retry attempts exceeded the maximum limit.")
                return None
        elif "timed out" in error_message:
            print("Request timed out. Retrying...")
            time.sleep(15)
            timeout = timeout + 1
            if retry_attempt < max_retry_attempt:
                return get_response(message,instruction,retry_attempt+1)
            else:
                print("Request timed out. Retry attempts exceeded the maximum limit.")
                return None
        elif "content management policy" in error_message:
            print("The prompt triggered Azure OpenAI's content management policy. Please modify your prompt and retry.")
            prompt_violence = prompt_violence+1
            time.sleep(2)
            if retry_attempt < max_retry_attempt:
                return get_response(message,instruction,retry_attempt+1)
            else:
                return None
        else:
            print("Some unexpected error occurred. Please notice.")
            Unexpected = Unexpected + 1
            return None
        
def generate_binary(subclaim_text):
    instruction = GENERAL_INSTRUCTION
    message = f'''according to the claim below, generate a binary question to CHECK THE FACTS in the claim: {subclaim_text}.
    Note that (1)ONLY REPLY THE QUESTION ITSELF!!! DO NOT INCLUDE ANYTHING ELSE!!!
    (2)Try to be more SPECIFIC, for example, if the claim is "Trump was a student.", 
    then you should AVOID GENERATING QUESTIONS CONTAINING PRONOUNS like "Was he a student?" 
    and instead generate "Was Trump a student?"
    (3)Try to NOTICE THE FACT in the claim and generate the binary question to CHECK THE FACT.
    For example: for a claim: "BJP MP Sushil Modi claims first five Indian education ministers were Muslims", the fact
    to be checked will be whether BJP MP Sushil really states the claim, instead of whether the first five Indian
    education ministers are Muslims. 
    Thus, you should generate "Did BJP MP Sushil Modi claim that the first five Indian education ministers were Muslims?"
    (4)Here are some EXAMPLES:
    If the claim is "Lionel Messi is loyal to FC Barcelona", 
    then the binary question should be "Is Lionel Messi loyal to FC Barcelona?".
    If the claim is "Biden has been to Beijing twice.", then the binary question should be "Has Biden been to Beijing twice?".'''
    return get_response(message,instruction,0)

def split_claim(claim):
    instruction = GENERAL_INSTRUCTION
    message = f'''Now I have a mission, and please help me deal with it: I have a claim: {claim}, 
    and I need to split it into different subclaims according to THE FACT it contains.  
    For example, if I have a claim: "Trump is a student born in 2005", then I want to split it into two parts
    (since there are two facts in it):"Trump is a student" and "Trump was born in 2005".
    For this special case, I need the response to be: "Trump is a student. Trump was born in 2005.".
    There are several RULES for the spliting process:
    (1)VERY IMPORTANT!!! PLEASE RETURN THE SUBCLAIMS ONLY (DO NOT INCLUDE ANYTHING ELSE!!!)
    and please separate the subclaims ONLY BY PERIOD instead of numbers.
    (2)VERY IMPORTANT: DO NOT GENERATE DUPLICATE SUBCLAIMS!!!!!!!
    (3)TRY TO BE MORE SPECIFIC and CLEAR(for example, if you want to generate "the orgarnization", 
    try to generate the orgarnization's name), and AVOID USING PRONOUNS. 
    (4)In most cases, the length of subclaims should be LESS THAN the length of the original claim. 
       And in most cases, each subclaims SHOULD NOT BE LONGER THAN 10 words.
    (5)Do not expand the meaning of the original claim or generate subclaims that do not exist in the original claim.
    (6)DO NOT generate a subclaim that is totally the same as the original claim UNLESS there is only one fact to check in the original claim.
    (7)For example: for the claim "BJP MP Sushil Modi claims first five Indian education ministers were Muslims",
    You should recognize that there is ONLY ONE FACT in the claim, which is whether BJP MP Sushil Modi really states the following claim
    , so the subclaim should be itself. At the same time, if there are several facts in the claim,
    you should split the claim into same amount of subclaim, each representing a fact.
    (8)If the claim is more that 30 words, try to generate at least 3 subclaims.
    (9)Here are some EXAMPLES:
    If the claim is "Lionel Messi is 36-year-old football player who has a long career.",
    then according to the claim, there are three facts introducing Lionel Messi, which are: 
    Lionel Messi is 36-year-old, Lionel Messi is a football player, LionelMessi has a long career.
    So what you should generate is: "Lionel Messi is 36-year-old. Lionel Messi is a football player. Lionel Messi has a long career.".'''
    res = get_response(message,instruction,0)
    return res


data = pd.read_json(LOAD_DATA_PATH, encoding='utf-8')

output = []
for num in range(index_start,index_end,1):
    print()
    print("progress:",str((num-index_start+1)*100/all_missions)+'%')
    print("processing:",data['claim'][num])
    claim_dic = {}
    claim = data['claim'][num]
    claim_dic['claim'] = claim
    questions = []
    claim_dic['claim_id'] = str(data['claim_id'][num])
    claim_dic['claim_date'] = data['claim_date'][num]
    claim_dic['speaker'] = data['speaker'][num]
    claim_dic['original_claim_url'] = data['original_claim_url'][num]
    claim_dic['reporting_source'] = data['reporting_source'][num]
    claim_dic['location_ISO_code'] = data['location_ISO_code'][num]
    claim_dic['evidence'] = []
    
    nlp = spacy.load(SPACY_MODEL)
    model_name = SPLIT_MODEL_NAME
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    subclaims = split_claim(claim)
    if isinstance(subclaims, str) == False:
        subclaim_invalid = subclaim_invalid + 1
        subclaims = str(subclaims)
    if isinstance(subclaims, str) and subclaims.strip():
        doc = nlp(subclaims)
        subclaims = list(doc.sents)
    
    #generate questions for a claim
    for subclaim in subclaims:
        if isinstance(subclaim, str) == False:
            subclaim = str(subclaim)
        question_dic = {}
        question_text = generate_binary(subclaim)
        question_dic['question'] = question_text
        claim_dic['evidence'].append(question_dic)
    
    SCOPES = SEARCH_SCOPE
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    authed_session = AuthorizedSession(credentials)
    claim_date_ddmmyyyy = data['claim_date'][num]
    
    if isinstance(claim_date_ddmmyyyy, str) == False:
        claim_date = 'null'
    else:
        claim_date = datetime.strptime(claim_date_ddmmyyyy, "%d-%m-%Y").strftime("%Y-%m-%d")
    
    for question_dic in claim_dic['evidence']:
        query = question_dic['question']
        num_results = 9
        if claim_date == 'null':
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={API_KEY}"
        else:
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={API_KEY}&dateRestrict=before:{claim_date}"
        request_Google_API = request_Google_API+1
        response = authed_session.get(url)
        search_results = response.json()
        
        majority_voting = []
        answers = []
        answer_dic = {}
        question_dic['url']=[]
        question_dic['scraped_text']=[]
        all_results = search_results.get('items',[])
        filtered_results = [item for item in all_results if 'snippet' in item]
        for item in filtered_results:
            instruction = GENERAL_INSTRUCTION
            scraped_text = item['snippet']
            retrieval_url = item['link']
            question_dic['url'].append(retrieval_url)
            question_dic['scraped_text'].append(scraped_text)
            message=f"According to the question: {query} and the approximate answer: {item['snippet']}, give me a yes or no answer.(only a word is needed)"
            answer=get_response(message,instruction,0)
            majority_voting.append(answer)
        if(len(majority_voting)==0):
            search_empty = search_empty+1
            valid_state = False
            valid_index = min(valid_index,num)
            search_empty_list.append(num)
            print("This combination causes the error:")
            print("SERVICE_ACCOUNT_FILE:",SERVICE_ACCOUNT_FILE)
            print("SEARCH_ENGINE_ID:",SEARCH_ENGINE_ID)
            print("API_KEY:",API_KEY)
        if(majority_voting.count('Yes')+majority_voting.count('Yes.')>=majority_voting.count('No')+majority_voting.count('No.')):
            print("final answer: Yes")
            answer_dic['answer'] = 'Yes'
        else:
            print("final answer: No")
            answer_dic['answer'] = 'No'
        answers.append(answer_dic)
        question_dic['answers'] = answers
    output.append(claim_dic)
    #PUT YOUR OUTPUT FILE PATH HERE
    output_file_path = f"<YOUR_PATH>/{num}.json"
    with open(output_file_path, "w", encoding='utf-8') as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)
    #PUT YOUR PATH HERE
    if os.path.exists(f"<YOUR_PATH>/{num-1}.json"):
        os.remove(f"<YOUR_PATH>/{num-1}.json")
    time.sleep(2)
    
output_file_path = OUTPUT_FILE_PATH
with open(output_file_path, "w", encoding='utf-8') as json_file:
    json.dump(output, json_file, ensure_ascii=False, indent=4)
print()
print("the index of claims that have been processed:", index_start, "~", index_end-1)
print("the number that search results are empty:", search_empty)
print("the index of the claims that cause the search results to be empty:", search_empty_list)
print("the number that the prompt violates the OpenAI policy:", prompt_violence)
print("the number that subclaim is invalid:", subclaim_invalid)
print("the number of requests made to Google API:", request_Google_API)
print("the number of timeout:", timeout)
print("the number of connection loss:", connection_loss)   
print("the number of Internal server error:", Internal_server_error)
print("the number of Rate limit exceeded:", Rate_limit_exceeded)
print("the number of unexpected error:", Unexpected)
print("GPT_tokens used:", GPT_tokens)
if(valid_state == True):
    print("The data is completely valid!")
else:
    print("The data is invalid from claim index "+str(valid_index))
