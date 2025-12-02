# Repository Dependency Graph Visualizer

A web application to visualize dependencies across fireforce6-f25 repositories using a Flask backend and React frontend with D3.js.

## Architecture

- **Backend**: Flask API server that fetches repository dependencies from GitHub
- **Frontend**: React application with D3.js for interactive graph visualization
- **Data Flow**: Python script uses GitHub App authentication to fetch `.settings.yaml` files from repositories

## Prerequisites

- Python 3.12+
- Node.js 23+
- npm 11+
- GitHub App credentials (PEM file, Client ID, Installation ID)

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
# Make sure .env file contains:
# PEM=path/to/your/pem/file
# CLIENT_ID=your_github_app_client_id
# INSTALLATION_ID=your_installation_id

# Start the Flask server
python3 app.py
```

The backend will run on `http://localhost:5001`

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:5173`

## Running the Application

1. Start the Flask backend in one terminal:
   ```bash
   cd backend && python3 app.py
   ```

2. Start the React frontend in another terminal:
   ```bash
   cd frontend && npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

## API Endpoints

- `GET /api/dependencies` - Returns raw dependency data for all repositories
- `GET /api/graph` - Returns formatted graph data (nodes and links) for D3.js
- `GET /health` - Health check endpoint

## Graph Visualization

The dependency graph shows:
- **Nodes**: Each repository is represented as a circle
- **Edges**: Arrows point from a repository to its dependencies
- **Colors**:
  - Blue: Repository has dependencies only
  - Orange: Repository is depended upon only
  - Green: Repository both has dependencies and is depended upon
  - Gray: Repository has no connections

**Interactions**:
- Drag nodes to rearrange the graph
- Hover over nodes to see dependency details
- Zoom and pan to navigate the graph
- The graph uses force-directed layout for automatic positioning

## Project Structure

```
.
├── backend/
│   ├── app.py                      # Flask API server
│   ├── get-dependencies.py         # GitHub API integration
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main React component
│   │   ├── DependencyGraph.jsx    # D3.js visualization component
│   │   ├── DependencyGraph.css    # Graph styles
│   │   └── index.css              # Global styles
│   └── package.json               # Node dependencies
└── SETUP.md                       # This file
```

## Troubleshooting

- **CORS errors**: Make sure Flask-CORS is installed and the backend is running
- **API errors**: Check that your GitHub App credentials are correct in `.env`
- **No data showing**: Verify that the repositories have `.settings.yaml` files in their main branch
