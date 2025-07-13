"""
User models for authentication and account management
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"

class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(BaseModel):
    """Model for user data"""
    user_id: str = Field(description="Unique user identifier")
    username: str = Field(description="Username for login")
    email: EmailStr = Field(description="User's email address")
    password_hash: str = Field(description="Hashed password")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Account status")
    
    # Google OAuth2 integration
    google_authenticated: bool = Field(default=False, description="Whether user has authenticated with Google")
    google_email: Optional[str] = Field(None, description="Google account email if different from primary email")
    google_token_file: Optional[str] = Field(None, description="Path to user's Google token file")
    
    # Profile information
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    company: Optional[str] = Field(None, description="User's company")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class UserRegistration(BaseModel):
    """Model for user registration data"""
    username: str = Field(description="Username for login")
    email: EmailStr = Field(description="User's email address")
    password: str = Field(description="Plain text password")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    company: Optional[str] = Field(None, description="User's company")

class UserLogin(BaseModel):
    """Model for user login data"""
    username: str = Field(description="Username or email")
    password: str = Field(description="Password")

class UserProfile(BaseModel):
    """Model for user profile data"""
    user_id: str = Field(description="Unique user identifier")
    username: str = Field(description="Username")
    email: EmailStr = Field(description="Email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    company: Optional[str] = Field(None, description="Company")
    role: UserRole = Field(description="User role")
    status: UserStatus = Field(description="Account status")
    google_authenticated: bool = Field(description="Google authentication status")
    google_email: Optional[str] = Field(None, description="Google account email if different from primary email")
    created_at: datetime = Field(description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login date")

class PasswordChange(BaseModel):
    """Model for password change data"""
    current_password: str = Field(description="Current password")
    new_password: str = Field(description="New password")
    confirm_password: str = Field(description="Confirm new password") 