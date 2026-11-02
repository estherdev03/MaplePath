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
      <body className="m-0 min-h-screen bg-[#0f111c] font-[family-name:var(--font-body)] text-[15px] leading-[1.55] text-[#e9e9ed]">
        <ProfileProvider>
          <Header />
          {children}
        </ProfileProvider>
      </body>
    </html>
  );
}
