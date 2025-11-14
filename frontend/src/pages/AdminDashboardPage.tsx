import { isAxiosError } from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";

import { httpClient } from "../lib/httpClient";

type UserRole = "STUDENT" | "PROFESSOR" | "INSTITUTION" | "MODERATOR";

type TargetType = "INSTITUTION" | "COURSE" | "PROFESSOR" | "SUBJECT";

type ChangeRequestStatus = "PENDING" | "APPROVED" | "REJECTED";

type CriterionKey = "rating_1" | "rating_2" | "rating_3" | "rating_4" | "rating_5";

interface UserProfile {
  id: number;
  role: UserRole;
  validated: boolean;
}

type ReviewRatings = Record<CriterionKey, number | null>;

interface ReviewModerationItem extends ReviewRatings {
  id: number;
  target_type: TargetType;
  target_id: number;
  target_name: string;
  text: string;
  created_at: string;
  approved: boolean;
  pending_reason?: string | null;
}

interface ChangeRequestResponse {
  id: number;
  target_type: TargetType;
  target_name: string;
  summary: string;
  created_at: string;
  status: ChangeRequestStatus;
  official: boolean;
}

const TARGET_LABELS: Record<TargetType, string> = {
  INSTITUTION: "Instituição",
  COURSE: "Curso",
  PROFESSOR: "Professor",
  SUBJECT: "Disciplina",
};

const RATING_KEYS: readonly CriterionKey[] = [
  "rating_1",
  "rating_2",
  "rating_3",
  "rating_4",
  "rating_5",
];

const cardClasses = "rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-lg";

function getErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string" && detail.trim().length > 0) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      const firstDetail = detail[0];
      if (typeof firstDetail === "string" && firstDetail.trim().length > 0) {
        return firstDetail;
      }
      if (firstDetail && typeof firstDetail === "object" && "msg" in firstDetail) {
        const message = (firstDetail as { msg?: unknown }).msg;
        if (typeof message === "string" && message.trim().length > 0) {
          return message;
        }
      }
    }
    if (error.response?.status === 401) {
      return "Sua sessão expirou ou você não está autenticado.";
    }
    if (error.response?.status === 403) {
      return "Você não tem permissão para acessar este recurso.";
    }
    if (typeof error.message === "string" && error.message.trim().length > 0) {
      return error.message;
    }
    return "Erro ao comunicar com a API.";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Ocorreu um erro inesperado. Tente novamente.";
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
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function computeAverage(ratings: ReviewRatings): string {
  const values = RATING_KEYS.map((key) => ratings[key]).filter(
    (value): value is number => typeof value === "number",
  );
  if (values.length === 0) {
    return "–";
  }
  const sum = values.reduce((total, value) => total + value, 0);
  const average = sum / values.length;
  return average.toFixed(1);
}

function describeChangeRequest(changeRequest: ChangeRequestResponse): string {
  if (changeRequest.summary.trim().length > 0) {
    return changeRequest.summary;
  }
  return "Solicitação sem resumo detalhado.";
}

