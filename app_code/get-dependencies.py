import sys
import time
import os
import jwt
import requests
import yaml
from dotenv import load_dotenv

def generate_jwt(pem, client_id):
    # Open PEM
    with open(pem, 'rb') as pem_file:
        signing_key = pem_file.read()
    
    payload = {
        # Issued at time
        'iat': int(time.time()),
        # JWT expiration time (10 minutes maximum)
        'exp': int(time.time()) + 600,
        
        # GitHub App's client ID
        'iss': client_id
    }
    
    # Create JWT
    encoded_jwt = jwt.encode(payload, signing_key, algorithm='RS256')
    
    return encoded_jwt

def generate_installation_token(installation_id, jwt):
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {jwt}"
    }

    response = requests.post(url, headers=headers)
    response.raise_for_status()
        
    data = response.json()
    installation_token = data["token"]
    
    return installation_token

# owner could be an organization or user
def fetch_dependencies(owner, repo, install_token):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/.settings.yaml"
    headers = {"Authorization": f"token {install_token}"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return []  # No dependencies.yaml, skip

    return yaml.safe_load(r.text)

def main():

    load_dotenv()

    pem = os.getenv("PEM")
    client_id = os.getenv("CLIENT_ID")
    installation_id = os.getenv("INSTALLATION_ID")

    # Define class wide repos
    repos = ["project-environment",
             "fire-warden",
             "mission-control",
             "modeling-environment",
             "copilot-environment",
             "fire-cloud"]

    jwt = generate_jwt(pem, client_id)

    install_token = generate_installation_token(installation_id, jwt)

    for repo in repos:
        dependencies = fetch_dependencies("fireforce6-f25 ", repo, install_token)
    
        print(f"{repo}: {dependencies}")

if __name__ == "__main__":
    main()
