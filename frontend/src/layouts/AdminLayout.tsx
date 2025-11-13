import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function AdminLayout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-10">
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
          <header className="mb-6 border-b border-slate-800 pb-4">
            <h1 className="text-2xl font-semibold">Painel de moderação</h1>
            <p className="text-sm text-slate-400">
              Gerencie avaliações pendentes e solicitações de alteração com segurança.
            </p>
          </header>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
