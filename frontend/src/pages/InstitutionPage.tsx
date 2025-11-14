import { isAxiosError } from "axios";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { httpClient } from "../lib/httpClient";

interface InstitutionResponse {
  id: number;
  name: string;
}

interface CourseResponse {
  id: number;
  name: string;
  institution_id: number;
}

type ReviewRatings = Record<CriterionKey, number>;

interface ReviewResponse extends ReviewRatings {
  id: number;
  text: string;
  approved: boolean;
  created_at: string;
}

interface MetricsResponse {
  count: number;
  average_rating_1: number | null;
  average_rating_2: number | null;
  average_rating_3: number | null;
  average_rating_4: number | null;
  average_rating_5: number | null;
  average_overall: number | null;
}

type CriterionKey = "rating_1" | "rating_2" | "rating_3" | "rating_4" | "rating_5";

const INSTITUTION_CRITERIA: ReadonlyArray<{ key: CriterionKey; label: string }> = [
  { key: "rating_1", label: "Estrutura física" },
  { key: "rating_2", label: "Serviços estudantis" },
  { key: "rating_3", label: "Transparência administrativa" },
  { key: "rating_4", label: "Atendimento institucional" },
  { key: "rating_5", label: "Inclusão e acessibilidade" },
];

const PENDING_WARNING_STORAGE_KEY = "opencampus.pendingReviewsWarningAcknowledged";
const PENDING_WARNING_MESSAGE =
  "As avaliações pendentes não passaram por moderação e podem conter conteúdo inadequado ou impreciso. Continue somente se concordar em visualizar materiais ainda não verificados.";

function getErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string" && detail.trim().length > 0) {
      return detail;
    }
    const message = error.message;
    if (typeof message === "string" && message.trim().length > 0) {
      return message;
    }
    return "Erro ao comunicar com a API.";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Ocorreu um erro inesperado. Tente novamente.";
}

function formatAverage(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "–";
  }
  return value.toFixed(1);
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Data desconhecida";
  }
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

function readPendingWarningAcknowledgement(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  try {
    return window.localStorage.getItem(PENDING_WARNING_STORAGE_KEY) === "true";
  } catch (error) {
    console.warn("Unable to read pending warning acknowledgement", error);
    return false;
  }
}

function persistPendingWarningAcknowledgement(): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(PENDING_WARNING_STORAGE_KEY, "true");
  } catch (error) {
    console.warn("Unable to persist pending warning acknowledgement", error);
  }
}

