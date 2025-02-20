from bson import ObjectId

def convert_mongo_document(document):
    if document is None:
        return None
    
    document['id'] = str(document.pop('_id'))
    return document
