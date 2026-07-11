from pydantic import BaseModel, PositiveInt, Field,field_validator, model_validator
from typing import Annotated,Literal
import json
from datetime import datetime,timezone
import re

from data_generator.ecommerce_data import HighVolumeDataGenerator

data = HighVolumeDataGenerator()
user_data= data.fetch_users_from_api()

class Name(BaseModel):
    first: Annotated[
        str,
        Field(
            title= 'First name',
            description='The first name of the user'
        )
    ]
    last: Annotated[
        str,
        Field(
            title='Last name ',
            description='This is the last name of the user'
        )
    ]
    title: str

    @field_validator('first','last')
    @classmethod

    def validate_first_and_last_name(cls,names):
        if not all(c.isalpha() or c in " -'" for c in names):
            raise ValueError("Invalid characters in name")

        return names
    
    @field_validator('title')
    @classmethod
    def validate_title(cls,value):
        allowed={
            "Mr",
            "Mrs",
            "Ms",
            "Miss",
            "Dr",
            "Prof",
            "Eng",
            "Mademoiselle",
            "Monsieur",
            "Madame"
        }

        if value not in allowed:
            raise ValueError(f'Title must be one of {allowed}')
        return value

class Location(BaseModel):
    city:str
    country:str
    state:str
    postcode:str
    latitude:float
    longitude:float

class Preference(BaseModel):
    preferred_brands: list[str]
    preferred_category: str
    price_sensitivity: Literal["Low","Medium","High"]
    shopping_frequency: Literal[
        "Hourly",
        "Daily",
        "Weekly",
        "Monthly",
        "Occasional",
        "Occasionally"
    ]

    @field_validator('preferred_brands')
    @classmethod
    def validate_brand(cls,brands):
        Allowed_brands={
            "Arc'teryx",
            "Salomon",
            "Patagonia",
            "Nike",
            "Adidas",
            "The North Face",
            "Hoka",
            "Brooks",
            "Under Armour"
        }
        invalid = [
            b for b in brands 
            if b not in Allowed_brands
        ]
        if invalid:
            raise ValueError(
                f'Unknown brands: {invalid}'
            )
        
        return brands 

class user(BaseModel):
    user_id:Annotated[
        str,
        Field(
            title='User id',
            description='Unique user id to all the users',
            min_length= 5
        )
    ]

    email: Annotated[
        str,
        Field(
            title="Email",
            description='Email of each user',

        )
    ]

    name: Name 

    gender: Annotated[
        str,
        Field(
            title='Gender',
            description="Describe sthe Gender of the user"
        )
    ]

    phone: Annotated[
        str,
        Field(
            title='Phone number',
            description="Describes the phone number of the user used for registration"
        )
    ]

    age:Annotated[
        PositiveInt,
        Field(
            title="Age",
            description="This is the age of the user "
        )
    ]

    location: Location
    nationality: str 
    picture: str 
    preferences: Preference

    past_purchases: list[str]
    loyalty_tier:Literal[
        'Bronze',
        'Silver',
        'Gold',
        'Platinum'
    ]

    avg_order_value: Annotated[
        float,
        Field(
            gt=0
        )
    ]
    registered_date: datetime
    last_active : datetime

    @field_validator('email')
    @classmethod

    def validate_email(cls,value):
        if "@" not in value:
            raise ValueError(f"Email must contain {'@'}")
        return value
    
    
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls,value):
        allowed={
            'male',
            'female'
        }

        if value not in allowed:
            raise ValueError(f"Gender must be one of {allowed}")
        
        return value 
        
    @field_validator('age')
    @classmethod

    def validate_age(cls,value):
        if value < 18:
            raise ValueError("Age should be above 18")
        return value
    

    
    @field_validator('past_purchases')
    @classmethod
    def validate_past_purchases(cls,purchases):
        valid_sku={
            "ARC-ATOM-M-BLK",
            "SAL-XULTRA-4-10",
            "PAT-NANO-M-BLK",
            "NIK-AIR-MAX",
            "ADID-ULTRABOOST",
            "COL-NORTH-FACE",
            "ARC-ATOM-W-BLK",
            "PAT-NANO-W-BLK",
            "NIK-AIR-WHITE",
            "ADID-ULTRABOOST-W",
            "SAL-XULTRA-W",
            "NORTH-DENALI",
            "PAT-BETTER-SWEAT",
            "ARC-COVERT",
            "NIK-AIR-FORCE",
            "HOKA-SPEEDGOAT",
            "BROOKS-GHOST",
            "UNDER-ARMOUR"
        }

        invalid = [
            sku for sku in purchases
            if sku not in valid_sku
        ]

        if invalid:
            raise ValueError(
                f"Unknown product SKUs: {invalid}"
            )
        
        return purchases 
    
    @model_validator(mode ='after')
    def validate_dates(self):

        registered = self.registered_date
        last_active=self.last_active

        if registered.tzinfo is None:
            registered=registered.replace(tzinfo=timezone.utc)

        if last_active.tzinfo is None:
            last_active= last_active.replace(tzinfo=timezone.utc)

        if last_active < registered:
            raise ValueError(
                "Last_active cannot be before registration"
            )
        
        return self

validated_users=[]

for record in user_data:
    try:
        validated=user.model_validate(record)
        validated_users.append(validated)

    except Exception as e:
        print(f'Validation Failed: {e}')

print(f'Validated {len(validated_users)} users')

if validated_users:
    print(validated_users[0])
else: 
    print('No Valid users were found')