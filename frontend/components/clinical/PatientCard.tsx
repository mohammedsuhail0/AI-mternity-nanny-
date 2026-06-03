"use client";

import { Card } from "@/components/ui/Card";
import { BadgeCheck, AlertTriangle, ChevronRight, Clock } from "lucide-react";

interface PatientCardProps {
  name: string;
  age: number;
  gestationalWeek: number;
  riskLevel: "low" | "moderate" | "high";
  lastVitalsTime: string;
  cSectionRisk?: number;
  onClick?: () => void;
}

const riskConfig = {
  low: {
    color: "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    icon: BadgeCheck,
    label: "Low Risk",
  },
  moderate: {
    color: "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    icon: AlertTriangle,
    label: "Moderate Risk",
  },
  high: {
    color: "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    icon: AlertTriangle,
    label: "High Risk",
  },
};

export function PatientCard({
  name,
  age,
  gestationalWeek,
  riskLevel,
  lastVitalsTime,
  cSectionRisk,
  onClick,
}: PatientCardProps) {
  const config = riskConfig[riskLevel];
  const Icon = config.icon;

  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-md ${onClick ? "hover:border-primary-200 dark:hover:border-primary-800" : ""}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              {name}
            </h3>
            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.color}`}>
              <Icon className="h-3 w-3" />
              {config.label}
            </span>
          </div>

          <div className="mt-2 flex gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span>Age: {age}</span>
            <span>{gestationalWeek} weeks</span>
          </div>

          <div className="mt-2 flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
            <Clock className="h-3 w-3" />
            Last vitals: {lastVitalsTime}
          </div>

          {cSectionRisk !== undefined && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500 dark:text-gray-400">
                  C-Section Risk
                </span>
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  {cSectionRisk}%
                </span>
              </div>
              <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                <div
                  className={`h-full rounded-full transition-all ${
                    cSectionRisk > 60
                      ? "bg-red-500"
                      : cSectionRisk > 35
                        ? "bg-amber-500"
                        : "bg-emerald-500"
                  }`}
                  style={{ width: `${cSectionRisk}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {onClick && (
          <ChevronRight className="h-5 w-5 text-gray-400" />
        )}
      </div>
    </Card>
  );
}
