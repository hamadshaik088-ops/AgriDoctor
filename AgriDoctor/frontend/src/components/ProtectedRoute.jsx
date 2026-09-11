import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children, user, token, role }) {
  if (!user || !token) {
    return <Navigate to="/login" replace />;
  }
  if (role && user.role !== role) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}
