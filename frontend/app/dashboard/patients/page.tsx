"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

type PatientSummary = {
  id: string;
  full_name: string;
  email: string;
  date_of_birth: string;
  medical_record_number: string;
  gestational_age_weeks: number | null;
  pregnancy_status: string | null;
  latest_fetal_heart_rate_bpm: number | null;
  latest_risk_category: string | null;
  latest_recommendation: string | null;
};

function getAge(dateOfBirth: string) {
  const birthDate = new Date(dateOfBirth);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDelta = today.getMonth() - birthDate.getMonth();
  if (monthDelta < 0 || (monthDelta === 0 && today.getDate() < birthDate.getDate())) {
    age -= 1;
  }
  return age;
}

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

export default function PatientsPage() {
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadPatients() {
      try {
        const res = await api.get("/patients");
        if (active) {
          setPatients(res.data);
        }
      } catch {
        if (active) {
          setError("Unable to load patient records.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadPatients();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-6 pb-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 sm:text-3xl">Patients</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 sm:text-base">
          Create and review maternal patient profiles.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Live Patient List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800">
                  <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Patient</th>
                  <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Age</th>
                  <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">MRN</th>
                  <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Week</th>
                  <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Risk</th>
                  <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">FHR</th>
                  <th className="pb-2 text-left font-medium text-slate-500 dark:text-slate-400">Status</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td className="py-4 text-slate-500" colSpan={7}>
                      Loading live patient records...
                    </td>
                  </tr>
                ) : patients.length ? (
                  patients.map((patient) => (
                    <tr key={patient.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                      <td className="py-3">
                        <div>
                          <p className="font-medium text-slate-900 dark:text-slate-100">{patient.full_name}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">{patient.email}</p>
                        </div>
                      </td>
                      <td className="py-3 text-slate-700 dark:text-slate-300">{getAge(patient.date_of_birth)}</td>
                      <td className="py-3 text-slate-700 dark:text-slate-300">{patient.medical_record_number}</td>
                      <td className="py-3 text-slate-700 dark:text-slate-300">{patient.gestational_age_weeks ?? "-"}</td>
                      <td className="py-3">
                        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${riskBadge(patient.latest_risk_category)}`}>
                          {patient.latest_risk_category ?? "low"}
                        </span>
                      </td>
                      <td className="py-3 text-slate-700 dark:text-slate-300">{patient.latest_fetal_heart_rate_bpm ?? "-"}</td>
                      <td className="py-3 text-slate-700 dark:text-slate-300">
                        {patient.latest_recommendation || patient.pregnancy_status || "Active"}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="py-4 text-slate-500" colSpan={7}>
                      No patient records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}