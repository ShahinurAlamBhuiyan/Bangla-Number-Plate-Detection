import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from fastapi import APIRouter, HTTPException
#DATABASE
app = FastAPI()

# MongoDB URI
uri = "mongodb+srv://admin:admin@cluster0.evtt2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize MongoDB client
my_client = AsyncIOMotorClient(uri)

# Access the database and collection
db = my_client.DhakaTraffic
vatara = db["Vatara"]
culprit = db["Culprit"]


# async def insert(data):
#     insertion = await culprit.insert_one(data)
#     print(insertion.acknowledged)
#
#
# asyncio.run(insert({"Charges": "Murder","area_english": "Dhaka Metro-H", "number_english": "22-6457"}))




# router = APIRouter()
# @router.post("/create/create_record")
# async def create_record(data):
#     try:
#         # Insert the data into the MongoDB collection
#         result = await vatara.insert_one(data)
#
#         if result.acknowledged:
#             return {"message": "Record successfully inserted into MongoDB"}
#         else:
#             raise HTTPException(status_code=500, detail="Failed to insert data into MongoDB")
#
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")