import requests
import json
import os

# Constants
SPLUNK_HOST = os.getenv("SPLUNKD_URL", "https://127.0.0.1:8089")
SPLUNK_USERNAME = os.getenv("SPLUNKD_USER", "admin")
SPLUNK_PASSWORD = os.getenv("SPLUNKD_PASSWORD", "Chang3d!")

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()


def get_splunk_session_key():
    """Authenticate with Splunk and obtain a session key."""
    auth_url = f"{SPLUNK_HOST}/services/auth/login?output_mode=json"
    data = {"username": SPLUNK_USERNAME, "password": SPLUNK_PASSWORD}
    response = requests.post(auth_url, data=data, verify=False)

    if response.status_code == 200:
        session_key = response.json()["sessionKey"]
        return session_key
    else:
        raise Exception(f"Failed to authenticate with Splunk: {response.text}")


def enable_token_authentication(session_key):
    """Enable token authentication in Splunk."""
    url = f"{SPLUNK_HOST}/services/admin/Token-auth/tokens_auth?disabled=false&expiration=&output_mode=json"
    headers = {"Authorization": f"Splunk {session_key}"}
    response = requests.post(url, headers=headers, verify=False)

    if response.status_code == 200:
        print("Token authentication enabled.")
    else:
        raise Exception(f"Failed to enable token authentication: {response.text}")


def write_token_to_env(token, filename=".tokenenv"):
    """Write the token to a .env file."""
    with open(filename, "w") as env_file:
        env_file.write(f"SPLUNKD_TOKEN={token}\n")
    print(f"Token written to {filename} file.")


def create_splunk_token(session_key):
    """Create a new token for Splunk authentication."""
    url = f"{SPLUNK_HOST}/services/authorization/tokens/create?output_mode=json"
    headers = {"Authorization": f"Splunk {session_key}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"name": SPLUNK_USERNAME, "audience": "default", "expires_on": "+90d"}
    response = requests.post(url, headers=headers, data=data, verify=False)

    if response.status_code == 201:
        token_info = response.json()
        token = token_info["entry"][0]["content"]["token"]
        print("Writing token to env file")
        write_token_to_env(token)
        return token
    else:
        raise Exception(f"Failed to create token: {response.text}")


if __name__ == "__main__":
    try:
        # Authenticate and obtain session key
        session_key = get_splunk_session_key()

        # Enable token authentication
        enable_token_authentication(session_key)

        # Create and return new token
        token = create_splunk_token(session_key)
        print(f"New token created: {token[:8]}...")
    except Exception as e:
        print(str(e))
