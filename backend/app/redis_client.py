import redis
from typing import Optional 
import json
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

class RedisClient:
    """Handles all Redis operations"""

    def __init__(self):

        # connect to Redis
        self.client = redis.Redis(
            host = os.getenv('REDIS_HOST','localhost'),
            port = int(os.getenv('REDIS_PORT',6379)),
            db = int(os.getenv('REDIS_DB',0)),
            decode_responses = True # tells Redis to output python str instead of bytes
        )
    
        # Test connection
        try:
            self.client.ping()
            print("Connected to Redis")    
        except redis.ConnectionError:
            print('Failed to connect to redis')
    
    def add_message(self, meeting_id:str, message:str):
        """ Add message to conversation history"""

        # Redis LIST to store messages
        key = f"Conversation:{meeting_id}"

        # add to list from the start(not the appending)
        self.client.lpush(key,message)

        # keep only last 100 messages (sliding window)
        self.client.ltrim(key, 0, 99)

        # set expiry to 1 hour (auto-cleanup)
        self.client.expire(key, 3600)
    
    def get_conversation(self, meeting_id: str, last_n:int=50):
        
        """Get recent conversation history"""
        key = f"Conversation:{meeting_id}"

        # get messages newest first so reverse -> returns the items from index 0 to index last_n-1
        messages = self.client.lrange(key, 0, last_n-1)

        return list(reversed(messages))
    
    def add_opportunity(self, meeting_id:str, opportunity:dict, score:float):
        """Add opportunity with priority score  """

        key  = f"opportunities:{meeting_id}"

        # use Redis SORTED SET for priorities
        self.client.zadd(key, {json.dumps(opportunity): score })

        #set expiry
        self.client.expire(key,3600)
    
    def get_top_opportunities(self, meeting_id: str, count: int= 5):
        """ Get top opportunities by priority """
        key = f"opportunities:{meeting_id}"

        # get highest scoring opportunities
        opportunities = self.client.zrange(
            key, 0 , count-1,
            desc = True,  # Highest score first
            withscores = True
        )

        # parse JSON and return with scores
        result = []
        for opp_json, score in opportunities:
            result.append({
                'opportunity':json.loads(opp_json),
                'score':score
            })
        
        return result
    
    def create_meeting(self, meeting_id:str, client_id:str):
        """Create new meeting session"""
        key = f"meeting:{meeting_id}"

        meeting_data = {
            'client_id': client_id,
            'status':'active',
            'start_time':self.client.time()[0]
        }

        # Use Redis HASH for meeting data
        self.client.hset(key, mapping=meeting_data)
        self.client.expire(key, 3600)

        return meeting_data

    def get_meeting(self, meeting_id: str):
        """Get meeting information"""
        key = f"meeting:{meeting_id}"
        return self.client.hgetall(key)

# create singleton instance
redis_client = RedisClient()






