const cardClasses = "rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-lg";

export default function AdminDashboardPage() {
  return (
    <div className="space-y-8 text-slate-100">
      <section className="grid gap-6 md:grid-cols-3">
        <div className={cardClasses}>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Avaliações pendentes</h2>
          <p className="mt-4 text-3xl font-bold text-white">0</p>
          <p className="mt-2 text-xs text-slate-400">
            Itens aguardando análise antes de se tornarem públicos na plataforma.
          </p>
        </div>
        <div className={cardClasses}>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Solicitações abertas</h2>
          <p className="mt-4 text-3xl font-bold text-white">0</p>
          <p className="mt-2 text-xs text-slate-400">
            Mudanças sugeridas por usuários aguardando parecer de um moderador.
          </p>
        </div>
        <div className={cardClasses}>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Ações recentes</h2>
          <p className="mt-4 text-3xl font-bold text-white">0</p>
          <p className="mt-2 text-xs text-slate-400">
            Aprovações ou rejeições registradas nas últimas 24 horas.
          </p>
        </div>
      </section>
      <section className={cardClasses}>
        <h2 className="text-lg font-semibold text-white">Fila de moderação</h2>
        <p className="mt-2 text-sm text-slate-400">
          Assim que houver avaliações pendentes, elas aparecerão aqui com detalhes anônimos para decisão rápida.
        </p>
      </section>
      <section className={cardClasses}>
        <h2 className="text-lg font-semibold text-white">Solicitações de alteração</h2>
        <p className="mt-2 text-sm text-slate-400">
          Esse painel exibirá ChangeRequests aguardando análise, destacando aquelas originadas por fontes oficiais.
        </p>
      </section>
    </div>
  );
}
