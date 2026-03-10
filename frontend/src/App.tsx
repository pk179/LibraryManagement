import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import BooksList from './pages/BooksList';
import MyLoans from './pages/MyLoans';
import AdminDashboard from './pages/AdminDashboard';


function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <div style={{ padding: '16px' }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Home />} />
            <Route path="/books" element={<BooksList />} />
            <Route path="/my-loans" element={<MyLoans />} />

          </Route>

          <Route element={<ProtectedRoute adminOnly={true} />}>
            <Route path="/admin" element={<AdminDashboard />} />

          </Route>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
