import { useState, useEffect } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Tabs,
  Tab,
  Paper,
  Divider,
  Avatar,
  InputBase,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { useNavigate } from "react-router-dom";
import * as Decrypt from "./DecryptMessage.jsx";

function ChatPage() {
  const [tab, setTab] = useState(0);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [users, setUsers] = useState([]);
  const [activeUser, setActiveUser] = useState(null);

  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/", { replace: true }); // redirige al login y borra el historial
  };

  const handleSend = async () => {
    if (!message.trim() || !activeUser) return;

    try{
      const response = await fetch(`http://localhost:8000/msg/message/${activeUser.correo}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          mensaje: message,
        }),
      });

      if (!response.ok) {
        throw new Error("Error al enviar el mensaje");
      }

      const data = await response.json();
      console.log("Mensaje enviado:", data);
      setMessages((prev) => [...prev, message]);
      setMessage("");
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  useEffect(() => {
    const getUsersData = async () => {
      try {
        const response = await fetch("http://localhost:8000/grupos/usuarios", {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        if (!response.ok) {
          throw new Error("Error al obtener los usuarios");
        }
        const data = await response.json();
        console.log("Usuarios obtenidos:", data);
        setUsers(data);
        if (data.length > 0) {
          setActiveUser(data[0]);
        }

      } catch (error) {
        console.error("Error fetching users:", error);
        setUsers([]);
      }
    };

    getUsersData();
  }, [accessToken]);

  useEffect(() => {
    const privateKeyPem = `-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgLf1PGaIkNFgdv8Wf\nsXRxK1xyf1tWHZzJFrr98uvjj7ihRANCAASn9jmB6VWpBh9zY+DSue1l4U6JpJW/\n2k19ZdUHja24md/M+Gb4dCby3teVctiWoMC8ih19lS8aJt1XJWDovtWm\n-----END PRIVATE KEY-----`;
    
    const getMessagesReceived = async () => {
      if (!activeUser) return;
      try {
        const response = await fetch(`http://localhost:8000/msg/message/received/${activeUser.correo}`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        if (!response.ok) {
          throw new Error("Error al obtener los mensajes");
        }
        const data = await response.json();
        console.log("Mensajes obtenidos:", data);

        const mensajesDescifrados = await Promise.all(
          data.map(async (msg) => {
            try {
              const contenido = JSON.parse(msg.message);
              const clave = JSON.parse(msg.clave_aes_cifrada);
              const textoPlano = await Decrypt.descifrarTodo(clave, contenido, privateKeyPem);
              setMessages((prev) => [...prev, textoPlano]);
              
              return {
                ...msg,
                contenido_descifrado: textoPlano,
              };
            } catch (e) {
              console.error("Error descifrando mensaje:", e);
              return { ...msg, contenido_descifrado: null };
            }
          })
        );

        console.log("Mensajes descifrados:", mensajesDescifrados);
      } catch (error) {
        console.error("Error fetching messages:", error);
      }
    };
    getMessagesReceived();
  }, [activeUser, accessToken]);

  useEffect(() => {
    const getMessagesSent = async () => {
      if (!activeUser) return;
      try {
        const response = await fetch(`http://localhost:8000/msg/message/sent/${activeUser.correo}`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        if (!response.ok) {
          throw new Error("Error al obtener los mensajes enviados");
        }
        const data = await response.json();
        console.log("Mensajes enviados obtenidos:", data);
      } catch (error) {
        console.error("Error fetching sent messages:", error);
      }
    };
    getMessagesSent();
  }, [activeUser, accessToken]);

  const filteredUsers = users.filter((user) =>
    `${user.nombre} ${user.correo}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleDownloadKey = async () => {
    try {
      const response = await fetch("http://localhost:8000/auth/download-private-key", {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) {
        throw new Error("Error al descargar la llave ECC");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "llave_ecc.zip";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      console.error("Error downloading key:", error);
    }
  }

  return (
    <Box
      sx={{
        height: "80vh",
        width: "150vh",
        marginLeft: "10vh",
        marginTop: "5vh",
        backgroundColor: "#1F1F1F",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        gap: 3,
        p: 3,
        fontFamily: "'Segoe UI', sans-serif",
      }}
    >
      {/* PANEL IZQUIERDO: Acciones + Usuarios/Grupos */}
      <Paper
        elevation={6}
        sx={{
          width: "300px",
          height: "100%",
          backgroundColor: "#2C2C2C",
          display: "flex",
          flexDirection: "column",
          borderRadius: 4,
          color: "#fff",
          overflow: "hidden",
        }}
      >
        {/* ACCIONES */}
        <Box
          sx={{
            p: 2,
            borderBottom: "1px solid #444",
            backgroundColor: "#1F1F1F",
          }}
        >
          <Typography
            variant="subtitle1"
            fontWeight="bold"
            mb={1}
            textAlign="center"
          >
            Acciones
          </Typography>
          <Button
            fullWidth
            variant="contained"
            sx={{
              backgroundColor: "white",
              color: "#000",
              fontWeight: "bold",
              borderRadius: 2,
              textTransform: "none",
              mb: 1,
              "&:hover": { backgroundColor: "#B0B0B0" },
            }}
            onClick={handleDownloadKey}
          >
            Descargar llave ECC
          </Button>
          <Button
            fullWidth
            variant="contained"
            sx={{
              backgroundColor: "white",
              color: "#000",
              fontWeight: "bold",
              borderRadius: 2,
              textTransform: "none",
              mb: 1,
              "&:hover": { backgroundColor: "#B0B0B0" },
            }}
          >
            Crear grupo nuevo
          </Button>
          <Button
            fullWidth
            variant="contained"
            onClick={handleLogout}
            sx={{
              backgroundColor: "white",
              color: "#000",
              fontWeight: "bold",
              borderRadius: 2,
              textTransform: "none",
              "&:hover": { backgroundColor: "#B0B0B0" },
            }}
          >
            Log Out
          </Button>
        </Box>

        {/* TABS */}
        <Tabs
          value={tab}
          onChange={(e, newVal) => setTab(newVal)}
          textColor="inherit"
          TabIndicatorProps={{
            style: {
              backgroundColor: "#fff",
            },
          }}
        >
          <Tab label="Usuarios" />
          <Tab label="Grupos" />
        </Tabs>

        <Divider sx={{ backgroundColor: "#444" }} />

        {/* BUSCADOR */}
        {tab === 0 && (
          <Box sx={{ px: 2, py: 1 }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                backgroundColor: "#1F1F1F",
                borderRadius: 2,
                px: 2,
                py: 1,
              }}
            >
              <SearchIcon sx={{ color: "#888" }} />
              <InputBase
                placeholder="Buscar usuario..."
                sx={{ ml: 1, flex: 1, color: "#fff" }}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </Box>
          </Box>
        )}

        {/* LISTADO DE USUARIOS / GRUPOS */}
        <Box sx={{ flex: 1, overflowY: "auto", px: 2, py: 1 }}>
          {(tab === 0 ? filteredUsers : ["Grupo A", "Grupo B", "Grupo C"]).map(
            (item, i) => (
              <Box
                key={i}
                sx={{
                  display: "flex",
                  alignItems: "center",
                  mb: 2,
                  gap: 1,
                  cursor: "pointer",
                  backgroundColor: activeUser?.id_pk === item.id_pk ? "#2a2a2a" : "transparent",
                  borderRadius: 1,
                  px: 1,
                  py: 0.5,
                  "&:hover": { backgroundColor: "#333" },
                }}
                onClick={() => setActiveUser(item)}
              >
                <Avatar
                  alt={tab === 0 ? item.nombre : item}
                  src="/broken-image.jpg"
                />
                <Box sx={{ display: "flex", flexDirection: "column" }}>
                  <Typography variant="body1" fontWeight="bold">
                    {tab === 0 ? item.nombre : item}
                  </Typography>
                  <Typography variant="subtitle2">
                    {tab === 0 ? item.correo : ""}
                  </Typography>
                </Box>
              </Box>
            )
          )}
        </Box>
      </Paper>

      {/* PANEL DE CHAT */}
      <Paper
        elevation={6}
        sx={{
          flex: 1,
          height: "100%",
          display: "flex",
          flexDirection: "column",
          borderRadius: 4,
          overflow: "hidden",
        }}
      >
        {/* HEADER */}
        <Box
          sx={{
            backgroundColor: "#1F1F1F",
            padding: 2,
            display: "flex",
            alignItems: "center",
            gap: 2,
            color: "#fff",
            borderBottom: "1px solid #444",
          }}
        >
          <Avatar
            alt={activeUser ? activeUser.nombre : "Usuario"}
            src="/broken-image.jpg"
          />
          <Typography variant="subtitle1" fontWeight="bold">
            {activeUser ? activeUser.nombre : "Selecciona un usuario"}
          </Typography>
        </Box>

        {/* MENSAJES */}
        <Box
          sx={{
            flex: 1,
            overflowY: "auto",
            p: 3,
            display: "flex",
            flexDirection: "column",
            gap: 2,
            backgroundColor: "#fff",
          }}
        >
          {messages.length === 0 ? (
            <Typography color="#888" textAlign="center">
              No hay mensajes aún
            </Typography>
          ) : (
            messages.map((msg, i) => (
              <Box
                key={i}
                sx={{
                  display: "flex",
                  justifyContent: i % 2 === 0 ? "flex-start" : "flex-end",
                }}
              >
                <Paper
                  sx={{
                    p: 1.5,
                    backgroundColor: i % 2 === 0 ? "#E0E0E0" : "#C3C3C3",
                    color: "#000",
                    borderRadius: 4,
                    maxWidth: "70%",
                  }}
                >
                  {msg}
                </Paper>
              </Box>
            ))
          )}
        </Box>

        {/* INPUT MENSAJE */}
        <Box
          sx={{
            p: 2,
            borderTop: "1px solid #ccc",
            display: "flex",
            gap: 2,
            backgroundColor: "#F5F5F5",
          }}
        >
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Escribe un mensaje..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            InputProps={{
              style: {
                backgroundColor: "#fff",
                borderRadius: 10,
              },
            }}
          />
          <Button
            variant="contained"
            onClick={handleSend}
            sx={{
              backgroundColor: "#1F1F1F",
              color: "white",
              fontWeight: "bold",
              borderRadius: 2,
              "&:hover": { backgroundColor: "#B0B0B0" },
            }}
          >
            ENVIAR
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}

export default ChatPage;
