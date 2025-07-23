"""
User preference service for managing notification preferences
"""
from sqlmodel import Session, select
from fastapi import HTTPException, status
from models.user_preference import UserPreference
from schemas.user_preference import (
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    BulkPreferenceUpdate
)
from typing import List, Optional
from datetime import datetime
import uuid


class PreferenceService:
    """Service for handling user preference operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_preference(self, preference_data: UserPreferenceCreate) -> UserPreferenceResponse:
        """Create user notification preferences"""
        # Check if preferences already exist for this user
        statement = select(UserPreference).where(UserPreference.user_id == preference_data.user_id)
        existing_preference = self.session.exec(statement).first()
        
        if existing_preference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preferences already exist for this user"
            )
        
        # Create preference
        preference = UserPreference(**preference_data.model_dump(exclude={"notification_preferences"}))
        
        # Set notification preferences
        if preference_data.notification_preferences:
            preference.set_notification_preferences_dict(preference_data.notification_preferences)
        
        self.session.add(preference)
        self.session.commit()
        self.session.refresh(preference)
        
        return self._create_preference_response(preference)
    
    async def get_preference(self, user_id: uuid.UUID) -> UserPreferenceResponse:
        """Get user preferences by user ID"""
        statement = select(UserPreference).where(UserPreference.user_id == user_id)
        preference = self.session.exec(statement).first()
        
        if not preference:
            # Create default preferences if none exist
            default_preference = UserPreference(
                user_id=user_id,
                user_type="user"
            )
            
            self.session.add(default_preference)
            self.session.commit()
            self.session.refresh(default_preference)
            
            preference = default_preference
        
        return self._create_preference_response(preference)
    
    async def update_preference(
        self, 
        user_id: uuid.UUID, 
        preference_data: UserPreferenceUpdate
    ) -> UserPreferenceResponse:
        """Update user notification preferences"""
        statement = select(UserPreference).where(UserPreference.user_id == user_id)
        preference = self.session.exec(statement).first()
        
        if not preference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User preferences not found"
            )
        
        # Update fields
        update_data = preference_data.model_dump(exclude_unset=True, exclude={"notification_preferences"})
        
        for field, value in update_data.items():
            setattr(preference, field, value)
        
        # Handle notification preferences separately
        if preference_data.notification_preferences is not None:
            preference.set_notification_preferences_dict(preference_data.notification_preferences)
        
        preference.updated_at = datetime.utcnow()
        
        self.session.add(preference)
        self.session.commit()
        self.session.refresh(preference)
        
        return self._create_preference_response(preference)
    
    async def delete_preference(self, user_id: uuid.UUID) -> dict:
        """Delete user preferences"""
        statement = select(UserPreference).where(UserPreference.user_id == user_id)
        preference = self.session.exec(statement).first()
        
        if not preference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User preferences not found"
            )
        
        self.session.delete(preference)
        self.session.commit()
        
        return {"message": "User preferences deleted successfully"}
    
    async def get_all_preferences(self, user_type: Optional[str] = None) -> List[UserPreferenceResponse]:
        """Get all user preferences, optionally filtered by user type"""
        query = select(UserPreference)
        
        if user_type:
            query = query.where(UserPreference.user_type == user_type)
        
        query = query.where(UserPreference.is_active == True)
        query = query.order_by(UserPreference.created_at.desc())
        
        preferences = self.session.exec(query).all()
        
        return [self._create_preference_response(p) for p in preferences]
    
    async def bulk_update_preferences(self, bulk_update: BulkPreferenceUpdate) -> dict:
        """Bulk update preferences for multiple users"""
        statement = select(UserPreference).where(UserPreference.user_id.in_(bulk_update.user_ids))
        preferences = self.session.exec(statement).all()
        
        if len(preferences) != len(bulk_update.user_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some user preferences not found"
            )
        
        # Update fields
        update_data = bulk_update.preferences.model_dump(exclude_unset=True, exclude={"notification_preferences"})
        updated_count = 0
        
        for preference in preferences:
            for field, value in update_data.items():
                setattr(preference, field, value)
            
            # Handle notification preferences
            if bulk_update.preferences.notification_preferences is not None:
                preference.set_notification_preferences_dict(bulk_update.preferences.notification_preferences)
            
            preference.updated_at = datetime.utcnow()
            self.session.add(preference)
            updated_count += 1
        
        self.session.commit()
        
        return {
            "message": f"Successfully updated {updated_count} user preferences",
            "updated_count": updated_count
        }
    
    async def get_users_by_channel_preference(
        self, 
        channel: str, 
        notification_type: Optional[str] = None
    ) -> List[UserPreferenceResponse]:
        """Get users who have enabled a specific channel"""
        query = select(UserPreference).where(UserPreference.is_active == True)
        
        # Filter by channel
        if channel == "email":
            query = query.where(UserPreference.email_enabled == True)
        elif channel == "sms":
            query = query.where(UserPreference.sms_enabled == True)
        elif channel == "push":
            query = query.where(UserPreference.push_enabled == True)
        elif channel == "whatsapp":
            query = query.where(UserPreference.whatsapp_enabled == True)
        
        preferences = self.session.exec(query).all()
        
        # Further filter by notification type if specified
        if notification_type:
            filtered_preferences = []
            for pref in preferences:
                prefs_dict = pref.get_notification_preferences_dict()
                type_prefs = prefs_dict.get(notification_type, {})
                if type_prefs.get(channel, True):  # Default to enabled
                    filtered_preferences.append(pref)
            preferences = filtered_preferences
        
        return [self._create_preference_response(p) for p in preferences]
    
    async def update_contact_info(
        self, 
        user_id: uuid.UUID, 
        email: Optional[str] = None, 
        phone: Optional[str] = None,
        push_token: Optional[str] = None
    ) -> UserPreferenceResponse:
        """Update user contact information"""
        statement = select(UserPreference).where(UserPreference.user_id == user_id)
        preference = self.session.exec(statement).first()
        
        if not preference:
            # Create new preference with contact info
            preference = UserPreference(
                user_id=user_id,
                email=email,
                phone=phone,
                push_token=push_token
            )
            self.session.add(preference)
        else:
            # Update existing preference
            if email is not None:
                preference.email = email
            if phone is not None:
                preference.phone = phone
            if push_token is not None:
                preference.push_token = push_token
            
            preference.updated_at = datetime.utcnow()
            self.session.add(preference)
        
        self.session.commit()
        self.session.refresh(preference)
        
        return self._create_preference_response(preference)
    
    def _create_preference_response(self, preference: UserPreference) -> UserPreferenceResponse:
        """Create preference response with calculated fields"""
        return UserPreferenceResponse(
            id=preference.id,
            user_id=preference.user_id,
            user_type=preference.user_type,
            email=preference.email,
            phone=preference.phone,
            push_token=preference.push_token,
            email_enabled=preference.email_enabled,
            sms_enabled=preference.sms_enabled,
            push_enabled=preference.push_enabled,
            whatsapp_enabled=preference.whatsapp_enabled,
            notification_preferences=preference.get_notification_preferences_dict(),
            quiet_hours_enabled=preference.quiet_hours_enabled,
            quiet_hours_start=preference.quiet_hours_start,
            quiet_hours_end=preference.quiet_hours_end,
            quiet_hours_timezone=preference.quiet_hours_timezone,
            max_emails_per_day=preference.max_emails_per_day,
            max_sms_per_day=preference.max_sms_per_day,
            preferred_language=preference.preferred_language,
            preferred_timezone=preference.preferred_timezone,
            is_active=preference.is_active,
            created_at=preference.created_at,
            updated_at=preference.updated_at,
            enabled_channels=preference.get_enabled_channels(),
            is_in_quiet_hours=preference.is_in_quiet_hours()
        )