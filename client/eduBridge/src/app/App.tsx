import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { PageTitleProvider } from '../context/PageTitleContext';
import Login from '../features/auth/pages/Login';
import Signup from '../features/auth/pages/Signup';
import EmailVerification from '../features/auth/pages/EmailVerification';
import ResetPassword from '../features/auth/pages/ResetPassword';

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
        </Routes>
      </PageTitleProvider>
    </BrowserRouter>
  );
}

export default App;