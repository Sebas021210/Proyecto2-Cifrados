import { useState } from "react";
import {
  Button,
  TextField,
  Typography,
  Box,
  Modal,
  Paper,
} from "@mui/material";

function LoginForm() {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [username, setUsername] = useState("");
  const [emailRegister, setEmailRegister] = useState("");
  const [passwordRegister, setPasswordRegister] = useState("");

  const handleLogin = () => {
    console.log("🔐 Simulación de inicio de sesión", { email, password });
    alert("Inicio de sesión simulado ✅");
  };

  const handleRegister = () => {
    console.log("🧾 Simulación de registro", {
      nombre,
      apellido,
      username,
      email: emailRegister,
      password: passwordRegister,
    });
    alert("Usuario registrado (simulado) ✅");
    setOpen(false);
  };

  return (
    <Box
      sx={{
        backgroundColor: "#284B63", // Fondo azul oscuro
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {!open && (
        <Box
          sx={{
            width: 360,
            display: "flex",
            flexDirection: "column",
            gap: 2,
            padding: 4,
            borderRadius: 3,
            backgroundColor: "#353535",
            boxShadow: "0px 4px 24px rgba(0, 0, 0, 0.5)",
            color: "#fff",
          }}
        >
          <Typography variant="h5" align="center">
            Iniciar Sesión
          </Typography>

          <TextField
            label="Correo electrónico"
            variant="filled"
            fullWidth
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            InputProps={{
              style: { backgroundColor: "#2c2c2c", color: "#fff" },
            }}
            InputLabelProps={{ style: { color: "#aaa" } }}
          />

          <TextField
            label="Contraseña"
            type="password"
            variant="filled"
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            InputProps={{
              style: { backgroundColor: "#2c2c2c", color: "#fff" },
            }}
            InputLabelProps={{ style: { color: "#aaa" } }}
          />

          <Button
            variant="contained"
            fullWidth
            onClick={handleLogin}
            sx={{
              backgroundColor: "#3C6E71",
              "&:hover": { backgroundColor: "#284B63" },
              fontWeight: "bold",
              color: "#fff",
            }}
          >
            INICIAR SESIÓN
          </Button>

          <Button
            variant="outlined"
            fullWidth
            onClick={() => setOpen(true)}
            sx={{
              borderColor: "#3C6E71", // azul claro
              color: "#3C6E71",
              fontWeight: "bold",
              "&:hover": {
                borderColor: "#fff",
                color: "#fff",
              },
            }}
          >
            REGISTRARSE
          </Button>
        </Box>
      )}

      <Modal open={open} onClose={() => setOpen(false)}>
        <Paper
          sx={{
            width: 420,
            margin: "auto",
            marginTop: "10vh",
            padding: 4,
            backgroundColor: "#1e1e1e",
            color: "white",
            display: "flex",
            flexDirection: "column",
            gap: 2,
          }}
        >
          <Typography variant="h6" align="center">
            Crear nuevo usuario
          </Typography>

          <TextField
            label="Nombre"
            variant="filled"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            InputProps={{
              style: { backgroundColor: "#2c2c2c", color: "#fff" },
            }}
            InputLabelProps={{ style: { color: "#aaa" } }}
          />

          <TextField
            label="Apellido"
            variant="filled"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            InputProps={{
              style: { backgroundColor: "#2c2c2c", color: "#fff" },
            }}
            InputLabelProps={{ style: { color: "#aaa" } }}
          />

          <TextField
            label="Nombre de usuario"
            variant="filled"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            InputProps={{
              style: { backgroundColor: "#2c2c2c", color: "#fff" },
            }}
            InputLabelProps={{ style: { color: "#aaa" } }}
          />

          <TextField
            label="Correo electrónico"
            variant="filled"
            value={emailRegister}
            onChange={(e) => setEmailRegister(e.target.value)}
            InputProps={{
              style: { backgroundColor: "#2c2c2c", color: "#fff" },
            }}
            InputLabelProps={{ style: { color: "#aaa" } }}
          />

          <TextField
            label="Contraseña"
            type="password"
            variant="filled"
            value={passwordRegister}
            onChange={(e) => setPasswordRegister(e.target.value)}
            InputProps={{
              style: { backgroundColor: "#2c2c2c", color: "#fff" },
            }}
            InputLabelProps={{ style: { color: "#aaa" } }}
          />

          <Button
            variant="contained"
            onClick={handleRegister}
            sx={{
              backgroundColor: "#FB8C00", // naranja
              "&:hover": { backgroundColor: "#e67600" },
              fontWeight: "bold",
            }}
          >
            REGISTRARME
          </Button>

          <Button
            onClick={() => setOpen(false)}
            sx={{
              color: "#FFC107", // amarillo
              fontWeight: "bold",
              "&:hover": { color: "#fff" },
            }}
          >
            CANCELAR
          </Button>
        </Paper>
      </Modal>
    </Box>
  );
}

export default LoginForm;
