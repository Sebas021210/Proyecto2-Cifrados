import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

function GoogleCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const token = searchParams.get("access_token");
    const email = searchParams.get("email");
    const privateKey = searchParams.get("private_key");

    if (token) {
      localStorage.setItem("access_token", token);
      console.log("Token guardado:", token);

      // Si viene la clave privada, descargamos
      if (privateKey && email) {
        const blob = new Blob([privateKey], { type: "application/x-pem-file" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${email.split("@")[0]}_clave_privada.pem`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }

      // Redirigir al home
      window.history.pushState(null, "", "/home");
      navigate("/home", { replace: true });
    } else {
      navigate("/", { replace: true });
    }
  }, []);

  return <div>Autenticando con Google...</div>;
}

export default GoogleCallback;
