"""
Supabase Database Client and Operations
Uses HTTP REST API for reliable connectivity
"""

from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import os
import logging
import requests
import json
from backend.shared.exceptions_v2 import DatabaseError

load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Wrapper around Supabase HTTP REST API for consensus data"""
    
    def __init__(self):
        """Initialize Supabase HTTP client"""
        self.url = os.getenv("SUPABASE_PROJECT_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.service_key:
            raise DatabaseError(
                "Missing SUPABASE_PROJECT_URL or SUPABASE_SERVICE_ROLE_KEY in .env"
            )
        
        if not self.anon_key:
            raise DatabaseError("Missing SUPABASE_ANON_KEY in .env")
        
        # Service role headers for admin operations
        self.admin_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key
        }
        
        # Anon headers for user auth operations
        self.anon_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.anon_key}",
            "apikey": self.anon_key
        }
    
    def save_consensus_result(
        self,
        session_id: str,
        sample_id: int,
        predicted_class: int,
        confidence: float,
        agent_predictions: Dict[str, tuple],
        weights: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Save consensus prediction result to database
        
        Args:
            session_id: Unique session identifier
            sample_id: Sample identifier
            predicted_class: Final predicted class
            confidence: Prediction confidence
            agent_predictions: Dict of agent predictions
            weights: Current agent weights
            
        Returns:
            Inserted record from database
        """
        try:
            data = {
                "session_id": session_id,
                "sample_id": sample_id,
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "agent_predictions": agent_predictions,
                "agent_weights": weights,
            }
            
            response = requests.post(
                f"{self.url}/rest/v1/consensus_results",
                headers=self.admin_headers,
                json=data,
                timeout=10
            )
            
            if response.status_code not in [200, 201]:
                raise DatabaseError(f"Failed to save consensus result: {response.text}")
            
            return response.json()[0] if response.json() else {}
        
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error saving consensus result (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error saving consensus result: {str(e)}")
    
    def save_weight_update(
        self,
        session_id: str,
        agent_name: str,
        previous_weight: float,
        new_weight: float,
        reason: str,
        true_label: int,
        predicted_label: int,
    ) -> Dict[str, Any]:
        """
        Save agent weight update to database
        
        Args:
            session_id: Unique session identifier
            agent_name: Name of agent
            previous_weight: Weight before update
            new_weight: Weight after update
            reason: Reason for update (reward/penalty)
            true_label: Ground truth label
            predicted_label: Agent's prediction
            
        Returns:
            Inserted record from database
        """
        try:
            data = {
                "session_id": session_id,
                "agent_name": agent_name,
                "previous_weight": float(previous_weight),
                "new_weight": float(new_weight),
                "reason": reason,
                "true_label": true_label,
                "predicted_label": predicted_label,
            }
            
            response = requests.post(
                f"{self.url}/rest/v1/weight_updates",
                headers=self.admin_headers,
                json=data,
                timeout=10
            )
            
            if response.status_code not in [200, 201]:
                raise DatabaseError(f"Failed to save weight update: {response.text}")
            
            return response.json()[0] if response.json() else {}
        
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error saving weight update (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error saving weight update: {str(e)}")
    
    def get_session_results(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all consensus results for a session"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/consensus_results?session_id=eq.{session_id}&select=*",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            return response.json() if response.json() else []
        
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error retrieving session results (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error retrieving session results: {str(e)}")
    
    def get_agent_weight_history(
        self,
        session_id: str,
        agent_name: str,
    ) -> List[Dict[str, Any]]:
        """Get weight update history for an agent in a session"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/weight_updates?session_id=eq.{session_id}&agent_name=eq.{agent_name}&order=created_at.asc&select=*",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            return response.json() if response.json() else []
        
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error retrieving weight history (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error retrieving weight history: {str(e)}")
    
    def get_agent_performance(
        self,
        agent_name: str,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """Get aggregated performance metrics for an agent"""
        try:
            # Get all predictions for this agent
            response = requests.get(
                f"{self.url}/rest/v1/weight_updates?agent_name=eq.{agent_name}&select=*&limit={limit}",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "agent_name": agent_name,
                    "total_predictions": 0,
                    "correct_predictions": 0,
                    "accuracy": 0.0,
                }
            
            data = response.json()
            if not data:
                return {
                    "agent_name": agent_name,
                    "total_predictions": 0,
                    "correct_predictions": 0,
                    "accuracy": 0.0,
                }
            
            correct = sum(1 for d in data if d.get("predicted_label") == d.get("true_label"))
            
            return {
                "agent_name": agent_name,
                "total_predictions": len(data),
                "correct_predictions": correct,
                "accuracy": correct / len(data) if data else 0.0,
            }
        
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error retrieving agent performance (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error retrieving agent performance: {str(e)}")
    
    def create_session(self, session_name: str, description: str = "") -> Dict[str, Any]:
        """Create a new consensus session"""
        try:
            data = {
                "session_name": session_name,
                "description": description,
            }
            
            response = requests.post(
                f"{self.url}/rest/v1/sessions",
                headers=self.admin_headers,
                json=data,
                timeout=10
            )
            
            if response.status_code not in [200, 201]:
                raise DatabaseError(f"Failed to create session: {response.text}")
            
            return response.json()[0] if response.json() else {}
        
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error creating session (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error creating session: {str(e)}")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session details"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/sessions?id=eq.{session_id}&select=*",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return {}
            
            data = response.json()
            return data[0] if data else {}
        
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error retrieving session (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error retrieving session: {str(e)}")
    
    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/sessions?select=*&order=created_at.desc&limit={limit}",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            return response.json() if response.json() else []
        
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error listing sessions (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error listing sessions: {str(e)}")
    
    # ==================== User Management ====================
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by auth ID"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/users?auth_id=eq.{user_id}&select=*",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            return data[0] if data else None
        except Exception as e:
            raise DatabaseError(f"Error fetching user {user_id}: {str(e)}")
    
    def get_user_by_auth_id(self, auth_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by auth_id (same as get_user_by_id but more explicit)"""
        return self.get_user_by_id(auth_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user profile by email"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/users?email=eq.{email}&select=*",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            return data[0] if data else None
        except Exception as e:
            raise DatabaseError(f"Error fetching user by email {email}: {str(e)}")
    
    def create_user(
        self,
        auth_id: str,
        email: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        role: str = "user"
    ) -> Dict[str, Any]:
        """Create a new user profile with auth_id linking to Supabase auth.users"""
        from datetime import datetime
        try:
            user_data = {
                "auth_id": auth_id,
                "email": email,
                "full_name": full_name,
                "avatar_url": avatar_url,
                "role": role,
                "is_active": True,
                "email_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f"{self.url}/rest/v1/users",
                headers=self.admin_headers,
                json=user_data,
                timeout=10
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"✗ Error creating user profile {email}: Status {response.status_code}, Body: {response.text}")
                raise DatabaseError(f"Failed to create user: {response.text}")
            
            logger.info(f"✓ User profile created in database: {email}")
            
            # Handle empty response
            if not response.text:
                return {"auth_id": auth_id, "email": email}
            
            try:
                json_data = response.json()
                return json_data[0] if isinstance(json_data, list) and json_data else json_data if json_data else {"auth_id": auth_id, "email": email}
            except:
                return {"auth_id": auth_id, "email": email}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error creating user profile {email} (network): {str(e)}")
            raise DatabaseError(f"Error creating user {email}: {str(e)}")
        except Exception as e:
            logger.error(f"✗ Error creating user profile {email}: {str(e)}")
            raise DatabaseError(f"Error creating user {email}: {str(e)}")
    
    def update_user(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user profile"""
        from datetime import datetime
        try:
            update_data = {"updated_at": datetime.utcnow().isoformat()}
            
            if full_name is not None:
                update_data["full_name"] = full_name
            
            if avatar_url is not None:
                update_data["avatar_url"] = avatar_url
            
            response = requests.patch(
                f"{self.url}/rest/v1/users?id=eq.{user_id}",
                headers=self.admin_headers,
                json=update_data,
                timeout=10
            )
            
            if response.status_code not in [200, 201]:
                raise DatabaseError(f"Failed to update user: {response.text}")
            
            return response.json()[0] if response.json() else {}
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error updating user {user_id} (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error updating user {user_id}: {str(e)}")
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user profile"""
        try:
            response = requests.delete(
                f"{self.url}/rest/v1/users?id=eq.{user_id}",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code not in [200, 204]:
                raise DatabaseError(f"Failed to delete user: {response.text}")
            
            return True
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error deleting user {user_id} (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error deleting user {user_id}: {str(e)}")
    
    def list_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all users with pagination"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/users?select=*&limit={limit}&offset={offset}",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            return response.json() if response.json() else []
        except requests.exceptions.RequestException as e:
            raise DatabaseError(f"Error listing users (network): {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Error listing users: {str(e)}")
    
    def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/users?email=eq.{email}&select=id",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            return bool(data) and len(data) > 0
        except requests.exceptions.RequestException:
            return False
        except Exception as e:
            raise DatabaseError(f"Error checking user existence {email}: {str(e)}")
    
    def get_recent_consensus_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent consensus prediction logs from database"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/consensus_results?order=created_at.desc&limit={limit}&select=*",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            results = response.json() if response.json() else []
            # Reverse to get chronological order (oldest first in list, newest last)
            return list(reversed(results))
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error retrieving consensus results: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving consensus results: {str(e)}")
            return []
    
    def get_recent_weight_updates(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent weight update history from database"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/weight_updates?order=created_at.desc&limit={limit}&select=*",
                headers=self.admin_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            results = response.json() if response.json() else []
            # Reverse to get chronological order
            return list(reversed(results))
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error retrieving weight updates: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving weight updates: {str(e)}")
            return []


# Singleton instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client singleton"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
