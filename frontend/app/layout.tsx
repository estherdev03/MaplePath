import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import { ProfileProvider } from "@/lib/profile-context";

export const metadata: Metadata = {
  title: "MaplePath",
  description: "Know exactly where you stand — category by category.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          minHeight: "100vh",
          background: "#0f111c",
          color: "#e9e9ed",
          fontFamily: "'Inter',system-ui,sans-serif",
          fontSize: 15,
          lineHeight: 1.55,
        }}
      >
        <ProfileProvider>
          <Header />
          {children}
        </ProfileProvider>
      </body>
    </html>
  );
}
