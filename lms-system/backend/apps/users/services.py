"""
User services for LMS System.

This module contains business logic for user management.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import PasswordResetToken, RefreshToken

User = get_user_model()


class UserService:
    """Service for user management."""
    
    @staticmethod
    def create_user(email: str, password: str, full_name: str = '', role: str = 'learner') -> User:
        """
        Create a new user.
        
        Args:
            email: User email
            password: User password
            full_name: User full name
            role: User role (admin, trainer, learner)
            
        Returns:
            Created User instance
        """
        return User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
        )
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """
        Deactivate a user.
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            True if user was deactivated, False otherwise
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save(update_fields=['is_active'])
            return True
        except User.DoesNotExist:
            return False
    
    @staticmethod
    def activate_user(user_id: int) -> bool:
        """
        Activate a user.
        
        Args:
            user_id: User ID to activate
            
        Returns:
            True if user was activated, False otherwise
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save(update_fields=['is_active'])
            return True
        except User.DoesNotExist:
            return False


class TokenService:
    """Service for token management."""
    
    @staticmethod
    def create_password_reset_token(user: User) -> PasswordResetToken:
        """
        Create a password reset token for a user.
        
        Args:
            user: User instance
            
        Returns:
            Created PasswordResetToken instance
        """
        # Invalidate previous tokens
        PasswordResetToken.objects.filter(
            user=user,
            used_at__isnull=True,
        ).update(used_at=timezone.now())
        
        return PasswordResetToken.objects.create(
            user=user,
            token=PasswordResetToken.objects.make_random_password(64),
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
    
    @staticmethod
    def validate_password_reset_token(token: str) -> tuple[User | None, str | None]:
        """
        Validate a password reset token.
        
        Args:
            token: Token string
            
        Returns:
            Tuple of (User instance or None, error message or None)
        """
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return None, 'Неверный токен.'
        
        if reset_token.is_used:
            return None, 'Токен уже использован.'
        
        if reset_token.is_expired:
            return None, 'Токен истёк.'
        
        return reset_token.user, None
    
    @staticmethod
    def revoke_all_refresh_tokens(user: User) -> int:
        """
        Revoke all refresh tokens for a user.
        
        Args:
            user: User instance
            
        Returns:
            Number of tokens revoked
        """
        return RefreshToken.objects.filter(
            user=user,
            revoked_at__isnull=True,
        ).update(revoked_at=timezone.now())