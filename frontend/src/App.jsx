import './App.css'
import { TeamAnalytics } from './components/analytics/TeamAnalytics'
import { PredictionDashboard } from './components/dashboard/PredictionDashboard'
import { AboutPage } from './components/about/AboutPage'
import Layout from './components/Layout'
import { useState } from 'react'
import { BrowserRouter, Routes, Route, Router } from 'react-router-dom'
import Navbar from './components/Navbar'


function App() {
  const [selectedTeamAnalytics, setSelectedTeamAnalytics] = useState("Celtics")

  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Layout />} >
          <Route index={true} element={<PredictionDashboard />}/>

          <Route path='analytics' 
            element={<TeamAnalytics 
              selectedTeam={selectedTeamAnalytics}
              setSelectedTeam={setSelectedTeamAnalytics}
            />} 
          />

          <Route path='about' element={<AboutPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
