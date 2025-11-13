import { useParams } from "react-router-dom";

export default function InstitutionPage() {
  const { institutionId } = useParams();

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Instituição #{institutionId}</h1>
        <p className="text-sm text-slate-600">
          Visão geral das avaliações aprovadas, métricas consolidadas e comentários da comunidade.
        </p>
      </header>
      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Médias das avaliações</h2>
          <p className="mt-2 text-sm text-slate-600">
            Em breve você encontrará dados consolidados com base apenas em avaliações moderadas.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Informações institucionais</h2>
          <p className="mt-2 text-sm text-slate-600">
            Painel dedicado para dados oficiais e solicitações aprovadas via ChangeRequests.
          </p>
        </div>
      </section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Avaliações recentes</h2>
        <p className="mt-2 text-sm text-slate-600">
          Quando houver avaliações aprovadas elas aparecerão aqui com anonimato garantido.
        </p>
      </section>
    </div>
  );
}
