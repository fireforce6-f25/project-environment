from flask import Flask, jsonify
from flask_cors import CORS
from get_dependencies import get_all_dependencies, get_all_hours
import re

app = Flask(__name__)


def parse_version(version_str):
    """
    Parse a version string into (major, minor, patch) tuple.
    Handles formats like "v1.2.3", "1.2.3", "1.2", "1", etc.
    Returns None if version cannot be parsed.
    """
    if not version_str or version_str in ('unversioned', 'unspecified', 'unknown'):
        return None

    # Remove leading 'v' or 'V' if present
    version_str = version_str.lstrip('vV')

    # Extract version numbers using regex
    match = re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?', version_str)
    if not match:
        return None

    major = int(match.group(1))
    minor = int(match.group(2)) if match.group(2) else 0
    patch = int(match.group(3)) if match.group(3) else 0

    return (major, minor, patch)


def get_version_compatibility_color(required_version, actual_version):
    """
    Compare required version with actual version and return a color:
    - 'green': exact match
    - 'yellow': same major version, different minor/patch
    - 'red': different major version
    - 'gray': unable to compare (missing or unparseable versions)
    """
    required = parse_version(required_version)
    actual = parse_version(actual_version)

    # If either version is unparseable, return gray
    if required is None or actual is None:
        return 'gray'

    req_major, req_minor, req_patch = required
    act_major, act_minor, act_patch = actual

    # Different major version -> red
    if req_major != act_major:
        return 'red'

    # Same major, check minor and patch
    if req_minor == act_minor and req_patch == act_patch:
        return 'green'

    # Same major, different minor/patch -> yellow
    return 'yellow'


CORS(app)  # Enable CORS for all routes

@app.route('/api/dependencies', methods=['GET'])
def get_dependencies():
    """
    API endpoint that returns dependency data for all repositories.
    Returns JSON with structure: { "repo-name": ["dep1", "dep2"], ... }
    """
    try:
        dependencies = get_all_dependencies()
        return jsonify({
            'success': True,
            'data': dependencies
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/graph', methods=['GET'])
def get_graph_data():
    """
    API endpoint that returns graph data in a format ready for D3.js visualization.
    Returns nodes (with versions) and links (with required dependency versions).
    """
    try:
        dependencies = get_all_dependencies()

        # Build nodes - each repository is a node with its version
        nodes = []
        node_set = set()

        # Add all repos as nodes with their versions
        for repo, repo_data in dependencies.items():
            if repo not in node_set:
                nodes.append({
                    'id': repo,
                    'name': repo,
                    'version': repo_data.get('version', 'unversioned')
                })
                node_set.add(repo)

        # Add any dependencies that might not be in our main repo list
        for repo, repo_data in dependencies.items():
            deps = repo_data.get('dependencies', {})
            for dep_name in deps.keys():
                if dep_name not in node_set:
                    nodes.append({
                        'id': dep_name,
                        'name': dep_name,
                        'version': 'unknown'  # External dependency, version unknown
                    })
                    node_set.add(dep_name)

        # Build a lookup for actual versions
        version_lookup = {node['id']: node['version'] for node in nodes}

        # Build links - directed edges from repo to its dependencies with required versions
        links = []
        for repo, repo_data in dependencies.items():
            deps = repo_data.get('dependencies', {})
            for dep_name, required_version in deps.items():
                actual_version = version_lookup.get(dep_name, 'unknown')
                color = get_version_compatibility_color(required_version, actual_version)
                links.append({
                    'source': repo,
                    'target': dep_name,
                    'requiredVersion': required_version,
                    'actualVersion': actual_version,
                    'color': color
                })

        return jsonify({
            'success': True,
            'data': {
                'nodes': nodes,
                'links': links
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hours', methods=['GET'])
def get_hours():
    """
    API endpoint that returns hours worked for each repository.
    Returns JSON with structure: { "repo-name": { "total_hours": 10, "hours_breakdown": {...} }, ... }
    """
    try:
        hours = get_all_hours()
        return jsonify({
            'success': True,
            'data': hours
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
