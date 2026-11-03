"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, ApiError, type User } from "@/lib/api";

type Status = "loading" | "authenticated" | "anonymous";

type SessionValue = {
  user: User | null;
  status: Status;
  setUser: (user: User | null) => void;
  reload: () => Promise<void>;
  signOut: () => Promise<void>;
};

const SessionContext = createContext<SessionValue | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<User | null>(null);
  const [status, setStatus] = useState<Status>("loading");

  const setUser = useCallback((next: User | null) => {
    setUserState(next);
    setStatus(next ? "authenticated" : "anonymous");
  }, []);

  const reload = useCallback(async () => {
    try {
      setUser(await api.me());
    } catch (error) {
      if (error instanceof ApiError && error.status !== 401 && error.status !== 0) {
        console.error(error);
      }
      setUser(null);
    }
  }, [setUser]);

  const signOut = useCallback(async () => {
    try {
      await api.logout();
    } finally {
      setUser(null);
    }
  }, [setUser]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const value = useMemo(
    () => ({ user, status, setUser, reload, signOut }),
    [user, status, setUser, reload, signOut],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionValue {
  const value = useContext(SessionContext);
  if (!value) throw new Error("useSession must be used inside <SessionProvider>");
  return value;
}
