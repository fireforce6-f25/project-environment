import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import DependencyGraph from './DependencyGraph'
import HoursChart from './HoursChart'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>FireForce6 Dashboard</h1>
          <nav className="app-nav">
            <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Dependencies
            </NavLink>
            <NavLink to="/hours" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Hours Worked
            </NavLink>
          </nav>
        </header>
        <Routes>
          <Route path="/" element={<DependencyGraph />} />
          <Route path="/hours" element={<HoursChart />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
