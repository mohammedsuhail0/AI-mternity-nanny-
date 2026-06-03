"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { Activity } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api.post("/auth/register", form);
      const { access_token, refresh_token } = res.data;
      await login(access_token, refresh_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      const errorData = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(errorData || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.12),_transparent_36%),linear-gradient(180deg,_#fff,_#f8fafc)] px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-screen w-full max-w-md items-center">
        <div className="w-full">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Activity className="h-8 w-8 text-primary-600" />
          <h1 className="text-2xl font-bold text-gray-900">
            Maternal<span className="text-primary-600">Monitor</span>
          </h1>
        </div>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Request clinical access</h2>
            <p className="text-sm text-gray-500">
              Create a new account for hospital staff
            </p>
          </CardHeader>

          <CardBody>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Full Name"
                name="full_name"
                type="text"
                placeholder="Dr. Jane Smith"
                value={form.full_name}
                onChange={handleChange}
                required
              />

              <Input
                label="Email Address"
                name="email"
                type="email"
                placeholder="clinician@hospital.org"
                value={form.email}
                onChange={handleChange}
                required
              />

              <Input
                label="Password"
                name="password"
                type="password"
                placeholder="Min. 8 characters"
                value={form.password}
                onChange={handleChange}
                required
              />

              {error && (
                <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
                  {error}
                </div>
              )}

              <Button type="submit" className="w-full" loading={loading}>
                Submit request
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-gray-600">
              Already have an account?{" "}
              <Link
                href="/auth/login"
                className="font-semibold text-primary-600 hover:text-primary-700"
              >
                Sign in
              </Link>
            </div>
          </CardBody>
        </Card>
      </div>
      </div>
    </div>
  );
}
