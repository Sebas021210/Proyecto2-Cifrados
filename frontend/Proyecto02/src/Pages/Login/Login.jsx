import LoginForm from "../../Components/LoginForm/LoginForm.jsx";

function Login() {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh", // Altura completa de la ventana
      }}
    >
      <LoginForm />
    </div>
  );
}

export default Login;
