from flask import Flask, jsonify
from flask_cors import CORS
from get_dependencies import get_all_dependencies

app = Flask(__name__)
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

        # Build links - directed edges from repo to its dependencies with required versions
        links = []
        for repo, repo_data in dependencies.items():
            deps = repo_data.get('dependencies', {})
            for dep_name, required_version in deps.items():
                links.append({
                    'source': repo,
                    'target': dep_name,
                    'requiredVersion': required_version
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
