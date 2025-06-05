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
import { useNavigate } from "react-router-dom";
import Logo from "../../assets/LogIn.png";
import axios from "axios";
import { useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";

import { LoadingButton } from "@mui/lab";

function LoginForm() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [username, setUsername] = useState("");
  const [emailRegister, setEmailRegister] = useState("");
  const [passwordRegister, setPasswordRegister] = useState("");
  const navigate = useNavigate();

  const [showPinModal, setShowPinModal] = useState(false);
  const [pendingEmail, setPendingEmail] = useState("");
  const [pin, setPin] = useState("");
  const [loadingPin, setLoadingPin] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate("/home", { replace: true });
    }
  }, []);

  const API_URL = "http://localhost:8000"; // cambia si es otro host/puerto

  const handleLogin = async () => {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password,
      });

      const token = response.data.access_token;
      localStorage.setItem("access_token", token);

      navigate("/home");
    } catch (error) {
      console.error("Error en login:", error.response?.data || error.message);
      alert("Contraseña o correo incorrecto");
    }
  };

  const downloadPrivateKey = (privateKey, filename = "clave_privada.pem") => {
    const blob = new Blob([privateKey], { type: "application/x-pem-file" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleRegister = async () => {
    if (!emailRegister || !passwordRegister || !nombre || !apellido) {
      alert("Por favor completa todos los campos.");
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/auth/send-pin`, {
        email: emailRegister,
      });

      setPendingEmail(emailRegister);
      setShowPinModal(true);
      setTimeout(() => {
        setShowPinModal(false);
        alert("⏱️ El tiempo para ingresar el PIN ha expirado");
      }, 180000); // 3 minutos

      alert(
        "Se ha enviado un PIN a tu correo. Tienes 3 minutos para ingresarlo."
      );
    } catch (error) {
      console.error(
        "Error al enviar PIN:",
        error.response?.data || error.message
      );
      alert("❌ No se pudo enviar el PIN de verificación");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/", { replace: true }); // esto borra el historial anterior
  };

  const handleVerifyPin = async () => {
    setLoadingPin(true);
    try {
      await axios.post(`${API_URL}/auth/verify-pin`, {
        email: pendingEmail,
        pin: pin,
      });

      alert("✅ Correo verificado correctamente. Se creará tu cuenta.");

      const fullName = `${nombre} ${apellido}`;
      const registerResponse = await axios.post(`${API_URL}/auth/register`, {
        email: emailRegister,
        password: passwordRegister,
        name: fullName,
      });

      const { private_key, email } = registerResponse.data;

      if (private_key) {
        const emailParts = email.split("@");
        const filename = `${emailParts[0]}_clave_privada.pem`;
        downloadPrivateKey(private_key, filename);
      }

      setShowPinModal(false);
      setIsRegistering(false);
    } catch (error) {
      console.error("Error al verificar PIN o registrar:", error);
      alert("❌ PIN incorrecto o expirado");
    } finally {
      setLoadingPin(false);
    }
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
                  control={
                    <Checkbox
                      checked={termsAccepted}
                      onChange={(e) => setTermsAccepted(e.target.checked)}
                    />
                  }
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
                  disabled={
                    !nombre || !apellido || !emailRegister || !passwordRegister
                  }
                  onClick={handleRegister}
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
                  disabled={!email || !password}
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

                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => {
                    window.location.href =
                      "http://localhost:8000/auth/login/google"; // cambia si tu backend está en otro host
                  }}
                  sx={{
                    borderColor: "#000",
                    color: "#000",
                    fontWeight: "bold",
                    textTransform: "none",
                    mt: 2,
                  }}
                >
                  Sign in with Google
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
      <Dialog open={showPinModal} onClose={() => {}}>
        <DialogTitle>Verifica tu correo electrónico</DialogTitle>
        <DialogContent>
          <Typography>
            Ingresa el código PIN que se te envió a tu correo.
          </Typography>
          <TextField
            margin="dense"
            label="PIN de verificación"
            fullWidth
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <LoadingButton
            onClick={handleVerifyPin}
            loading={loadingPin}
            variant="contained"
            color="primary"
          >
            Verificar PIN
          </LoadingButton>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default LoginForm;
