"""
Dummy Transcript Service
Generates realistic financial advisor conversations for demo purposes
"""

import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import random

class DummyTranscriptService:
    """Service to generate realistic dummy conversations"""
    
    def __init__(self):
        self.active_demos: Dict[str, asyncio.Task] = {}
        
        # Conversation scenarios with realistic timing
        self.scenarios = {
            "retirement_planning": {
                "name": "Retirement Planning",
                "duration": 90,  # seconds
                "messages": [
                    {"speaker": "Client", "text": "Hi, thanks for meeting with me today.", "delay": 2},
                    {"speaker": "Advisor", "text": "Of course! I'm excited to help you plan for retirement. Tell me about your current situation.", "delay": 3},
                    {"speaker": "Client", "text": "Well, I'm turning 60 next year and starting to think seriously about retirement.", "delay": 4},
                    {"speaker": "Advisor", "text": "That's a great milestone! What's your current retirement savings looking like?", "delay": 3},
                    {"speaker": "Client", "text": "I have about $800,000 in my 401k and another $150,000 in a traditional IRA.", "delay": 5},
                    {"speaker": "Advisor", "text": "That's a solid foundation. Do you have any other assets or income sources?", "delay": 4},
                    {"speaker": "Client", "text": "My wife and I own our home, it's worth about $400,000. We also have some savings.", "delay": 4},
                    {"speaker": "Advisor", "text": "Excellent. What are your monthly expenses currently?", "delay": 3},
                    {"speaker": "Client", "text": "We spend about $6,000 per month including everything - mortgage, utilities, food, entertainment.", "delay": 5},
                    {"speaker": "Advisor", "text": "I see. And what about Social Security - have you checked your estimated benefits?", "delay": 4},
                    {"speaker": "Client", "text": "Yes, I looked online and it shows about $2,800 per month if I wait until 67.", "delay": 4},
                    {"speaker": "Advisor", "text": "That's helpful. With your current savings, you're in a good position. Let me run some projections.", "delay": 4},
                    {"speaker": "Client", "text": "I'm also wondering about catch-up contributions. Can I still contribute more to my 401k?", "delay": 5},
                    {"speaker": "Advisor", "text": "Absolutely! Since you're over 50, you can contribute an extra $7,500 this year.", "delay": 4},
                    {"speaker": "Client", "text": "That's good to know. I'm also thinking about a Roth conversion. Is that something we should consider?", "delay": 5},
                    {"speaker": "Advisor", "text": "Great question! A Roth conversion could be very beneficial for you. Let me explain the strategy.", "delay": 4},
                    {"speaker": "Client", "text": "I'm also worried about healthcare costs in retirement. Medicare doesn't cover everything.", "delay": 4},
                    {"speaker": "Advisor", "text": "You're absolutely right to think about that. Healthcare is often the biggest retirement expense.", "delay": 4},
                    {"speaker": "Client", "text": "Should we look into long-term care insurance? My father needed care for several years.", "delay": 5},
                    {"speaker": "Advisor", "text": "That's a very important consideration. Let's discuss your options for long-term care planning.", "delay": 4},
                    {"speaker": "Client", "text": "This is all very helpful. I feel much more confident about my retirement planning now.", "delay": 4},
                    {"speaker": "Advisor", "text": "I'm glad I could help! We'll create a comprehensive plan that addresses all your concerns.", "delay": 3}
                ]
            },
            
            "education_planning": {
                "name": "Education Planning",
                "duration": 75,
                "messages": [
                    {"speaker": "Client", "text": "Hi, I'm here to talk about saving for my daughter's college education.", "delay": 2},
                    {"speaker": "Advisor", "text": "Wonderful! Education planning is so important. How old is your daughter?", "delay": 3},
                    {"speaker": "Client", "text": "She's 16 and a junior in high school. She's been looking at colleges.", "delay": 4},
                    {"speaker": "Advisor", "text": "That's exciting! What schools is she considering?", "delay": 3},
                    {"speaker": "Client", "text": "She's really interested in Northwestern University and a few other private schools.", "delay": 4},
                    {"speaker": "Advisor", "text": "Northwestern is an excellent school. Do you know what the current tuition costs are?", "delay": 4},
                    {"speaker": "Client", "text": "I looked it up and it's about $60,000 per year including room and board.", "delay": 4},
                    {"speaker": "Advisor", "text": "That's quite an investment. What have you saved so far for her education?", "delay": 4},
                    {"speaker": "Client", "text": "We have about $40,000 in a regular savings account, but I know that's not the best way to save.", "delay": 5},
                    {"speaker": "Advisor", "text": "You're right about that. Have you heard of 529 education savings plans?", "delay": 4},
                    {"speaker": "Client", "text": "I've heard the name but don't really understand how they work.", "delay": 3},
                    {"speaker": "Advisor", "text": "529 plans offer tax-free growth and withdrawals for qualified education expenses.", "delay": 4},
                    {"speaker": "Client", "text": "That sounds great! Can we still open one even though she's already 16?", "delay": 4},
                    {"speaker": "Advisor", "text": "Absolutely! Even with just two years, you can still benefit from tax-free growth.", "delay": 4},
                    {"speaker": "Client", "text": "What about financial aid? Will having a 529 plan affect her eligibility?", "delay": 5},
                    {"speaker": "Advisor", "text": "Good question! 529 plans are treated favorably in financial aid calculations.", "delay": 4},
                    {"speaker": "Client", "text": "She's also looking at some state schools that are much more affordable.", "delay": 4},
                    {"speaker": "Advisor", "text": "That's smart to have options. 529 funds can be used at any qualified institution.", "delay": 4},
                    {"speaker": "Client", "text": "What if she gets scholarships? Can we use the money for other things?", "delay": 4},
                    {"speaker": "Advisor", "text": "Yes, you can withdraw the earnings penalty-free up to the scholarship amount.", "delay": 4},
                    {"speaker": "Client", "text": "This is really helpful. I feel much better about planning for her education.", "delay": 4},
                    {"speaker": "Advisor", "text": "I'm glad! Let's set up a 529 plan and create a strategy that works for your family.", "delay": 3}
                ]
            },
            
            "life_changes": {
                "name": "Life Changes & Planning",
                "duration": 80,
                "messages": [
                    {"speaker": "Client", "text": "Hi, I have some big life changes happening and need help with my financial planning.", "delay": 2},
                    {"speaker": "Advisor", "text": "I'd be happy to help! What changes are you experiencing?", "delay": 3},
                    {"speaker": "Client", "text": "Well, my wife and I are expecting our first child in six months.", "delay": 4},
                    {"speaker": "Advisor", "text": "Congratulations! That's wonderful news. How exciting!", "delay": 3},
                    {"speaker": "Client", "text": "Thank you! We're thrilled but also a bit overwhelmed with all the planning.", "delay": 4},
                    {"speaker": "Advisor", "text": "That's completely normal. Let's talk about what financial adjustments you'll need to make.", "delay": 4},
                    {"speaker": "Client", "text": "I also just got a promotion at work with a $20,000 raise.", "delay": 4},
                    {"speaker": "Advisor", "text": "That's fantastic! A promotion and a baby - lots of positive changes.", "delay": 3},
                    {"speaker": "Client", "text": "Yes, but I'm not sure how to best use the extra income with a baby on the way.", "delay": 4},
                    {"speaker": "Advisor", "text": "Great question. Let's look at your current budget and see where the extra money can have the most impact.", "delay": 4},
                    {"speaker": "Client", "text": "We're also thinking about buying a bigger house. Our current place is getting cramped.", "delay": 4},
                    {"speaker": "Advisor", "text": "That makes sense with a baby coming. What's your current housing situation?", "delay": 4},
                    {"speaker": "Client", "text": "We have a two-bedroom condo with about $100,000 in equity.", "delay": 4},
                    {"speaker": "Advisor", "text": "That's a good foundation. Have you started looking at homes in your price range?", "delay": 4},
                    {"speaker": "Client", "text": "We've been looking at houses around $400,000. The mortgage would be manageable with my raise.", "delay": 5},
                    {"speaker": "Advisor", "text": "That sounds reasonable. What about life insurance? Have you thought about that?", "delay": 4},
                    {"speaker": "Client", "text": "Actually, that's something I've been meaning to look into. I have some through work but probably not enough.", "delay": 5},
                    {"speaker": "Advisor", "text": "You're right to think about that. With a baby coming, you'll want to protect your family.", "delay": 4},
                    {"speaker": "Client", "text": "What about a will? We don't have one yet and I know we should.", "delay": 4},
                    {"speaker": "Advisor", "text": "Absolutely! Estate planning becomes crucial when you have children.", "delay": 3},
                    {"speaker": "Client", "text": "This is all so much to think about. I'm glad we're getting organized now.", "delay": 4},
                    {"speaker": "Advisor", "text": "You're doing the right thing by planning ahead. Let's create a comprehensive strategy.", "delay": 3}
                ]
            }
        }
    
    async def start_demo(self, meeting_id: str, scenario: str, send_callback, opportunity_callback=None):
        """Start a dummy conversation demo"""
        if meeting_id in self.active_demos:
            await self.stop_demo(meeting_id)
        
        if scenario not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        scenario_data = self.scenarios[scenario]
        
        async def run_demo():
            try:
                for message in scenario_data["messages"]:
                    # Send the message
                    await send_callback({
                        "type": "message",
                        "speaker": message["speaker"],
                        "text": message["text"],
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Trigger opportunity detection if callback provided
                    if opportunity_callback:
                        await opportunity_callback(message["text"], message["speaker"])
                    
                    # Wait for the specified delay
                    await asyncio.sleep(message["delay"])
                
                # Demo completed
                await send_callback({
                    "type": "demo_complete",
                    "message": f"Demo conversation completed! Scenario: {scenario_data['name']}"
                })
                
            except asyncio.CancelledError:
                # Demo was stopped
                pass
            finally:
                # Clean up
                if meeting_id in self.active_demos:
                    del self.active_demos[meeting_id]
        
        # Start the demo task
        task = asyncio.create_task(run_demo())
        self.active_demos[meeting_id] = task
        
        return task
    
    async def stop_demo(self, meeting_id: str):
        """Stop a running demo"""
        if meeting_id in self.active_demos:
            task = self.active_demos[meeting_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.active_demos[meeting_id]
    
    def get_available_scenarios(self):
        """Get list of available scenarios"""
        return {key: {"name": data["name"], "duration": data["duration"]} 
                for key, data in self.scenarios.items()}
    
    def is_demo_running(self, meeting_id: str) -> bool:
        """Check if a demo is currently running for a meeting"""
        return meeting_id in self.active_demos

# Global instance
dummy_transcript_service = DummyTranscriptService()
