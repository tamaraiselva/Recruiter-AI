from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

client = AsyncIOMotorClient("mongodb://localhost:27017/db")
database = client.job_description_db
job_description_collection = database.get_collection("job_descriptions")
