from datetime import datetime
from app.models.license import License
from app.db.database import db
from fastapi import HTTPException

async def create_license(license: License):
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    result = await db["licenses"].insert_one(license.dict())
    return result.inserted_id

async def get_available_licenses(user_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    
    current_time = datetime.utcnow()
    licenses = await db["licenses"].find({
        "user_id": user_id,
        "expire_date": {"$gt": current_time.isoformat()}
    }).to_list(length=None)

    # Convert ObjectId to string and return as a list of dictionaries
    return [
        {
            "user_id": str(license["user_id"]),
            "license_key": license["license_key"],
            "expire_date": license["expire_date"],
            "device_number": license.get("device_number")  # Use .get() to avoid KeyError
        }
        for license in licenses
    ]

async def check_and_update_device_address(license_key: str, device_address: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    
    license_entry = await db["licenses"].find_one({"license_key": license_key})
    
    if not license_entry:
        raise HTTPException(status_code=404, detail="License key not found")
    
    current_device_address = license_entry.get("device_number")
    
    if current_device_address is None:
        # Update the device address if it's not set
        await db["licenses"].update_one(
            {"license_key": license_key},
            {"$set": {"device_number": device_address}}
        )
        return {"status": "success", "message": "Device address set successfully"}
    elif current_device_address != device_address:
        # If the device address is already set and doesn't match
        raise HTTPException(status_code=400, detail="Device address does not match")
    
    return {"status": "success", "message": "Device address is already set and matches"}