import sys
sys.path.append("")

from pymongo import MongoClient
from typing import Optional, Dict, Any, List, Literal
import json
from bson import ObjectId
from src.Utils.utils import read_config

class MongoDatabase:
    def __init__(self, config_path: str):
        # Load the YAML configuration file using the provided utility function
        self.config_path = config_path
        self.config = read_config(path=self.config_path)

        # Initialize MongoDB connection
        print("uri", str(self.config['mongodb']['uri']))
        self.client = MongoClient(str(self.config['mongodb']['uri']))
        # self.client = MongoClient(host = str(self.config['mongodb']['uri'])) 
        print("Mongo info", self.client.server_info() )
        self.db = self.client[self.config['mongodb']['database']]
        self.collection = self.db[self.config['mongodb']['collection']]

    def create_document(self, data: Dict[str, Any]) -> str:
        # Insert a new document and return the automatically generated document ID
        result = self.collection.insert_one(data)
        return str(result.inserted_id)


    def get_documents(self, filters: Dict[str, Any], page: int = 1, limit: int = 10, 
                      sort:Literal['asc', 'desc']='asc') -> List[Dict[str, Any]]:
        # Apply filters and pagination to get documents
        if sort == 'asc':
            sort_idx = 1
        else:
            sort_idx = -1

        skip = (page - 1) * limit
        documents = self.collection.find(filters).sort("created_at", sort_idx).skip(skip).limit(limit)
        return list(documents)

    
    def get_document_by_id(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a document by its MongoDB _id.

        :param document_id: The _id of the document to retrieve.
        :return: The document as a dictionary, or None if not found.
        """
        # Convert document_id from string to ObjectId
        object_id = ObjectId(document_id)
        
        # Find the document by its _id
        document = self.collection.find_one({'_id': object_id})
        
        return document if document else None
    
    
    def get_all_document_ids(self) -> List[str]:
        # Get the _id of all documents in the collection
        document_ids = self.collection.find({}, {"_id": 1})
        return [str(doc["_id"]) for doc in document_ids]
    
    def delete_document_by_id(self, document_id: str) -> bool:
        # Delete a document based on its MongoDB _id
        result = self.collection.delete_one({'_id': ObjectId(document_id)})
        return result.deleted_count > 0

    def update_document_by_id(self, document_id: str, update_fields: Dict[str, Any]) -> bool:
        """
        Update a document based on its MongoDB _id with the provided update fields.

        :param document_id: The _id of the document to update.
        :param update_fields: A dictionary containing the fields to update and their new values.
        :return: True if the update was successful, False otherwise.
        """
        # Convert document_id from string to ObjectId
        object_id = ObjectId(document_id)
        
        # Update the document based on its _id
        result = self.collection.update_one(
            {'_id': object_id},
            {'$set': update_fields}
        )
        
        # Return whether the document was updated
        return result.modified_count > 0
    

    def delete_all_documents(self) -> bool:
        """
        Delete all documents in the collection.

        :return: True if documents were deleted, False otherwise.
        """
        result = self.collection.delete_many({})
        return result.deleted_count > 0

    def start_change_stream(self):
        change_stream = change_stream = self.collection.watch([{
                '$match': {
                    'operationType': { '$in': ['insert'] }
                }
            }])
        return change_stream


if __name__ == "__main__":
    # Load sample JSON file
    with open('config/sample_mongo_doc.json', 'r') as f:
        sample_data = json.load(f)

    # Define filter criteria (example: using `user_uuid`)
    filter_criteria = {"created_by": sample_data["created_by"]}

    # Instantiate MongoDatabase
    mongo_db = MongoDatabase(config_path='config/config.yaml')
    # change_stream = mongo_db.client.changestream.collection.watch()
    # from bson.json_util import dumps
    # for change in change_stream:
    #     print(dumps(change))
    #     print('') # for readability only

    # Test creating a document
    inserted_id = mongo_db.create_document(sample_data)
    print(f"Inserted document ID: {inserted_id}")

    # # Test retrieving the document
    # retrieved_docs = mongo_db.get_documents(filter_criteria)
    # print(f"Retrieved Document: {retrieved_docs}")

    # # Test deleting the document
    # delete = mongo_db.delete_document_by_id("66e01492dec2de3b4942ad33")
    # print(f"Delete Success: {delete}")

    # mongo_db.delete_all_documents()

    docs = mongo_db.get_all_document_ids()
    # Get the total number of documents in the collection
    print("Documents ids:", docs)

    # print("Number of documents:", len(docs))

    # document_id = docs[0]
    # update_fields = {
    #     'invoice_info': {'item': 'Laptop', 'amount': 1200},
    #     'created_at': datetime.now().isoformat()
    # }

    # update_success = mongo_db.update_document_by_id(document_id, update_fields)
    # print(f"Update Success: {update_success}")

    # Retrieve and print the updated document to verify changes
    docs = mongo_db.get_documents({'created_by': '1111_1111_1111_1111'})
    print(f"Document: {len(docs)}")

    doc = mongo_db.get_document_by_id(document_id="66e2aeb0632bfcd289eeb7ee")
    print('doc', doc)