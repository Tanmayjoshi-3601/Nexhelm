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
        self.client = None
        self.connected = False
        
        # connect to Redis
        try:
            self.client = redis.Redis(
                host = os.getenv('REDIS_HOST','localhost'),
                port = int(os.getenv('REDIS_PORT',6379)),
                db = int(os.getenv('REDIS_DB',0)),
                decode_responses = True, # tells Redis to output python str instead of bytes
                socket_connect_timeout=5,  # 5 second timeout
                socket_timeout=5
            )
            
            # Test connection
            self.client.ping()
            self.connected = True
            print("✅ Connected to Redis successfully")    
            
        except redis.ConnectionError as e:
            print(f"❌ Failed to connect to Redis: {e}")
            print("💡 Make sure Redis is running: redis-server")
            self.connected = False
            self.client = None
        except Exception as e:
            print(f"❌ Unexpected error connecting to Redis: {e}")
            self.connected = False
            self.client = None
    
    def add_message(self, meeting_id:str, message:str):
        """ Add message to conversation history"""
        if not self.connected or not self.client:
            print("⚠️ Redis not connected - message not stored")
            return

        # Redis LIST to store messages
        key = f"Conversation:{meeting_id}"

        try:
            # add to list from the start(not the appending)
            self.client.lpush(key,message)

            # keep only last 100 messages (sliding window)
            self.client.ltrim(key, 0, 99)

            # set expiry to 1 hour (auto-cleanup)
            self.client.expire(key, 3600)
        except Exception as e:
            print(f"❌ Error adding message to Redis: {e}")
    
    def get_conversation(self, meeting_id: str, last_n:int=50):
        """Get recent conversation history"""
        if not self.connected or not self.client:
            print("⚠️ Redis not connected - returning empty conversation")
            return []

        key = f"Conversation:{meeting_id}"

        try:
            # get messages newest first so reverse -> returns the items from index 0 to index last_n-1
            messages = self.client.lrange(key, 0, last_n-1)
            return list(reversed(messages))
        except Exception as e:
            print(f"❌ Error getting conversation from Redis: {e}")
            return []
    
    def add_opportunity(self, meeting_id:str, opportunity:dict, score:float):
        """Add opportunity with priority score"""
        if not self.connected or not self.client:
            print("⚠️ Redis not connected - opportunity not stored")
            return

        key  = f"opportunities:{meeting_id}"

        try:
            # use Redis SORTED SET for priorities
            self.client.zadd(key, {json.dumps(opportunity): score })

            #set expiry
            self.client.expire(key,3600)
        except Exception as e:
            print(f"❌ Error adding opportunity to Redis: {e}")
    
    def get_top_opportunities(self, meeting_id: str, count: int= 5):
        """ Get top opportunities by priority """
        if not self.connected or not self.client:
            print("⚠️ Redis not connected - returning empty opportunities")
            return []

        key = f"opportunities:{meeting_id}"

        try:
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
        except Exception as e:
            print(f"❌ Error getting opportunities from Redis: {e}")
            return []
    
    def create_meeting(self, meeting_id:str, client_id:str):
        """Create new meeting session"""
        if not self.connected or not self.client:
            print("⚠️ Redis not connected - creating meeting in memory only")
            return {
                'client_id': client_id,
                'status': 'active',
                'start_time': 'unknown'
            }

        key = f"meeting:{meeting_id}"

        try:
            meeting_data = {
                'client_id': client_id,
                'status':'active',
                'start_time':self.client.time()[0]
            }

            # Use Redis HASH for meeting data
            self.client.hset(key, mapping=meeting_data)
            self.client.expire(key, 3600)

            return meeting_data
        except Exception as e:
            print(f"❌ Error creating meeting in Redis: {e}")
            return {
                'client_id': client_id,
                'status': 'active',
                'start_time': 'unknown'
            }

    def get_meeting(self, meeting_id: str):
        """Get meeting information"""
        if not self.connected or not self.client:
            print("⚠️ Redis not connected - returning empty meeting data")
            return {}

        key = f"meeting:{meeting_id}"
        
        try:
            return self.client.hgetall(key)
        except Exception as e:
            print(f"❌ Error getting meeting from Redis: {e}")
            return {}

# create singleton instance
redis_client = RedisClient()






