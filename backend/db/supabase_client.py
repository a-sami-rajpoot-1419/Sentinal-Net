"""
Supabase Database Client and Operations
"""

from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from backend.shared.exceptions_v2 import DatabaseError

load_dotenv()


class SupabaseClient:
    """Wrapper around Supabase client for consensus data"""
    
    def __init__(self):
        """Initialize Supabase client"""
        url = os.getenv("SUPABASE_PROJECT_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not service_key:
            raise DatabaseError(
                "Missing SUPABASE_PROJECT_URL or SUPABASE_SERVICE_ROLE_KEY in .env"
            )
        
        # Service role key for admin operations (consensus, user management)
        self.client: Client = create_client(url, service_key)
        
        # Anon key for user auth operations (sign up, login)
        if not anon_key:
            raise DatabaseError("Missing SUPABASE_ANON_KEY in .env")
        self.auth_client: Client = create_client(url, anon_key)
    
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
            response = self.client.table("consensus_results").insert({
                "session_id": session_id,
                "sample_id": sample_id,
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "agent_predictions": agent_predictions,
                "agent_weights": weights,
            }).execute()
            
            return response.data[0] if response.data else {}
        
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
            response = self.client.table("weight_updates").insert({
                "session_id": session_id,
                "agent_name": agent_name,
                "previous_weight": float(previous_weight),
                "new_weight": float(new_weight),
                "reason": reason,
                "true_label": true_label,
                "predicted_label": predicted_label,
            }).execute()
            
            return response.data[0] if response.data else {}
        
        except Exception as e:
            raise DatabaseError(f"Error saving weight update: {str(e)}")
    
    def get_session_results(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all consensus results for a session"""
        try:
            response = self.client.table("consensus_results").select(
                "*"
            ).eq(
                "session_id", session_id
            ).execute()
            
            return response.data if response.data else []
        
        except Exception as e:
            raise DatabaseError(f"Error retrieving session results: {str(e)}")
    
    def get_agent_weight_history(
        self,
        session_id: str,
        agent_name: str,
    ) -> List[Dict[str, Any]]:
        """Get weight update history for an agent in a session"""
        try:
            response = self.client.table("weight_updates").select(
                "*"
            ).eq(
                "session_id", session_id
            ).eq(
                "agent_name", agent_name
            ).order(
                "created_at", desc=False
            ).execute()
            
            return response.data if response.data else []
        
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
            response = self.client.table("weight_updates").select(
                "*"
            ).eq(
                "agent_name", agent_name
            ).limit(
                limit
            ).execute()
            
            if not response.data:
                return {
                    "agent_name": agent_name,
                    "total_predictions": 0,
                    "correct_predictions": 0,
                    "accuracy": 0.0,
                }
            
            data = response.data
            correct = sum(1 for d in data if d.get("predicted_label") == d.get("true_label"))
            
            return {
                "agent_name": agent_name,
                "total_predictions": len(data),
                "correct_predictions": correct,
                "accuracy": correct / len(data) if data else 0.0,
            }
        
        except Exception as e:
            raise DatabaseError(f"Error retrieving agent performance: {str(e)}")
    
    def create_session(self, session_name: str, description: str = "") -> Dict[str, Any]:
        """Create a new consensus session"""
        try:
            response = self.client.table("sessions").insert({
                "session_name": session_name,
                "description": description,
            }).execute()
            
            return response.data[0] if response.data else {}
        
        except Exception as e:
            raise DatabaseError(f"Error creating session: {str(e)}")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session details"""
        try:
            response = self.client.table("sessions").select(
                "*"
            ).eq(
                "id", session_id
            ).execute()
            
            return response.data[0] if response.data else {}
        
        except Exception as e:
            raise DatabaseError(f"Error retrieving session: {str(e)}")
    
    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions"""
        try:
            response = self.client.table("sessions").select(
                "*"
            ).order(
                "created_at", desc=True
            ).limit(
                limit
            ).execute()
            
            return response.data if response.data else []
        
        except Exception as e:
            raise DatabaseError(f"Error listing sessions: {str(e)}")
    
    # ==================== User Management ====================
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by auth ID"""
        try:
            response = self.client.table("users").select("*").eq("auth_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise DatabaseError(f"Error fetching user {user_id}: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user profile by email"""
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise DatabaseError(f"Error fetching user by email {email}: {str(e)}")
    
    def create_user(
        self,
        user_id: str,
        email: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        role: str = "user"
    ) -> Dict[str, Any]:
        """Create a new user profile"""
        from datetime import datetime
        try:
            user_data = {
                "auth_id": user_id,
                "email": email,
                "full_name": full_name,
                "avatar_url": avatar_url,
                "role": role,
                "is_active": True,
                "email_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("users").insert(user_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
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
            
            response = self.client.table("users").update(update_data).eq("id", user_id).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            raise DatabaseError(f"Error updating user {user_id}: {str(e)}")
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user profile"""
        try:
            self.client.table("users").delete().eq("id", user_id).execute()
            return True
        except Exception as e:
            raise DatabaseError(f"Error deleting user {user_id}: {str(e)}")
    
    def list_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all users with pagination"""
        try:
            response = self.client.table("users").select("*").range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            raise DatabaseError(f"Error listing users: {str(e)}")
    
    def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        try:
            response = self.client.table("users").select("id").eq("email", email).execute()
            return response.data and len(response.data) > 0
        except Exception as e:
            raise DatabaseError(f"Error checking user existence {email}: {str(e)}")


# Singleton instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client singleton"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
