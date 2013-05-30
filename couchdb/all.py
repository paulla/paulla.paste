def function(doc):
    if (doc['doc_type'] == "Paste"):
        yield doc['created'], doc
