"use client";

import React, { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { create } from "zustand";
import { toast } from "sonner";
import api from "@/lib/api";
import { clearTokens, getToken, setRefreshToken, setToken } from "@/lib/auth";

// ── Auth store (Zustand) ─────────────────────────────────────────────────────
interface AuthUser {
  id: string;
  email: string;
  full_name?: string;
  role?: string;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: AuthUser | null) => void;
  login: (accessToken: string, refreshToken: string) => Promise<void>;
  register: (accessToken: string, refreshToken: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  login: async (accessToken: string, refreshToken: string) => {
    setToken(accessToken);
    setRefreshToken(refreshToken);
    try {
      const res = await api.get("/auth/me");
      set({ user: res.data, isAuthenticated: true });
      toast.success("Welcome back!");
    } catch (err) {
      clearTokens();
      set({ user: null, isAuthenticated: false });
      throw err;
    }
  },

  register: async (accessToken: string, refreshToken: string) => {
    setToken(accessToken);
    setRefreshToken(refreshToken);
    const res = await api.get("/auth/me");
    set({ user: res.data, isAuthenticated: true });
    toast.success("Account created!");
  },

  logout: () => {
    clearTokens();
    set({ user: null, isAuthenticated: false });
    toast.info("Signed out");
  },

  fetchUser: async () => {
    if (!getToken()) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      const res = await api.get("/auth/me");
      set({ user: res.data, isAuthenticated: true });
    } catch {
      clearTokens();
      set({ user: null, isAuthenticated: false });
    } finally {
      set({ isLoading: false });
    }
  },
}));

// ── React hook ───────────────────────────────────────────────────────────────
export function useAuth() {
  return useAuthStore();
}

// ── Provider ─────────────────────────────────────────────────────────────────
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const fetchUser = useAuthStore((s) => s.fetchUser);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const isDashboardRoute = pathname?.startsWith("/dashboard");
    if (isDashboardRoute) {
      fetchUser();
      return;
    }

    useAuthStore.setState({ isLoading: false });
  }, [fetchUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated && pathname?.startsWith("/dashboard")) {
      const publicPaths = ["/auth/login", "/auth/register", "/patient-companion"];
      if (!publicPaths.includes(pathname ?? "")) {
        router.push("/auth/login");
      }
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}
