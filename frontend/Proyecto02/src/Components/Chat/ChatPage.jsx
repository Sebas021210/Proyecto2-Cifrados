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
import * as Decrypt from "./DecryptMessage.jsx";

function ChatPage() {
  const [tab, setTab] = useState(0);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [users, setUsers] = useState([]);
  const [activeUser, setActiveUser] = useState(null);
  const [privateKeyFile, setPrivateKeyFile] = useState(null);
  const [privateKeyPem, setPrivateKeyPem] = useState(null);

  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");

  const [openGroupModal, setOpenGroupModal] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [selectedUsers, setSelectedUsers] = useState([]);

  const [grupos, setGrupos] = useState([]);

  const [openMembersModal, setOpenMembersModal] = useState(false);
  const [miembrosGrupo, setMiembrosGrupo] = useState([]);
  const [grupoActual, setGrupoActual] = useState(null);
  const [grupoActualId, setGrupoActualId] = useState(null);
  const [activeGroup, setActiveGroup] = useState(null);
  const [groupMessages, setGroupMessages] = useState([]); // mensajes grupales

  const mensajesVisibles = activeGroup ? groupMessages : messages;

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/", { replace: true }); // redirige al login y borra el historial
  };

  const handleSend = async () => {
    if (!message.trim() || !activeUser || !privateKeyPem) return;

    try {
      const response = await fetch(
        `http://localhost:8000/msg/message/${activeUser.correo}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            mensaje: message,
            clave_privada_pem: privateKeyPem,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Error al enviar el mensaje");
      }

      const data = await response.json();
      console.log("Mensaje enviado:", data);

      setMessages((prev) => [
        ...prev,
        {
          text: message,
          type: "sent",
        },
      ]);

      setMessage("");
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setPrivateKeyFile(file);
      readPemFile(file);
    }
  };

  const handleFileDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      setPrivateKeyFile(file);
      readPemFile(file);
    }
  };

  const readPemFile = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      setPrivateKeyPem(e.target.result);
    };
    reader.readAsText(file);
  };

  const handleToggleUser = (correo) => {
    setSelectedUsers((prev) =>
      prev.includes(correo)
        ? prev.filter((email) => email !== correo)
        : [...prev, correo]
    );
  };

  const handleCreateGroup = async () => {
    if (!groupName.trim() || selectedUsers.length === 0) {
      alert("El nombre del grupo y al menos un usuario son requeridos.");
      return;
    }

    try {
      // Convertir correos seleccionados en IDs de usuarios
      const miembrosIds = selectedUsers
        .map((correo) => {
          const user = users.find((u) => u.correo === correo);
          return user ? user.id_pk : null;
        })
        .filter((id) => id !== null);

      const responseGrupo = await fetch(
        "http://localhost:8000/grupos/newGroup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            nombre: groupName,
            miembros_ids: miembrosIds,
          }),
        }
      );

      if (!responseGrupo.ok) {
        const errMsg = await responseGrupo.text();
        throw new Error(`Error al crear el grupo: ${errMsg}`);
      }

      const grupoData = await responseGrupo.json();
      console.log("Grupo creado:", grupoData);

      alert("Grupo creado exitosamente con sus miembros.");
      setOpenGroupModal(false);
      setGroupName("");
      setSelectedUsers([]);
    } catch (error) {
      console.error("Error en la creación del grupo:", error);
      alert("Ocurrió un error al crear el grupo.");
    }
  };

  const handleOpenGroupDetails = async (grupoId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/grupos/GroupDetails/${grupoId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) throw new Error("Error al obtener detalles del grupo");

      const data = await response.json();
      setGrupoActual(data.nombre_de_grupo);
      setMiembrosGrupo(data.miembros);
      setOpenMembersModal(true);
      setGrupoActualId(grupoId);
    } catch (error) {
      console.error("Error fetching group details:", error);
    }
  };

  const handleDeleteMember = async (id_usuario, nombre) => {
    const confirm = window.confirm(
      `¿Estás seguro que quieres eliminar a ${nombre} del grupo?`
    );
    if (!confirm) return;

    try {
      const response = await fetch(`http://localhost:8000/grupos/miembros`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          id_grupo: grupoActualId,
          id_usuario: id_usuario,
        }),
      });

      if (!response.ok) throw new Error("Error al eliminar miembro");

      // Actualizar lista localmente
      setMiembrosGrupo((prev) => prev.filter((u) => u.id_pk !== id_usuario));
      alert("Miembro eliminado exitosamente");
    } catch (error) {
      console.error("Error al eliminar miembro:", error);
      alert("Hubo un error al eliminar el miembro");
    }
  };

  const fetchGroupMessages = async (grupo = activeGroup) => {
    if (!grupo || !privateKeyPem) return;

    try {
      const resMsgs = await fetch(
        `http://localhost:8000/grupos/GroupMessages/${grupo.id_pk}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      if (!resMsgs.ok) throw new Error("Error al obtener mensajes del grupo");
      const mensajes = await resMsgs.json();

      const resClave = await fetch(
        "http://localhost:8000/grupos/descifrar_llave_privada",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            group_id: grupo.id_pk,
            user_private_key_pem: privateKeyPem,
          }),
        }
      );
      if (!resClave.ok)
        throw new Error("Error al descifrar la llave privada del grupo");

      const { llave_privada_grupo } = await resClave.json();

      const mensajesDescifrados = await Promise.all(
        mensajes.map(async (msg) => {
          try {
            let claveParsed = msg.clave_aes_cifrada;
            if (typeof claveParsed === "string") {
              claveParsed = JSON.parse(claveParsed);
            }

            const resDescifrado = await fetch(
              "http://localhost:8000/grupos/descifrar_mensaje_grupo",
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  Authorization: `Bearer ${accessToken}`,
                },
                body: JSON.stringify({
                  mensaje_cifrado: msg.mensaje,
                  nonce: msg.nonce,
                  clave_aes_cifrada: claveParsed,
                  private_key_grupo_pem: llave_privada_grupo,
                }),
              }
            );

            if (!resDescifrado.ok) {
              const errMsg = await resDescifrado.text();
              console.error("❌ Backend error:", errMsg);
              throw new Error("Error al descifrar mensaje");
            }

            const { mensaje_plano } = await resDescifrado.json();

            const remitente = users.find(
              (u) => u.id_pk === msg.id_remitente_fk
            );
            const remitenteNombre = remitente
              ? remitente.nombre
              : "Desconocido";

            return {
              text: `${remitenteNombre}: ${mensaje_plano}`,
              type:
                msg.id_remitente_fk === remitente?.id_pk &&
                remitente?.correo === activeUser?.correo
                  ? "sent"
                  : "received",
              timestamp: msg.timestamp,
            };
          } catch (e) {
            console.error("❌ Error descifrando mensaje grupal:", e);
            return null;
          }
        })
      );

      setGroupMessages(mensajesDescifrados.filter(Boolean));
    } catch (error) {
      console.error("❌ Error al obtener mensajes grupales:", error);
    }
  };

  useEffect(() => {
    setGroupMessages([]);
    if (activeGroup && privateKeyPem) {
      fetchGroupMessages();
    }
  }, [activeGroup, privateKeyPem]);

  useEffect(() => {
    if (activeGroup && privateKeyPem) {
      console.log("🔁 Cambio de grupo detectado:", activeGroup.nombre_de_grupo);
      fetchGroupMessages();
    }
  }, [activeGroup, privateKeyPem]);

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
    setMessages([]);
  }, [activeUser]);

  const handleSendGroupMessage = async () => {
    if (!message.trim() || !activeGroup || !privateKeyPem) return;

    try {
      const response = await fetch(
        `http://localhost:8000/grupos/group/message/${activeGroup.id_pk}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            mensaje: message,
            clave_privada_usuario_pem: privateKeyPem,
          }),
        }
      );

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Error al enviar mensaje grupal: ${errText}`);
      }

      // Añadir el mensaje nuevo al chat de grupo
      setGroupMessages((prev) => [
        ...prev,
        {
          text: message,
          type: "sent",
        },
      ]);

      setMessage("");
    } catch (error) {
      console.error("Error enviando mensaje grupal:", error);
      alert(error.message);
    }
  };

  useEffect(() => {
    const getAllMessages = async () => {
      if (!activeUser || !privateKeyPem) return;

      try {
        // 1. Fetch recibidos
        const resReceived = await fetch(
          `http://localhost:8000/msg/message/received/${activeUser.correo}`,
          {
            headers: { Authorization: `Bearer ${accessToken}` },
          }
        );
        if (!resReceived.ok)
          throw new Error("Error al obtener mensajes recibidos");
        const receivedData = await resReceived.json();

        const mensajesRecibidos = await Promise.all(
          receivedData.map(async (msg) => {
            try {
              const contenido = JSON.parse(msg.message);
              const clave = JSON.parse(msg.clave_aes_cifrada);
              const textoPlano = await Decrypt.descifrarTodo(
                clave,
                contenido,
                privateKeyPem
              );
              return {
                text: textoPlano,
                type: "received",
                timestamp: msg.timestamp,
              };
            } catch (e) {
              console.error("Error descifrando recibido:", e);
              return null;
            }
          })
        );

        // 2. Fetch enviados
        const resSent = await fetch(
          `http://localhost:8000/msg/message/sent/${activeUser.correo}`,
          {
            headers: { Authorization: `Bearer ${accessToken}` },
          }
        );
        if (!resSent.ok) throw new Error("Error al obtener mensajes enviados");
        const sentData = await resSent.json();

        const mensajesEnviados = sentData.map((msg) => ({
          text: msg.message,
          type: "sent",
          timestamp: msg.timestamp,
        }));

        // 3. Combinar, filtrar nulos y ordenar
        const todos = [
          ...mensajesRecibidos.filter(Boolean),
          ...mensajesEnviados,
        ];
        todos.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

        // 4. Guardar
        setMessages(todos);
      } catch (error) {
        console.error("Error obteniendo mensajes:", error);
      }
    };

    // Limpiar mensajes antes de cargar nuevos al cambiar de usuario
    setMessages([]);
    getAllMessages();
  }, [activeUser, accessToken, privateKeyPem]);

  const filteredUsers = users.filter((user) =>
    `${user.nombre} ${user.correo}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const fetchGrupos = async () => {
      try {
        const response = await fetch("http://localhost:8000/grupos/getGroups", {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        if (!response.ok) {
          throw new Error("Error al obtener los grupos");
        }
        const data = await response.json();
        console.log("Grupos obtenidos:", data);
        setGrupos(data);
      } catch (error) {
        console.error("Error fetching grupos:", error);
      }
    };

    fetchGrupos();
  }, [accessToken]);

  return (
    <Box
      sx={{
        height: "80vh",
        width: "165vh",
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
          {(tab === 0 ? filteredUsers : grupos).map((item, i) => (
            <Box
              key={i}
              sx={{
                display: "flex",
                alignItems: "center",
                mb: 2,
                gap: 1,
                justifyContent: "space-between",
                cursor: "pointer",
                backgroundColor:
                  tab === 0 && activeUser?.id_pk === item.id_pk
                    ? "#2a2a2a"
                    : "transparent",
                borderRadius: 1,
                px: 1,
                py: 0.5,
                "&:hover": { backgroundColor: "#333" },
              }}
            >
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1 }}
                onClick={() => {
                  if (tab === 0) {
                    setActiveUser(item);
                    setActiveGroup(null); // asegurarte de limpiar el grupo
                  } else {
                    setActiveGroup(item); // <- aquí está el cambio principal
                    setActiveUser(null); // opcional: limpiar usuario si se va a grupo
                  }
                }}
              >
                <Avatar alt={tab === 0 ? item.nombre : item.nombre_de_grupo} />
                <Box sx={{ display: "flex", flexDirection: "column" }}>
                  <Typography variant="body1" fontWeight="bold">
                    {tab === 0 ? item.nombre : item.nombre_de_grupo}
                  </Typography>
                  <Typography variant="subtitle2">
                    {tab === 0 ? item.correo : `Cifrado: ${item.tipo_cifrado}`}
                  </Typography>
                </Box>
              </Box>

              {tab === 1 && (
                <Button
                  variant="outlined"
                  size="small"
                  sx={{
                    color: "#fff",
                    borderColor: "#aaa",
                    fontSize: "0.7rem",
                    textTransform: "none",
                    "&:hover": { borderColor: "#fff" },
                  }}
                  onClick={() => handleOpenGroupDetails(item.id_pk)}
                >
                  Ver miembros
                </Button>
              )}
            </Box>
          ))}
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
            {activeUser
              ? activeUser.nombre
              : activeGroup
              ? activeGroup.nombre_de_grupo
              : "Selecciona un usuario o grupo"}
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
          {mensajesVisibles.length === 0 ? (
            <Typography color="#888" textAlign="center">
              No hay mensajes aún
            </Typography>
          ) : (
            mensajesVisibles.map((msg, i) => (
              <Box
                key={i}
                sx={{
                  display: "flex",
                  justifyContent:
                    msg.type === "received" ? "flex-start" : "flex-end",
                }}
              >
                <Paper
                  sx={{
                    p: 1.5,
                    backgroundColor:
                      msg.type === "received" ? "#E0E0E0" : "#C3C3C3",
                    color: "#000",
                    borderRadius: 4,
                    maxWidth: "70%",
                  }}
                >
                  {msg.text}
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
            onChange={(e) => {
              const nuevoTexto = e.target.value;
              if (nuevoTexto === message) return; // Evita doble render innecesario
              setMessage(nuevoTexto);
            }}
            InputProps={{
              style: {
                backgroundColor: "#fff",
                borderRadius: 10,
              },
            }}
          />
          <Button
            variant="contained"
            onClick={activeGroup ? handleSendGroupMessage : handleSend}
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

      {/* Modal para ver miembros del grupo */}
      <Dialog
        open={openMembersModal}
        onClose={() => setOpenMembersModal(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ backgroundColor: "#1F1F1F", color: "#fff" }}>
          Miembros del grupo
        </DialogTitle>
        <DialogContent sx={{ backgroundColor: "#2C2C2C" }}>
          {miembrosGrupo.length === 0 ? (
            <Typography color="#aaa">
              Este grupo no tiene miembros aún.
            </Typography>
          ) : (
            miembrosGrupo.map((miembro, index) => (
              <Box
                key={index}
                sx={{
                  mb: 1,
                  p: 1,
                  borderBottom: "1px solid #444",
                  color: "#fff",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Box>
                  <Typography fontWeight="bold">{miembro.nombre}</Typography>
                  <Typography variant="body2">{miembro.correo}</Typography>
                </Box>
                <Button
                  onClick={() =>
                    handleDeleteMember(miembro.id_pk, miembro.nombre)
                  }
                  sx={{
                    minWidth: "30px",
                    color: "#f44336",
                    borderColor: "#f44336",
                    fontSize: "1.2rem",
                    "&:hover": { backgroundColor: "#440000" },
                  }}
                >
                  🗑️
                </Button>
              </Box>
            ))
          )}
        </DialogContent>
        <DialogActions sx={{ backgroundColor: "#2C2C2C", p: 2 }}>
          <Button
            onClick={() => setOpenMembersModal(false)}
            sx={{ color: "#ccc", textTransform: "none" }}
          >
            Cerrar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ChatPage;