export default function AdminDashboardPage() {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [userError, setUserError] = useState<string | null>(null);

  const [pendingReviews, setPendingReviews] = useState<ReviewModerationItem[]>([]);
  const [approvedReviews, setApprovedReviews] = useState<ReviewModerationItem[]>([]);
  const [changeRequests, setChangeRequests] = useState<ChangeRequestResponse[]>([]);
  const [loadingData, setLoadingData] = useState(false);
  const [dataError, setDataError] = useState<string | null>(null);

  const [selectedReviewIds, setSelectedReviewIds] = useState<Set<number>>(() => new Set<number>());
  const selectedReviewIdsArray = useMemo(() => Array.from(selectedReviewIds), [selectedReviewIds]);

  const [processingReviewIds, setProcessingReviewIds] = useState<Set<number>>(() => new Set<number>());
  const [processingChangeRequestIds, setProcessingChangeRequestIds] = useState<Set<number>>(
    () => new Set<number>(),
  );
  const [bulkAction, setBulkAction] = useState<"approve" | "reject" | null>(null);

  const [actionFeedback, setActionFeedback] = useState<{ type: "success" | "error"; message: string } | null>(
    null,
  );

  const fetchCurrentUser = useCallback(async () => {
    setLoadingUser(true);
    setUserError(null);
    try {
      const response = await httpClient.get<UserProfile>("/users/me");
      setCurrentUser(response.data);
    } catch (error) {
      setCurrentUser(null);
      if (isAxiosError(error)) {
        if (error.response?.status === 401) {
          setUserError("Faça login com uma conta moderadora para acessar este painel.");
        } else if (error.response?.status === 403) {
          setUserError("Apenas contas de moderador podem acessar este painel.");
        } else {
          setUserError(getErrorMessage(error));
        }
      } else {
        setUserError(getErrorMessage(error));
      }
    } finally {
      setLoadingUser(false);
    }
  }, []);

  const loadModerationData = useCallback(async () => {
    setLoadingData(true);
    setDataError(null);
    try {
      const [pendingResponse, approvedResponse, changeRequestsResponse] = await Promise.all([
        httpClient.get<ReviewModerationItem[]>("/moderation/reviews", { params: { status: "PENDING" } }),
        httpClient.get<ReviewModerationItem[]>("/moderation/reviews", {
          params: { status: "APPROVED", limit: 5 },
        }),
        httpClient.get<ChangeRequestResponse[]>("/moderation/change-requests", { params: { status: "PENDING" } }),
      ]);
      setPendingReviews(pendingResponse.data);
      setApprovedReviews(approvedResponse.data);
      setChangeRequests(changeRequestsResponse.data);
      setSelectedReviewIds(() => new Set<number>());
    } catch (error) {
      setDataError(getErrorMessage(error));
    } finally {
      setLoadingData(false);
    }
  }, []);

  useEffect(() => {
    void fetchCurrentUser();
  }, [fetchCurrentUser]);

  useEffect(() => {
    if (currentUser?.role === "MODERATOR") {
      void loadModerationData();
    }
  }, [currentUser, loadModerationData]);

  const toggleReviewSelection = useCallback((reviewId: number) => {
    setSelectedReviewIds((current) => {
      const next = new Set(current);
      if (next.has(reviewId)) {
        next.delete(reviewId);
      } else {
        next.add(reviewId);
      }
      return next;
    });
  }, []);

  const executeReviewAction = useCallback(
    async (reviewIds: number[], action: "approve" | "reject", isBulk: boolean) => {
      if (reviewIds.length === 0) {
        return;
      }
      setActionFeedback(null);
      if (isBulk) {
        setBulkAction(action);
      }
      setProcessingReviewIds((current) => {
        const next = new Set(current);
        reviewIds.forEach((id) => next.add(id));
        return next;
      });
      try {
        const actionPath = action === "approve" ? "approve" : "reject";
        await Promise.all(
          reviewIds.map((reviewId) => httpClient.post(`/moderation/reviews/${reviewId}/${actionPath}`)),
        );
        setActionFeedback({
          type: "success",
          message:
            action === "approve"
              ? "Avaliação(ões) aprovada(s) com sucesso."
              : "Avaliação(ões) rejeitada(s) com sucesso.",
        });
        await loadModerationData();
      } catch (error) {
        setActionFeedback({ type: "error", message: getErrorMessage(error) });
      } finally {
        setProcessingReviewIds((current) => {
          const next = new Set(current);
          reviewIds.forEach((id) => next.delete(id));
          return next;
        });
        if (isBulk) {
          setBulkAction(null);
        }
      }
    },
    [loadModerationData],
  );

  const handleBulkAction = useCallback(
    (action: "approve" | "reject") => {
      void executeReviewAction(selectedReviewIdsArray, action, true);
    },
    [executeReviewAction, selectedReviewIdsArray],
  );

  const handleSingleReviewAction = useCallback(
    (reviewId: number, action: "approve" | "reject") => {
      void executeReviewAction([reviewId], action, false);
    },
    [executeReviewAction],
  );

  const handleChangeRequestAction = useCallback(
    async (changeRequestId: number, action: "approve" | "reject") => {
      setActionFeedback(null);
      setProcessingChangeRequestIds((current) => {
        const next = new Set(current);
        next.add(changeRequestId);
        return next;
      });
      try {
        await httpClient.post(`/moderation/change-requests/${changeRequestId}/${action}`);
        setActionFeedback({
          type: "success",
          message:
            action === "approve"
              ? "Solicitação de alteração aprovada com sucesso."
              : "Solicitação de alteração rejeitada com sucesso.",
        });
        await loadModerationData();
      } catch (error) {
        setActionFeedback({ type: "error", message: getErrorMessage(error) });
      } finally {
        setProcessingChangeRequestIds((current) => {
          const next = new Set(current);
          next.delete(changeRequestId);
          return next;
        });
      }
    },
    [loadModerationData],
  );

  if (loadingUser) {
    return (
      <div className="flex min-h-[200px] items-center justify-center text-slate-300">
        Carregando credenciais do moderador...
      </div>
    );
  }

  if (!currentUser) {
    return (
      <div className="space-y-4 text-slate-100">
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
          {userError ?? "É necessário autenticar-se como moderador para acessar este painel."}
        </div>
        <button
          type="button"
          className="inline-flex items-center rounded-lg border border-amber-500/50 bg-transparent px-4 py-2 text-sm font-medium text-amber-200 transition hover:bg-amber-500/10"
          onClick={() => void fetchCurrentUser()}
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  if (currentUser.role !== "MODERATOR") {
    return (
      <div className="space-y-4 text-slate-100">
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          Acesso restrito: apenas contas de moderador podem visualizar e atuar na fila de moderação.
        </div>
      </div>
    );
  }

  const isAllSelected =
    pendingReviews.length > 0 && pendingReviews.every((review) => selectedReviewIds.has(review.id));
  const pendingCount = pendingReviews.length;
  const changeRequestCount = changeRequests.length;
  const approvedCount = approvedReviews.length;
  const selectedCount = selectedReviewIds.size;

  return (
    <div className="space-y-8 text-slate-100">
      <section className="grid gap-6 md:grid-cols-3">
        <div className={cardClasses}>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
            Avaliações pendentes
          </h2>
          <p className="mt-4 text-3xl font-bold text-white">{pendingCount}</p>
          <p className="mt-2 text-xs text-slate-400">
            Itens aguardando análise antes de se tornarem públicos na plataforma.
          </p>
        </div>
        <div className={cardClasses}>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
            Solicitações abertas
          </h2>
          <p className="mt-4 text-3xl font-bold text-white">{changeRequestCount}</p>
          <p className="mt-2 text-xs text-slate-400">
            Mudanças sugeridas por usuários aguardando parecer de um moderador.
          </p>
        </div>
        <div className={cardClasses}>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
            Aprovações recentes
          </h2>
          <p className="mt-4 text-3xl font-bold text-white">{approvedCount}</p>
          <p className="mt-2 text-xs text-slate-400">
            Últimas avaliações liberadas para exibição pública após moderação.
          </p>
        </div>
      </section>

      {actionFeedback && (
        <div
          className={[
            "rounded-xl border px-4 py-3 text-sm",
            actionFeedback.type === "success"
              ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
              : "border-red-500/40 bg-red-500/10 text-red-200",
          ].join(" ")}
        >
          {actionFeedback.message}
        </div>
      )}

      <section className="space-y-4">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-white">Fila de moderação</h2>
            <p className="text-sm text-slate-400">
              Apenas avaliações pendentes aparecem aqui. Os autores permanecem anônimos durante todo o processo.
            </p>
          </div>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-800"
            onClick={() => void loadModerationData()}
            disabled={loadingData}
          >
            {loadingData ? "Atualizando..." : "Atualizar"}
          </button>
        </header>

        {dataError && (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {dataError}
          </div>
        )}

        {loadingData && pendingReviews.length === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-6 text-center text-sm text-slate-400">
            Carregando fila de moderação...
          </div>
        ) : pendingReviews.length === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-6 text-center text-sm text-slate-400">
            Nenhuma avaliação aguarda análise no momento.
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-sm">
              <div className="text-slate-300">
                {selectedCount > 0 ? (
                  <span>
                    {selectedCount} avaliação(ões) selecionada(s) para ação em lote.
                  </span>
                ) : (
                  <span>Selecione avaliações para aprovar ou rejeitar em lote.</span>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-200 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                  onClick={() =>
                    setSelectedReviewIds(() =>
                      isAllSelected
                        ? new Set<number>()
                        : new Set<number>(pendingReviews.map((review) => review.id)),
                    )
                  }
                  disabled={pendingReviews.length === 0}
                >
                  {isAllSelected ? "Limpar seleção" : "Selecionar todas"}
                </button>
                <button
                  type="button"
                  className="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-white shadow shadow-emerald-600/30 transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={() => handleBulkAction("approve")}
                  disabled={selectedCount === 0 || bulkAction !== null || loadingData}
                >
                  {bulkAction === "approve" ? "Aprovando..." : "Aprovar selecionadas"}
                </button>
                <button
                  type="button"
                  className="rounded-lg bg-red-600 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-white shadow shadow-red-600/30 transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={() => handleBulkAction("reject")}
                  disabled={selectedCount === 0 || bulkAction !== null || loadingData}
                >
                  {bulkAction === "reject" ? "Rejeitando..." : "Rejeitar selecionadas"}
                </button>
              </div>
            </div>

            <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
              <table className="min-w-full divide-y divide-slate-800 text-left text-sm">
                <thead className="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-400">
                  <tr>
                    <th className="px-4 py-3">
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded border-slate-600 bg-slate-900 text-slate-100 focus:ring-slate-500"
                        checked={isAllSelected}
                        onChange={() =>
                          setSelectedReviewIds(() =>
                            isAllSelected
                              ? new Set<number>()
                              : new Set<number>(pendingReviews.map((review) => review.id)),
                          )
                        }
                      />
                    </th>
                    <th className="px-4 py-3 font-semibold">Alvo</th>
                    <th className="px-4 py-3 font-semibold">Resumo</th>
                    <th className="px-4 py-3 font-semibold">Média</th>
                    <th className="px-4 py-3 font-semibold">Enviada em</th>
                    <th className="px-4 py-3 font-semibold text-right">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {pendingReviews.map((review) => {
                    const isSelected = selectedReviewIds.has(review.id);
                    const isProcessing = processingReviewIds.has(review.id);
                    return (
                      <tr key={review.id} className={isSelected ? "bg-slate-900" : "bg-slate-950/40"}>
                        <td className="px-4 py-3">
                          <input
                            type="checkbox"
                            className="h-4 w-4 rounded border-slate-600 bg-slate-900 text-slate-100 focus:ring-slate-500"
                            checked={isSelected}
                            onChange={() => toggleReviewSelection(review.id)}
                          />
                        </td>
                        <td className="px-4 py-3 align-top">
                          <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                              {TARGET_LABELS[review.target_type]}
                            </span>
                            <span className="text-sm font-semibold text-white">{review.target_name}</span>
                            {review.pending_reason && (
                              <span className="text-xs text-amber-300/90">
                                Motivo do destaque: {review.pending_reason}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 align-top text-sm text-slate-300">
                          <p className="whitespace-pre-wrap text-sm text-slate-200">{review.text}</p>
                        </td>
                        <td className="px-4 py-3 align-top text-sm font-semibold text-white">
                          {computeAverage(review)}
                        </td>
                        <td className="px-4 py-3 align-top text-sm text-slate-300">{formatDate(review.created_at)}</td>
                        <td className="px-4 py-3 align-top">
                          <div className="flex flex-col items-end gap-2">
                            <button
                              type="button"
                              className="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
                              onClick={() => handleSingleReviewAction(review.id, "approve")}
                              disabled={isProcessing || loadingData}
                            >
                              {isProcessing ? "Processando..." : "Aprovar"}
                            </button>
                            <button
                              type="button"
                              className="inline-flex items-center justify-center rounded-lg bg-red-600 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
                              onClick={() => handleSingleReviewAction(review.id, "reject")}
                              disabled={isProcessing || loadingData}
                            >
                              {isProcessing ? "Processando..." : "Rejeitar"}
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-emerald-800/40 bg-emerald-950/20 p-6 shadow-inner">
        <header className="mb-4">
          <h2 className="text-lg font-semibold text-white">Conteúdo aprovado recentemente</h2>
          <p className="text-sm text-emerald-200/80">
            Registros abaixo já estão disponíveis ao público e separados da fila pendente para evitar confusões.
          </p>
        </header>
        {approvedReviews.length === 0 ? (
          <p className="text-sm text-emerald-200/80">Nenhuma avaliação aprovada recentemente.</p>
        ) : (
          <ul className="space-y-3">
            {approvedReviews.map((review) => (
              <li key={review.id} className="rounded-xl border border-emerald-800/40 bg-emerald-900/30 p-4">
                <div className="flex flex-col gap-1 text-sm text-emerald-100">
                  <span className="text-xs font-semibold uppercase tracking-wide text-emerald-300">
                    {TARGET_LABELS[review.target_type]}
                  </span>
                  <span className="text-base font-semibold text-white">{review.target_name}</span>
                  <span className="text-xs text-emerald-200/70">Aprovada em {formatDate(review.created_at)}</span>
                  <span className="text-xs font-medium text-emerald-200/80">Média geral: {computeAverage(review)}</span>
                  <p className="mt-2 whitespace-pre-wrap text-sm text-emerald-100/90">{review.text}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-4">
        <header>
          <h2 className="text-lg font-semibold text-white">Solicitações de alteração</h2>
          <p className="text-sm text-slate-400">
            ChangeRequests aguardando decisão. Destacamos aquelas originadas de fontes oficiais validadas.
          </p>
        </header>

        {loadingData && changeRequests.length === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-6 text-center text-sm text-slate-400">
            Carregando solicitações pendentes...
          </div>
        ) : changeRequests.length === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-6 text-center text-sm text-slate-400">
            Nenhuma solicitação de alteração pendente.
          </div>
        ) : (
          <div className="space-y-3">
            {changeRequests.map((request) => {
              const isProcessing = processingChangeRequestIds.has(request.id);
              return (
                <div
                  key={request.id}
                  className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 shadow-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="space-y-2 text-sm text-slate-200">
                      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                        <span>{TARGET_LABELS[request.target_type]}</span>
                        {request.official && (
                          <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-200">
                            Fonte oficial
                          </span>
                        )}
                      </div>
                      <p className="text-base font-semibold text-white">{request.target_name}</p>
                      <p className="text-sm text-slate-300">{describeChangeRequest(request)}</p>
                      <p className="text-xs text-slate-400">Aberta em {formatDate(request.created_at)}</p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <button
                        type="button"
                        className="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
                        onClick={() => handleChangeRequestAction(request.id, "approve")}
                        disabled={isProcessing || loadingData}
                      >
                        {isProcessing ? "Processando..." : "Aprovar"}
                      </button>
                      <button
                        type="button"
                        className="inline-flex items-center justify-center rounded-lg bg-red-600 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
                        onClick={() => handleChangeRequestAction(request.id, "reject")}
                        disabled={isProcessing || loadingData}
                      >
                        {isProcessing ? "Processando..." : "Rejeitar"}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
