from contextlib import closing
import copy
import json
from multiprocessing import Pool
import re
from urllib.parse import urlparse
import requests
from tqdm import tqdm


def is_uri(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_var(string):
    if string[0] == '?':
        return True
    else:
        return False


def query(args):
    q, idx = args
    payload = {'query': q, 'format': 'application/json'}
    try:
        jena_response = requests.get('http://localhost:3030/dbpedia/query', params={"query": q})
        #print(q,jena_response.json())
        return jena_response.status_code, jena_response.json(),q if jena_response.status_code == 200 else None, idx
        
    except:
        return 0, None, idx
    
def jena_formatting(item):

    if item.startswith("'") and item.endswith("'"):
        #print("we remove the stuff for item", item)
        item = item[1:-1]
        
    if is_uri(item):
        item = "<"+item+">"
        return item
    elif is_var(item):
        return item
    elif item.startswith("<") and item.endswith(">"):
        return item
    else: 
        item = "'"+item+"'"
        #print("we add thing on", item)
        return item

  
def mutli_var_complex_query(valid_walks):
    tripples = valid_walks[0::2]
    total = 0
    
    #get all edges 
    subject_predicate_object_list=[]
    #in what commits did izzrybz make
    #subject = ?u1 predicate = <author> object = izzyrybz
    
    for tripple in tripples:
        tripple = tripple.split()
        #print(tripple)
        subject_predicate_object_list.append([tripple[0], tripple[1], tripple[2]])
    
    #print(edge_list)

    #all_combinations_of_edges = .create_all_combinations_for_edges(edge_list)
    count=0
    used_triples=[]
    total = len(tripples)*len(tripples)
    
    list_with_elements_and_sparql_final=[]
    with tqdm(total=total)as pbar:
        for subject1,predicate1,object1 in subject_predicate_object_list:
            for subject2,predicate2,object2 in subject_predicate_object_list:
                #print(edge2,source2,dest2,subject1,predicate1,dest1)
                if (subject1 == subject2 and predicate1 == predicate2 and object1 == object2) or ((subject1, predicate1, object1, subject2, predicate2, object2) in used_triples) or ((subject2, predicate2, object2, subject1, predicate1, object1) in used_triples):
                    # If the two triples are the same or have been used before, skip to the next iteration
                    pbar.update(1)
                    continue
                else:
                    # If the two triples are different and have not been used before, add them to the used triples list and process them
                    print(subject1, predicate1, object1, subject2, predicate2, object2)
                    used_triples.append((subject1, predicate1, object1, subject2, predicate2, object2))
                    list_with_elements_and_sparql_final.append(complex_query_process(subject1,predicate1,object1, subject2,predicate2,object2))
                    pbar.update(1)

                
            #.__extend_edge
        #print(used_triples)
        #print(list_with_elements_and_sparql_final)
    with open('trash2.txt','w') as fp:
        for item in list_with_elements_and_sparql_final:
            for sparql in item:

                fp.writelines(sparql)
                fp.writelines('\n')
    return list_with_elements_and_sparql_final
     

def complex_query_process(subject1,predicate1,object1, subject2,predicate2,object2):
    output = set()
    var_node = None

    results = two_hop_graph(subject1,predicate1,object1, subject2,predicate2,object2)
    #print(result)
    #with tqdm(total=len(results)) as pbar:
    list_with_elements_and_sparql=[]
    if results is not None:
        for result in results:
            #valid_walks which we are trying append to has the format of
            # elements within query, such as ?u1 <http://example.org/action/delete> ?u3 
            # the sparql query SELECT * WHERE { + elements + }
            
            modified_query = result[0].replace('ASK WHERE {', '')
            modified_query_with_sparlq = result[0].replace('ASK WHERE {', 'SELECT * WHERE { ')
            
            if modified_query[-1] == '}':
                modified_query = modified_query.replace('}','')
            #print(str(modified_query))
            list_with_elements_and_sparql.append(str(modified_query_with_sparlq))
            list_with_elements_and_sparql.append(str(modified_query))
  
    return list_with_elements_and_sparql

def one_hop_graph( entity1_uri, relation_uri, entity2_uri):
        #print("THIS IS ENTITIES" ,entity1_uri,relation_uri, entity2_uri )
        if entity2_uri is None:
            entity2_uri = "?u1"
        else:
            entity2_uri = entity2_uri
        
        entity1_uri = jena_formatting(entity1_uri)
        relation_uri = jena_formatting(relation_uri)
        entity2_uri = jena_formatting(entity2_uri)


        query_types = [u"{ent2} {rel} {ent1}",
                       u"{ent1} {rel} {ent2}",
                       u"?u1 {rel} {ent1}",
                       u"{ent1} {rel} ?u1",
                       u"?u1 {type} {rel}",
                       u"?u1 {type} ?u2",
                       u"?u2 {rel} ?u1",
                       ]
        where = ""
        for i in range(len(query_types)):
            #print("THIS IS I", i)
                        
            where = where + u"UNION {{ values ?m {{ {} }} {{select ?u1 where {{ {} }} }} }}\n". \
                format(i,
                       query_types[
                           i].format(
                           rel=relation_uri,
                           ent1=entity1_uri,
                           ent2=entity2_uri,
                           type = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
                           prefix = ""
                           ))
        where = where[6:]
        
        #print("THIS IS WHERE WE HAVE THE UNION THING DO WE SEND IN MORE THAN ONE THING?",where)
        #where = .transform_q_into_jena(where)

        query = u"""{prefix}
SELECT DISTINCT ?m WHERE {{ {where} }} """.format(prefix="", where=where)
        
        response = requests.get("http://localhost:3030/dbpedia/sparql", params={"query": query})

        if response.status_code == 200:
            results = response.json()
            output = results["results"]["bindings"]
            return output,query
            # Process the results
        #else:
            #print("Query failed with status code", response.status_code)

def two_hop_graph_template(subject1,predicate1,object1,subject2,predicate2,object2):
    # print('kb two_hop_graph_template')
    query_types = [[0, u"{subject1} {predicate1} {object1} . {subject2} {predicate2} {object2}"],
                #[1, u"{object1} {predicate1} {subject1} . {object2} {predicate2} {subject2}"],
                [2, u"{subject1} {predicate1} {object1} . {object2} {predicate2} {subject2}"],
                #[3, u"{object1} {predicate1} {subject1} . {subject2} {predicate2} {object2}"],
                [4, u"{subject1} {predicate1} {object1} . {subject2} {predicate2} ?u3 "],
                #[5, u"{object1} {predicate1} {subject1} . {object2} {predicate2} ?u3"],
                [6, u"{subject1} {predicate1} ?u3 . {subject2} {predicate2} {object2}"],
                #[7, u"{object1} {predicate1} ?u3' . {subject2} {predicate2} {object2}"]
                ]
    #could use extension
    output = [[item[0], item[1].format(predicate1=predicate1, subject1=subject1,
                                    object1=object1, predicate2=predicate2,
                                        subject2=subject2,object2=object2, 
                                    type="<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>")] for item in query_types]

    return output

def two_hop_graph(subject1,predicate1,object1, subject2,predicate2,object2):
    # print('kb two_hop_graph')
    
    subject1 = jena_formatting(subject1)
    predicate1 = jena_formatting(predicate1)
    object1 = jena_formatting(object1)
    subject2 = jena_formatting(subject2)
    predicate2 = jena_formatting(predicate2)
    object2 = jena_formatting(object2)
    queries = two_hop_graph_template(subject1,predicate1,object1, subject2,predicate2,object2)
    
    output = None
    if len(queries) > 0:
        #ye this might get fucked
        output = parallel_query(queries)    
    # print('queries: ', queries)
    #print('output: ', output)
    return output

def parallel_query(query_templates):
    
    args = []
    for i in range(len(query_templates)):
        args.append(
            (u"{} ASK WHERE {{ {} }}".format("", query_templates[i][1]),
            query_templates[i][0]))
    with closing(Pool(len(query_templates))) as pool:
        query_results = pool.map(query, args)
        pool.terminate()
        results = []
        
        #query_results[number within the template][0] = statuscode
        #query_results[number within the template][1] = response
        #query_results[number within the template][2] = q
        for i in range(len(query_results)):
            if query_results[i][0] == 200:
                results.append((query_results[i][2], query_results[i][1]["boolean"]))
                
        
        return results

#idea send in the tripples from the whole sparql
#gives all types of things

q ='SELECT ?subject ?predicate ?object WHERE {?subject ?predicate ?object}'
args=q,0
query_results=query(args)
count=0
list=[]
for binding in query_results[1]['results']['bindings']:
    subject = binding['subject']['value']
    predicate = binding['predicate']['value']
    object = binding['object']['value']
    #print(subject)

    result = one_hop_graph(subject,predicate,object)
    data = result
    select_query=[]
    possible_queries=[]
    working_queries=[]
    m=[]
    for item in result:
        for index,elemt in enumerate(item):
            #print(index,elemt)
            m.append(int(item[index]['m']['value']))
        break
    #print(m,subject,predicate,object)
    
    
    query_lines = data[1].split('\n')
    for line in query_lines:
        #print(line)
        match = re.search(r'select\s+\?u1\s+where\s+\{[^}]+\}', line, re.IGNORECASE)
        if match:
            subquery = match.group()
            select_query.append(subquery)
                    
    #print(select_query)
    for index in m:
        possible_queries.append(select_query[index])
    
    for query in possible_queries:
        jena_response = requests.get('http://localhost:3030/dbpedia/query', params={"query": query})
        if jena_response.status_code == 200:
            response = jena_response.json()
            if len(response['results']['bindings'])> 1:
                working_queries.append(query)
    #print(working_queries)

    generated_queries=[]
    for query in working_queries:
        
        query_without_select = query.replace('select ?u1 where {','')
        query_without_select = query_without_select.replace('}','')
        dict={'correct':'x','query':query_without_select,"target_var":"?u1"}
        generated_queries.append(copy.deepcopy(dict))
        print("adding this dict",dict)
        dict.clear()
        print(dict)
    print(generated_queries)
    count=count+1
    full_entry={'answer':'','features':[],'generated_queries':generated_queries,'id':count,'query':'','question':''}

    list.append(full_entry)

with open('gold.json','w') as fp:
    json.dump(list, fp, sort_keys=True)

    
           
        
    

    

    
