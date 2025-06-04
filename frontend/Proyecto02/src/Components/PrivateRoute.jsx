import { Navigate } from "react-router-dom";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("access_token");

  return token ? children : <Navigate to="/" replace />;
}

export default PrivateRoute;
