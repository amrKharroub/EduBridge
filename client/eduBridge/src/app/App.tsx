import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { PageTitleProvider } from '../context/PageTitleContext';
import Login from '../features/auth/pages/Login';
import Signup from '../features/auth/pages/Signup';

function App() {
  return (
    <BrowserRouter>
      <PageTitleProvider>
        <Routes>
          {/* Auth routes - no sidebar */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
        </Routes>
      </PageTitleProvider>
    </BrowserRouter>
  );
}

export default App;