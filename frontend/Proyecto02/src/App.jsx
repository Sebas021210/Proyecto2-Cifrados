import "./App.css";
import Login from "./Pages/Login/Login";
import { Routes, Route } from "react-router-dom";
import Home from "./Pages/Chat/Home";
import PrivateRoute from "./Components/PrivateRoute";
import GoogleCallback from "./Components/GoogleCallback";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route
        path="/home"
        element={
          <PrivateRoute>
            <Home />
          </PrivateRoute>
        }
      />
      <Route path="/auth/callback" element={<GoogleCallback />} />
    </Routes>
  );
}

export default App;
