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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormControlLabel,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { useNavigate } from "react-router-dom";

function ChatPage() {
  const [tab, setTab] = useState(0);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [users, setUsers] = useState([]);
  const [privateKeyFile, setPrivateKeyFile] = useState(null);

  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");

  const [openGroupModal, setOpenGroupModal] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [selectedUsers, setSelectedUsers] = useState([]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/", { replace: true }); // redirige al login y borra el historial
  };

  const handleSend = () => {
    if (message.trim()) {
      setMessages([...messages, message]);
      setMessage("");
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) setPrivateKeyFile(file);
  };

  const handleFileDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) setPrivateKeyFile(file);
  };

  const handleToggleUser = (correo) => {
    setSelectedUsers((prev) =>
      prev.includes(correo)
        ? prev.filter((email) => email !== correo)
        : [...prev, correo]
    );
  };

  const handleCreateGroup = () => {
    console.log("Grupo:", groupName);
    console.log("Integrantes:", selectedUsers);
    setOpenGroupModal(false);
    setGroupName("");
    setSelectedUsers([]);
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
      } catch (error) {
        console.error("Error fetching users:", error);
        setUsers([]);
      }
    };

    getUsersData();
  }, [accessToken]);

  const filteredUsers = users.filter((user) =>
    `${user.nombre} ${user.correo}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  return (
    <Box
      sx={{
        height: "80vh",
        width: "170vh",
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
            onClick={() => setOpenGroupModal(true)}
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
                }}
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
          <Avatar src="/broken-image.jpg" />
          <Typography variant="subtitle1" fontWeight="bold">
            Chat con Usuario 1
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

      {/* PANEL DERECHO: Subir Llave Privada */}
      <Paper
        elevation={6}
        sx={{
          height: "95%",
          backgroundColor: "#2C2C2C",
          borderRadius: 4,
          color: "#fff",
          p: 2,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
        }}
        onDrop={handleFileDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        <Typography variant="h6" fontWeight="bold">
          Llave Privada
        </Typography>
        <Box
          sx={{
            border: "2px dashed #aaa",
            borderRadius: 4,
            width: "97%",
            height: 500,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            p: 2,
            mt: 3,
            textAlign: "center",
            color: "#ccc",
          }}
        >
          {privateKeyFile ? privateKeyFile.name : "Arrastra tu archivo aquí"}
        </Box>
        <Button
          variant="contained"
          component="label"
          sx={{
            backgroundColor: "#1F1F1F",
            color: "white",
            fontWeight: "bold",
            borderRadius: 2,
            textTransform: "none",
            "&:hover": { backgroundColor: "#B0B0B0" },
          }}
        >
          Subir Archivo
          <input type="file" hidden onChange={handleFileUpload} />
        </Button>
      </Paper>

      {/* Modal para crear un grupo nuevo */}
      <Dialog
        open={openGroupModal}
        onClose={() => setOpenGroupModal(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ backgroundColor: "#1F1F1F", color: "#fff" }}>
          Crear nuevo grupo
        </DialogTitle>
        <DialogContent sx={{ backgroundColor: "#2C2C2C" }}>
          <TextField
            label="Nombre del grupo"
            variant="outlined"
            fullWidth
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            sx={{ my: 2, input: { color: "#fff" }, label: { color: "#aaa" } }}
          />
          <Typography variant="subtitle1" color="#fff" gutterBottom>
            Selecciona usuarios:
          </Typography>
          {users.map((user, i) => (
            <FormControlLabel
              key={i}
              control={
                <Checkbox
                  checked={selectedUsers.includes(user.correo)}
                  onChange={() => handleToggleUser(user.correo)}
                  sx={{ color: "#fff" }}
                />
              }
              label={
                <Typography color="#fff">
                  {user.nombre} ({user.correo})
                </Typography>
              }
            />
          ))}
        </DialogContent>
        <DialogActions sx={{ backgroundColor: "#2C2C2C", p: 2 }}>
          <Button
            onClick={() => setOpenGroupModal(false)}
            sx={{ color: "#ccc", textTransform: "none" }}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleCreateGroup}
            variant="contained"
            sx={{
              backgroundColor: "#1F1F1F",
              color: "#fff",
              fontWeight: "bold",
              borderRadius: 2,
              textTransform: "none",
              "&:hover": { backgroundColor: "#B0B0B0" },
            }}
          >
            Crear grupo
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ChatPage;
