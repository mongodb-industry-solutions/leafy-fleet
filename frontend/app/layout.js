import "@fontsource/geist-mono";
import '@/node_modules/bootstrap/dist/css/bootstrap.min.css'
import "./globals.css";
import LoginManager from "@/components/LoginManager/LoginManager";
import StoreProvider from "./StoreProvide";
import PageHeader from "@/components/PageHeader/PageHeader";
export const metadata = {
  title: "Agentic Framework",
  description: "This AI Agent listens to complaints and advises on next course of action",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "'Geist Mono', monospace" }}>
        <StoreProvider> 
        <PageHeader />
        {children}
        <LoginManager />
        </StoreProvider>
      </body>
    </html>
  );
}
