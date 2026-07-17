import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import Dashboard from './pages/Dashboard';
import WorkflowBuilder from './pages/WorkflowBuilder';
import ReasoningHub from './pages/ReasoningHub';
import AgentMonitor from './pages/AgentMonitor';
import Integrations from './pages/Integrations';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="builder" element={<WorkflowBuilder />} />
          <Route path="reasoning" element={<ReasoningHub />} />
          <Route path="agents" element={<AgentMonitor />} />
          <Route path="integrations" element={<Integrations />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
