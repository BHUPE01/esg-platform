import client from "./client";

export const getDataSources = (orgId) =>
  client.get("/ingestion/data-sources/", { params: { org: orgId } });

export const getBatches = (orgId) =>
  client.get("/ingestion/batches/", { params: { org: orgId } });

export const uploadFile = (dataSouceId, file, onProgress) => {
  const formData = new FormData();
  formData.append("data_source_id", dataSouceId);
  formData.append("file", file);
  return client.post("/ingestion/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
    },
  });
};

export const normalizeBatch = (batchId) =>
  client.post("/normalization/normalize-batch/", { batch_id: batchId });

export const validateBatch = (batchId) =>
  client.post("/validation/validate-batch/", { batch_id: batchId });