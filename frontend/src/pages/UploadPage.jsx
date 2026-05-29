import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { getDataSources, uploadFile, normalizeBatch, validateBatch } from "../api/ingestion";
import { Upload, CheckCircle, AlertCircle, Loader } from "lucide-react";

export default function UploadPage() {
  const { orgId } = useAuth();
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState("");
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState("idle"); // idle | uploading | normalizing | validating | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDataSources(orgId).then((res) => setSources(res.data));
  }, [orgId]);

  const handleUpload = async () => {
    if (!selectedSource || !file) return;
    setStep("uploading");
    setError("");
    setResult(null);

    try {
      const uploadRes = await uploadFile(selectedSource, file, setProgress);
      const batch = uploadRes.data;

      setStep("normalizing");
      const normRes = await normalizeBatch(batch.id);

      setStep("validating");
      const valRes = await validateBatch(batch.id);

      setResult({
        batch,
        normalized: normRes.data,
        validation: valRes.data,
      });
      setStep("done");
    } catch (err) {
      setError(err.response?.data?.error || "Upload failed");
      setStep("error");
    }
  };

  const reset = () => {
    setStep("idle");
    setFile(null);
    setProgress(0);
    setResult(null);
    setError("");
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Upload ESG Data</h1>
        <p className="text-gray-500 mt-1">
          Upload SAP CSV, utility CSV, or travel JSON. Data will be ingested, normalized, and validated automatically.
        </p>
      </div>

      {step === "idle" || step === "error" ? (
        <div className="card p-6 space-y-5">
          {/* Source selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Source
            </label>
            <select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm 
                         focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Select a data source...</option>
              {sources.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.source_type})
                </option>
              ))}
            </select>
          </div>

          {/* File drop zone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              File
            </label>
            <label className="flex flex-col items-center justify-center w-full h-40 
                              border-2 border-dashed border-gray-300 rounded-lg cursor-pointer
                              hover:bg-gray-50 transition-colors">
              <Upload className="w-8 h-8 text-gray-400 mb-2" />
              {file ? (
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-700">{file.name}</p>
                  <p className="text-xs text-gray-400">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              ) : (
                <div className="text-center">
                  <p className="text-sm text-gray-600">
                    Click to select or drag & drop
                  </p>
                  <p className="text-xs text-gray-400 mt-1">.csv or .json files</p>
                </div>
              )}
              <input
                type="file"
                className="hidden"
                accept=".csv,.json"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </label>
          </div>

          {error && (
            <div className="flex items-center gap-2 bg-red-50 text-red-700 p-3 rounded-lg text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!selectedSource || !file}
            className="btn-primary w-full py-2.5"
          >
            Upload & Process
          </button>
        </div>
      ) : step === "done" ? (
        <div className="card p-6 space-y-4">
          <div className="flex items-center gap-3 text-esg-green">
            <CheckCircle className="w-6 h-6" />
            <h2 className="text-lg font-semibold">Processing Complete</h2>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-gray-900">{result.batch.total_rows}</p>
              <p className="text-xs text-gray-500 mt-1">Rows Ingested</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-esg-green">{result.normalized.normalized}</p>
              <p className="text-xs text-gray-500 mt-1">Normalized</p>
            </div>
            <div className="bg-amber-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-esg-amber">{result.validation.flags_raised}</p>
              <p className="text-xs text-gray-500 mt-1">Flags Raised</p>
            </div>
          </div>

          {result.normalized.failed > 0 && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm">
              {result.normalized.failed} rows failed normalization
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={reset} className="btn-secondary flex-1">
              Upload Another
            </button>
            <a href="/records" className="btn-primary flex-1 text-center">
              View Records
            </a>
          </div>
        </div>
      ) : (
        /* Processing state */
        <div className="card p-8 text-center">
          <Loader className="w-10 h-10 text-primary-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-700 font-medium">
            {step === "uploading" && `Uploading... ${progress}%`}
            {step === "normalizing" && "Normalizing records..."}
            {step === "validating" && "Running validation rules..."}
          </p>
          <div className="w-full bg-gray-100 rounded-full h-2 mt-4">
            <div
              className="bg-primary-500 h-2 rounded-full transition-all"
              style={{
                width: step === "uploading"
                  ? `${progress}%`
                  : step === "normalizing"
                  ? "66%"
                  : "90%",
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}