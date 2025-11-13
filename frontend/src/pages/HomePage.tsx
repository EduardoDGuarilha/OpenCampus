import { Link } from "react-router-dom";

const heroLinks = [
  { label: "Conheça instituições", to: "/institutions/1" },
  { label: "Explore cursos", to: "/courses/1" },
  { label: "Pesquise professores", to: "/professors/1" },
  { label: "Veja disciplinas", to: "/subjects/1" },
];

const primaryButtonClasses = [
  "rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white",
  "shadow-lg shadow-slate-900/20 transition",
  "hover:-translate-y-0.5 hover:bg-slate-800",
].join(" ");

const secondaryButtonClasses = [
  "rounded-lg border border-slate-900 px-5 py-3 text-sm font-semibold text-slate-900",
  "transition hover:bg-slate-900 hover:text-white",
].join(" ");

const heroLinkClasses = [
  "flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3",
  "text-sm font-medium text-slate-700 transition",
  "hover:border-slate-900 hover:bg-white hover:text-slate-900",
].join(" ");

export default function HomePage() {
  return (
    <div className="space-y-12">
      <section className="grid gap-6 lg:grid-cols-2 lg:items-center">
        <div className="space-y-6">
          <span className="inline-flex items-center rounded-full bg-slate-900 px-4 py-1 text-xs font-semibold uppercase tracking-wider text-white">
            Portal de transparência acadêmica
          </span>
          <h1 className="text-4xl font-bold text-slate-900">
            Avaliações anônimas e moderadas para elevar a qualidade do ensino.
          </h1>
          <p className="text-lg text-slate-600">
            O OpenCampus reúne percepções reais de estudantes, mediadas por um processo de moderação responsável. Descubra insights sobre instituições, cursos, professores e disciplinas antes de tomar decisões importantes.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/reviews/new" className={primaryButtonClasses}>
              Compartilhe sua experiência
            </Link>
            <Link to="/login" className={secondaryButtonClasses}>
              Entrar na plataforma
            </Link>
          </div>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-900/5">
          <h2 className="text-lg font-semibold text-slate-900">
            Mergulhe em dados confiáveis
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            Navegue pelos relatórios públicos e métricas construídas apenas com avaliações moderadas.
          </p>
          <ul className="mt-6 grid gap-3">
            {heroLinks.map((item) => (
              <li key={item.to}>
                <Link to={item.to} className={heroLinkClasses}>
                  <span>{item.label}</span>
                  <span aria-hidden className="text-lg">
                    →
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>
      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-900/5">
        <h2 className="text-xl font-semibold text-slate-900">Como funciona</h2>
        <div className="mt-6 grid gap-6 md:grid-cols-3">
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-slate-900">Avaliações responsáveis</h3>
            <p className="text-sm text-slate-600">
              Estudantes validados compartilham experiências reais sobre seus contextos acadêmicos.
            </p>
          </div>
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-slate-900">Moderação dedicada</h3>
            <p className="text-sm text-slate-600">
              Moderadores analisam e aprovam o conteúdo antes da publicação para garantir imparcialidade.
            </p>
          </div>
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-slate-900">Dados para decisões</h3>
            <p className="text-sm text-slate-600">
              Métricas públicas exibem apenas informações confirmadas, ajudando você a escolher com confiança.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
