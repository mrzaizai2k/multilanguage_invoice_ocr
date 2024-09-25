import sys
sys.path.append("")

from pymongo import MongoClient
from typing import  Dict, Any, List, Literal
from bson import ObjectId
from src.Utils.utils import read_config, get_current_time

class MongoDatabase:
    def __init__(self, config_path: str, logger = None):
        # Load the YAML configuration file using the provided utility function
        self.config_path = config_path
        self.config = read_config(path=self.config_path)
        try:
            print(f"mongo URI: {str(self.config['mongodb']['uri'])}")
            self.client = MongoClient(str(self.config['mongodb']['uri']), connect=True)
            print(f"Connected to MongoDB. Version: {self.client.server_info()['version']}")
        except Exception as e:
            try:
                print(f"mongo URI: {str(self.config['mongodb']['uri'])}")
                self.client = MongoClient("mongodb://mongodb:27017/", connect=True)
                print(f"Connected to fallback MongoDB. Version: {self.client.server_info()['version']}")
            except Exception as e:
                print(f"Failed to connect to fallback MongoDB. Error: {str(e)}")
                raise

        # self.client = MongoClient(host = str(self.config['mongodb']['uri'])) 
        self.db = self.client[self.config['mongodb']['database']]
        self.collection = self.db[self.config['mongodb']['collection']]

        if logger:
            self.logger=logger
            self.logger.info(f"Using database: {self.config['mongodb']['database']}, collection: {self.config['mongodb']['collection']}")


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
    # with open('config/sample_mongo_doc.json', 'r') as f:
    #     sample_data = json.load(f)

    from src.validate_invoice import Invoice1
    from datetime import date, time
    json_1 = {
        "invoice_info": {
            "name": "Tümmler, Dirk",
            "project_number": "V240045",
            "customer": "Magua",
            "city": "Salzgitter",
            "kw": "",
            "land": "DE",
            "lines": [
                {
                    "date": date(2008, 6, 28),
                    "start_time": "17:46:26",
                    "end_time": "17:46:26",
                    "break_time": 0.5,
                    "description": "support",
                    "has_customer_signature": True
                },
                {
                    "date":  date(2008, 6, 28),
                    "start_time": "17:46:26",
                    "end_time": "17:46:26",
                    "break_time": 0.0,
                    "description": "Supports",
                    "has_customer_signature": True
                }
            ],
            "is_process_done": True,
            "is_commissioned_work": True,
            "is_without_measuring_technology": False,
            "sign_date": date(2008, 6, 28),
            "has_employee_signature": True
        }
    }


    invoice = Invoice1(invoice_info=json_1['invoice_info'])
    sample_data = invoice.model_dump(exclude_unset=False)

    # Instantiate MongoDatabase
    mongo_db = MongoDatabase(config_path='config/config.yaml')

    # Test creating a document
    inserted_id = mongo_db.create_document(sample_data)
    print(f"Inserted document ID: {inserted_id}")

    docs = mongo_db.get_all_document_ids()
    # Get the total number of documents in the collection
    print("Documents ids:", docs)

    # # Test retrieving the document
    # Define filter criteria (example: using `user_uuid`)
    filter_criteria = {"created_by": "1111_1111_1111_1111"}
    retrieved_docs = mongo_db.get_documents(filter_criteria)
    print(f"Retrieved Document: {len(retrieved_docs)}")


    # print("Number of documents:", len(docs))

    document_id = docs[0]

    update_fields = {
        'invoice_info': {'item': 'Laptop', 'amount': 1200},
        'created_at': get_current_time()
    }

    update_success = mongo_db.update_document_by_id(document_id, update_fields)
    print(f"Update Success: {update_success}")

    # Retrieve and print the updated document to verify changes
    docs = mongo_db.get_documents({'created_by': '2111_1111_1111_1111'})
    print(f"Document: {len(docs)}")

    doc = mongo_db.get_document_by_id(document_id=document_id)['created_at']
    print('doc', doc)

    # Test deleting the document
    delete = mongo_db.delete_document_by_id(document_id=document_id)
    print(f"Delete Success: {delete}")

    # mongo_db.delete_all_documents()