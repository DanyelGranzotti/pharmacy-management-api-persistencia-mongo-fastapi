import motor.motor_asyncio
from decouple import config

# Get MongoDB configuration from environment variables
MONGODB_USERNAME = config("MONGODB_USERNAME")
MONGODB_PASSWORD = config("MONGODB_PASSWORD")
MONGODB_CLUSTER = config("MONGODB_CLUSTER")
DATABASE_NAME = config("MONGODB_DATABASE")

# Construct MongoDB connection URL
MONGODB_URL = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=Cluster"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

async def check_database_connection():
    try:
        # Ping the database
        await client.admin.command('ping')
        return {"status": "healthy", "message": "Successfully connected to MongoDB"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}
