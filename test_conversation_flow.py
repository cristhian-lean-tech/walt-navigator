"""
Test script for conversation flow with memory.

This script tests the conversation flow with clarification and memory management.
"""

from app.services.faqs_service2 import FaqsService2
from app.services.session_manager import session_manager


def test_conversation_flow():
    """Test the conversation flow with clarification."""
    
    service = FaqsService2()
    user_id = "test_user_123"
    contract_type = "contractor"
    
    print("=" * 80)
    print("TEST 1: Ambiguous question requiring clarification")
    print("=" * 80)
    
    # First question - should trigger clarification
    question1 = "How can I get help with my computer?"
    print(f"\nUser: {question1}")
    
    response1 = service.ask_faqs_agent(question1, contract_type, user_id)
    print(f"Bot: {response1.answer}")
    print(f"Link: {response1.link}")
    print(f"Point of Contact: {response1.point_of_contact}")
    
    # Check if clarification is pending
    session = session_manager.get_session(user_id)
    print(f"\nSession State:")
    print(f"  - Pending Clarification: {session.pending_clarification}")
    print(f"  - Last User Question: {session.last_user_question}")
    print(f"  - Pending FAQs Count: {len(session.pending_faqs) if session.pending_faqs else 0}")
    
    if session.pending_clarification:
        print("\n" + "=" * 80)
        print("TEST 2: User responds to clarification")
        print("=" * 80)
        
        # User responds with clarification
        question2 = "Yes, I need IT support"
        print(f"\nUser: {question2}")
        
        response2 = service.ask_faqs_agent(question2, contract_type, user_id)
        print(f"Bot: {response2.answer[:200]}...")  # Truncate long answers
        print(f"Link: {response2.link}")
        print(f"Point of Contact: {response2.point_of_contact}")
        
        # Check if clarification was cleared
        session = session_manager.get_session(user_id)
        print(f"\nSession State After Response:")
        print(f"  - Pending Clarification: {session.pending_clarification}")
    
    # Clean up
    session_manager.clear_session(user_id)
    
    print("\n" + "=" * 80)
    print("TEST 3: Direct question with high accuracy")
    print("=" * 80)
    
    question3 = "How can I participate in English classes?"
    print(f"\nUser: {question3}")
    
    response3 = service.ask_faqs_agent(question3, contract_type, user_id)
    print(f"Bot: {response3.answer[:200]}...")  # Truncate long answers
    print(f"Link: {response3.link}")
    print(f"Point of Contact: {response3.point_of_contact}")
    
    # Check session state
    session = session_manager.get_session(user_id)
    print(f"\nSession State:")
    print(f"  - Pending Clarification: {session.pending_clarification}")
    
    # Clean up
    session_manager.clear_session(user_id)
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_conversation_flow()

