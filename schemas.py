"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal, Dict, Any

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class Demolead(BaseModel):
    """
    Demo leads collected from the website demo or CTA
    Collection name: "demolead"
    """
    name: str = Field(..., min_length=1)
    email: EmailStr
    company: Optional[str] = None
    message: Optional[str] = None
    lang: Literal['en', 'fr'] = 'en'
    source: Literal['demo', 'cta'] = 'demo'

class Demotranscript(BaseModel):
    """
    Conversation messages for demo sessions
    Collection name: "demotranscript"
    """
    session_id: str = Field(..., min_length=8)
    role: Literal['user', 'assistant']
    text: str = Field(..., min_length=1)
    lang: Literal['en', 'fr'] = 'en'

class Demosession(BaseModel):
    """
    Tracks demo sessions and lightweight memory
    Collection name: "demosession"
    """
    session_id: str = Field(..., min_length=8)
    name: Optional[str] = None
    company: Optional[str] = None
    lang: Literal['en', 'fr'] = 'en'
    last_intent: Optional[str] = None

class Demoevent(BaseModel):
    """
    Analytics events for demo interactions
    Collection name: "demoevent"
    """
    session_id: str = Field(..., min_length=8)
    type: str = Field(..., description="Event type, e.g., session_start, message_sent, suggestion_click, tts_played")
    data: Optional[Dict[str, Any]] = None

class Demoappointment(BaseModel):
    """
    Booked appointments from demo flow
    Collection name: "demoappointment"
    """
    session_id: str = Field(..., min_length=8)
    slot_iso: str = Field(..., description="ISO 8601 datetime for the appointment")
    name: Optional[str] = None
    company: Optional[str] = None
    lang: Literal['en', 'fr'] = 'en'
    channel: Literal['web', 'chat', 'phone'] = 'web'
