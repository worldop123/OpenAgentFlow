import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { WorkflowProvider } from './contexts/WorkflowContext'
import { AgentProvider } from './contexts/AgentContext'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import WorkflowEditor from './pages/WorkflowEditor'
import AgentManager from './pages/AgentManager'
import ToolManager from './pages/ToolManager'
import Settings from './pages/Settings'
import Documentation from './pages/Documentation'
import NotFound from './pages/NotFound'

function App() {
  return (
    <Router>
      <WorkflowProvider>
        <AgentProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/workflow/:id?" element={<WorkflowEditor />} />
              <Route path="/agents" element={<AgentManager />} />
              <Route path="/tools" element={<ToolManager />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/docs" element={<Documentation />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        </AgentProvider>
      </WorkflowProvider>
    </Router>
  )
}

export default App