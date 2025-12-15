import './App.css'
import { TeamAnalytics } from './components/analytics/TeamAnalytics'
import { PredictionDashboard } from './components/dashboard/PredictionDashboard'
import { AboutPage } from './components/about/AboutPage'
import Layout from './components/layout/Layout'
import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Router } from 'react-router-dom'


function App() {
  const [teamData, setTeamData] = useState([]);
  
  useEffect(() => {
    const getTeamNames = async () => {
      const serverApiUrl = import.meta.env.VITE_SERVER_APIS_BASE_URL;
      const teamNamesUrl = `${serverApiUrl}teamnames`;

      try {
        const response = await fetch(teamNamesUrl);

        if (!response.ok) {
          throw new Error(`Error in fetching team names: ${response.status}`)
        }

        const data = await response.json();
        setTeamData(data['team_names']);
      } catch (err) {
        console.warn(err.message);
      }
    }
    
    getTeamNames();
  }, [])


  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Layout />} >
          <Route index={true} element={<PredictionDashboard teamData={teamData} />}/>

          <Route path='analytics' 
            element={<TeamAnalytics />} 
          />

          <Route path='about' element={<AboutPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
