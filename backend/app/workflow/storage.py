"""
Simulated document store and data systems for the workflow system.
Provides in-memory storage for client data, documents, and accounts.
"""

from typing import Optional, List, Dict, Any


class SimulatedDocumentStore:
    """
    Simulates a document storage system for client documents.
    """
    
    def __init__(self):
        """Initialize with sample data for john_smith_123"""
        self.documents = {
            "john_smith_123": {
                "drivers_license": {
                    "status": "valid",
                    "uploaded": True,
                    "verified": True
                },
                "tax_return_2023": {
                    "status": "valid",
                    "income": 145000,
                    "year": 2023
                },
                "ira_application": {
                    "status": "pending",
                    "signature_page3": False,
                    "submitted": False
                }
            }
        }
    
    def _normalize_doc_type(self, doc_type: str) -> str:
        """Normalize document type names to match stored documents"""
        doc_type_lower = doc_type.lower().strip()
        
        # Map common variations to stored document names
        if "driver" in doc_type_lower and "license" in doc_type_lower:
            return "drivers_license"
        elif "tax" in doc_type_lower and "return" in doc_type_lower:
            return "tax_return_2023"
        elif "ira" in doc_type_lower and "application" in doc_type_lower:
            return "ira_application"
        elif "roth" in doc_type_lower and "ira" in doc_type_lower and "application" in doc_type_lower:
            return "ira_application"
        else:
            # Return original if no mapping found
            return doc_type
    
    def get_document(self, client_id: str, doc_type: str) -> Optional[dict]:
        """Get a specific document for a client"""
        normalized_doc_type = self._normalize_doc_type(doc_type)
        if client_id in self.documents and normalized_doc_type in self.documents[client_id]:
            return self.documents[client_id][normalized_doc_type]
        return None
    
    def update_document(self, client_id: str, doc_type: str, data: dict) -> bool:
        """Update a document for a client"""
        if client_id not in self.documents:
            self.documents[client_id] = {}
        
        normalized_doc_type = self._normalize_doc_type(doc_type)
        self.documents[client_id][normalized_doc_type] = data
        return True
    
    def list_documents(self, client_id: str) -> List[str]:
        """List all document types for a client"""
        if client_id in self.documents:
            return list(self.documents[client_id].keys())
        return []


class SimulatedCRM:
    """
    Simulates a Customer Relationship Management system.
    """
    
    def __init__(self):
        """Initialize with sample client data"""
        self.clients = {
            "john_smith_123": {
                "name": "John Smith",
                "age": 45,
                "email": "john@example.com",
                "existing_accounts": ["checking", "brokerage"],
                "income": 145000
            }
        }
    
    def get_client(self, client_id: str) -> Optional[dict]:
        """Get client information by ID"""
        return self.clients.get(client_id)
    
    def update_client(self, client_id: str, field: str, value: Any) -> bool:
        """Update a specific field for a client"""
        if client_id in self.clients:
            self.clients[client_id][field] = value
            return True
        return False


class SimulatedAccountSystem:
    """
    Simulates an account management system.
    """
    
    def __init__(self):
        """Initialize with account counter"""
        self.accounts = {}
        self.counter = 1000  # Start account numbers at 1000
    
    def open_account(self, client_id: str, account_type: str) -> dict:
        """Open a new account for a client"""
        # Check if client already has an account of this type
        for account in self.accounts.values():
            if account["client_id"] == client_id and account["account_type"] == account_type:
                return {
                    "error": f"Client {client_id} already has a {account_type} account: {account['account_number']}"
                }
        
        account_number = f"{account_type.upper()}-{self.counter}"
        self.counter += 1
        
        account_data = {
            "account_number": account_number,
            "client_id": client_id,
            "account_type": account_type,
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        self.accounts[account_number] = account_data
        
        return {
            "account_number": account_number,
            "status": "active",
            "created_at": account_data["created_at"]
        }
    
    def get_account(self, account_number: str) -> Optional[dict]:
        """Get account information by account number"""
        return self.accounts.get(account_number)


# Module-level instances for easy import (singleton pattern)
_doc_store = None
_crm = None
_account_system = None

def get_doc_store():
    global _doc_store
    if _doc_store is None:
        _doc_store = SimulatedDocumentStore()
    return _doc_store

def get_crm():
    global _crm
    if _crm is None:
        _crm = SimulatedCRM()
    return _crm

def get_account_system():
    global _account_system
    if _account_system is None:
        _account_system = SimulatedAccountSystem()
    return _account_system

# Backward compatibility
doc_store = get_doc_store()
crm = get_crm()
account_system = get_account_system()
