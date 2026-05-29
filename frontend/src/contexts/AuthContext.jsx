import { createContext, useContext, useState, useEffect } from "react";
import { getCurrentUser, login as apiLogin, logout as apiLogout } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  // For demo, hardcode org=1. In production, user picks from their memberships.
  const [orgId] = useState(1);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      getCurrentUser()
        .then((res) => setUser(res.data))
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    await apiLogin(username, password);
    const res = await getCurrentUser();
    setUser(res.data);
  };

  const logout = () => {
    apiLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, orgId }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);