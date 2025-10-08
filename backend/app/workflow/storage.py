"""
Simulated document store and data systems for the workflow system.
Provides in-memory storage for client data, documents, and accounts.
"""

from typing import Optional, List, Dict, Any
import csv
import os
from datetime import datetime


class SimulatedDocumentStore:
    """
    Simulates a document storage system for client documents.
    """
    
    def __init__(self):
        """Initialize with sample data for john_smith_123 and test clients"""
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
                    "status": "valid",
                    "signature_complete": True,
                    "submitted": True
                }
            },
            "test_client_complete": {
                "drivers_license": {
                    "status": "valid",
                    "uploaded": True,
                    "verified": True
                },
                "tax_return_2023": {
                    "status": "valid",
                    "income": 120000,
                    "year": 2023
                },
                "ira_application": {
                    "status": "valid",
                    "signature_complete": True,
                    "submitted": True
                }
            }
        }
    
    def _normalize_doc_type(self, doc_type: str) -> str:
        """Normalize document type names to match stored documents"""
        doc_type_lower = doc_type.lower().strip()
        
        # Map common variations to stored document names
        if "driver" in doc_type_lower or "license" in doc_type_lower:
            return "drivers_license"
        elif "tax" in doc_type_lower or "return" in doc_type_lower or "income" in doc_type_lower:
            return "tax_return_2023"
        elif "application" in doc_type_lower or ("ira" in doc_type_lower and "form" in doc_type_lower):
            return "ira_application"
        elif doc_type_lower in ["roth_ira", "traditional_ira", "roth ira", "traditional ira"]:
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
    
    def get_all_documents(self) -> Dict[str, Dict[str, Any]]:
        """Get all documents for all clients"""
        return self.documents


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
            },
            "test_client_complete": {
                "name": "Test Client Complete",
                "age": 35,
                "email": "test@example.com",
                "existing_accounts": [],
                "income": 120000
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
    
    def get_all_clients(self) -> Dict[str, Dict[str, Any]]:
        """Get all clients"""
        return self.clients


class SimulatedAccountSystem:
    """
    Simulates an account management system with CSV logging.
    """
    
    def __init__(self):
        """Initialize with account counter and CSV log"""
        self.accounts = {}
        self.counter = 1000  # Start account numbers at 1000
        self.csv_log_path = os.path.join(os.path.dirname(__file__), "../../accounts_log.csv")
        self._initialize_csv_log()
    
    def _initialize_csv_log(self):
        """Initialize CSV log file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_log_path):
            with open(self.csv_log_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Account Number', 'Client ID', 'Account Type', 'Status'])
    
    def _log_account_creation(self, account_data: dict):
        """Log account creation to CSV file"""
        try:
            with open(self.csv_log_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    account_data['account_number'],
                    account_data['client_id'],
                    account_data['account_type'],
                    account_data['status']
                ])
                print(f"📝 Logged account creation to CSV: {account_data['account_number']}")
        except Exception as e:
            print(f"⚠️  Failed to log account to CSV: {e}")
    
    def open_account(self, client_id: str, account_type: str) -> dict:
        """Open a new account for a client and update CRM"""
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
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.accounts[account_number] = account_data
        
        # Log to CSV
        self._log_account_creation(account_data)
        
        # Update CRM to add this account to client's existing_accounts
        crm = get_crm()
        client = crm.get_client(client_id)
        if client:
            if 'existing_accounts' not in client:
                client['existing_accounts'] = []
            # Add the account type to existing accounts if not already there
            if account_type not in client['existing_accounts']:
                client['existing_accounts'].append(account_type)
                print(f"✅ Updated CRM: Added {account_type} to {client_id}'s existing accounts")
        
        return {
            "account_number": account_number,
            "status": "active",
            "created_at": account_data["created_at"]
        }
    
    def get_account(self, account_number: str) -> Optional[dict]:
        """Get account information by account number"""
        return self.accounts.get(account_number)
    
    def get_csv_log_path(self) -> str:
        """Get the path to the CSV log file"""
        return self.csv_log_path
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts as a list"""
        return list(self.accounts.values())


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
