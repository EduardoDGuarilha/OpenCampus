import { Outlet } from "react-router-dom";

const containerClasses = [
  "flex min-h-screen items-center justify-center",
  "bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700",
  "p-6 text-white",
].join(" ");

export default function AuthLayout() {
  return (
    <div className={containerClasses}>
      <div className="w-full max-w-md rounded-2xl bg-white/10 p-8 shadow-xl backdrop-blur">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold">OpenCampus</h1>
          <p className="text-sm text-slate-200">
            Acesse sua conta ou crie um perfil para participar da comunidade acadêmica.
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
