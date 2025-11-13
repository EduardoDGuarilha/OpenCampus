import { NavLink } from "react-router-dom";

const linkClasses = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-3 py-2 text-sm font-medium transition-colors ${
    isActive
      ? "bg-slate-900 text-white"
      : "text-slate-600 hover:bg-slate-200 hover:text-slate-900"
  }`;

export default function Navbar() {
  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <NavLink to="/" className="text-lg font-semibold text-slate-900">
          OpenCampus
        </NavLink>
        <nav className="flex items-center gap-1">
          <NavLink to="/institutions/1" className={linkClasses}>
            Instituições
          </NavLink>
          <NavLink to="/courses/1" className={linkClasses}>
            Cursos
          </NavLink>
          <NavLink to="/professors/1" className={linkClasses}>
            Professores
          </NavLink>
          <NavLink to="/subjects/1" className={linkClasses}>
            Disciplinas
          </NavLink>
          <NavLink to="/reviews/new" className={linkClasses}>
            Nova avaliação
          </NavLink>
          <NavLink to="/admin" className={linkClasses}>
            Painel
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
