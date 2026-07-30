import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import Sidebar from './Sidebar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TaskListPage from './pages/TaskListPage';
import CreateTaskPage from './pages/CreateTaskPage';
import TaskDetailPage from './pages/TaskDetailPage';
import StatusHistoryPage from './pages/StatusHistoryPage';
import {
  DeveloperTaskView,
  TestingL2QueuePage,
  ReworkQueuePage,
  DeliveryReadyPage,
  DeliveryCompletedPage,
} from './pages/QueuePages';

function RequireAuth() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/tasks" element={<TaskListPage />} />
        <Route path="/tasks/create" element={<CreateTaskPage />} />
        <Route path="/tasks/:taskId" element={<TaskDetailPage />} />
        <Route path="/tasks/:taskId/history" element={<StatusHistoryPage />} />
        <Route path="/developer-view" element={<DeveloperTaskView />} />
        <Route path="/testing-l2-queue" element={<TestingL2QueuePage />} />
        <Route path="/rework-queue" element={<ReworkQueuePage />} />
        <Route path="/delivery-ready" element={<DeliveryReadyPage />} />
        <Route path="/delivery-completed" element={<DeliveryCompletedPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
