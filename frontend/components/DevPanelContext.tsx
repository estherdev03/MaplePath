"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

interface DevPanelContextValue {
  devOpen: boolean;
  toggleDev: () => void;
}

const DevPanelContext = createContext<DevPanelContextValue | null>(null);

export function DevPanelProvider({ children }: { children: ReactNode }) {
  const [devOpen, setDevOpen] = useState(false);
  return (
    <DevPanelContext.Provider value={{ devOpen, toggleDev: () => setDevOpen((v) => !v) }}>
      {children}
    </DevPanelContext.Provider>
  );
}

export function useDevPanel() {
  const ctx = useContext(DevPanelContext);
  if (!ctx) throw new Error("useDevPanel must be used within a DevPanelProvider");
  return ctx;
}
