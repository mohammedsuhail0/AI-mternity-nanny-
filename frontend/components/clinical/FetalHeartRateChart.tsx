"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Heart, AlertCircle } from "lucide-react";

interface DataPoint {
  time: string;
  value: number;
}

interface FetalHeartRateChartProps {
  data: DataPoint[];
  baseline: number;
  variability?: "minimal" | "moderate" | "marked";
  accelerations?: number;
  decelerations?: number;
  alert?: boolean;
}

const normalRange = { min: 110, max: 160 };

export function FetalHeartRateChart({
  data,
  baseline,
  variability = "moderate",
  accelerations = 0,
  decelerations = 0,
  alert = false,
}: FetalHeartRateChartProps) {
  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Heart className="h-5 w-5 text-rose-500" />
            Fetal Heart Rate
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="py-8 text-center text-sm text-gray-500">
            No data available
          </p>
        </CardContent>
      </Card>
    );
  }

  const width = 600;
  const height = 200;
  const padding = { top: 20, right: 20, bottom: 30, left: 40 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const yMin = 60;
  const yMax = 200;
  const yRange = yMax - yMin;

  const points = data.map((d, i) => ({
    x: padding.left + (i / (data.length - 1 || 1)) * chartWidth,
    y: padding.top + chartHeight - ((d.value - yMin) / yRange) * chartHeight,
    value: d.value,
    time: d.time,
  }));

  const pathD = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  const baselineY = padding.top + chartHeight - ((baseline - yMin) / yRange) * chartHeight;
  const normalMinY = padding.top + chartHeight - ((normalRange.min - yMin) / yRange) * chartHeight;
  const normalMaxY = padding.top + chartHeight - ((normalRange.max - yMin) / yRange) * chartHeight;

  const variabilityConfig = {
    minimal: { color: "text-amber-500", label: "Minimal" },
    moderate: { color: "text-emerald-500", label: "Moderate" },
    marked: { color: "text-blue-500", label: "Marked" },
  };

  return (
    <Card className={alert ? "border-red-200 dark:border-red-900" : ""}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Heart className="h-5 w-5 text-rose-500" />
            Fetal Heart Rate
          </CardTitle>

          {alert && (
            <div className="flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              <AlertCircle className="h-3 w-3" />
              Alert
            </div>
          )}
        </div>

        <div className="mt-2 flex gap-6 text-sm">
          <div>
            <span className="text-gray-500 dark:text-gray-400">Baseline: </span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {baseline} bpm
            </span>
          </div>

          <div>
            <span className="text-gray-500 dark:text-gray-400">Variability: </span>
            <span className={`font-medium ${variabilityConfig[variability].color}`}>
              {variabilityConfig[variability].label}
            </span>
          </div>

          <div>
            <span className="text-gray-500 dark:text-gray-400">Accelerations: </span>
            <span className="font-medium text-emerald-600 dark:text-emerald-400">
              {accelerations}
            </span>
          </div>

          <div>
            <span className="text-gray-500 dark:text-gray-400">Decelerations: </span>
            <span className={`font-medium ${decelerations > 0 ? "text-red-600 dark:text-red-400" : "text-gray-900 dark:text-gray-100"}`}>
              {decelerations}
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="w-full overflow-hidden">
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="h-auto w-full"
            preserveAspectRatio="none"
          >
            {/* Normal range background */}
            <rect
              x={padding.left}
              y={normalMaxY}
              width={chartWidth}
              height={normalMinY - normalMaxY}
              fill="currentColor"
              className="text-emerald-50 dark:text-emerald-900/20"
            />

            {/* Normal range labels */}
            <text
              x={width - padding.right + 5}
              y={normalMaxY + 4}
              className="fill-gray-400 text-xs"
              fontSize="10"
            >
              160
            </text>
            <text
              x={width - padding.right + 5}
              y={normalMinY + 4}
              className="fill-gray-400 text-xs"
              fontSize="10"
            >
              110
            </text>

            {/* Baseline dashed line */}
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={baselineY}
              y2={baselineY}
              stroke="currentColor"
              strokeDasharray="4 4"
              className="text-gray-300 dark:text-gray-600"
              strokeWidth="1"
            />

            {/* Y-axis gridlines */}
            {[80, 100, 120, 140, 160, 180].map((val) => {
              const y = padding.top + chartHeight - ((val - yMin) / yRange) * chartHeight;
              return (
                <g key={val}>
                  <line
                    x1={padding.left}
                    x2={width - padding.right}
                    y1={y}
                    y2={y}
                    stroke="currentColor"
                    className="text-gray-100 dark:text-gray-800"
                    strokeWidth="1"
                  />
                  <text
                    x={padding.left - 8}
                    y={y + 4}
                    textAnchor="end"
                    className="fill-gray-400"
                    fontSize="10"
                  >
                    {val}
                  </text>
                </g>
              );
            })}

            {/* X-axis labels */}
            {data
              .filter((_, i) => i % Math.max(1, Math.floor(data.length / 6)) === 0)
              .map((d, i) => {
                const idx = data.indexOf(d);
                const x = padding.left + (idx / (data.length - 1 || 1)) * chartWidth;
                return (
                  <text
                    key={i}
                    x={x}
                    y={height - 5}
                    textAnchor="middle"
                    className="fill-gray-400"
                    fontSize="10"
                  >
                    {d.time}
                  </text>
                );
              })}

            {/* Data line */}
            <path
              d={pathD}
              fill="none"
              stroke="currentColor"
              className="text-rose-500"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Data points */}
            {points.map((p, i) => (
              <circle
                key={i}
                cx={p.x}
                cy={p.y}
                r="3"
                fill="currentColor"
                className={
                  p.value < normalRange.min || p.value > normalRange.max
                    ? "text-red-500"
                    : "text-rose-500"
                }
              />
            ))}
          </svg>
        </div>
      </CardContent>
    </Card>
  );
}
