import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Ingest from "./pages/Ingest";
import Models from "./pages/Models";
import DataViewer from "./pages/DataViewer";
import Backtesting from "./pages/Backtesting";
import WalkForwardBacktest from "./pages/WalkForwardBacktest";
import { Button } from "@/components/ui/button";

function NavLinks() {
  const location = useLocation();
  const navItems = [
    { href: "/", label: "Dashboard" },
    { href: "/ingest", label: "Ingest" },
    { href: "/data", label: "Data Viewer" },
    { href: "/models", label: "Models" },
    { href: "/backtesting", label: "Backtesting" },
    { href: "/walkforward", label: "Walk-Forward" },
  ];

  return (
    <nav className="flex gap-4">
      {navItems.map((item) => (
        <Button
          asChild
          key={item.href}
          variant={location.pathname === item.href ? "secondary" : "ghost"}
          className="font-medium"
        >
          <Link to={item.href}>{item.label}</Link>
        </Button>
      ))}
    </nav>
  );
}

function App() {
  return (
    <Router>
      <main className="min-h-screen bg-gray-50 text-gray-900">
        <header className="py-6 mb-8 shadow bg-white">
          <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <h1 className="text-3xl font-bold tracking-tight">Polaris Quant Demo</h1>
            <NavLinks />
          </div>
        </header>
        <section className="container mx-auto px-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ingest" element={<Ingest />} />
            <Route path="/data" element={<DataViewer />} />
            <Route path="/models" element={<Models />} />
            <Route path="/backtesting" element={<Backtesting />} />
            <Route path="/walkforward" element={<WalkForwardBacktest />} />
          </Routes>
        </section>
      </main>
    </Router>
  );
}

export default App;
