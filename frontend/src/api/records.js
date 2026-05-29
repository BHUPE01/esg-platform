import client from "./client";

export const getNormalizedRecords = (params) =>
  client.get("/normalization/records/", { params });

export const getRecord = (id) =>
  client.get(`/normalization/records/${id}/`);

export const approveRecord = (id, notes) =>
  client.post(`/review/records/${id}/approve/`, { notes });

export const rejectRecord = (id, notes) =>
  client.post(`/review/records/${id}/reject/`, { notes });

export const editRecord = (id, data) =>
  client.patch(`/review/records/${id}/edit/`, data);

export const getReviewQueue = (orgId) =>
  client.get("/review/queue/", { params: { org: orgId } });

export const getAuditLogs = (params) =>
  client.get("/core/audit-logs/", { params });

export const getDashboard = (orgId) =>
  client.get("/core/dashboard/", { params: { org: orgId } });

export const getFlags = (params) =>
  client.get("/validation/flags/", { params });

export const resolveFlag = (id, status, notes) =>
  client.post(`/validation/flags/${id}/resolve/`, { status, resolution_notes: notes });