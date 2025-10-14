export default function useAuth(requiredRole) {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("rol");

  if (!token) {
    window.location.href = "/";
  }
  if (requiredRole && role !== requiredRole && role !== "admin") {
    window.location.href = "/no-autorizado";
  }

  return { role };
}
