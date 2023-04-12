
import json
from rdflib import Graph, Literal, Namespace, RDF, XSD, URIRef
import requests
from pathlib import Path
from datetime import datetime
import copy
from isodate import parse_datetime
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.plugins.stores import sparqlstore


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
    commit = {"commit_ref": "", "author": "", "description": "" ,"date":"" ,"changed_files": [], "parents" :[]} #, "branches":""
    history = []
    date_format = "%a %b %d %H:%M:%S %Y %z"
    with open(path,'r') as f:
        first_star=True
        
        for line in f:
            line = line.strip()
            line = line.split(',')
            parents_array=[]
            if line == ['']:
                continue
            #print(line)
            for index, element in enumerate(line):
                #print(index,element)
                if ('commit:' in element):
                    #print(element)
                    hash = element[element.index(":") + 1:]
                    commit["commit_ref"]  = hash
                elif('Author:' in element): 
                    #print("adding person",line[index+1])
                    name = element[element.index(":") + 1:].strip()
                    name = name.replace(' ','_')
                    commit["author"] = name
                    print(name)
                    '''if '@' in name:
                        name = name.split("@")[0]
                        commit["author"] = name
                    else:
                        print("we have commit without valid username")
                        commit["author"] = "invalid_username"'''
                    
                elif('Description:' in element): 
                    #print("adding person",line[index+1])
                    description = element[element.index(":") + 1:].strip()
                    commit["description"] = description

                elif('Date:' in element):
                    date = element[element.index(":") + 1:]
                    #print(date)
                    date_obj = datetime.strptime(date, date_format)
                    date_string_with_t = date_obj.isoformat()
                    #print(date_string_with_t)                    
                    
                    commit["date"] = date_string_with_t

                #Possible to add branch info here

                elif('Parents:' in element): 
                    
                    parents = element[element.index(":") + 1:].strip().split()
                    commit.setdefault("parents", []).extend(parents)
                    
                    '''print(element[element.index(":") + 1:].strip())
                    parents = element[element.index(":") + 1:].strip()
                    
                    parents= parents.split(' ')
                    
                    for parent in parents:
                        #parents_array.append(parents)
                        commit["parents"].add(parent)'''
                
                elif('Lines:' in element): 
                    #print(element[element.index(":") + 1:].strip())
                    parents = element[element.index(":") + 1:].strip()
                    commit["parents"] = parents

                #if ('M' in element or 'D' in element or ' A ' in element or 'R100' in element and not ':' in element):
                elif ('M' in element or 'D' in element or ' A ' in element or 'R100' in element):
                    
                    element = element.split()
                    element = [x for x in element if x != '|']
                    print("this is the problem", element)
                    
                    if(element[0] == 'R100'):
                        files_and_action= [element[0],element[1],element[2]]
                        commit["changed_files"].append(files_and_action)
                    
                    if(Path(element[1]).suffix):
                        #print(element[2])
                        file_and_action = [element[0],element[1].strip("'","")]
                        #commit["changed_files"] = file_and_action
                        commit["changed_files"].append(file_and_action)
                

                    
                elif('*' in element):
                    #print("now we are saving and")
                    #print("this is a ",commit)
                    if(first_star):
                        first_star=False
                        continue
                    else:
                        parents_array=[]
                        print(commit)
                        history.append(commit)
                        commit = copy.deepcopy(commit)
                        commit["changed_files"]=[]
                        commit["parents"]=[]
                    
               
    #print(history)
    with open("history.txt", "w") as fp:
        for commit in history:
            json.dump(commit, fp, indent=4)
            fp.write('\n')
    

    
    ############################################ TO CREATE THE RDF TRIPPLES #############################################
    print("past the generation of the history")
    #commits = URIRef("http://dbpedia.org/resource/Commit_(version_control)")
    Commits = URIRef("http://example.org/entity/commit")
    Commits_hash = URIRef("http://example.org/entity/hash/")

    Author = URIRef("http://example.org/ontology/author")
    Description = URIRef("http://example.org/ontology/description")
    Calendar_date = URIRef("http://example.org/ontology/Calendar_date")
    Entity = URIRef("http://example.org/entity/")

    #I am not sure if these are correct but we are working with it
    Parent = URIRef("http://example.org/entity/parents")

    #Branches = URIRef("http://example.org/entity/branches")

    Modify = URIRef("http://example.org/action/modify")
    Delete = URIRef("http://example.org/action/delete")
    Add = URIRef("http://example.org/action/add")
    Rename = URIRef("http://example.org/action/rename")

    data=[]
    g = Graph()

    for commit in history:
        urirefstring = Commits_hash+ commit['commit_ref']
        urirefstring= urirefstring.replace(" ", "")
        commit_uri = URIRef(urirefstring)
        g.add((commit_uri, RDF.type, Commits_hash))
        g.add((commit_uri, Author, Entity+commit['author']))
        #g.add((commit_uri, Description, Literal(commit['description'])))
        print(commit['date'])
        g.add((commit_uri, Calendar_date, Literal(commit['date'], datatype=XSD.dateTime)))

        '''for parent in commit['parents']:
            print(parent)
            g.add((commit_uri, Parent,Entity+parent ))'''
        #if it has been renamed, there is two files
        for array in commit["changed_files"]:
            if len(array) == 2:
                action=array[0]
                file=array[1]
                if (action == 'M'):
                    #print("Modify") 
                    g.add((commit_uri, Modify, Entity+file))
                elif (action == 'A'):
                    #print("Modify") 
                    g.add((commit_uri, Add, Entity+file))
                elif (action == 'D'):
                    #print("Modify") 
                    g.add((commit_uri, Delete, Entity+file))
            if len(array) == 3:
                action=array[0]
                file1=array[1]
                file2=array[1]
                if (action == 'R100'):
                    #print("Modify") 
                    g.add((commit_uri, Rename, Entity+file1+'-to-'+file2))
            


    # To save the graph to a file
    g.serialize(destination='commit_history_turtle_teammate_repo.ttl', format='turtle')



    ################################################## PUT THE GRAPH INTO JENA ###################################3

    return
    
    #okay cannot get this to work. moving on
    '''store = sparqlstore.SPARQLUpdateStore(endpoint_uri='http://localhost:3030/test2/update')
    g = Graph(store=store)
    print(g)
    g.parse("commit_history_turtle.ttl", format="turtle")

    store = SPARQLStore('http://localhost:3030/test2/update')
    g = Graph(store=store)
    g.parse('commit_history_turtle.ttl', format="ttl")'''

    '''
    # Set up the TDB dataset
    dataset_dir = "/path/to/my_dataset"
    tdb_dataset = TDB.factory.create_dataset(dataset_dir)

    # Load the TTL file into a Jena model
    model = ModelFactory.create_default_model()
    ttl_file = "/path/to/my_ttl_file.ttl"
    model.read(ttl_file, format="ttl")

    # Add the model to the TDB dataset
    with tdb_dataset.begin(write=True) as tdb_txn:
        tdb_txn.add(model)

    # Close the TDB dataset
    tdb_dataset.close()
    
    
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
        print("Query failed with status code", response.status_code)'''

        
        
        
    #question =  input("What is your question?")
