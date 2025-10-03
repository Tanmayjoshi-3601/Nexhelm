#!/usr/bin/env python3
"""
Test script for LLM opportunity detection
"""

import sys
import os
sys.path.append('.')

from app.opportunity_detector import OpportunityDetector

def test_llm_detection():
    print("🧪 Testing LLM Opportunity Detection")
    print("=" * 50)
    
    # Initialize detector
    detector = OpportunityDetector()
    
    if not detector.llm_available:
        print("❌ No OpenAI API key found - cannot test LLM detection")
        return
    
    # Test transcript
    test_transcript = """
    Client: Hi, I'm 45 years old and I'm starting to think about retirement. 
    I have a 401k at work but I'm not sure if I'm saving enough.
    I also have two kids who will be going to college in about 10 years.
    My wife and I are worried about paying for their education.
    """
    
    print(f"📝 Test transcript: {test_transcript.strip()}")
    print()
    
    # Test pattern detection only
    print("🔍 Testing pattern detection...")
    pattern_opportunities = detector.detect_opportunities(test_transcript, use_llm=False)
    print(f"Found {len(pattern_opportunities)} opportunities via pattern matching:")
    for opp in pattern_opportunities:
        print(f"  - {opp['title']} (Score: {opp['score']})")
    print()
    
    # Test LLM detection
    print("🤖 Testing LLM detection...")
    try:
        llm_opportunities = detector.detect_opportunities(test_transcript, use_llm=True)
        print(f"Found {len(llm_opportunities)} opportunities via LLM:")
        for opp in llm_opportunities:
            print(f"  - {opp['title']} (Score: {opp['score']})")
            print(f"    Trigger: {opp['trigger']}")
            print(f"    Detected by: {opp['detected_by']}")
            print()
    except Exception as e:
        print(f"❌ LLM detection failed: {e}")
    
    print("✅ Test completed!")

if __name__ == "__main__":
    test_llm_detection()