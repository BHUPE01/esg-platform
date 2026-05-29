import client from "./client";

export const login = async (username, password) => {
  const res = await client.post("/auth/token/", { username, password });
  localStorage.setItem("access_token", res.data.access);
  localStorage.setItem("refresh_token", res.data.refresh);
  return res.data;
};

export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

export const getCurrentUser = () => client.get("/core/me/");