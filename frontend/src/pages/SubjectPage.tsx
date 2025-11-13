import { useParams } from "react-router-dom";

export default function SubjectPage() {
  const { subjectId } = useParams();

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Disciplina #{subjectId}</h1>
        <p className="text-sm text-slate-600">
          Explore avaliações moderadas sobre conteúdos, carga horária e estratégias de avaliação.
        </p>
      </header>
      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Indicadores principais</h2>
          <p className="mt-2 text-sm text-slate-600">
            Métricas agregadas serão exibidas aqui apenas quando as avaliações forem aprovadas.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Materiais e atualizações</h2>
          <p className="mt-2 text-sm text-slate-600">
            Solicitações oficiais aprovadas aparecerão neste espaço para orientar novos estudantes.
          </p>
        </div>
      </section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Avaliações recentes</h2>
        <p className="mt-2 text-sm text-slate-600">
          Quando houver avaliações moderadas elas serão listadas aqui com indicação de pendências.
        </p>
      </section>
    </div>
  );
}
