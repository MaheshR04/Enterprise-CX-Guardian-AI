import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import CustomerDashboard from './pages/CustomerDashboard';
import ChatPage from './pages/ChatPage';
import Customer360 from './pages/Customer360';
import TicketManagement from './pages/TicketManagement';
import ManagerDashboard from './pages/ManagerDashboard';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import SettingsPage from './pages/SettingsPage';
import WorkflowBuilder from './pages/WorkflowBuilder';
import ReasoningHub from './pages/ReasoningHub';
import AgentMonitor from './pages/AgentMonitor';
import TicketsWorkspace from './pages/TicketsWorkspace';
import NotFoundPage from './pages/NotFoundPage';

import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            {/* Marketing / Auth */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Managed Console Layout */}
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<ManagerDashboard />} />
              <Route path="/analytics" element={<AnalyticsDashboard />} />
              <Route path="/customer" element={<CustomerDashboard />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/customer360" element={<Customer360 />} />
              <Route path="/tickets" element={<TicketManagement />} />
              <Route path="/workspace" element={<TicketsWorkspace />} />
              <Route path="/builder" element={<WorkflowBuilder />} />
              <Route path="/reasoning" element={<ReasoningHub />} />
              <Route path="/agents" element={<AgentMonitor />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>

            {/* 404 Catch-All */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
