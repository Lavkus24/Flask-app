import requests

def is_instagram_session_valid(session_id):
    """Check if an Instagram session ID is valid"""
    try:
        cookies = {
            'sessionid': session_id
        }
        # Make a request to Instagram to verify if the session is valid
        response = requests.get('https://www.instagram.com/', cookies=cookies, allow_redirects=False)
        
        # If the session is valid, Instagram should not redirect us to the login page
        is_valid = response.status_code == 200 and 'login' not in response.url
        return is_valid
    except Exception as e:
        print(f"Error checking session validity: {e}")
        return False