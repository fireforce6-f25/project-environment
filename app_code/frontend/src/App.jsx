import DependencyGraph from './DependencyGraph'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <h1>Repository Dependency Graph</h1>
        <p>Visualizing dependencies across fireforce6-f25 repositories</p>
      </header>
      <DependencyGraph />
    </div>
  )
}

export default App
