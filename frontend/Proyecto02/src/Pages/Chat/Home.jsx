import ChatPage from "../../Components/Chat/ChatPage";
import backgroundImage from "../../assets/LogIn.png"; // reemplaza con la ruta correcta

function Home() {
  return (
    <div
      style={{
        position: "relative",
        height: "100vh", // ⬅️ Altura controlada
        overflow: "hidden",
        backgroundColor: "#1F1F1F",
      }}
    >
      {/* Líneas diagonales estilo fondo */}
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1000 900"
        preserveAspectRatio="none"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          zIndex: 0,
          pointerEvents: "none",
        }}
      >
        <line
          x1="0"
          y1="0"
          x2="1000"
          y2="900"
          stroke="white"
          strokeWidth="0.5"
        />
        <line
          x1="0"
          y1="900"
          x2="1000"
          y2="0"
          stroke="white"
          strokeWidth="0.5"
        />
        <line
          x1="250"
          y1="0"
          x2="1250"
          y2="900"
          stroke="white"
          strokeWidth="0.3"
        />
        <line
          x1="-250"
          y1="0"
          x2="750"
          y2="900"
          stroke="white"
          strokeWidth="0.3"
        />
      </svg>

      {/* Imagen abstracta como fondo */}
      <img
        src={backgroundImage}
        alt="Fondo decorativo"
        style={{
          position: "absolute",
          bottom: 0,
          right: 0,
          width: "280px",
          opacity: 0.15,
          zIndex: 0,
        }}
      />

      {/* Contenido encima del fondo */}
      <div
        style={{
          position: "relative",
          height: "100%",
          zIndex: 1,
        }}
      >
        <ChatPage />
      </div>
    </div>
  );
}

export default Home;
