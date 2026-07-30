import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import Sidebar from './Sidebar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import EmployeeListPage from './pages/EmployeeListPage';
import CreateEmployeePage from './pages/CreateEmployeePage';
import EmployeeDetailPage from './pages/EmployeeDetailPage';
import ProductListPage from './pages/ProductListPage';
import StockCountPage from './pages/StockCountPage';
import DemoSettingsPage from './pages/DemoSettingsPage';
import { listDemoSettings } from './api';

function BugWarningBanner() {
  const [activeBugs, setActiveBugs] = useState<string[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      listDemoSettings()
        .then(settings => {
          const active = settings.filter(s => s.enabled).map(s => s.key);
          setActiveBugs(active);
        })
        .catch(() => {});
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  if (activeBugs.length === 0) return null;

  return (
    <div data-testid="bug-warning-banner" className="bug-warning-banner">
      <span>⚠ DEMO BUG MODE ACTIVE: [{activeBugs.join(', ')}]</span>
      <span style={{ fontSize: 11, opacity: 0.8 }}>System demonstrating intentional defects</span>
    </div>
  );
}

function RequireAuth() {
  const { user } = useAuth();
  console.log(`RequireAuth rendered. User is: ${user ? user.username : 'null'}`);
  if (!user) return <Navigate to="/login" replace />;
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <BugWarningBanner />
        <Outlet />
      </main>
    </div>
  );
}

function AdminRoute() {
  const { user } = useAuth();
  if (user?.role !== 'DEMO_ADMIN') {
    return <Navigate to="/dashboard" replace />;
  }
  return <Outlet />;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/hr/employees" element={<EmployeeListPage />} />
        <Route path="/hr/employees/new" element={<CreateEmployeePage />} />
        <Route path="/hr/employees/:id" element={<EmployeeDetailPage />} />
        <Route path="/inventory/products" element={<ProductListPage />} />
        <Route path="/inventory/stock-count" element={<StockCountPage />} />
        <Route element={<AdminRoute />}>
          <Route path="/demo-settings" element={<DemoSettingsPage />} />
        </Route>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
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
