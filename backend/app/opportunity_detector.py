import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class OpportunityDetector:
    """
    This class is responsible for detecting financial opportunities
    from conversation transcripts. It's the brain that understands
    implicitly what the client needs.
    """

    def __init__(self):

         # Store API key but don't create client yet
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Check if LLM is available
        if self.api_key:
            print(f"✓ OpenAI API key found, will use model: {self.model}")
            self.llm_available = True
        else:
            print("⚠️ No OpenAI API key found - LLM detection disabled")
            self.llm_available = False

        # layer 1: keyword/ patterns
        self.trigger_patterns = {
             'life_events': {
                # Each key is an event type, value is list of phrases that indicate it
                'marriage': [
                    'getting married', 'engaged', 'wedding', 
                    'fiancé', 'fiancée', 'propose', 'engagement'
                ],
                'baby': [
                    'expecting', 'pregnant', 'baby', 'child',
                    'newborn', 'maternity', 'paternity'
                ],
                'job_change': [
                    'new job', 'quit', 'fired', 'laid off',
                    'retirement', 'retiring', 'career change',
                    'promotion', 'new position'
                ],
                'death': [
                    'passed away', 'died', 'death', 'funeral',
                    'estate', 'inheritance', 'widow', 'widower'
                ],
                'education': [
                    'college', 'university', 'tuition', 'student',
                    'scholarship', 'degree', 'graduate', 'school'
                ],
                'property': [
                    'house', 'home', 'mortgage', 'rent',
                    'property', 'real estate', 'buying', 'selling'
                ]
            },
            
            'financial_products': {
                # Financial products they might need
                '401k': [
                    '401k', '401(k)', 'four oh one kay',
                    'employer match', 'company retirement'
                ],
                'ira': [
                    'ira', 'roth', 'traditional ira',
                    'individual retirement', 'rollover'
                ],
                'insurance': [
                    'insurance', 'life insurance', 'term life',
                    'whole life', 'disability', 'long-term care'
                ],
                '529': [
                    '529', 'college savings', 'education savings',
                    'coverdell', 'esa'
                ]
            }

        }

        # age triggers
        self.age_triggers = {
            50: ['catch_up_contributions'],  # IRS allows extra retirement savings
            59.5: ['penalty_free_withdrawals'],  # Can withdraw from retirement accounts
            62: ['social_security_early'],  # Earliest Social Security age
            65: ['medicare'],  # Medicare eligibility
            67: ['full_retirement_age'],  # Full Social Security benefits
            70.5: ['required_distributions'],  # Must start taking from retirement accounts
            72: ['rmd_current']  # Current RMD age (changed from 70.5)
        }

        # opportunity definitions
        # detail about what to recommend

        self.opportunities = {
            'retirement_planning': {
                'title': '401(k) and Retirement Planning Review',
                'description': 'Client may benefit from retirement account optimization',
                'base_score': 75,  # Base priority score (0-100)
                'keywords': ['retirement', '401k', 'retire', 'pension'],
                'min_age': 25,  # Don't suggest to people too young
                'max_age': 70   # Don't suggest to already retired
            },
            
            'education_planning': {
                'title': '529 Education Savings Plan',
                'description': 'Client has education funding needs',
                'base_score': 80,
                'keywords': ['college', 'university', 'tuition', 'education'],
                'min_age': 25,  # Likely to have children
                'max_age': 60   # Children likely already through college
            },
            
            'life_insurance': {
                'title': 'Life Insurance Coverage Review',
                'description': 'Client may need life insurance for family protection',
                'base_score': 85,
                'keywords': ['baby', 'married', 'mortgage', 'family'],
                'min_age': 25,
                'max_age': 65
            },
            
            'estate_planning': {
                'title': 'Estate Planning and Will Preparation',
                'description': 'Client should consider estate planning documents',
                'base_score': 70,
                'keywords': ['inheritance', 'estate', 'will', 'trust'],
                'min_age': 35,
                'max_age': 90
            },
            
            'tax_optimization': {
                'title': 'Tax Optimization Strategy',
                'description': 'Client could benefit from tax-efficient strategies',
                'base_score': 65,
                'keywords': ['tax', 'deduction', 'capital gains', 'tax bracket'],
                'min_age': 30,
                'max_age': 75
            }
        }
    
    def detect_opportunities(
        self,
        transcript: str,
        client_profile: Optional[Dict] = None,
        use_llm: bool = True
    ) -> List[Dict]:

        """
        Main method that coordinates all detection layers.
        
        Parameters:
        -----------
        transcript : str
            The conversation text to analyze
        client_profile : Optional[Dict]
            Information about the client (age, income, etc.)
            Optional means it can be None
        use_llm : bool
            Whether to use GPT-4 for deep analysis (costs money)
            
        Returns:
        --------
        List[Dict] : List of opportunity dictionaries, sorted by score
        """

        # initialize lis of opportunities
        all_opportunities = []

        # layer 1: Pattern-based detection
        pattern_opportunities = self._detect_patterns(transcript)
        all_opportunities.extend(pattern_opportunities)

        # layer 2: Contextual detection (combines patterns with client profile)
        if client_profile:
            contextual_opportunities = self._detect_contextual(transcript,client_profile)
            all_opportunities.extend(contextual_opportunities)

        # layer 3: LLM-based detection
        if use_llm and self.llm_available:
            llm_opportunties = self._detect_with_llm(transcript,client_profile)
            all_opportunities.extend(llm_opportunties)
        
        # remove duplicates and sort by score
        unique_opportunities = {}
        for opp in all_opportunities:
            opp_type = opp.get('type')

            # if unseen / high score, keep it
            if opp_type not in unique_opportunities or opp.get('score') > unique_opportunities[opp_type].get('score',0):
                unique_opportunities[opp_type] = opp

        # convert back to sorted opportunities-> highest score first
        sorted_opportunities = sorted(
            unique_opportunities.values(),
            key = lambda x: x.get('score',0),
            reverse = True
        )

        return sorted_opportunities

    def _detect_patterns(self, transcript: str)-> List[Dict]:
        """
        Layer 1: Simple pattern matching.
        
        This method looks for keywords and phrases in the transcript.
        It's fast and doesn't cost anything (no API calls).
        
        Parameters:
        -----------
        transcript : str
            The text to search through
            
        Returns:
        --------
        List[Dict] : Opportunities found through pattern matching
        """

        opportunities = []

        transcript_lower = transcript.lower()

        for opp_type, opp_details in self.opportunities.items():

            # get keywords for this opportunity
            keywords = opp_details.get('keywords',[])

            # check if keyword in transcript
            for keyword in keywords:
                if keyword in transcript_lower:
                    # match -> create opportunity
                    opportunity = {
                        'type': opp_type,
                        'title': opp_details['title'],
                        'description': opp_details['description'],
                        'score': opp_details['base_score'],
                        'detected_by': 'pattern_matching',
                        'trigger': f'Keyword: {keyword}',
                        'timestamp': datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)
                    
                    # Break to avoid duplicate opportunities of same type
                    break

        # Check for life events 
        for event_category, events in self.trigger_patterns['life_events'].items():
            for trigger_phrase in events:
                if trigger_phrase in transcript_lower:
                    # Map life events to opportunities
                    if event_category == 'baby':
                        opportunity = {
                            'type': 'life_insurance',
                            'title': 'Life Insurance for New Parents',
                            'description': 'New baby mentioned - life insurance critical',
                            'score': 90,  # High priority for new parents
                            'detected_by': 'pattern_matching',
                            'trigger': f'Life event: {trigger_phrase}',
                            'timestamp': datetime.now().isoformat()
                        }
                        opportunities.append(opportunity)
                    
                    elif event_category == 'education':
                        opportunity = {
                            'type': 'education_planning',
                            'title': '529 College Savings Plan',
                            'description': 'Education mentioned - explore 529 plans',
                            'score': 85,
                            'detected_by': 'pattern_matching',
                            'trigger': f'Education: {trigger_phrase}',
                            'timestamp': datetime.now().isoformat()
                        }
                        opportunities.append(opportunity)
                    
                    # Only match first trigger to avoid duplicates
                    break
        
        return opportunities
    
    def _detect_contextual(
        self, 
        transcript: str, 
        client_profile: Dict
    ) -> List[Dict]:
        """
        Layer 2: Contextual detection using client profile.
        
        This combines what we know about the client (age, income, etc.)
        with what they're saying to find opportunities.
        
        Example: 58-year-old saying "tired of working" = early retirement
        
        Parameters:
        -----------
        transcript : str
            The conversation text
        client_profile : Dict
            Client information like {'age': 58, 'income': 150000}
            
        Returns:
        --------
        List[Dict] : Context-aware opportunities
        """
        
        opportunities = []
        transcript_lower = transcript.lower()
        
        # Get client age, default to 40 if not provided
        client_age = client_profile.get('age', 40)
        
        # Age-based opportunities
        if client_age >= 50 and client_age < 60:
            # Check for retirement interest
            retirement_hints = [
                'tired', 'exhausted', 'stress', 'retire',
                'slowing down', 'next chapter', 'grandkids'
            ]
            
            for hint in retirement_hints:
                if hint in transcript_lower:
                    opportunity = {
                        'type': 'early_retirement',
                        'title': 'Early Retirement Planning',
                        'description': f'At age {client_age}, client showing retirement interest',
                        'score': 88,
                        'detected_by': 'contextual_analysis',
                        'trigger': f'Age {client_age} + mentioned "{hint}"',
                        'timestamp': datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)
                    break
        
        # Catch-up contributions (age 50+)
        if client_age >= 50:
            # IRS allows extra retirement contributions at 50+
            if any(word in transcript_lower for word in ['saving', 'retirement', '401k', 'ira']):
                opportunity = {
                    'type': 'catch_up_contributions',
                    'title': 'Catch-Up Contribution Strategy',
                    'description': f'Age {client_age} qualifies for additional $7,500 401(k) contributions',
                    'score': 82,
                    'detected_by': 'contextual_analysis',
                    'trigger': f'Age {client_age} + retirement discussion',
                    'timestamp': datetime.now().isoformat()
                }
                opportunities.append(opportunity)
        
        # High income opportunities
        income = client_profile.get('income', 0)
        if income > 200000:
            if 'tax' in transcript_lower or 'income' in transcript_lower:
                opportunity = {
                    'type': 'tax_optimization',
                    'title': 'High-Income Tax Strategy',
                    'description': f'Income ${income:,} may benefit from advanced tax strategies',
                    'score': 85,
                    'detected_by': 'contextual_analysis',
                    'trigger': f'High income + tax discussion',
                    'timestamp': datetime.now().isoformat()
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_with_llm(
        self, 
        transcript: str, 
        client_profile: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Layer 3: AI-powered detection using GPT-4.
        
        This sends the conversation to GPT-4 for intelligent analysis.
        It can understand context, implications, and subtle hints that
        rule-based systems would miss.
        
        Parameters:
        -----------
        transcript : str
            The conversation to analyze
        client_profile : Optional[Dict]
            Client information to provide context to GPT-4
            
        Returns:
        --------
        List[Dict] : AI-detected opportunities
        """
        
        # Check API key exists
        if not self.llm_available:
            print("No OpenAI API key found - skipping LLM detection")
            return []
        
        try:
            # Build the prompt for GPT-4
            prompt = self._build_llm_prompt(transcript, client_profile)
            
            # Use direct HTTP requests to avoid client initialization issues
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {
                        "role": "system",
                        "content": "You are a financial advisor assistant specialized in identifying opportunities from client conversations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                'temperature': 0.3,
                'max_tokens': 500
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            response_data = response.json()
            llm_response = response_data['choices'][0]['message']['content']
            
            # Parse the LLM response into opportunities
            opportunities = self._parse_llm_response(llm_response)
            
            return opportunities
            
        except Exception as e:
            print(f"LLM detection failed: {e}")
            return []
    
    def _build_llm_prompt(
        self, 
        transcript: str, 
        client_profile: Optional[Dict]
    ) -> str:
        """
        Build a detailed prompt for GPT-4.
        
        This method creates a structured prompt that tells GPT-4
        exactly what we want it to analyze and how to format its response.
        
        Parameters:
        -----------
        transcript : str
            The conversation to analyze
        client_profile : Optional[Dict]
            Client context information
            
        Returns:
        --------
        str : The formatted prompt for GPT-4
        """
        
        # Start with client context if available
        if client_profile:
            income = client_profile.get('income', 'Unknown')
            if isinstance(income, (int, float)):
                income_str = f"${income:,}"
            else:
                income_str = str(income)
                
            context = f"""
Client Profile:
- Age: {client_profile.get('age', 'Unknown')}
- Income: {income_str}
- Family: {client_profile.get('family_status', 'Unknown')}
- Current Products: {client_profile.get('products', [])}
"""
        else:
            context = "No client profile available."
        
        # Build the complete prompt
        prompt = f"""
Analyze this financial advisor-client conversation for opportunities:

{context}

Conversation:
{transcript}

Identify financial planning opportunities. For each opportunity, provide:
1. Type (e.g., retirement_planning, education_planning, insurance)
2. Specific recommendation
3. Priority score (0-100)
4. Reasoning

Format your response as a JSON array like this:
[
    {{
        "type": "opportunity_type",
        "title": "Specific Opportunity Title",
        "description": "Why this is relevant",
        "score": 85,
        "reasoning": "Client mentioned X which indicates Y"
    }}
]

Focus on opportunities that are:
- Directly relevant to the conversation
- Actionable for the advisor
- Appropriate for the client's age and situation

Return ONLY the JSON array, no other text.
"""
        
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> List[Dict]:
        """
        Parse the GPT-4 response into opportunity dictionaries.
        
        GPT-4 returns text that should be JSON. We need to:
        1. Extract the JSON from the response
        2. Parse it into Python objects
        3. Add our metadata
        
        Parameters:
        -----------
        llm_response : str
            The text response from GPT-4
            
        Returns:
        --------
        List[Dict] : Parsed opportunities with metadata added
        """
        
        opportunities = []
        
        try:
            # Find JSON in the response
            # Sometimes GPT-4 adds explanation before/after the JSON
            json_start = llm_response.find('[')
            json_end = llm_response.rfind(']') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = llm_response[json_start:json_end]
                
                # Parse the JSON
                parsed_opportunities = json.loads(json_str)
                
                # Add our metadata to each opportunity
                for opp in parsed_opportunities:
                    # Ensure required fields exist
                    if 'type' in opp and 'title' in opp:
                        opportunity = {
                            'type': opp.get('type'),
                            'title': opp.get('title'),
                            'description': opp.get('description', ''),
                            'score': opp.get('score', 70),
                            'detected_by': 'llm_analysis',
                            'trigger': opp.get('reasoning', 'AI analysis'),
                            'timestamp': datetime.now().isoformat()
                        }
                        opportunities.append(opportunity)
                        
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            # Could still try to extract insights even if JSON parsing fails
            # This is a fallback mechanism
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
        
        return opportunities

    def score_opportunity(
        self, 
        opportunity: Dict, 
        client_profile: Optional[Dict] = None
    ) -> float:
        """
        Calculate final score for an opportunity.
        
        This method adjusts the base score based on various factors:
        - Client age appropriateness
        - Income level
        - Urgency indicators in conversation
        
        Parameters:
        -----------
        opportunity : Dict
            The opportunity to score
        client_profile : Optional[Dict]
            Client information for scoring adjustments
            
        Returns:
        --------
        float : Adjusted score (0-100)
        """
        
        # Start with base score
        score = opportunity.get('score', 50)
        
        if not client_profile:
            return score
        
        # Age adjustment
        client_age = client_profile.get('age', 40)
        opp_type = opportunity.get('type')
        
        # Get age range for this opportunity type
        if opp_type in self.opportunities:
            min_age = self.opportunities[opp_type].get('min_age', 0)
            max_age = self.opportunities[opp_type].get('max_age', 100)
            
            # Reduce score if client is outside ideal age range
            if client_age < min_age:
                score *= 0.7  # 30% reduction if too young
            elif client_age > max_age:
                score *= 0.7  # 30% reduction if too old
        
        # Income adjustment for certain opportunities
        income = client_profile.get('income', 0)
        if income > 150000 and opp_type in ['tax_optimization', 'estate_planning']:
            score *= 1.2  # 20% boost for high-income relevant opportunities
        
        # Cap score at 100
        score = min(score, 100)
        
        return score