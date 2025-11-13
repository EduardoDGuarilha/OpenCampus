import { Link } from "react-router-dom";

const inputClasses = [
  "w-full rounded-lg border border-white/20 bg-white/10",
  "px-4 py-2 text-sm text-white",
  "placeholder:text-slate-300 focus:border-white focus:outline-none",
].join(" ");

export default function LoginPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-2xl font-semibold text-white">Acesse sua conta</h2>
        <p className="text-sm text-slate-200">
          Entre com suas credenciais para acompanhar avaliações, comentar e participar das discussões.
        </p>
      </div>
      <form className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium text-slate-100">
            E-mail institucional
          </label>
          <input id="email" type="email" className={inputClasses} placeholder="seu.email@exemplo.br" />
        </div>
        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium text-slate-100">
            Senha
          </label>
          <input id="password" type="password" className={inputClasses} placeholder="••••••••" />
        </div>
        <button
          type="submit"
          className="w-full rounded-lg bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-200"
        >
          Entrar
        </button>
      </form>
      <p className="text-center text-xs text-slate-300">
        Ainda não tem uma conta? {" "}
        <Link to="/register" className="font-medium text-white underline">
          Cadastre-se agora
        </Link>
      </p>
    </div>
  );
}
