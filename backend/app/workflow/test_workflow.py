#!/usr/bin/env python3
"""
Test script for the workflow system.
Can be run independently to test the workflow functionality.
"""

from .storage import get_doc_store
from .main import run_workflow


def test_successful_workflow():
    """Test successful IRA opening workflow"""
    print("🧪 Testing successful workflow...")
    
    # Setup: Ensure documents are valid
    doc_store = get_doc_store()
    doc_store.update_document("john_smith_123", "ira_application", {
        "status": "submitted",
        "signature_page3": True,
        "submitted": True
    })
    
    # Run workflow
    result = run_workflow("john_smith_123", "open_roth_ira")
    
    # Verify success
    assert result["status"] == "completed"
    assert len(result["tasks"]) == 5
    assert all(t["status"] == "completed" for t in result["tasks"])
    assert result["outcome"] is not None
    assert "account_number" in result["outcome"]
    
    print("✅ Successful workflow test passed!")
    return result


def test_failed_workflow():
    """Test workflow with missing signature"""
    print("\n🧪 Testing failed workflow (missing signature)...")
    
    # Setup: Document missing signature
    doc_store = get_doc_store()
    doc_store.update_document("john_smith_123", "ira_application", {
        "status": "submitted",
        "signature_page3": False,
        "submitted": True
    })
    
    # Run workflow
    result = run_workflow("john_smith_123", "open_roth_ira")
    
    # Verify failure
    assert result["status"] == "failed"
    assert len(result["blockers"]) > 0
    assert any("signature" in b["description"].lower() for b in result["blockers"])
    
    print("✅ Failed workflow test passed!")
    return result


def test_income_eligibility():
    """Test income eligibility verification"""
    print("\n🧪 Testing income eligibility...")
    
    # Setup: High income client and valid documents
    from .storage import get_crm, get_doc_store
    crm = get_crm()
    doc_store = get_doc_store()
    
    # Set high income
    crm.update_client("john_smith_123", "income", 200000)  # Above Roth IRA limit
    
    # Ensure valid documents
    doc_store.update_document("john_smith_123", "ira_application", {
        "status": "submitted",
        "signature_page3": True,
        "submitted": True
    })
    
    # Update tax return with high income
    doc_store.update_document("john_smith_123", "tax_return_2023", {
        "status": "valid",
        "income": 200000,
        "year": 2023
    })
    
    # Run workflow
    result = run_workflow("john_smith_123", "open_roth_ira")
    
    # Should fail due to income limit
    assert result["status"] == "failed"
    assert len(result["blockers"]) > 0
    assert any("income" in b["description"].lower() for b in result["blockers"])
    
    # Reset income and tax return
    crm.update_client("john_smith_123", "income", 145000)
    doc_store.update_document("john_smith_123", "tax_return_2023", {
        "status": "valid",
        "income": 145000,
        "year": 2023
    })
    
    print("✅ Income eligibility test passed!")
    return result


if __name__ == "__main__":
    print("🚀 Starting Nexhelm Workflow System Tests")
    print("=" * 50)
    
    try:
        # Run all tests
        test_successful_workflow()
        test_failed_workflow()
        test_income_eligibility()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! The workflow system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
