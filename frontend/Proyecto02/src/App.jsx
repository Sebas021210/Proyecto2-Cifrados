import { useState } from "react";
import "./App.css";
import Login from "./Pages/Login/Login";
import { Routes, Route } from "react-router-dom";
import Home from "./Pages/Chat/Home";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/home" element={<Home />} />
    </Routes>
  );
}

export default App;
