from langchain_core.tools import tool
import requests
import os

@tool("get_user_info", description="Get employee information from the Walt API")
def get_user_info() -> dict:
    """Fetch employee information from the Walt API"""
    base_url = os.getenv('WALT_API')
    token = os.getenv('WALT_TOKEN')
    
    if not base_url or not token:
        return {"error": "WALT_API or WALT_TOKEN environment variables not set"}
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{base_url}/v1/user/user-info",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract the model object which contains the employee info
        if "model" in data:
            return data["model"]
        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch user info: {str(e)}"}

tools = [get_user_info]
