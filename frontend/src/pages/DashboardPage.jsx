import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { getDashboard } from "../api/records";
import {
  Database, CheckCircle, AlertTriangle, XCircle,
  Flag, Upload, TrendingUp
} from "lucide-react";

function StatCard({ label, value, icon: Icon, color = "blue", subtitle }) {
  const colors = {
    blue: "bg-primary-50 text-primary-600",
    green: "bg-green-50 text-esg-green",
    amber: "bg-amber-50 text-esg-amber",
    red: "bg-red-50 text-esg-red",
    purple: "bg-purple-50 text-purple-600",
  };

  return (
    <div className="card p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{label}</p>
          <p className="text-3xl font-bold text-gray-900">{value ?? "—"}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-2.5 rounded-lg ${colors[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}

const SOURCE_LABELS = {
  sap_csv: "SAP CSV",
  utility_csv: "Utility",
  travel_api: "Travel API",
};

export default function DashboardPage() {
  const { orgId } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard(orgId)
      .then((res) => setData(res.data))
      .finally(() => setLoading(false));
  }, [orgId]);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <div className="text-gray-400">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">ESG Data Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of all ingested, normalized, and reviewed records</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total Raw Records"
          value={data?.total_raw_records}
          icon={Database}
          color="blue"
          subtitle={`${data?.total_upload_batches} upload batches`}
        />
        <StatCard
          label="Approved"
          value={data?.approved}
          icon={CheckCircle}
          color="green"
        />
        <StatCard
          label="Pending Review"
          value={data?.pending_review}
          icon={TrendingUp}
          color="amber"
        />
        <StatCard
          label="Flagged Records"
          value={data?.flagged}
          icon={Flag}
          color="amber"
          subtitle={`${data?.open_flags} open flags`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Source breakdown */}
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Records by Source</h2>
          <div className="space-y-3">
            {data?.source_breakdown?.map((s) => (
              <div key={s.source_type} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  {SOURCE_LABELS[s.source_type] || s.source_type}
                </span>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-primary-500 h-2 rounded-full"
                      style={{
                        width: `${Math.min(
                          100,
                          (s.count / (data?.total_normalized_records || 1)) * 100
                        )}%`,
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-8 text-right">
                    {s.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent batches */}
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Recent Uploads</h2>
          <div className="space-y-3">
            {data?.recent_batches?.map((b) => (
              <div key={b.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-800">{b.source}</p>
                  <p className="text-xs text-gray-400">
                    {new Date(b.created_at).toLocaleDateString()} · {b.total_rows} rows
                  </p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  b.status === "completed"
                    ? "bg-green-100 text-green-700"
                    : b.status === "failed"
                    ? "bg-red-100 text-red-700"
                    : "bg-yellow-100 text-yellow-700"
                }`}>
                  {b.status}
                </span>
              </div>
            ))}
            {!data?.recent_batches?.length && (
              <p className="text-sm text-gray-400">No uploads yet</p>
            )}
          </div>
        </div>

        {/* Review summary */}
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Review Status Breakdown</h2>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Approved", value: data?.approved, color: "text-esg-green", bg: "bg-green-50" },
              { label: "Pending", value: data?.pending_review, color: "text-esg-amber", bg: "bg-amber-50" },
              { label: "Flagged", value: data?.flagged, color: "text-orange-600", bg: "bg-orange-50" },
              { label: "Rejected", value: data?.rejected, color: "text-esg-red", bg: "bg-red-50" },
            ].map(({ label, value, color, bg }) => (
              <div key={label} className={`${bg} rounded-lg p-4 text-center`}>
                <p className={`text-2xl font-bold ${color}`}>{value ?? 0}</p>
                <p className="text-xs text-gray-500 mt-1">{label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Open flags summary */}
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Validation Alerts</h2>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
              <XCircle className="w-5 h-5 text-esg-red" />
              <div>
                <p className="text-sm font-medium text-gray-900">{data?.error_flags} Error Flags</p>
                <p className="text-xs text-gray-500">Require immediate attention</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-amber-50 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-esg-amber" />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {(data?.open_flags || 0) - (data?.error_flags || 0)} Warning Flags
                </p>
                <p className="text-xs text-gray-500">Pending analyst review</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}