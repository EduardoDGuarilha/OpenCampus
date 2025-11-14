import { isAxiosError } from "axios";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { httpClient } from "../lib/httpClient";

type CriterionKey = "rating_1" | "rating_2" | "rating_3" | "rating_4" | "rating_5";

type ReviewRatings = Record<CriterionKey, number>;

interface SubjectResponse {
  id: number;
  name: string;
  course_id: number;
}

interface CourseResponse {
  id: number;
  name: string;
  institution_id: number;
}

interface InstitutionResponse {
  id: number;
  name: string;
}

interface ReviewResponse extends ReviewRatings {
  id: number;
  text: string;
  approved: boolean;
  created_at: string;
}

interface CommentResponse {
  id: number;
  review_id: number;
  text: string;
  created_at: string;
  is_official: boolean;
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

const SUBJECT_CRITERIA: ReadonlyArray<{ key: CriterionKey; label: string }> = [
  { key: "rating_1", label: "Clareza do conteúdo" },
  { key: "rating_2", label: "Carga de trabalho" },
  { key: "rating_3", label: "Relevância para o curso" },
  { key: "rating_4", label: "Material de apoio" },
  { key: "rating_5", label: "Integração com outras disciplinas" },
];

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

export default function SubjectPage() {
  const { subjectId } = useParams();
  const numericSubjectId = useMemo(() => {
    if (!subjectId) {
      return null;
    }
    const parsed = Number(subjectId);
    if (!Number.isInteger(parsed) || parsed <= 0) {
      return null;
    }
    return parsed;
  }, [subjectId]);

  const [subject, setSubject] = useState<SubjectResponse | null>(null);
  const [course, setCourse] = useState<CourseResponse | null>(null);
  const [institution, setInstitution] = useState<InstitutionResponse | null>(null);
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [reviews, setReviews] = useState<ReviewResponse[]>([]);
  const [commentsByReview, setCommentsByReview] = useState<Record<number, CommentResponse[]>>({});

  const [pageError, setPageError] = useState<string | null>(null);
  const [reviewsError, setReviewsError] = useState<string | null>(null);
  const [commentsError, setCommentsError] = useState<string | null>(null);
  const [isLoadingPage, setIsLoadingPage] = useState(true);
  const [isLoadingReviews, setIsLoadingReviews] = useState(false);
  const [isLoadingComments, setIsLoadingComments] = useState(false);

  useEffect(() => {
    if (numericSubjectId === null) {
      setPageError("Disciplina não encontrada.");
      setSubject(null);
      setCourse(null);
      setInstitution(null);
      setMetrics(null);
      setIsLoadingPage(false);
      return;
    }

    let cancelled = false;

    async function loadBaseData() {
      setIsLoadingPage(true);
      setPageError(null);

      try {
        const subjectResponse = await httpClient.get<SubjectResponse>(`/subjects/${numericSubjectId}`);
        if (cancelled) {
          return;
        }

        const subjectData = subjectResponse.data;

        const [metricsResponse, courseResponse] = await Promise.all([
          httpClient.get<MetricsResponse>("/reviews/metrics", {
            params: { target_type: "SUBJECT", target_id: subjectData.id },
          }),
          httpClient.get<CourseResponse>(`/courses/${subjectData.course_id}`),
        ]);

        if (cancelled) {
          return;
        }

        setSubject(subjectData);
        setMetrics(metricsResponse.data);
        setCourse(courseResponse.data);

        const institutionId = courseResponse.data.institution_id;
        if (institutionId) {
          try {
            const institutionResponse = await httpClient.get<InstitutionResponse>(`/institutions/${institutionId}`);
            if (!cancelled) {
              setInstitution(institutionResponse.data);
            }
          } catch (institutionError) {
            if (!cancelled) {
              console.warn("Falha ao carregar instituição vinculada", institutionError);
              setInstitution(null);
            }
          }
        } else {
          setInstitution(null);
        }
      } catch (error) {
        if (!cancelled) {
          setPageError(getErrorMessage(error));
          setSubject(null);
          setCourse(null);
          setInstitution(null);
          setMetrics(null);
        }
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
  }, [numericSubjectId]);

  useEffect(() => {
    if (numericSubjectId === null) {
      setReviews([]);
      setCommentsByReview({});
      return;
    }

    let cancelled = false;

    async function loadReviews() {
      setIsLoadingReviews(true);
      setReviewsError(null);

      try {
        const response = await httpClient.get<ReviewResponse[]>("/reviews", {
          params: { target_type: "SUBJECT", target_id: numericSubjectId },
        });
        if (cancelled) {
          return;
        }

        const approvedReviews = response.data.filter((review) => review.approved);
        setReviews(approvedReviews);
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
  }, [numericSubjectId]);

  useEffect(() => {
    if (reviews.length === 0) {
      setCommentsByReview({});
      setCommentsError(null);
      setIsLoadingComments(false);
      return;
    }

    let cancelled = false;

    async function loadComments() {
      setIsLoadingComments(true);
      setCommentsError(null);

      try {
        const entries = await Promise.all(
          reviews.map(async (review) => {
            const response = await httpClient.get<CommentResponse[]>("/comments", {
              params: { review_id: review.id },
            });
            return [review.id, response.data] as const;
          }),
        );

        if (cancelled) {
          return;
        }

        const map = entries.reduce<Record<number, CommentResponse[]>>((accumulator, [reviewId, comments]) => {
          const sorted = comments.slice().sort((a, b) => a.created_at.localeCompare(b.created_at));
          accumulator[reviewId] = sorted;
          return accumulator;
        }, {});
        setCommentsByReview(map);
      } catch (error) {
        if (!cancelled) {
          setCommentsError(getErrorMessage(error));
          setCommentsByReview({});
        }
      } finally {
        if (!cancelled) {
          setIsLoadingComments(false);
        }
      }
    }

    loadComments();

    return () => {
      cancelled = true;
    };
  }, [reviews]);

  const subjectName = subject?.name ?? (numericSubjectId ? `Disciplina #${numericSubjectId}` : "Disciplina");
  const courseName = course?.name ?? "Curso";
  const institutionName = institution?.name ?? "Instituição";
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

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">{subjectName}</h1>
        <p className="text-sm text-slate-600">
          Indicadores e relatos aqui apresentados refletem apenas avaliações já moderadas, mantendo a autoria estudantil anônima.
        </p>
        {course && (
          <p className="text-xs text-slate-500">
            <span className="font-semibold text-slate-700">Curso vinculado:</span>{" "}
            <Link to={`/courses/${course.id}`} className="text-slate-900 underline-offset-2 hover:underline">
              {courseName}
            </Link>
          </p>
        )}
        {institution && (
          <p className="text-xs text-slate-500">
            <span className="font-semibold text-slate-700">Instituição:</span>{" "}
            <Link to={`/institutions/${institution.id}`} className="text-slate-900 underline-offset-2 hover:underline">
              {institutionName}
            </Link>
          </p>
        )}
      </header>

      {pageError && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{pageError}</div>
      )}

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Indicadores da disciplina</h2>
              <p className="mt-1 text-xs text-slate-500">Somente avaliações aprovadas alimentam este painel.</p>
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
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Média geral</p>
                <p className="mt-1 text-3xl font-semibold text-slate-900">{formatAverage(metrics.average_overall)}</p>
              </div>
              <dl className="grid gap-3 sm:grid-cols-2">
                {SUBJECT_CRITERIA.map((criterion) => {
                  const value = criterionAverages ? criterionAverages[criterion.key] : null;
                  return (
                    <div key={criterion.key} className="rounded-xl border border-slate-200 p-3">
                      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">{criterion.label}</dt>
                      <dd className="mt-1 text-lg font-semibold text-slate-900">{formatAverage(value ?? null)}</dd>
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
          <h2 className="text-lg font-semibold text-slate-900">Contexto da disciplina</h2>
          <p className="mt-2 text-sm text-slate-600">
            Utilize esta visão para compreender expectativas de conteúdo, carga de estudos e alinhamento com o curso, sempre com relatos anônimos.
          </p>
          <p className="mt-2 text-xs text-slate-500">
            Comentários oficiais validados aparecem destacados e nunca revelam dados pessoais de quem avaliou.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Avaliações aprovadas</h2>
            <p className="mt-1 text-xs text-slate-500">
              Autores permanecem anônimos. Comentários de fontes oficiais trazem identificação visual própria para o público.
            </p>
          </div>
        </div>

        {reviewsError && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{reviewsError}</div>
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
              const average =
                (review.rating_1 + review.rating_2 + review.rating_3 + review.rating_4 + review.rating_5) / 5;
              const comments = commentsByReview[review.id] ?? [];

              return (
                <article key={review.id} className="space-y-4 rounded-2xl border border-slate-200 p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
                      Avaliação anônima · Média {average.toFixed(1)} / 5
                    </span>
                    <span className="text-xs text-slate-500">Publicada em {formatDate(review.created_at)}</span>
                  </div>
                  <p className="text-sm leading-relaxed text-slate-700">{review.text}</p>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {SUBJECT_CRITERIA.map((criterion) => (
                      <div
                        key={criterion.key}
                        className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-600"
                      >
                        <span>{criterion.label}</span>
                        <span className="font-semibold text-slate-900">{review[criterion.key].toFixed(1)}</span>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-slate-900">Comentários moderados</h3>
                      {isLoadingComments && <span className="text-xs text-slate-500">Carregando comentários…</span>}
                    </div>

                    {commentsError ? (
                      <p className="text-xs text-red-600">{commentsError}</p>
                    ) : comments.length > 0 ? (
                      <ul className="space-y-3">
                        {comments.map((comment) => (
                          <li
                            key={comment.id}
                            className={[
                              "rounded-lg border px-3 py-2 text-xs leading-relaxed",
                              comment.is_official
                                ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                                : "border-slate-200 bg-white text-slate-700",
                            ].join(" ")}
                          >
                            <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wide">
                              <span>{comment.is_official ? "Comentário oficial" : "Comentário anônimo"}</span>
                              <span className="text-slate-400 normal-case font-normal">{formatDate(comment.created_at)}</span>
                            </div>
                            <p className="mt-1 whitespace-pre-line text-xs text-current">{comment.text}</p>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-xs text-slate-500">Nenhum comentário aprovado para esta avaliação.</p>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <p className="mt-6 text-sm text-slate-600">
            Ainda não existem avaliações aprovadas para esta disciplina. Compartilhe sua experiência quando a moderação estiver disponível.
          </p>
        )}
      </section>
    </div>
  );
}
