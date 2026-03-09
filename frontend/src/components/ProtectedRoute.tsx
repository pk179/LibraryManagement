import { Navigate, Outlet } from 'react-router-dom';

interface ProtectedRouteProps {
  adminOnly?: boolean;
}

function ProtectedRoute({ adminOnly = false }: ProtectedRouteProps) {
  const token = localStorage.getItem('access_token');
  const role = localStorage.getItem('role');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

export default ProtectedRoute;
