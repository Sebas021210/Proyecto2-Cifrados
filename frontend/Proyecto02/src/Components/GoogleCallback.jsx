import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

function GoogleCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const token = searchParams.get("access_token");

    if (token) {
      localStorage.setItem("access_token", token);
      console.log(token);
      window.history.pushState(null, "", "/home");
      navigate("/home", { replace: true });
    } else {
      navigate("/", { replace: true });
    }
  }, []);

  return <div>Autenticando con Google...</div>;
}

export default GoogleCallback;
