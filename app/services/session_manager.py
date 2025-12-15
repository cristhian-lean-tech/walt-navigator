from typing import Dict, Optional
from app.dtos.faqs import SessionState


class SessionManager:
    """
    Manages conversation sessions for users to maintain context across interactions.
    """
    
    def __init__(self):
        # In-memory storage: user_id -> SessionState
        self._sessions: Dict[str, SessionState] = {}
    
    def get_session(self, user_id: str) -> SessionState:
        """
        Get or create a session for a user.
        
        Args:
            user_id: The unique identifier for the user
            
        Returns:
            SessionState object for the user
        """
        if user_id not in self._sessions:
            self._sessions[user_id] = SessionState()
        return self._sessions[user_id]
    
    def update_session(self, user_id: str, session_state: SessionState) -> None:
        """
        Update the session state for a user.
        
        Args:
            user_id: The unique identifier for the user
            session_state: The updated SessionState object
        """
        self._sessions[user_id] = session_state
    
    def clear_session(self, user_id: str) -> None:
        """
        Clear the session for a user.
        
        Args:
            user_id: The unique identifier for the user
        """
        if user_id in self._sessions:
            del self._sessions[user_id]
    
    def has_pending_clarification(self, user_id: str) -> bool:
        """
        Check if a user has a pending clarification.
        
        Args:
            user_id: The unique identifier for the user
            
        Returns:
            True if the user has a pending clarification, False otherwise
        """
        session = self.get_session(user_id)
        return session.pending_clarification
    
    def set_pending_clarification(
        self, 
        user_id: str, 
        question: str,
        bot_question: str,
        faqs: list[dict],
        rag_indexes: list[int],
        intent: str = "IN_SCOPE"
    ) -> None:
        """
        Set a pending clarification for a user.
        
        Args:
            user_id: The unique identifier for the user
            question: The user's original question
            bot_question: The clarifying question asked by the bot
            faqs: List of FAQ metadata awaiting clarification
            rag_indexes: Indexes of the relevant FAQs
            intent: The intent classification
        """
        session = self.get_session(user_id)
        session.pending_clarification = True
        session.last_user_question = question
        session.last_bot_question = bot_question
        session.pending_faqs = faqs
        session.rag_state_indexes = rag_indexes
        session.last_intent = intent
        self.update_session(user_id, session)
    
    def clear_pending_clarification(self, user_id: str) -> None:
        """
        Clear the pending clarification for a user.
        
        Args:
            user_id: The unique identifier for the user
        """
        session = self.get_session(user_id)
        session.pending_clarification = False
        session.last_bot_question = None
        session.pending_faqs = None
        session.rag_state_indexes = None
        self.update_session(user_id, session)


# Global singleton instance
session_manager = SessionManager()

