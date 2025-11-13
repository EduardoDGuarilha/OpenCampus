import { useState } from "react";

const TARGET_OPTIONS = [
  { value: "INSTITUTION", label: "Instituição" },
  { value: "COURSE", label: "Curso" },
  { value: "PROFESSOR", label: "Professor" },
  { value: "SUBJECT", label: "Disciplina" },
] as const;

type TargetType = (typeof TARGET_OPTIONS)[number]["value"];

const criteriaByTarget: Record<TargetType, string[]> = {
  INSTITUTION: ["Estrutura", "Serviços estudantis", "Transparência"],
  COURSE: ["Organização curricular", "Infraestrutura", "Suporte ao aluno"],
  PROFESSOR: ["Didática", "Avaliação justa", "Disponibilidade"],
  SUBJECT: ["Clareza do conteúdo", "Carga de trabalho", "Relevância"],
};

const fieldClasses = [
  "w-full rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm text-slate-900",
  "focus:border-slate-900 focus:outline-none",
].join(" ");

const submitButtonClasses = [
  "rounded-lg bg-slate-900 px-6 py-3 text-sm font-semibold text-white",
  "shadow-lg shadow-slate-900/20 transition",
  "hover:-translate-y-0.5 hover:bg-slate-800",
].join(" ");

export default function ReviewCreatePage() {
  const [targetType, setTargetType] = useState<TargetType>("INSTITUTION");

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Enviar avaliação moderada</h1>
        <p className="text-sm text-slate-600">
          Escolha o tipo de alvo, preencha os critérios obrigatórios e compartilhe sua experiência. Todas as avaliações são
          anônimas para o público e começam como pendentes até a moderação concluir a análise.
        </p>
      </header>
      <form className="space-y-6">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700">Tipo de alvo</label>
          <select
            value={targetType}
            onChange={(event) => setTargetType(event.target.value as TargetType)}
            className={fieldClasses}
          >
            {TARGET_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-slate-500">
            O backend garante que cada estudante envie apenas uma avaliação aprovada por alvo associado.
          </p>
        </div>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Critérios obrigatórios</h2>
          {criteriaByTarget[targetType].map((criterion) => (
            <div key={criterion} className="space-y-2 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-900">{criterion}</span>
                <span className="text-xs text-slate-500">Nota de 1 a 5</span>
              </div>
              <input type="range" min="1" max="5" defaultValue="3" className="w-full" />
            </div>
          ))}
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700">Relato detalhado</label>
          <textarea
            rows={6}
            className={fieldClasses}
            placeholder="Conte como foi sua experiência. Dados pessoais nunca são exibidos publicamente."
          />
          <p className="text-xs text-slate-500">
            Ao enviar você confirma que suas informações são verdadeiras e compreende que o conteúdo passará por moderação.
          </p>
        </div>
        <button type="submit" className={submitButtonClasses}>
          Enviar avaliação para moderação
        </button>
      </form>
    </div>
  );
}
