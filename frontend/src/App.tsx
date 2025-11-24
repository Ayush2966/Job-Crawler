import React from 'react'
import JobSearchForm from './components/JobSearchForm'
import './App.css'

function App() {
  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🔍 Job Crawler Configuration</h1>
          <p>Configure your job search preferences and notification settings</p>
        </header>
        <JobSearchForm />
      </div>
    </div>
  )
}

export default App

