import copy
import json
import random

# Generate a random float between 0 and 1
print(random.random())

# Generate a random integer between 1 and 10
print(random.randint(1, 10))



# Choose a random element from a list
question = "How many users have made commits that deleted a file?"

answer= "?u2 <http://example.org/ontology/author> ?u1"

features = ["list","multivar"]
count=30

#run the q for some of the questions

with open('result.txt', 'r') as fp:
    result = fp.readlines()


possible_answer_list=[]
result= result[0::2]
for i in range(random.randint(1, 10)):
    possible_answer = result[random.randint(1,len(result))]
    if possible_answer == answer:
        continue
    else:
        possible_answer_list.append(possible_answer.replace('\n',''))


#print(possible_answer_list)



generated_queries=[]
fulllist=[]

dict={'correct':'true','query':answer,"target_var":"?u1"}
generated_queries.append(copy.deepcopy(dict))
dict.clear()
for query in possible_answer_list:
    dict={'correct':'false','query':query,"target_var":"?u1"}
    generated_queries.append(copy.deepcopy(dict))
    print("adding this dict",dict)
    dict.clear()
    print(dict)


print(generated_queries)


full_entry={'answer':'correct','features':features,'generated_queries':generated_queries,'id':count,'query':'SELECT COUNT( DISTINCT ?u1) WHERE {'+answer+'}','question':question}

fulllist.append(full_entry)

with open('potato.json','a') as fp:
    json.dump(fulllist, fp, sort_keys=True)

''',{
        "answer": "correct",
        "features": ["multivar",
        "count"],
        "generated_queries": [
            {
                "correct": true,
                "query": " ?u2 <http://dbpedia.org/ontology/author> ?u1. ?u2 <http://example.org/action/modify> ?u3",
                "target_var": "?u1"
            }
        ],
        "id": "13",
        "query": "SELECT COUNT(DISTINCT ?u1) WHERE {?u2 <http://dbpedia.org/ontology/author> ?u1. ?u2 <http://example.org/action/modify> ?u3}",
        "question": "How many users have made commits that changed files??"
    },'''