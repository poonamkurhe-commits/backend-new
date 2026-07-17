from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        try:
            # Get MongoDB Atlas connection string from environment
            mongodb_url = os.getenv("MONGODB_URL")
            
            if not mongodb_url:
                raise ValueError("MONGODB_URL environment variable is not set")
            
            # Connect to MongoDB Atlas with SSL/TLS
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # Get database
            db_name = os.getenv("DB_NAME", "prepace")
            cls.db = cls.client[db_name]
            
            # Test connection
            await cls.client.admin.command('ping')
            print(f"✅ Successfully connected to MongoDB Atlas! Database: {db_name}")
            print(f"📍 Cluster: {cls.client.address}")
            
            # Create indexes for better performance
            await cls._create_indexes()
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB Atlas connection failed: {e}")
            print("Please check your MONGODB_URL in .env file")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()
            print("✅ Disconnected from MongoDB Atlas")

    @classmethod
    def get_collection(cls, name):
        if cls.db is None:
            raise Exception("Database not initialized. Call connect() first.")
        return cls.db[name]

    @classmethod
    async def _create_indexes(cls):
        """Create indexes for better query performance"""
        try:
            # Users collection indexes
            users = cls.db["users"]
            await users.create_index("email", unique=True)
            await users.create_index("username", unique=True)
            
            # Questions collection indexes
            questions = cls.db["questions"]
            await questions.create_index([("subject", 1), ("type", 1)])
            await questions.create_index("topic")
            
            # Results collection indexes
            results = cls.db["results"]
            await results.create_index([("user_id", 1), ("completed_at", -1)])
            await results.create_index("subject")
            
            print("✅ Database indexes created successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")