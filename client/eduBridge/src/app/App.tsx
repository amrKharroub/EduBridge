import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { PageTitleProvider } from '../context/PageTitleContext';
import Login from '../features/auth/pages/Login';
import Signup from '../features/auth/pages/Signup';
import EmailVerification from '../features/auth/pages/EmailVerification';
import ResetPassword from '../features/auth/pages/ResetPassword';
import DashboardLayout from '../components/layout/DashboardLayout';
import MyFiles from '../features/drive/pages/MyFiles';
import SharedWithMe from '../features/drive/pages/SharedWithMe';
import Community from '../features/drive/pages/Community';

function App() {
  return (
    <BrowserRouter>
      <PageTitleProvider>
        <Routes>
          {/* Auth routes - no sidebar */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/account/verify-email/:key" element={<EmailVerification />} />
          <Route path="/account/reset-password" element={<ResetPassword />} />

          <Route
            path="/drive"
            element={
              <DashboardLayout>
                <Navigate to="/drive/my-files" replace />
              </DashboardLayout>
            }
          />
          <Route
            path="/drive/my-files"
            element={
              <DashboardLayout>
                <MyFiles />
              </DashboardLayout>
            }
          />
          <Route
            path="/drive/shared"
            element={
              <DashboardLayout>
                <SharedWithMe />
              </DashboardLayout>
            }
          />
          <Route
            path="/drive/community"
            element={
              <DashboardLayout>
                <Community />
              </DashboardLayout>
            }
          />
        </Routes>
      </PageTitleProvider>
    </BrowserRouter>
  );
}

export default App;