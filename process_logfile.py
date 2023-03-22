
import json
from rdflib import Graph, Literal, Namespace, RDF, XSD, URIRef
import requests
from pathlib import Path
from datetime import datetime
import copy
from isodate import parse_datetime


    ###################################### TO CREATE THE COMMITS FROM THE TXT ################################################################





def isdictempty(dict):
    for value in dict.values():
        if value:
            return False
        else:
            return True


def info_between_elements(lst, A, B):
    #print(lst)
    result = []
    first_commit_flag = True
    found_A = False
    for i, elem in enumerate(lst):
        #print(elem)
        if A in elem:
            found_A = True
        if found_A:
            elem = elem.strip()
            #print(elem)
            result.append(elem)
        if B in elem:
            if first_commit_flag:
                first_commit_flag=False
                continue
            else:
                break
    result.pop(0)
    result.pop(1)
    #for result
    #print(result)
    return result

    ############################################ PROCESS THE INFORMATION FROM THE LOGFILE ###################################3

def process_logfile(path):
    commit = {"commit_ref": "", "author": "", "date":"" ,"changed_files": [], "parents" :""}
    history = []
    date_format = "%a %b %d %H:%M:%S %Y %z"
    with open(path,'r') as f:
        
        for line in f:
            line = line.strip()
            line = line.split(',')
            if line == ['']:
                continue
            #print(line)
            for index, element in enumerate(line):
                #print(index,element)
                if ('commit:' in element):
                    #print(element)
                    hash = element[element.index(":") + 1:]

                    commit["commit_ref"]  = hash
                if('Author:' in element): 
                    #print("adding person",line[index+1])
                    name = element[element.index(":") + 1:].strip()
                    commit["author"] = name

                if('Date:' in element):
                    date = element[element.index(":") + 1:]
                    #print(date)
                    date_obj = datetime.strptime(date, date_format)
                    date_string_with_t = date_obj.isoformat()
                    #print(date_string_with_t)                    
                    
                    commit["date"] = date_string_with_t
                
                if('Parents:' in element): 
                    #print(element[element.index(":") + 1:].strip())
                    parents = element[element.index(":") + 1:].strip()
                    commit["parents"] = parents

                if ('M' in element or 'D' in element or ' A ' in element or 'R100' in element):
                     
                    element = element.split()
                    if(element[1] == 'R100'):
                        files_and_action= [element[1],element[2],element[3]]
                        commit["changed_files"].append(files_and_action)
                    
                    if(Path(element[2]).suffix):
                        #print(element[2])
                        file_and_action = [element[1],element[2]]
                        #commit["changed_files"] = file_and_action
                        commit["changed_files"].append(file_and_action)
                    
                if('*' in element):
                    #print("now we are saving and")
                    #print("this is a ",commit)
                    history.append(commit)
                    commit = copy.deepcopy(commit)
                    
               
    #print(history)
    with open("history.txt", "w") as fp:
        for commit in history:
            json.dump(commit, fp, indent=4)
            fp.write('\n')
       

    
    ############################################ TO CREATE THE RDF TRIPPLES #############################################
    print("past the generation of the history")
    #commits = URIRef("http://dbpedia.org/resource/Commit_(version_control)")
    commits = URIRef("http://example.org/entity/commit")


    Author = URIRef("http://dbpedia.org/ontology/author")
    #Description = URIRef("http://dbpedia.org/ontology/description")
    Calendar_date = URIRef("http://dbpedia.org/ontology/Calendar_date")
    Entity = URIRef("http://example.org/entity/")

    #I am not sure if these are correct but we are working with it
    Parent = URIRef("http://example.org/entity/parents")
    Modify = URIRef("http://example.org/entity/modify")
    Add = URIRef("http://example.org/entity/add")
    Rename = URIRef("http://example.org/entity/rename")

    data=[]
    g = Graph()

    for commit in history:
        urirefstring = "http://example.org/"+ commit['commit_ref']
        urirefstring= urirefstring.replace(" ", "")
        commit_uri = URIRef(urirefstring)
        g.add((commit_uri, RDF.type, commits))
        g.add((commit_uri, Author, Entity+commit['author']))
        #only works when we print before??????
        print(commit['date'])
        g.add((commit_uri, Calendar_date, Literal(commit['date'], datatype=XSD.dateTime)))
        g.add((commit_uri, Parent,Entity+commit['parents'] ))
        #if it has been renamed, there is two files
        '''for action,file,_ in commit["changed_files"]:
            if (action == 'M'):
                #print("Modify") 
                g.add((commit_uri, Modify, Entity+file))
            elif (action == 'A'):
                #print("Modify") 
                g.add((commit_uri, Add, Entity+file))
            elif (action == 'R100'):
                #print("Modify") 
                g.add((commit_uri, Rename, Entity+file))'''
            


    # To save the graph to a file
    g.serialize(destination='commit_history_turtle.ttl', format='turtle')



    ################################################## TRYING TO FIGURE OUT HOW TO USE SPARQL ###################################3

    query = """
    SELECT ?subject ?predicate ?object
    WHERE {
    ?subject ?predicate ?object
    }
    """

    response = requests.get("http://localhost:3030/dbpedia/sparql", params={"query": query})
    ##TODO CHANGE THE http://example.com/sparql with the endpoint of our need.
    #print(response)

    if response.status_code == 200:
        results = response.json()
        
        # Process the results
    else:
        print("Query failed with status code", response.status_code)

        
        
        
    #question =  input("What is your question?")
