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
        return {}  # No dependencies.yaml, skip

    return yaml.safe_load(r.text)

def fetch_repo_version(owner, repo, install_token):
    """
    Fetches the latest release or tag version for a repository.
    Returns the version string or "unversioned" if no releases/tags exist.
    """
    # Try to get the latest release first
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {install_token}"
    }

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        release_data = r.json()
        return release_data.get('tag_name', 'unversioned')

    # If no releases, try to get the latest tag
    url = f"https://api.github.com/repos/{owner}/{repo}/tags"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        tags = r.json()
        if tags and len(tags) > 0:
            return tags[0]['name']

    return "unversioned"

def get_github_credentials():
    """Load and return GitHub credentials."""
    load_dotenv()
    pem = os.getenv("PEM")
    client_id = os.getenv("CLIENT_ID")
    installation_id = os.getenv("INSTALLATION_ID")
    return pem, client_id, installation_id


def get_repos():
    """Return list of class repos."""
    return ["project-environment",
            "fire-warden",
            "mission-control",
            "modeling-environment",
            "copilot-environment",
            "fire-cloud"]


def get_all_dependencies():
    """
    Fetches dependencies for all repos and returns structured data.
    Returns a dictionary with:
    - repo names as keys
    - values containing: repo version, dependencies dict (name -> required version)
    """
    pem, client_id, installation_id = get_github_credentials()
    repos = get_repos()

    jwt_token = generate_jwt(pem, client_id)
    install_token = generate_installation_token(installation_id, jwt_token)

    result = {}
    for repo in repos:
        # Fetch the repo's own version from GitHub releases/tags
        repo_version = fetch_repo_version("fireforce6-f25", repo, install_token)

        # Fetch dependencies and their required versions
        settings = fetch_dependencies("fireforce6-f25", repo, install_token)
        dependencies = settings.get('dependencies', {}) if isinstance(settings, dict) else {}

        # Handle both old format (list) and new format (dict)
        if isinstance(dependencies, list):
            # Old format: convert to dict with "unspecified" versions
            dependencies = {dep: "unspecified" for dep in dependencies}

        result[repo] = {
            'version': repo_version,
            'dependencies': dependencies
        }

    return result


def get_all_hours():
    """
    Fetches hours worked for all repos from their .settings.yaml files.
    Returns a dictionary with repo names as keys and total hours as values.

    Expected .settings.yaml format:
    hours:
      11/21/25: 1
      11/22/25: 2.5
    """
    pem, client_id, installation_id = get_github_credentials()
    repos = get_repos()

    jwt_token = generate_jwt(pem, client_id)
    install_token = generate_installation_token(installation_id, jwt_token)

    result = {}
    for repo in repos:
        settings = fetch_dependencies("fireforce6-f25", repo, install_token)
        hours_data = settings.get('hours', {}) if isinstance(settings, dict) else {}

        # Sum up all hours from the dictionary
        total_hours = 0
        if isinstance(hours_data, dict):
            for date, hours in hours_data.items():
                try:
                    total_hours += float(hours)
                except (ValueError, TypeError):
                    pass  # Skip invalid hour entries

        result[repo] = {
            'total_hours': total_hours,
            'hours_breakdown': hours_data
        }

    return result

def main():
    """CLI entry point - prints dependencies to console."""
    dependencies = get_all_dependencies()
    for repo, deps in dependencies.items():
        print(f"{repo}: {deps}")

if __name__ == "__main__":
    main()
