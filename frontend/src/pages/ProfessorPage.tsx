import { useParams } from "react-router-dom";

export default function ProfessorPage() {
  const { professorId } = useParams();

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Professor #{professorId}</h1>
        <p className="text-sm text-slate-600">
          Acompanhe percepções aprovadas de estudantes e comunicações oficiais da instituição.
        </p>
      </header>
      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Resumo das avaliações</h2>
          <p className="mt-2 text-sm text-slate-600">
            Indicadores de didática, avaliação justa e acompanhamento serão exibidos aqui.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Reconhecimentos oficiais</h2>
          <p className="mt-2 text-sm text-slate-600">
            Espaço reservado para mensagens oficiais e ajustes aprovados pela moderação.
          </p>
        </div>
      </section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Discussões recentes</h2>
        <p className="mt-2 text-sm text-slate-600">
          Comentários aprovados aparecerão aqui com sinalização de origem oficial quando aplicável.
        </p>
      </section>
    </div>
  );
}
