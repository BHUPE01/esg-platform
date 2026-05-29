import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { getNormalizedRecords, approveRecord, rejectRecord } from "../api/records";
import { CheckCircle, XCircle, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

const STATUS_BADGE = {
  pending: <span className="badge-pending">Pending</span>,
  approved: <span className="badge-approved">Approved</span>,
  rejected: <span className="badge-rejected">Rejected</span>,
  flagged: <span className="badge-flagged">Flagged</span>,
};

const SOURCE_LABEL = {
  sap_csv: "SAP",
  utility_csv: "Utility",
  travel_api: "Travel",
};

function RecordRow({ record, onAction }) {
  const [expanded, setExpanded] = useState(false);
  const [notes, setNotes] = useState("");
  const [acting, setActing] = useState(false);

  const handleApprove = async () => {
    setActing(true);
    try {
      await approveRecord(record.id, notes);
      onAction();
    } finally {
      setActing(false);
    }
  };

  const handleReject = async () => {
    if (!notes) { alert("Please enter rejection notes"); return; }
    setActing(true);
    try {
      await rejectRecord(record.id, notes);
      onAction();
    } finally {
      setActing(false);
    }
  };

  return (
    <>
      <tr
        className="hover:bg-gray-50 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <td className="px-4 py-3 text-sm text-gray-500">#{record.id}</td>
        <td className="px-4 py-3">
          <span className="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-1 rounded">
            {SOURCE_LABEL[record.source_type] || record.source_type}
          </span>
        </td>
        <td className="px-4 py-3 text-sm text-gray-700">
          {record.site_code || record.traveler || "—"}
        </td>
        <td className="px-4 py-3 text-sm text-gray-700">
          {record.quantity
            ? `${parseFloat(record.quantity_normalized).toLocaleString()} ${record.unit_normalized}`
            : record.hotel_nights != null
            ? `${record.hotel_nights} nights`
            : "—"}
        </td>
        <td className="px-4 py-3 text-sm text-gray-500">
          {record.record_date || "—"}
        </td>
        <td className="px-4 py-3">{STATUS_BADGE[record.review_status]}</td>
        <td className="px-4 py-3">
          {record.normalization_warnings?.length > 0 && (
            <span className="text-xs text-amber-600">
              ⚠ {record.normalization_warnings.length} warnings
            </span>
          )}
        </td>
        <td className="px-4 py-3 text-gray-400">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </td>
      </tr>

      {expanded && (
        <tr>
          <td colSpan={8} className="px-4 pb-4">
            <div className="bg-gray-50 rounded-lg p-4 space-y-4">
              {/* Raw data */}
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Raw Data (original)</p>
                <pre className="text-xs bg-white border border-gray-200 rounded p-3 overflow-auto max-h-40">
                  {JSON.stringify(record.raw_data, null, 2)}
                </pre>
              </div>

              {/* Warnings */}
              {record.normalization_warnings?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Warnings</p>
                  {record.normalization_warnings.map((w, i) => (
                    <div key={i} className="text-xs text-amber-700 bg-amber-50 px-3 py-1.5 rounded mb-1">
                      ⚠ {w}
                    </div>
                  ))}
                </div>
              )}

              {/* Review actions */}
              {record.review_status === "pending" || record.review_status === "flagged" ? (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Review</p>
                  <textarea
                    className="w-full text-sm border border-gray-300 rounded-lg p-2 mb-3 
                               focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Notes (required for rejection)..."
                    rows={2}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleApprove(); }}
                      disabled={acting}
                      className="flex items-center gap-1.5 bg-green-600 text-white text-sm px-4 py-2 
                                 rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Approve
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleReject(); }}
                      disabled={acting}
                      className="flex items-center gap-1.5 btn-danger text-sm"
                    >
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-500">
                  Reviewed by <strong>{record.reviewed_by || "—"}</strong> on{" "}
                  {record.reviewed_at ? new Date(record.reviewed_at).toLocaleString() : "—"}
                  {record.review_notes && (
                    <p className="mt-1 italic">"{record.review_notes}"</p>
                  )}
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export default function RecordsPage() {
  const { orgId } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [sourceFilter, setSourceFilter] = useState("");

  const load = () => {
    setLoading(true);
    getNormalizedRecords({
      org: orgId,
      review_status: statusFilter || undefined,
      source_type: sourceFilter || undefined,
    })
      .then((res) => setRecords(res.data.results || res.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [orgId, statusFilter, sourceFilter]);

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Normalized Records</h1>
          <p className="text-gray-500 mt-1">Review and approve ESG data records</p>
        </div>
        <div className="flex gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none 
                       focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="flagged">Flagged</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none 
                       focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All sources</option>
            <option value="sap_csv">SAP CSV</option>
            <option value="utility_csv">Utility</option>
            <option value="travel_api">Travel API</option>
          </select>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                {["ID", "Source", "Site / Traveler", "Quantity", "Date", "Status", "Warnings", ""].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-400 text-sm">
                    Loading records...
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-400 text-sm">
                    No records found. Upload some data first.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <RecordRow key={r.id} record={r} onAction={load} />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}