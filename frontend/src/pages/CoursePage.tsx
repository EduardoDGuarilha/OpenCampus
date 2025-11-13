import { useParams } from "react-router-dom";

export default function CoursePage() {
  const { courseId } = useParams();

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Curso #{courseId}</h1>
        <p className="text-sm text-slate-600">
          Compare indicadores oficiais e avaliações aprovadas para compreender a experiência acadêmica.
        </p>
      </header>
      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Panorama do curso</h2>
          <p className="mt-2 text-sm text-slate-600">
            Espaço para grade curricular, indicadores de evasão e outros dados moderados.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Médias das avaliações</h2>
          <p className="mt-2 text-sm text-slate-600">
            Assim que as primeiras avaliações forem aprovadas, elas alimentarão este painel.
          </p>
        </div>
      </section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Comentários recentes</h2>
        <p className="mt-2 text-sm text-slate-600">
          Comentários oficiais e da comunidade serão exibidos aqui com distinções claras.
        </p>
      </section>
    </div>
  );
}
