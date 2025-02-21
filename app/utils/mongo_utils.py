from bson import ObjectId

def convert_mongo_document(document):
    if document is None:
        return None
    if isinstance(document, list):
        return [convert_mongo_document(item) for item in document]
    if isinstance(document, dict):
        new_doc = {}
        for key, value in document.items():
            if isinstance(value, ObjectId):
                new_doc[key] = str(value)
            elif isinstance(value, (dict, list)):
                new_doc[key] = convert_mongo_document(value)
            else:
                new_doc[key] = value
        if '_id' in new_doc:
            new_doc['id'] = str(new_doc.pop('_id'))
        return new_doc
    if isinstance(document, ObjectId):
        return str(document)
    return document
