"use client";

import { useEffect, useState } from "react";
import { Activity, Heart, Users, AlertTriangle } from "lucide-react";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

type PatientSummary = {
  id: string;
  full_name: string;
  email: string;
  gestational_age_weeks: number | null;
  pregnancy_status: string | null;
  latest_fetal_heart_rate_bpm: number | null;
  latest_risk_category: string | null;
  latest_recommendation: string | null;
};

type DashboardAlert = {
  patient_name: string;
  level: "info" | "warning" | "critical";
  message: string;
  triggered_at: string;
};

type DashboardOverview = {
  total_patients: number;
  active_patients: number;
  monitoring_patients: number;
  high_risk_patients: number;
  avg_fetal_heart_rate: number | null;
  alerts_count: number;
  recent_patients: PatientSummary[];
  alerts: DashboardAlert[];
};

function riskBadge(risk: string | null) {
  switch (risk) {
    case "high":
    case "critical":
      return "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
    case "medium":
      return "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400";
    default:
      return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
  }
}

function formatNumber(value: number | null) {
  return value == null ? "-" : value.toString();
}

export default function DashboardPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadOverview() {
      try {
        const res = await api.get("/dashboard/overview");
        if (active) {
          setOverview(res.data);
        }
      } catch {
        if (active) {
          setError("Unable to load dashboard data.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadOverview();

    return () => {
      active = false;
    };
  }, []);

  const stats = overview
    ? [
        {
          title: "Active Patients",
          value: overview.total_patients.toString(),
          icon: Users,
          change: `${overview.high_risk_patients} high risk`,
          color: "text-blue-600",
          bgColor: "bg-blue-50 dark:bg-blue-950/50",
        },
        {
          title: "Monitoring",
          value: overview.monitoring_patients.toString(),
          icon: Activity,
          change: `${overview.active_patients} active pregnancies`,
          color: "text-green-600",
          bgColor: "bg-green-50 dark:bg-green-950/50",
        },
        {
          title: "Avg FHR (bpm)",
          value: formatNumber(overview.avg_fetal_heart_rate),
          icon: Heart,
          change: "Live from seeded data",
          color: "text-pink-600",
          bgColor: "bg-pink-50 dark:bg-pink-950/50",
        },
        {
          title: "Alerts",
          value: overview.alerts_count.toString(),
          icon: AlertTriangle,
          change: "Requires review",
          color: "text-amber-600",
          bgColor: "bg-amber-50 dark:bg-amber-950/50",
        },
      ]
    : [];

  return (
    <div className="space-y-6 pb-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 sm:text-3xl">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 sm:text-base">
          Maternal and fetal monitoring overview
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {loading
          ? Array.from({ length: 4 }).map((_, index) => (
              <Card key={index} className="h-full animate-pulse">
                <CardContent className="p-4 sm:p-5">
                  <div className="h-4 w-24 rounded bg-slate-200 dark:bg-slate-800" />
                  <div className="mt-4 h-8 w-14 rounded bg-slate-200 dark:bg-slate-800" />
                  <div className="mt-2 h-3 w-32 rounded bg-slate-200 dark:bg-slate-800" />
                </CardContent>
              </Card>
            ))
          : stats.map((stat) => {
              const Icon = stat.icon;
              return (
                <Card key={stat.title} className="h-full">
                  <CardContent className="p-4 sm:p-5">
                    <div className="flex items-start justify-between gap-3">
                      <div className={`rounded-xl p-2.5 ${stat.bgColor}`}>
                        <Icon className={`h-5 w-5 ${stat.color}`} />
                      </div>
                      <span className="text-xs font-medium text-slate-500 dark:text-slate-400">
                        {stat.change}
                      </span>
                    </div>
                    <div className="mt-4">
                      <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                        {stat.value}
                      </p>
                      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                        {stat.title}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Recent Patients</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[620px] text-sm">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800">
                    <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Patient</th>
                    <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Week</th>
                    <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">FHR</th>
                    <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Risk</th>
                    <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td className="py-4 text-slate-500" colSpan={5}>
                        Loading live patient data...
                      </td>
                    </tr>
                  ) : (
                    overview?.recent_patients.map((patient) => (
                      <tr key={patient.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                        <td className="py-3">
                          <div>
                            <p className="font-medium text-slate-900 dark:text-slate-100">{patient.full_name}</p>
                            <p className="text-xs text-slate-500 dark:text-slate-400">{patient.email}</p>
                          </div>
                        </td>
                        <td className="py-3 text-slate-700 dark:text-slate-300">{patient.gestational_age_weeks ?? "-"}</td>
                        <td className="py-3 text-slate-700 dark:text-slate-300">{formatNumber(patient.latest_fetal_heart_rate_bpm)}</td>
                        <td className="py-3">
                          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${riskBadge(patient.latest_risk_category)}`}>
                            {patient.latest_risk_category ?? "low"}
                          </span>
                        </td>
                        <td className="py-3 text-slate-700 dark:text-slate-300">
                          {patient.latest_recommendation || patient.pregnancy_status || "Active"}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Risk Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {loading ? (
                <p className="text-sm text-slate-500">Loading alerts...</p>
              ) : overview?.alerts.length ? (
                overview.alerts.map((alert) => (
                  <div
                    key={`${alert.patient_name}-${alert.triggered_at}`}
                    className={`rounded-xl border p-3 ${
                      alert.level === "critical"
                        ? "border-red-200 bg-red-50 dark:border-red-900/50 dark:bg-red-950/30"
                        : "border-amber-200 bg-amber-50 dark:border-amber-900/50 dark:bg-amber-950/30"
                    }`}
                  >
                    <p className={`text-sm font-medium ${alert.level === "critical" ? "text-red-800 dark:text-red-200" : "text-amber-800 dark:text-amber-200"}`}>
                      {alert.patient_name}
                    </p>
                    <p className={`mt-1 text-xs ${alert.level === "critical" ? "text-red-700 dark:text-red-300" : "text-amber-700 dark:text-amber-300"}`}>
                      {alert.message}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No active alerts right now.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}