import chromadb
import os
from .schemas import QueryRequest, AuditResponse, LogIngest

# 1. SETUP THE PATH
# This tells Python where to find the 'chroma_db' folder relative to this file.
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../chroma_db")

# 2. INITIALIZE THE CLIENT
# This 'wakes up' the database engine inside your folder.
client = chromadb.PersistentClient(path=CHROMA_PATH)

# 3. GET THE COLLECTION
# This is like opening a specific drawer in your filing cabinet.
collection = client.get_or_create_collection(name="security_logs")

# 4. THE WORKER FUNCTIONS
def add_log_to_db(log_id, text, metadata):
    """
    Saves a single log entry into ChromaDB.
    """
    collection.add(
        ids=[log_id],
        documents=[text],
        metadatas=[metadata]
    )

def secure_retrieval(query_text, user_clearance):
    """
    Searches the database but filters out anything 
    above the user's clearance level.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=3,
        # The '$lte' (Less Than or Equal To) is our security guard.
        where={"security_level": {"$lte": user_clearance}}
    )
    return results