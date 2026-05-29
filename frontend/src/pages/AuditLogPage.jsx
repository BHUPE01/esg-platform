import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { getAuditLogs } from "../api/records";
import { History } from "lucide-react";

const ACTION_COLORS = {
  approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  flagged: "bg-orange-100 text-orange-700",
  updated: "bg-blue-100 text-blue-700",
  ingested: "bg-purple-100 text-purple-700",
  normalized: "bg-gray-100 text-gray-700",
  created: "bg-teal-100 text-teal-700",
};

export default function AuditLogPage() {
  const { orgId } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    getAuditLogs({ org: orgId })
      .then((res) => setLogs(res.data.results || res.data))
      .finally(() => setLoading(false));
  }, [orgId]);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
        <p className="text-gray-500 mt-1">
          Immutable record of all changes — approvals, rejections, edits, ingestions
        </p>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                {["Timestamp", "Action", "Entity", "Changed By", "Notes", "Diff"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-400 text-sm">
                    Loading audit log...
                  </td>
                </tr>
              ) : logs.map((log) => (
                <>
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium px-2 py-1 rounded-full ${ACTION_COLORS[log.action] || "bg-gray-100 text-gray-600"}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {log.entity_type} #{log.entity_id}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {log.changed_by?.username || "system"}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">
                      {log.notes || "—"}
                    </td>
                    <td className="px-4 py-3">
                      {(log.old_value || log.new_value) && (
                        <button
                          className="text-xs text-primary-600 hover:underline"
                          onClick={() => setExpanded(expanded === log.id ? null : log.id)}
                        >
                          {expanded === log.id ? "Hide" : "View diff"}
                        </button>
                      )}
                    </td>
                  </tr>
                  {expanded === log.id && (
                    <tr key={`${log.id}-diff`}>
                      <td colSpan={6} className="px-4 pb-4">
                        <div className="grid grid-cols-2 gap-4 bg-gray-50 rounded-lg p-4">
                          <div>
                            <p className="text-xs font-semibold text-gray-400 mb-2">BEFORE</p>
                            <pre className="text-xs bg-white border border-gray-200 rounded p-3 overflow-auto max-h-40">
                              {JSON.stringify(log.old_value, null, 2) || "null"}
                            </pre>
                          </div>
                          <div>
                            <p className="text-xs font-semibold text-gray-400 mb-2">AFTER</p>
                            <pre className="text-xs bg-white border border-gray-200 rounded p-3 overflow-auto max-h-40">
                              {JSON.stringify(log.new_value, null, 2) || "null"}
                            </pre>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}