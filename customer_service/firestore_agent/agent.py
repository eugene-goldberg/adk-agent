# customer_service/firestore_agent/agent.py

import logging
import json
from google.cloud import firestore
from ..config import Config  # Import the main Config

logger = logging.getLogger(__name__)

class FirestoreAgent:
    def __init__(self):
        # Load Firestore configuration
        app_config = Config()
        self.firestore_config = app_config.firestore_settings

        logger.info(
            "FirestoreAgent initialized with Project ID: %s, Database ID: %s",
            self.firestore_config.project_id,
            self.firestore_config.database_id,
        )

        # Initialize the Firestore client
        try:
            # Check if credentials path is defined in config
            if hasattr(self.firestore_config, 'credentials_path') and self.firestore_config.credentials_path:
                self.db = firestore.Client.from_service_account_json(
                    self.firestore_config.credentials_path,
                    project=self.firestore_config.project_id,
                    database=self.firestore_config.database_id
                )
            else:
                # Use Application Default Credentials
                self.db = firestore.Client(
                    project=self.firestore_config.project_id,
                    database=self.firestore_config.database_id
                )
            logger.info("Firestore client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            # Still create the agent but without an active connection
            self.db = None
            logger.warning("FirestoreAgent created but without an active Firestore connection.")

    async def process_query(self, query: str):
        """
        Process different types of Firestore queries.
        
        The query string should follow this format:
        operation:collection_name:document_id:data
        
        Operations:
        - read: Read a document
        - write: Write a document
        - update: Update a document
        - delete: Delete a document
        - query: Query a collection
        
        Examples:
        - read:customers:user123
        - write:customers:user123:{"name":"John Doe","email":"john@example.com"}
        - update:customers:user123:{"status":"active"}
        - delete:customers:user123
        - query:customers:{"filters":[{"field":"status","op":"==","value":"active"}],"limit":10}
        
        Args:
            query: The formatted query string
            
        Returns:
            The result of the operation
        """
        from . import tools
        import json
        
        if not self.db:
            return json.dumps({"error": "Firestore client not initialized"})
            
        try:
            # Handle queries with JSON that might have colons inside them
            parts = []
            # First split by the first colon to get the operation
            operation_split = query.split(':', 1)
            if len(operation_split) < 2:
                return json.dumps({
                    "error": "Invalid query format. Expected format: operation:collection:document_id[:data]"
                })
                
            parts.append(operation_split[0])  # Add operation
            
            # Now split the rest by the next colon to get the collection
            collection_split = operation_split[1].split(':', 1)
            if len(collection_split) < 2:
                return json.dumps({
                    "error": "Invalid query format. Expected format: operation:collection:document_id[:data]"
                })
                
            parts.append(collection_split[0])  # Add collection
            
            # The rest could be document_id or document_id:data or query_params
            parts.append(collection_split[1])
            
            if len(parts) < 2:
                return json.dumps({
                    "error": "Invalid query format. Expected format: operation:collection:document_id[:data]"
                })
                
            operation = parts[0].lower()
            collection_name = parts[1]
            
            # Handle different operations
            if operation == "read" and len(parts) >= 3:
                document_id = parts[2]
                result = await tools.read_document(self.db, collection_name, document_id)
                
            elif operation == "write" and len(parts) >= 3:
                # Handle the document_id and data part
                rest_parts = parts[2].split(':', 1)
                if len(rest_parts) >= 2:
                    document_id = rest_parts[0] if rest_parts[0] else None
                    try:
                        data = json.loads(rest_parts[1])
                        result = await tools.write_document(self.db, collection_name, document_id, data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in write data: {rest_parts[1]}")
                        return json.dumps({"error": "Invalid JSON in write data"})
                else:
                    return json.dumps({"error": "Missing data for write operation"})
                
            elif operation == "update" and len(parts) >= 3:
                # Handle the document_id and data part
                rest_parts = parts[2].split(':', 1)
                if len(rest_parts) >= 2:
                    document_id = rest_parts[0]
                    try:
                        data = json.loads(rest_parts[1])
                        result = await tools.update_document(self.db, collection_name, document_id, data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in update data: {rest_parts[1]}")
                        return json.dumps({"error": "Invalid JSON in update data"})
                else:
                    return json.dumps({"error": "Missing data for update operation"})
                
            elif operation == "delete" and len(parts) >= 3:
                document_id = parts[2]
                result = await tools.delete_document(self.db, collection_name, document_id)
                
            elif operation == "query" and len(parts) >= 3:
                # Get the query parameters part
                query_params_str = parts[2]
                
                # Handle empty query parameters case (list all documents)
                if query_params_str == "{}" or not query_params_str.strip():
                    filters = None
                    limit = None
                    order_by = None
                    direction = "DESCENDING"
                else:
                    try:
                        query_params = json.loads(query_params_str)
                        filters = query_params.get("filters")
                        limit = query_params.get("limit")
                        order_by = query_params.get("order_by")
                        direction = query_params.get("direction", "DESCENDING")
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in query parameters: {query_params_str}")
                        return json.dumps({"error": "Invalid JSON in query parameters"})
                
                result = await tools.query_collection(
                    self.db, 
                    collection_name, 
                    filters, 
                    limit, 
                    order_by, 
                    direction
                )
                # Ensure we have a success key for consistency
                if "success" not in result and "documents" in result:
                    result["success"] = True
                
            else:
                result = {"error": f"Unsupported operation: {operation}"}
                
            return json.dumps(result)
            
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON data in query"})
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return json.dumps({"error": str(e)})
