# customer_service/firestore_agent/tools.py

import logging
import json
from typing import Dict, Any, List, Optional, Union
from google.cloud.firestore_v1.base_query import FieldFilter

logger = logging.getLogger(__name__)

async def read_document(db, collection_name: str, document_id: str) -> Dict[str, Any]:
    """
    Reads a document from a Firestore collection.
    
    Args:
        db: Firestore database client
        collection_name: Name of the collection
        document_id: ID of the document to read
        
    Returns:
        Dict containing document data or error message
    """
    try:
        if not db:
            return {"error": "Firestore client not initialized"}
            
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return {"success": True, "data": doc.to_dict(), "id": doc.id}
        else:
            return {"success": False, "error": f"Document {document_id} not found in collection {collection_name}"}
    except Exception as e:
        logger.error(f"Error reading document: {e}")
        return {"success": False, "error": str(e)}

async def write_document(db, collection_name: str, document_id: Optional[str], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Writes a document to a Firestore collection.
    
    Args:
        db: Firestore database client
        collection_name: Name of the collection
        document_id: ID of the document (if None, Firestore will auto-generate ID)
        data: Document data to write
        
    Returns:
        Dict containing operation result
    """
    try:
        if not db:
            return {"error": "Firestore client not initialized"}
            
        if document_id:
            doc_ref = db.collection(collection_name).document(document_id)
            doc_ref.set(data)
            return {"success": True, "id": document_id}
        else:
            doc_ref = db.collection(collection_name).add(data)[1]
            return {"success": True, "id": doc_ref.id}
    except Exception as e:
        logger.error(f"Error writing document: {e}")
        return {"success": False, "error": str(e)}

async def update_document(db, collection_name: str, document_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates specific fields in a Firestore document.
    
    Args:
        db: Firestore database client
        collection_name: Name of the collection
        document_id: ID of the document to update
        data: Document data to update (only these fields will be updated)
        
    Returns:
        Dict containing operation result
    """
    try:
        if not db:
            return {"error": "Firestore client not initialized"}
            
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return {"success": False, "error": f"Document {document_id} not found in collection {collection_name}"}
            
        doc_ref.update(data)
        return {"success": True, "id": document_id}
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        return {"success": False, "error": str(e)}

async def delete_document(db, collection_name: str, document_id: str) -> Dict[str, Any]:
    """
    Deletes a document from a Firestore collection.
    
    Args:
        db: Firestore database client
        collection_name: Name of the collection
        document_id: ID of the document to delete
        
    Returns:
        Dict containing operation result
    """
    try:
        if not db:
            return {"error": "Firestore client not initialized"}
            
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return {"success": False, "error": f"Document {document_id} not found in collection {collection_name}"}
            
        doc_ref.delete()
        return {"success": True, "message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return {"success": False, "error": str(e)}

async def query_collection(db, collection_name: str, filters: Optional[List[Dict[str, Any]]] = None, 
                          limit: Optional[int] = None, order_by: Optional[str] = None, 
                          direction: Optional[str] = "DESCENDING") -> Dict[str, Any]:
    """
    Queries documents in a Firestore collection based on filters.
    
    Args:
        db: Firestore database client
        collection_name: Name of the collection
        filters: List of filter dictionaries, each with 'field', 'op', and 'value' keys
                 Operators can be: '==', '!=', '>', '>=', '<', '<='
        limit: Maximum number of documents to return
        order_by: Field to order results by
        direction: Sort direction, either "ASCENDING" or "DESCENDING"
        
    Returns:
        Dict containing query results
    """
    try:
        if not db:
            return {"error": "Firestore client not initialized"}
            
        query = db.collection(collection_name)
        
        # Apply filters if provided
        if filters:
            for filter_dict in filters:
                field = filter_dict.get('field')
                op = filter_dict.get('op')
                value = filter_dict.get('value')
                
                if field and op and value is not None:
                    query = query.where(filter=FieldFilter(field, op, value))
        
        # Apply sorting if order_by is provided
        if order_by:
            # Set direction - use string literals for direction since firestore-v1 handles them appropriately
            sort_direction = "DESCENDING" if direction.upper() == "DESCENDING" else "ASCENDING"
            query = query.order_by(order_by, direction=sort_direction)
            
        # Apply limit if provided
        if limit:
            query = query.limit(limit)
            
        # Execute query
        results = query.stream()
        documents = []
        
        for doc in results:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id
            
            # Convert non-serializable types to strings
            for key, value in doc_data.items():
                # Handle Firestore DatetimeWithNanoseconds
                if hasattr(value, 'isoformat'):
                    doc_data[key] = value.isoformat()
                # Handle arrays/lists with non-serializable types
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if hasattr(item, 'isoformat'):
                            value[i] = item.isoformat()
                    
            documents.append(doc_data)
            
        return {"success": True, "documents": documents, "count": len(documents)}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error querying collection: {error_msg}")
        
        # Check if this is an index error and provide a more helpful message
        if "The query requires an index" in error_msg:
            return {
                "success": False, 
                "error": "This query requires a Firestore index to be created.",
                "details": error_msg,
                "hint": "For simpler queries, try removing the sorting or filtering."
            }
        return {"success": False, "error": error_msg}
