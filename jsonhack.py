import json as JSON
bruh = {'7ec7764a12e8410e85ce268f6bd7daf2': [{'id': '4bb966ef-87f4-483b-8f44-ddb5ad4f9f6e', 'category': 'Available', 'date': '2021-02-15', 'time': '21:04', 'done': False}, {'id': '7f1caec6-5b9e-4589-a5ba-2e4516ac9eac', 'category': 'Available', 'date': '2021-02-18', 'time': '09:07', 'done': False}]}

#goal to retrieve the tutor id, so need to split
jsonbruh = JSON.dumps(bruh)
# print(jsonbruh)
stringed = str(jsonbruh)
# print("this is string versioned",stringed)
splitted = stringed.split("\"")
# print(splitted)
tutor_id = splitted[1]
#
replacedquotes = jsonbruh.replace("\'", "\"")
#
dictparsed = JSON.loads(replacedquotes)
#
print(dictparsed[tutor_id])

todoList = dictparsed[tutor_id]
print(type(todoList))
print(todoList[1])