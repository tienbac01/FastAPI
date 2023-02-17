import motor.motor_asyncio
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from fastapi.encoders import jsonable_encoder
from pprint import pprint

MONGODB_URL = "mongodb://localhost:27017"
app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.IOPS

collection_user = db.get_collection("user")


class User(BaseModel):
    fullname: str
    password: str
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Nguyen Van A",
                "password": "****",
                "email": "john@gmail.com",
            }
        }


def ResponseModel(data, message):
    return {"data": [data], "code": 200, "message": message}


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "fullname": user["fullname"],
        "email": user["email"],
    }


@app.post("/users/register")
async def users_create(user: User):
    data = jsonable_encoder(user)
    add_user = await collection_user.insert_one(data)
    new_user = await collection_user.find_one({"_id": add_user.inserted_id})

    return ResponseModel(user_helper(new_user), "User created successfully")
@app.get("/s")
