import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-10">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="mx-auto max-w-6xl px-4 text-sm text-slate-500">
          © {new Date().getFullYear()} OpenCampus. Transparência acadêmica para todos.
        </div>
      </footer>
    </div>
  );
}
