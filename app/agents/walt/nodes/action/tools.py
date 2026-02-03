from langchain_core.tools import tool
import requests
import os
from typing import Optional

def get_headers():
    """Get authorization headers"""
    token = os.getenv('WALT_TOKEN')
    if not token:
        raise ValueError("WALT_TOKEN environment variable not set")
    return {"Authorization": f"Bearer {token}"}

def get_base_url():
    """Get base API URL"""
    base_url = os.getenv('WALT_API')
    if not base_url:
        raise ValueError("WALT_API environment variable not set")
    return base_url

@tool("request_time_off", description="Request time-off (service interruption) benefit. Requires: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), returning_date (YYYY-MM-DD), comments (string), and days (integer)")
def request_time_off(
    start_date: str,
    end_date: str,
    returning_date: str,
    comments: str,
    days: int
) -> str:
    """Request time-off benefit"""
    try:
        headers = get_headers()
        base_url = get_base_url()
        
        payload = {
            "user_benefit": {"id": "b5af1ef3-3769-4bb3-b6cf-f005d7b3b7f6"},
            "start_at": str(start_date),
            "end_at": str(end_date),
            "additional_data": {"returning_date": str(returning_date)},
            "comments": str(comments),
            "days": int(days)  # Ensure it's a proper integer
        }

        print(f"[DEBUG] PAYLOAD: ", payload)
        
        response = requests.post(
            f"{base_url}/api/v2/benefit_request/service-interruption",            
            json=payload,
            headers=headers
        )
        print(f"[DEBUG] RESPONSE: ", response)
        response.raise_for_status()
        return f"Time-off request submitted successfully for {start_date} to {end_date} ({days} days)."
    except Exception as e:
        print(f"[DEBUG] ERROR: ", e)
        return f"Error submitting time-off request: {str(e)}"

@tool("request_certificate", description="Request a commercial relationship certificate. Requires: fees_included (boolean) and language (must be 'english' or 'spanish')")
def request_certificate(
    fees_included: bool,
    language: str
) -> str:
    """Request a commercial relationship certificate"""
    if language not in ["english", "spanish"]:
        return f"Error: Language must be 'english' or 'spanish', got '{language}'"
    
    try:
        headers = get_headers()
        base_url = get_base_url()
        
        payload = {
            "fees_included": bool(fees_included),  # Ensure it's a proper boolean (True/False -> true/false in JSON)
            "language": str(language)  # Ensure it's a string
        }
        response = requests.post(
            f"{base_url}/api/v2/document-request/contractor/commercial-relationship",
            json=payload,  # requests will automatically convert True/False to true/false
            headers=headers
        )
        response.raise_for_status()
        lang_display = "English" if language == "english" else "Spanish"
        return f"Certificate request submitted successfully in {lang_display} (fees included: {fees_included})."
    except Exception as e:
        return f"Error submitting certificate request: {str(e)}"

@tool("request_book_benefit", description="Request a book benefit (brain power). Requires: name (string) and amount (float). Optionally accepts file_path (string) - defaults to company file if not provided")
def request_book_benefit(
    name: str,
    amount: float,
    file_path: Optional[str] = None
) -> str:
    """Request a book benefit"""
    try:
        headers = get_headers()
        base_url = get_base_url()
        
        # Use default file if not provided
        if file_path is None:
            file_path = "src/static/lana_rey.png"
        
        # Prepare multipart form data
        data = {
            "user_benefit": "35a56081-0f4f-4399-8c5a-278708309370",
            "name": str(name),
            "amount": str(amount),  # Convert float to string for form data
            "subject": "Hardskill"
        }
        
        # Open and send file
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{base_url}/api/v2/wellness-request/brain-power-request/contractor",
                data=data,
                files=files,
                headers=headers
            )
            response.raise_for_status()
        
        return f"Book benefit request submitted successfully for '{name}' (amount: {amount})."
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error submitting book benefit request: {str(e)}"

@tool("request_gym_benefit", description="Request a gym membership benefit. Requires: start_date (YYYY-MM-DD), service_provider (string), receipt_date (YYYY-MM-DD), receipt_amount (float). Optional: currency (defaults to 'USD'), period (defaults to 'Monthly'), file_path (defaults to company file if not provided)")
def request_gym_benefit(
    start_date: str,
    service_provider: str,
    receipt_date: str,
    receipt_amount: float,
    currency: str = "USD",
    period: str = "Monthly",
    file_path: Optional[str] = None
) -> str:
    """Request a gym membership benefit"""
    try:
        headers = get_headers()
        base_url = get_base_url()
        
        # Use default file if not provided
        if file_path is None:
            file_path = "src/static/lana_rey.png"
        
        # Prepare multipart form data
        data = {
            "user_benefit": "0c440b29-8b6f-489e-b830-9bf489d0b4cc",
            "start_date": str(start_date),
            "service_provider": str(service_provider),
            "receipt_date": str(receipt_date),
            "currency": str(currency),
            "period": str(period),
            "receipt_amount": int(receipt_amount)
        }

        
        # Open and send file
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{base_url}/api/v2/wellness-request/gym-request/contractor",
                data=data,
                files=files,
                headers=headers
            )
            response.raise_for_status()
        
        return f"Gym benefit request submitted successfully for {service_provider} (amount: {receipt_amount} {currency}, period: {period})."
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error submitting gym benefit request: {str(e)}"

tools = [
    request_time_off,
    request_certificate,
    request_book_benefit,
    request_gym_benefit
]
