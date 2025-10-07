"""
Tools that LLM agents can use to interact with systems.
These tools provide the agents with capabilities to read/write data.
"""

from typing import Dict, List, Optional, Any
from ..storage import get_crm, get_doc_store, get_account_system
import json


class AgentTools:
    """
    Collection of tools that agents can use to interact with systems.
    Each tool is a function that agents can call to perform actions.
    """
    
    def __init__(self):
        self.crm = get_crm()
        self.doc_store = get_doc_store()
        self.account_system = get_account_system()
    
    def get_client_info(self, client_id: str) -> Dict[str, Any]:
        """
        Get comprehensive client information from CRM.
        
        Args:
            client_id: The client's unique identifier
            
        Returns:
            Dict containing client information
        """
        client = self.crm.get_client(client_id)
        if not client:
            return {"error": f"Client {client_id} not found"}
        
        # Get client documents
        documents = self.doc_store.list_documents(client_id)
        doc_details = {}
        for doc_type in documents:
            doc_details[doc_type] = self.doc_store.get_document(client_id, doc_type)
        
        return {
            "client": client,
            "documents": doc_details,
            "available_documents": documents
        }
    
    def update_client_info(self, client_id: str, field: str, value: Any) -> Dict[str, Any]:
        """
        Update client information in CRM.
        
        Args:
            client_id: The client's unique identifier
            field: The field to update
            value: The new value
            
        Returns:
            Dict with success status
        """
        success = self.crm.update_client(client_id, field, value)
        return {"success": success, "message": f"Updated {field} for client {client_id}"}
    
    def get_document(self, client_id: str, doc_type: str) -> Dict[str, Any]:
        """
        Get a specific document for a client.
        
        Args:
            client_id: The client's unique identifier
            doc_type: Type of document (e.g., 'ira_application', 'tax_return_2023')
            
        Returns:
            Dict containing document information
        """
        # Validate doc_type is a string
        if not isinstance(doc_type, str):
            return {"error": f"Tool execution failed: doc_type must be a string, got {type(doc_type).__name__}"}
        
        doc = self.doc_store.get_document(client_id, doc_type)
        if not doc:
            return {"error": f"Document {doc_type} not found for client {client_id}"}
        
        return {"document": doc, "doc_type": doc_type, "client_id": client_id}
    
    def update_document(self, client_id: str, doc_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a document for a client.
        
        Args:
            client_id: The client's unique identifier
            doc_type: Type of document
            data: Document data to update
            
        Returns:
            Dict with success status
        """
        success = self.doc_store.update_document(client_id, doc_type, data)
        return {"success": success, "message": f"Updated {doc_type} for client {client_id}"}
    
    def create_document(self, client_id: str, doc_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new document for a client.
        
        Args:
            client_id: The client's unique identifier
            doc_type: Type of document
            data: Document data
            
        Returns:
            Dict with success status
        """
        success = self.doc_store.update_document(client_id, doc_type, data)
        return {"success": success, "message": f"Created {doc_type} for client {client_id}"}
    
    def open_account(self, client_id: str, account_type: str) -> Dict[str, Any]:
        """
        Open a new account for a client.
        
        Args:
            client_id: The client's unique identifier
            account_type: Type of account (e.g., 'roth_ira', 'traditional_ira')
            
        Returns:
            Dict containing account information or error
        """
        result = self.account_system.open_account(client_id, account_type)
        
        # Check if the account system returned an error
        if "error" in result:
            return {
                "success": False,
                "error": result["error"],
                "message": result["error"]
            }
        
        return {
            "success": True,
            "account": result,
            "message": f"Successfully created {account_type} account for client {client_id}"
        }
    
    def get_account(self, account_number: str) -> Dict[str, Any]:
        """
        Get account information by account number.
        
        Args:
            account_number: The account number
            
        Returns:
            Dict containing account information
        """
        account = self.account_system.get_account(account_number)
        if not account:
            return {"error": f"Account {account_number} not found"}
        
        return {"account": account}
    
    def check_eligibility(self, client_id: str, product_type: str) -> Dict[str, Any]:
        """
        Check client eligibility for a financial product.
        
        Args:
            client_id: The client's unique identifier
            product_type: Type of product (e.g., 'roth_ira', 'traditional_ira')
            
        Returns:
            Dict containing eligibility information
        """
        client_info = self.get_client_info(client_id)
        if "error" in client_info:
            return client_info
        
        client = client_info["client"]
        
        # Roth IRA eligibility check
        if product_type.lower() == "roth_ira":
            # Get tax return for income verification
            tax_doc = self.doc_store.get_document(client_id, "tax_return_2023")
            if not tax_doc:
                return {"eligible": False, "reason": "No tax return found for income verification"}
            
            income = tax_doc.get("income", 0)
            # 2024 Roth IRA income limits
            if income >= 161000:  # Single filer limit
                return {
                    "eligible": False, 
                    "reason": f"Income ${income:,} exceeds Roth IRA limit of $161,000",
                    "income": income,
                    "limit": 161000
                }
            
            return {
                "eligible": True,
                "reason": f"Income ${income:,} is within Roth IRA limit",
                "income": income,
                "limit": 161000
            }
        
        # Add other product eligibility checks here
        return {"eligible": True, "reason": f"Eligibility check for {product_type} not implemented"}
    
    def validate_document(self, client_id: str, doc_type: str) -> Dict[str, Any]:
        """
        Validate a document for completeness and accuracy.
        
        Args:
            client_id: The client's unique identifier
            doc_type: Type of document to validate
            
        Returns:
            Dict containing validation results
        """
        # Validate doc_type is a string
        if not isinstance(doc_type, str):
            return {"error": f"Tool execution failed: doc_type must be a string, got {type(doc_type).__name__}"}
        
        doc = self.doc_store.get_document(client_id, doc_type)
        if not doc:
            return {"valid": False, "errors": [f"Document {doc_type} not found"]}
        
        errors = []
        warnings = []
        
        # IRA Application validation
        if doc_type == "ira_application":
            if not doc.get("signature_page3", False):
                errors.append("Missing signature on page 3")
            
            if not doc.get("submitted", False):
                warnings.append("Application not yet submitted")
            
            if doc.get("status") != "submitted":
                warnings.append(f"Application status is '{doc.get('status')}', expected 'submitted'")
        
        # Tax Return validation
        elif doc_type == "tax_return_2023":
            if not doc.get("income"):
                errors.append("Income information missing")
            
            if not doc.get("year") or doc.get("year") != 2023:
                errors.append("Tax return year must be 2023")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "document": doc
        }
    
    def send_notification(self, client_id: str, message_type: str, content: str) -> Dict[str, Any]:
        """
        Send a notification to a client.
        
        Args:
            client_id: The client's unique identifier
            message_type: Type of message (e.g., 'form_sent', 'account_opened', 'status_update')
            content: Message content
            
        Returns:
            Dict with success status
        """
        # In a real system, this would integrate with email/SMS systems
        # For now, we'll just log the notification
        print(f"📧 NOTIFICATION SENT to {client_id}")
        print(f"   Type: {message_type}")
        print(f"   Content: {content}")
        
        return {
            "success": True,
            "message": f"Notification sent to client {client_id}",
            "type": message_type,
            "content": content
        }
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """
        Get list of available tools for the agent.
        
        Returns:
            List of tool descriptions
        """
        return [
            {
                "name": "get_client_info",
                "description": "Get comprehensive client information including documents"
            },
            {
                "name": "update_client_info", 
                "description": "Update client information in CRM"
            },
            {
                "name": "get_document",
                "description": "Get a specific document for a client"
            },
            {
                "name": "update_document",
                "description": "Update a document for a client"
            },
            {
                "name": "create_document",
                "description": "Create a new document for a client"
            },
            {
                "name": "open_account",
                "description": "Open a new account for a client"
            },
            {
                "name": "get_account",
                "description": "Get account information by account number"
            },
            {
                "name": "check_eligibility",
                "description": "Check client eligibility for financial products"
            },
            {
                "name": "validate_document",
                "description": "Validate a document for completeness and accuracy"
            },
            {
                "name": "send_notification",
                "description": "Send a notification to a client"
            }
        ]


# Global instance for easy access
agent_tools = AgentTools()
