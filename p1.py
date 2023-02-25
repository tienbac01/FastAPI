import motor.motor_asyncio
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from fastapi.encoders import jsonable_encoder
from pprint import pprint
from bson import ObjectId

MONGODB_URL = "mongodb://localhost:27017"
app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.IOPS

collection_user = db.get_collection("user")


class User(BaseModel):
    fullname: str | None = None
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


class UpdateUser(BaseModel):
    fullname: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Nguyen Van A",
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


@app.get("/users/{id}")
async def get_user(id: str):
    user = await collection_user.find_one({"_id": ObjectId(id)})

    try:
        return ResponseModel(user_helper(user), "Query success.")
    except:
        return ErrorResponseModel("Invalid request", 400, "Error")
    # if user:
    #     return user_helper(user)
    # else:
    #     return ErrorResponseModel("Empty DB", 201, "Success")


@app.put("/users/{id}")
async def user_update(id: str, req: UpdateUser):
    data = {k: v for k, v in req.dict().items() if v is not None}

    try:
        user = await collection_user.find_one({"_id": ObjectId(id)})
        pprint(user)
        pprint(user)
        if user:
            updated_user = await collection_user.update_one(
                {"_id": ObjectId(id)}, {"$set": data}
            )

            if updated_user:
                return ResponseModel(
                    "Update with id {} name is formated".format(id),
                    "User update successfully",
                )
            return ErrorResponseModel("An error occurred", 404, "Error edit data")
    except:
        return ErrorResponseModel("Invalid request", 400, "Error")


@app.delete("/users/{id}")
async def delete_user(id: str):
    try:
        user = await collection_user.find_one({"_id": ObjectId(id)})
        if user:
            await collection_user.delete_one({"_id": ObjectId(id)})
            return ResponseModel(
                "User with id {} is deleted".format(id),
                "User deleted successfully",
            )
    except:
        return ErrorResponseModel("Invalid request", 400, "Error")
