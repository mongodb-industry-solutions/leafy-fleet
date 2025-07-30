import "@fontsource/geist-mono";
import "@/node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";
import LoginManager from "@/components/LoginManager/LoginManager";
import StoreProvider from "./StoreProvide";
import PageHeader from "@/components/PageHeader/PageHeader";
export const metadata = {
  title: "Leafy Fleet",
  description:
    "Fleet Management System with AI-driven diagnostics and recommendations",
  icons: [
    {
      url: "/favicon_light.png",
      media: "(prefers-color-scheme: light)",
    },
    {
      url: "/favicon_dark.png",
      media: "(prefers-color-scheme: dark)",
    },
  ],
};

// Check if the current route starts with "/extensions", and exclude "/" (root)  



export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "'Geist Mono', monospace" }}>
        <StoreProvider>
          <PageHeader />
          <div className="main-content">{children}</div>
          <LoginManager />
        </StoreProvider>
      </body>
    </html>
  );
}
