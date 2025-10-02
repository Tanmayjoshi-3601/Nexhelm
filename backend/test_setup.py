print("Testing imports")

try:
    import fastapi
    print("✓ FastAPI installed")
except:
    print("✗ FastAPI missing")

try:
    import socketio
    print("✓ SocketIO installed")
except:
    print("✗ SocketIO missing")

try:
    import redis
    print("✓ Redis client installed")
except:
    print("✗ Redis client missing")

try:
    import openai
    print("✓ OpenAI installed")
except:
    print("✗ OpenAI missing")


# test redis connection
try:
    import redis
    r = redis.Redis(host='localhost',port = 6379, decode_responses = True)
    r.ping()
    print("Redis server runing")
except:
    print("Redis server not running")

    