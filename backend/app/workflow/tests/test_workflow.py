"""
Test cases for the workflow system.
Tests successful completion and error scenarios.
"""


def test_successful_ira_opening():
    """Test complete workflow without issues"""
    
    # Setup: Ensure documents are valid
    from ..storage import doc_store
    doc_store.update_document("john_smith_123", "ira_application", {
        "status": "submitted",
        "signature_page3": True,
        "submitted": True
    })
    
    # Run workflow
    from ..main import run_workflow
    result = run_workflow("john_smith_123", "open_roth_ira")
    
    # Assertions
    assert result["status"] == "completed"
    assert len(result["tasks"]) == 5
    assert all(t["status"] == "completed" for t in result["tasks"])
    assert result["outcome"] is not None
    assert "account_number" in result["outcome"]
    
    print("✅ Test 1 passed: Happy path successful")


def test_missing_signature():
    """Test workflow with missing signature"""
    
    # Setup: Document missing signature
    from ..storage import doc_store
    doc_store.update_document("john_smith_123", "ira_application", {
        "status": "submitted",
        "signature_page3": False,
        "submitted": True
    })
    
    # Run workflow
    from ..main import run_workflow
    result = run_workflow("john_smith_123", "open_roth_ira")
    
    # Assertions
    assert len(result["blockers"]) > 0
    assert any("signature" in b["description"].lower() for b in result["blockers"])
    assert any(m["from_agent"] == "operations_agent" and 
              m["to_agent"] == "advisor_agent" 
              for m in result["messages"])
    
    print("✅ Test 2 passed: Blocker detected correctly")


def test_state_updates():
    """Verify state updates correctly through workflow"""
    
    from ..main import run_workflow
    result = run_workflow("john_smith_123", "open_roth_ira")
    
    # Check workflow_id was generated
    assert result["workflow_id"] != ""
    assert len(result["workflow_id"]) > 0
    
    # Check timestamps
    assert result["created_at"] != ""
    assert result["updated_at"] != ""
    
    # Check messages were added
    assert len(result["messages"]) > 0
    assert all("from_agent" in m for m in result["messages"])
    assert all("to_agent" in m for m in result["messages"])
    
    # Check decisions were logged
    assert len(result["decisions"]) > 0
    assert all("reasoning" in d for d in result["decisions"])
    
    print("✅ Test 3 passed: State updates correctly")


def test_income_eligibility():
    """Test income eligibility verification"""
    
    # Setup: High income client
    from ..storage import doc_store, crm
    doc_store.update_document("john_smith_123", "tax_return_2023", {
        "status": "valid",
        "income": 200000,  # Above Roth IRA limit
        "year": 2023
    })
    
    # Run workflow
    from ..main import run_workflow
    result = run_workflow("john_smith_123", "open_roth_ira")
    
    # Should fail due to income limit
    assert result["status"] == "failed"
    assert len(result["blockers"]) > 0
    assert any("income" in b["description"].lower() for b in result["blockers"])
    
    print("✅ Test 4 passed: Income eligibility check works")


if __name__ == "__main__":
    test_successful_ira_opening()
    test_missing_signature()
    test_state_updates()
    test_income_eligibility()
    print("\n✅ All tests passed!")
