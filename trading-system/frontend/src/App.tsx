import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Models from "./pages/Models";
import DataViewer from "./pages/DataViewer";

function App() {
  return (
    <Router>
      <main className="min-h-screen bg-gray-50 text-gray-900">
        <header className="py-6 mb-8 shadow bg-white">
          <div className="container mx-auto px-4 flex items-center justify-between">
            <h1 className="text-3xl font-bold tracking-tight">Polaris Quant Demo</h1>
            <nav className="flex gap-6">
              <Link to="/" className="hover:underline font-medium">Ingest</Link>
              <Link to="/data" className="hover:underline font-medium">Data Viewer</Link>
              <Link to="/models" className="hover:underline font-medium">Models</Link>
            </nav>
          </div>
        </header>
        <section className="container mx-auto px-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/data" element={<DataViewer />} />
            <Route path="/models" element={<Models />} />
          </Routes>
        </section>
      </main>
    </Router>
  );
}

export default App;
