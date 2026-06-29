from pydantic import BaseModel, field_validator, model_validator, EmailStr
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 1 — CSV (Telco Customer Churn)
# Columns: customerID, gender, SeniorCitizen, tenure, PhoneService,
#          Contract, MonthlyCharges, TotalCharges, Churn
# ─────────────────────────────────────────────────────────────────────────────

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"


class ContractEnum(str, Enum):
    month_to_month = "Month-to-month"
    one_year = "One year"
    two_year = "Two year"


class CsvCustomerRecord(BaseModel):
    customerID: str
    gender: GenderEnum
    SeniorCitizen: int                      # 0 or 1
    tenure: int                             # months as customer
    PhoneService: str
    Contract: ContractEnum
    MonthlyCharges: float
    TotalCharges: Optional[float] = None    # can be blank for new customers

    # Derived / output field — not in raw CSV, we compute it
    Churn: str

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("customerID")
    @classmethod
    def customer_id_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("customerID cannot be blank")
        return v.strip()

    @field_validator("SeniorCitizen")
    @classmethod
    def senior_citizen_must_be_binary(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError(f"SeniorCitizen must be 0 or 1, got {v}")
        return v

    @field_validator("tenure")
    @classmethod
    def tenure_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"tenure must be >= 0, got {v}")
        return v

    @field_validator("MonthlyCharges")
    @classmethod
    def monthly_charges_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"MonthlyCharges must be >= 0, got {v}")
        return round(v, 2)

    @field_validator("TotalCharges", mode="before")
    @classmethod
    def total_charges_coerce_empty(cls, v):
        """
        Telco CSV has blank TotalCharges for customers with tenure=0.
        Coerce empty string / None → None instead of crashing.
        """
        if v == "" or v is None:
            return None
        try:
            val = float(v)
            if val < 0:
                raise ValueError(f"TotalCharges must be >= 0, got {val}")
            return round(val, 2)
        except (ValueError, TypeError):
            raise ValueError(f"TotalCharges must be a number, got: {v!r}")

    @field_validator("Churn")
    @classmethod
    def churn_must_be_yes_or_no(cls, v: str) -> str:
        if v not in ("Yes", "No"):
            raise ValueError(f"Churn must be 'Yes' or 'No', got {v!r}")
        return v

    @field_validator("PhoneService")
    @classmethod
    def phone_service_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("PhoneService cannot be blank")
        return v.strip()


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 2 — REST API (JSONPlaceholder /posts)
# Shape: { "userId": int, "id": int, "title": str, "body": str }
# ─────────────────────────────────────────────────────────────────────────────

class ApiPostRecord(BaseModel):
    userId: int
    id: int
    title: str
    body: str

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("userId", "id")
    @classmethod
    def ids_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError(f"ID fields must be > 0, got {v}")
        return v

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be blank")
        if len(v) > 500:
            raise ValueError(f"title too long ({len(v)} chars), max 500")
        return v

    @field_validator("body")
    @classmethod
    def body_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("body cannot be blank")
        return v


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 3 — MongoDB (users collection)
# Your mongo_extractor.py fetches from the "users" collection.
# We define a realistic user document shape here.
# Shape: { "_id": str, "name": str, "email": str, "age": int,
#          "country": str (2-char ISO), "is_active": bool,
#          "tags": list[str] (optional) }
# ─────────────────────────────────────────────────────────────────────────────

class MongoUserRecord(BaseModel):
    id: str
    name: str
    email: EmailStr
    age: int
    country: str
    is_active: bool
    tags: Optional[list[str]] = None

    model_config = {"populate_by_name": True}

    @field_validator("id")
    @classmethod
    def id_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("_id cannot be blank")
        return v.strip()

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be blank")
        return v

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("age")
    @classmethod
    def age_must_be_realistic(cls, v: int) -> int:
        if v < 0 or v > 120:
            raise ValueError(f"age must be between 0 and 120, got {v}")
        return v

    @field_validator("country")
    @classmethod
    def country_must_be_2_chars(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 2:
            raise ValueError(
                f"country must be a 2-letter ISO code (e.g. 'US', 'PK'), got {v!r}"
            )
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def tags_default_to_empty(cls, v):
        if v is None:
            return []
        return v

    @model_validator(mode="before")
    @classmethod
    def map_mongo_id(cls, data: dict) -> dict:
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id")
        return data