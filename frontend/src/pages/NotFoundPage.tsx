import { Link } from "react-router-dom";

const buttonClasses = [
  "rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white",
  "shadow shadow-slate-900/10 transition",
  "hover:bg-slate-800",
].join(" ");

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center gap-6 py-20 text-center">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-widest text-slate-500">Erro 404</p>
        <h1 className="text-3xl font-semibold text-slate-900">Página não encontrada</h1>
        <p className="max-w-xl text-sm text-slate-600">
          O conteúdo que você procura não está disponível ou requer permissões específicas. Use a navegação para encontrar a
          seção desejada do OpenCampus.
        </p>
      </div>
      <Link to="/" className={buttonClasses}>
        Voltar para a página inicial
      </Link>
    </div>
  );
}
