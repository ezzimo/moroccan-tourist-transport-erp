import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/context/AuthContext';
import { ProtectedRoute } from './auth/components/ProtectedRoute';
import LoginPage from './auth/pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CustomersPage from './crm/pages/CustomersPage';
import CustomerDetailPage from './crm/pages/CustomerDetailPage';
import FeedbackPage from './crm/pages/FeedbackPage';
import SegmentsPage from './crm/pages/SegmentsPage';
import InteractionsPage from './crm/pages/InteractionsPage';
import VehiclesPage from './fleet/pages/VehiclesPage';
import VehicleDetailPage from './fleet/pages/VehicleDetailPage';
import DriversPage from './driver/pages/DriversPage';
import DriverDetailPage from './driver/pages/DriverDetailPage';
import InvoicesPage from './finance/pages/InvoicesPage';
import PaymentsPage from './finance/pages/PaymentsPage';
import ExpensesPage from './finance/pages/ExpensesPage';
import FinancialDashboardPage from './finance/pages/FinancialDashboardPage';
import BookingsPage from './booking/pages/BookingsPage';
import BookingDetailPage from './booking/pages/BookingDetailPage';
import ToursPage from './tour/pages/ToursPage';
import TourTemplatesPage from './tour/pages/TourTemplatesPage';
import TourInstancesPage from './tour/pages/TourInstancesPage';
import TourIncidentsPage from './tour/pages/TourIncidentsPage';
import CreateTourTemplatePage from './tour/pages/CreateTourTemplatePage';
import TourTemplateDetailPage from './tour/pages/TourTemplateDetailPage';
import TourDetailPage from './tour/pages/TourDetailPage';
import QAPage from './qa/pages/QAPage';
import AuditsPage from './qa/pages/AuditsPage';
import EmployeesPage from './hr/pages/EmployeesPage';
import EmployeeDetailPage from './hr/pages/EmployeeDetailPage';
import TrainingPage from './hr/pages/TrainingPage';
import RecruitmentPage from './hr/pages/RecruitmentPage';
import HRAnalyticsPage from './hr/pages/HRAnalyticsPage';
import InventoryItemsPage from './inventory/pages/InventoryItemsPage';
import InventoryDashboardPage from './inventory/pages/InventoryDashboardPage';
import NotificationsPage from './notification/pages/NotificationsPage';
import SendNotificationPage from './notification/pages/SendNotificationPage';
import TemplatesPage from './notification/pages/TemplatesPage';
import CreateTemplatePage from './notification/pages/CreateTemplatePage';
import Layout from './components/Layout';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected routes */}
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="customers" element={<CustomersPage />} />
          <Route path="customers/:id" element={<CustomerDetailPage />} />
          <Route path="feedback" element={<FeedbackPage />} />
          <Route path="segments" element={<SegmentsPage />} />
          <Route path="interactions" element={<InteractionsPage />} />
          <Route path="fleet" element={<VehiclesPage />} />
          <Route path="fleet/vehicles/:id" element={<VehicleDetailPage />} />
          <Route path="drivers" element={<DriversPage />} />
          <Route path="drivers/:id" element={<DriverDetailPage />} />
          <Route path="finance" element={<FinancialDashboardPage />} />
          <Route path="invoices" element={<InvoicesPage />} />
          <Route path="payments" element={<PaymentsPage />} />
          <Route path="expenses" element={<ExpensesPage />} />
          <Route path="bookings" element={<BookingsPage />} />
          <Route path="bookings/:id" element={<BookingDetailPage />} />
          <Route path="tours" element={<ToursPage />} />
          <Route path="tours/templates" element={<TourTemplatesPage />} />
          <Route path="tours/templates/create" element={<CreateTourTemplatePage />} />
          <Route path="tours/templates/:id" element={<TourTemplateDetailPage />} />
          <Route path="tours/instances" element={<TourInstancesPage />} />
          <Route path="tours/incidents" element={<TourIncidentsPage />} />
          <Route path="tours/:id" element={<TourDetailPage />} />
          <Route path="qa" element={<QAPage />} />
          <Route path="qa/audits" element={<AuditsPage />} />
          <Route path="hr/employees" element={<EmployeesPage />} />
          <Route path="hr/employees/:id" element={<EmployeeDetailPage />} />
          <Route path="hr/trainings" element={<TrainingPage />} />
          <Route path="hr/recruitment" element={<RecruitmentPage />} />
          <Route path="hr/analytics" element={<HRAnalyticsPage />} />
          <Route path="inventory/items" element={<InventoryItemsPage />} />
          <Route path="inventory/dashboard" element={<InventoryDashboardPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="notifications/send" element={<SendNotificationPage />} />
          <Route path="templates" element={<TemplatesPage />} />
          <Route path="templates/create" element={<CreateTemplatePage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;