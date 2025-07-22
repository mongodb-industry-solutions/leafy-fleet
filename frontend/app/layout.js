import "@fontsource/geist-mono";
import "@/node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";
import LoginManager from "@/components/LoginManager/LoginManager";
import StoreProvider from "./StoreProvide";
import PageHeader from "@/components/PageHeader/PageHeader";
export const metadata = {
  title: "Leafy Fleet",
  description:
    "This AI Agent listens to complaints and advises on next course of action",
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
