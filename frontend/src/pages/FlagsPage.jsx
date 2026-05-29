import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { getFlags, resolveFlag } from "../api/records";
import { AlertTriangle, XCircle, CheckCircle } from "lucide-react";

export default function FlagsPage() {
  const { orgId } = useAuth();
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("open");

  const load = () => {
    setLoading(true);
    getFlags({ org: orgId, status: statusFilter || undefined })
      .then((res) => setFlags(res.data.results || res.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [orgId, statusFilter]);

  const handleResolve = async (id, status) => {
    const notes = status === "dismissed"
      ? prompt("Reason for dismissal?") || ""
      : "Resolved by analyst";
    await resolveFlag(id, status, notes);
    load();
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Validation Flags</h1>
          <p className="text-gray-500 mt-1">Suspicious records flagged by validation rules</p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="text-sm border border-gray-300 rounded-lg px-3 py-2"
        >
          <option value="open">Open</option>
          <option value="resolved">Resolved</option>
          <option value="dismissed">Dismissed</option>
          <option value="">All</option>
        </select>
      </div>

      <div className="space-y-3">
        {loading ? (
          <div className="card p-8 text-center text-gray-400 text-sm">Loading flags...</div>
        ) : flags.length === 0 ? (
          <div className="card p-8 text-center">
            <CheckCircle className="w-10 h-10 text-esg-green mx-auto mb-3" />
            <p className="text-gray-500">No {statusFilter} flags found</p>
          </div>
        ) : flags.map((flag) => (
          <div key={flag.id} className="card p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                {flag.severity === "error" ? (
                  <XCircle className="w-5 h-5 text-esg-red flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-esg-amber flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      flag.severity === "error"
                        ? "bg-red-100 text-red-700"
                        : "bg-amber-100 text-amber-700"
                    }`}>
                      {flag.severity}
                    </span>
                    <span className="text-xs text-gray-400">{flag.rule_name}</span>
                    <span className="text-xs text-gray-400">
                      · Record #{flag.normalized_record_id}
                    </span>
                  </div>
                  <p className="text-sm text-gray-800">{flag.message}</p>
                  {flag.field_name && (
                    <p className="text-xs text-gray-500 mt-1">
                      Field: <code className="bg-gray-100 px-1 rounded">{flag.field_name}</code>
                      {" = "}
                      <code className="bg-gray-100 px-1 rounded">{flag.field_value || "empty"}</code>
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(flag.created_at).toLocaleString()}
                  </p>
                </div>
              </div>

              {flag.status === "open" && (
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => handleResolve(flag.id, "resolved")}
                    className="text-xs bg-green-50 text-green-700 border border-green-200 
                               px-3 py-1.5 rounded-lg hover:bg-green-100"
                  >
                    Resolve
                  </button>
                  <button
                    onClick={() => handleResolve(flag.id, "dismissed")}
                    className="text-xs bg-gray-50 text-gray-600 border border-gray-200 
                               px-3 py-1.5 rounded-lg hover:bg-gray-100"
                  >
                    Dismiss
                  </button>
                </div>
              )}

              {flag.status !== "open" && (
                <span className="text-xs text-gray-400 capitalize">{flag.status}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}