export default function InstitutionPage() {
  const { institutionId } = useParams();
  const numericInstitutionId = useMemo(() => {
    if (!institutionId) {
      return null;
    }
    const parsed = Number(institutionId);
    if (!Number.isInteger(parsed) || parsed <= 0) {
      return null;
    }
    return parsed;
  }, [institutionId]);

  const [institution, setInstitution] = useState<InstitutionResponse | null>(null);
  const [courses, setCourses] = useState<CourseResponse[]>([]);
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [reviews, setReviews] = useState<ReviewResponse[]>([]);

  const [pageError, setPageError] = useState<string | null>(null);
  const [reviewsError, setReviewsError] = useState<string | null>(null);
  const [isLoadingPage, setIsLoadingPage] = useState(true);
  const [isLoadingReviews, setIsLoadingReviews] = useState(false);

  const [includePending, setIncludePending] = useState(false);
  const [pendingWarningVisible, setPendingWarningVisible] = useState(false);
  const [pendingWarningAcknowledged, setPendingWarningAcknowledged] = useState(() =>
    readPendingWarningAcknowledgement(),
  );

  useEffect(() => {
    if (numericInstitutionId === null) {
      setPageError("Instituição não encontrada.");
      setInstitution(null);
      setMetrics(null);
      setCourses([]);
      setIsLoadingPage(false);
      return;
    }

    let cancelled = false;
    async function loadBaseData() {
      setIsLoadingPage(true);
      setPageError(null);
      try {
        const [institutionResponse, metricsResponse, coursesResponse] = await Promise.all([
          httpClient.get<InstitutionResponse>(`/institutions/${numericInstitutionId}`),
          httpClient.get<MetricsResponse>("/reviews/metrics", {
            params: { target_type: "INSTITUTION", target_id: numericInstitutionId },
          }),
          httpClient.get<CourseResponse[]>("/courses/"),
        ]);

        if (cancelled) {
          return;
        }

        const relatedCourses = coursesResponse.data
          .filter((course) => course.institution_id === numericInstitutionId)
          .sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));

        setInstitution(institutionResponse.data);
        setMetrics(metricsResponse.data);
        setCourses(relatedCourses);
      } catch (error) {
        if (cancelled) {
          return;
        }
        setPageError(getErrorMessage(error));
        setInstitution(null);
        setMetrics(null);
        setCourses([]);
      } finally {
        if (!cancelled) {
          setIsLoadingPage(false);
        }
      }
    }

    loadBaseData();

    return () => {
      cancelled = true;
    };
  }, [numericInstitutionId]);

  useEffect(() => {
    if (numericInstitutionId === null) {
      setReviews([]);
      setIncludePending(false);
      return;
    }

    const targetId = numericInstitutionId;
    let cancelled = false;
    async function loadReviews() {
      setIsLoadingReviews(true);
      setReviewsError(null);
      try {
        const params: Record<string, string | number | boolean> = {
          target_type: "INSTITUTION",
          target_id: targetId,
        };
        if (includePending) {
          params.include_pending = true;
        }
        const response = await httpClient.get<ReviewResponse[]>("/reviews", { params });
        if (!cancelled) {
          setReviews(response.data);
        }
      } catch (error) {
        if (!cancelled) {
          setReviewsError(getErrorMessage(error));
          setReviews([]);
        }
      } finally {
        if (!cancelled) {
          setIsLoadingReviews(false);
        }
      }
    }

    loadReviews();

    return () => {
      cancelled = true;
    };
  }, [includePending, numericInstitutionId]);

  const institutionName =
    institution?.name ?? (numericInstitutionId !== null ? `Instituição #${numericInstitutionId}` : "Instituição");

  const hasMetrics = metrics !== null && metrics.count > 0;
  const criterionAverages: Record<CriterionKey, number | null> | null = metrics
    ? {
        rating_1: metrics.average_rating_1,
        rating_2: metrics.average_rating_2,
        rating_3: metrics.average_rating_3,
        rating_4: metrics.average_rating_4,
        rating_5: metrics.average_rating_5,
      }
    : null;

  function handleTogglePending() {
    if (includePending) {
      setIncludePending(false);
      return;
    }

    if (!pendingWarningAcknowledged) {
      setPendingWarningVisible(true);
      return;
    }

    setIncludePending(true);
  }

  function handleConfirmPendingWarning() {
    persistPendingWarningAcknowledgement();
    setPendingWarningAcknowledged(true);
    setPendingWarningVisible(false);
    setIncludePending(true);
  }

  function handleCancelPendingWarning() {
    setPendingWarningVisible(false);
  }

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">{institutionName}</h1>
        <p className="text-sm text-slate-600">
          Indicadores consolidados com base em avaliações aprovadas e acesso rápido às unidades acadêmicas relacionadas.
        </p>
      </header>

      {pageError && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {pageError}
        </div>
      )}

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Métricas consolidadas</h2>
              <p className="mt-1 text-xs text-slate-500">
                Apenas avaliações aprovadas alimentam os indicadores abaixo.
              </p>
            </div>
            {isLoadingPage ? (
              <span className="text-xs text-slate-400">Carregando…</span>
            ) : (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                {metrics?.count ?? 0} avaliações
              </span>
            )}
          </div>

          {isLoadingPage ? (
            <div className="mt-4 space-y-2 text-sm text-slate-500">
              <div className="h-4 w-3/4 rounded bg-slate-100" />
              <div className="h-4 w-1/2 rounded bg-slate-100" />
              <div className="h-4 w-2/3 rounded bg-slate-100" />
            </div>
          ) : hasMetrics && metrics ? (
            <div className="mt-4 space-y-4">
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Média geral
                </p>
                <p className="mt-1 text-3xl font-semibold text-slate-900">
                  {formatAverage(metrics.average_overall)}
                </p>
              </div>
              <dl className="grid gap-3 sm:grid-cols-2">
                {INSTITUTION_CRITERIA.map((criterion) => {
                  const value = criterionAverages ? criterionAverages[criterion.key] : null;
                  return (
                    <div key={criterion.key} className="rounded-xl border border-slate-200 p-3">
                      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                        {criterion.label}
                      </dt>
                      <dd className="mt-1 text-lg font-semibold text-slate-900">
                        {formatAverage(value ?? null)}
                      </dd>
                    </div>
                  );
                })}
              </dl>
            </div>
          ) : (
            <p className="mt-4 text-sm text-slate-600">
              Ainda não há avaliações aprovadas suficientes para gerar indicadores públicos.
            </p>
          )}
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Cursos vinculados</h2>
          <p className="mt-1 text-xs text-slate-500">
            Acompanhe cursos moderados pela comunidade e navegue para métricas específicas.
          </p>

          {isLoadingPage ? (
            <div className="mt-4 space-y-2">
              <div className="h-4 w-2/3 rounded bg-slate-100" />
              <div className="h-4 w-1/2 rounded bg-slate-100" />
              <div className="h-4 w-3/5 rounded bg-slate-100" />
            </div>
          ) : courses.length > 0 ? (
            <ul className="mt-4 space-y-2">
              {courses.map((course) => (
                <li key={course.id}>
                  <Link
                    to={`/courses/${course.id}`}
                    className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
                  >
                    <span>{course.name}</span>
                    <span className="text-xs text-slate-400">Ver detalhes</span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-sm text-slate-600">
              Não há cursos cadastrados para esta instituição no momento.
            </p>
          )}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Avaliações da comunidade</h2>
            <p className="mt-1 text-xs text-slate-500">
              As avaliações abaixo preservam o anonimato e seguem a política de moderação do OpenCampus.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-xs font-medium text-slate-600">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900"
                checked={includePending}
                onChange={handleTogglePending}
              />
              Incluir avaliações pendentes
            </label>
          </div>
        </div>

        {pendingWarningVisible && (
          <div className="mt-4 space-y-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            <p className="font-semibold">Aviso sobre conteúdo não moderado</p>
            <p>{PENDING_WARNING_MESSAGE}</p>
            <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={handleCancelPendingWarning}
                className="rounded-lg border border-amber-300 px-4 py-2 text-xs font-semibold text-amber-900 transition hover:bg-amber-100"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleConfirmPendingWarning}
                className="rounded-lg bg-amber-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-amber-700"
              >
                Entendi e desejo continuar
              </button>
            </div>
          </div>
        )}

        {includePending && pendingWarningAcknowledged && (
          <p className="mt-3 text-xs text-amber-700">
            Você optou por visualizar avaliações ainda pendentes de moderação. Elas não impactam métricas públicas até que sejam aprovadas.
          </p>
        )}

        {reviewsError && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {reviewsError}
          </div>
        )}

        {isLoadingReviews ? (
          <div className="mt-6 space-y-4">
            <div className="space-y-3 rounded-xl border border-slate-100 p-4">
              <div className="h-4 w-1/3 rounded bg-slate-100" />
              <div className="h-3 w-full rounded bg-slate-100" />
              <div className="h-3 w-5/6 rounded bg-slate-100" />
            </div>
            <div className="space-y-3 rounded-xl border border-slate-100 p-4">
              <div className="h-4 w-1/4 rounded bg-slate-100" />
              <div className="h-3 w-full rounded bg-slate-100" />
              <div className="h-3 w-3/4 rounded bg-slate-100" />
            </div>
          </div>
        ) : reviews.length > 0 ? (
          <div className="mt-6 space-y-4">
            {reviews.map((review) => {
              const isPending = !review.approved;
              const average =
                (review.rating_1 + review.rating_2 + review.rating_3 + review.rating_4 + review.rating_5) / 5;

              return (
                <article key={review.id} className="space-y-3 rounded-2xl border border-slate-200 p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
                      Média {average.toFixed(1)} / 5
                    </span>
                    <span className="text-xs text-slate-500">{formatDate(review.created_at)}</span>
                    {isPending && (
                      <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700">
                        Pendente de moderação
                      </span>
                    )}
                  </div>
                  <p className="text-sm leading-relaxed text-slate-700">{review.text}</p>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {INSTITUTION_CRITERIA.map((criterion) => (
                      <div key={criterion.key} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-600">
                        <span>{criterion.label}</span>
                        <span className="font-semibold text-slate-900">
                          {review[criterion.key].toFixed(1)}
                        </span>
                      </div>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <p className="mt-6 text-sm text-slate-600">
            Ainda não existem avaliações aprovadas para esta instituição. Seja o primeiro a contribuir com uma experiência moderada.
          </p>
        )}
      </section>
    </div>
  );
}
