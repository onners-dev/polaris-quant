import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <header className="py-6 mb-8 shadow bg-white">
        <div className="container mx-auto px-4 flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight">Polaris Quant Demo</h1>
        </div>
      </header>
      <section className="container mx-auto px-4">
        <Dashboard />
      </section>
    </main>
  );
}

export default App;
