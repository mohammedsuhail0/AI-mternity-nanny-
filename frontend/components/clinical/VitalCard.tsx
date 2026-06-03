"use client";

import { Card } from "@/components/ui/Card";
import { Heart, Activity, Thermometer, Droplets, TrendingUp, TrendingDown, Minus } from "lucide-react";

type VitalType = "heart_rate" | "blood_pressure" | "temperature" | "oxygen" | "contractions";

type Trend = "up" | "down" | "stable";

interface VitalCardProps {
  type: VitalType;
  value: string;
  unit: string;
  trend: Trend;
  timestamp: string;
  alert?: boolean;
}

const vitalConfig: Record<VitalType, { label: string; icon: typeof Heart; color: string }> = {
  heart_rate: {
    label: "Heart Rate",
    icon: Heart,
    color: "text-rose-500",
  },
  blood_pressure: {
    label: "Blood Pressure",
    icon: Activity,
    color: "text-blue-500",
  },
  temperature: {
    label: "Temperature",
    icon: Thermometer,
    color: "text-amber-500",
  },
  oxygen: {
    label: "SpO2",
    icon: Droplets,
    color: "text-cyan-500",
  },
  contractions: {
    label: "Contractions",
    icon: Activity,
    color: "text-purple-500",
  },
};

const trendIcons: Record<Trend, typeof TrendingUp> = {
  up: TrendingUp,
  down: TrendingDown,
  stable: Minus,
};

const trendColors: Record<Trend, string> = {
  up: "text-red-500",
  down: "text-emerald-500",
  stable: "text-gray-400",
};

export function VitalCard({ type, value, unit, trend, timestamp, alert }: VitalCardProps) {
  const config = vitalConfig[type];
  const Icon = config.icon;
  const TrendIcon = trendIcons[trend];

  return (
    <Card className={alert ? "border-red-200 bg-red-50/50 dark:border-red-900/50 dark:bg-red-950/20" : ""}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`rounded-lg bg-gray-50 p-2 dark:bg-gray-800`}>
            <Icon className={`h-5 w-5 ${config.color}`} />
          </div>

          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {config.label}
            </p>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                {value}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {unit}
              </span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className={`flex items-center gap-1 ${trendColors[trend]}`}>
            <TrendIcon className="h-4 w-4" />
            <span className="text-xs font-medium capitalize">{trend}</span>
          </div>
          <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
            {timestamp}
          </p>
        </div>
      </div>
    </Card>
  );
}
