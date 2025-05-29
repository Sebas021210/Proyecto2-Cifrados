import { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import Logo from "../../assets/LogIn.png";

function LoginForm() {
  const [isRegistering, setIsRegistering] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [username, setUsername] = useState("");
  const [emailRegister, setEmailRegister] = useState("");
  const [passwordRegister, setPasswordRegister] = useState("");

  const handleLogin = () => {
    alert("Inicio de sesión simulado ✅");
  };

  const handleRegister = () => {
    alert("Usuario registrado (simulado) ✅");
    setIsRegistering(false);
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor: "#1F1F1F",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        px: 2,
      }}
    >
      <Box
        sx={{
          display: "flex",
          width: "95%",
          maxWidth: "1200px",
          minHeight: "85vh",
          borderRadius: 4,
          overflow: "hidden",
          boxShadow: "0px 4px 24px rgba(0, 0, 0, 0.5)",
          backgroundColor: "#2C2C2C", // borde exterior contenedor
        }}
      >
        {/* Panel Izquierdo */}
        <Box
          sx={{
            flex: 1,
            backgroundColor: "#1F1F1F",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            px: 4,
            color: "#fff",
          }}
        >
          <Typography variant="h4" fontWeight="bold" mb={2}>
            Proyecto 02
          </Typography>
          <Typography variant="h6" sx={{ textAlign: "center", color: "#ccc" }}>
            Plataforma de Chat Seguro con Firma Digital, Cifrado Avanzado y
            Blockchain
          </Typography>
          <Box
            component="img"
            src={Logo}
            alt="Decoración abstracta"
            sx={{
              width: "60%",
              maxWidth: "300px",
              mt: 4,
            }}
          />
        </Box>

        {/* Panel Derecho */}
        <Box
          sx={{
            flex: 1,
            backgroundColor: "#1F1F1F",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            p: 4,
          }}
        >
          <Paper
            elevation={6}
            sx={{
              width: "100%",
              maxWidth: 500,
              padding: 4,
              borderRadius: 4,
              backgroundColor: "#fff",
              display: "flex",
              flexDirection: "column",
              gap: 2,
              alignItems: "center",
              justifyContent: "center",
              minHeight: "70vh",
            }}
          >
            <Typography variant="h5" fontWeight="bold" mb={2}>
              {isRegistering ? "Sign up now" : "Log in"}
            </Typography>

            {isRegistering ? (
              <>
                <Box sx={{ display: "flex", gap: 2 }}>
                  <TextField
                    fullWidth
                    label="First name"
                    variant="outlined"
                    value={nombre}
                    onChange={(e) => setNombre(e.target.value)}
                  />
                  <TextField
                    fullWidth
                    label="Last name"
                    variant="outlined"
                    value={apellido}
                    onChange={(e) => setApellido(e.target.value)}
                  />
                </Box>
                <TextField
                  fullWidth
                  label="Email address"
                  variant="outlined"
                  value={emailRegister}
                  onChange={(e) => setEmailRegister(e.target.value)}
                />
                <TextField
                  fullWidth
                  label="Username"
                  variant="outlined"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
                <TextField
                  fullWidth
                  label="Password"
                  variant="outlined"
                  type="password"
                  value={passwordRegister}
                  onChange={(e) => setPasswordRegister(e.target.value)}
                />

                <Typography variant="caption" color="text.secondary">
                  Use 8 or more characters with a mix of letters, numbers &
                  symbols
                </Typography>

                <FormControlLabel
                  control={<Checkbox />}
                  label={
                    <Typography variant="body2">
                      I agree to the <strong>Terms of use</strong> and{" "}
                      <strong>Privacy Policy</strong>
                    </Typography>
                  }
                />

                <FormControlLabel
                  control={<Checkbox />}
                  label={
                    <Typography variant="body2">
                      I consent to receive SMS and marketing messages.
                    </Typography>
                  }
                />

                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleLogin}
                  sx={{
                    backgroundColor: "#C3C3C3",
                    color: "#000", // texto negro para buen contraste
                    fontWeight: "bold",
                    "&:hover": {
                      backgroundColor: "#B0B0B0", // un poco más oscuro al pasar el mouse
                    },
                  }}
                >
                  SIGN UP
                </Button>

                <Typography variant="body2" align="center" sx={{ mt: 2 }}>
                  Already have an account?{" "}
                  <Button onClick={() => setIsRegistering(false)}>
                    Log in
                  </Button>
                </Typography>
              </>
            ) : (
              <>
                <TextField
                  fullWidth
                  label="Email address"
                  variant="outlined"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <TextField
                  fullWidth
                  label="Password"
                  variant="outlined"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />

                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleLogin}
                  sx={{
                    backgroundColor: "#C3C3C3",
                    color: "#000", // texto negro para buen contraste
                    fontWeight: "bold",
                    "&:hover": {
                      backgroundColor: "#B0B0B0", // un poco más oscuro al pasar el mouse
                    },
                  }}
                >
                  Log in
                </Button>

                <Typography variant="body2" align="center" sx={{ mt: 2 }}>
                  Don't have an account?{" "}
                  <Button onClick={() => setIsRegistering(true)}>
                    Sign up
                  </Button>
                </Typography>
              </>
            )}
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}

export default LoginForm;
