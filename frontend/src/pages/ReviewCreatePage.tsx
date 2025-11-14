import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { ApiError, apiFetch, buildQuery, getAuthToken } from "../lib/api";

type TargetType = "INSTITUTION" | "COURSE" | "PROFESSOR" | "SUBJECT";

type UserRole = "STUDENT" | "PROFESSOR" | "INSTITUTION" | "MODERATOR";

interface UserProfile {
  id: number;
  role: UserRole;
  validated: boolean;
}

interface InstitutionResponse {
  id: number;
  name: string;
}

interface CourseResponse {
  id: number;
  name: string;
  institution_id: number;
}

interface ProfessorResponse {
  id: number;
  name: string;
  course_id: number;
}

interface SubjectResponse {
  id: number;
  name: string;
  course_id: number;
}

interface ReviewSummary {
  id: number;
  approved: boolean;
}

interface TargetOption {
  id: number;
  label: string;
}

interface RatingsState {
  rating_1: number;
  rating_2: number;
  rating_3: number;
  rating_4: number;
  rating_5: number;
}

type RatingKey = keyof RatingsState;

const TARGET_OPTIONS: ReadonlyArray<{ value: TargetType; label: string }> = [
  { value: "INSTITUTION", label: "Instituição" },
  { value: "COURSE", label: "Curso" },
  { value: "PROFESSOR", label: "Professor" },
  { value: "SUBJECT", label: "Disciplina" },
];

const TARGET_LABELS: Record<TargetType, string> = TARGET_OPTIONS.reduce(
  (labels, option) => ({ ...labels, [option.value]: option.label }),
  {
    INSTITUTION: "Instituição",
    COURSE: "Curso",
    PROFESSOR: "Professor",
    SUBJECT: "Disciplina",
  } as Record<TargetType, string>,
);

const CRITERIA_BY_TARGET: Record<
  TargetType,
  ReadonlyArray<{ key: RatingKey; label: string; helper?: string }>
> = {
  INSTITUTION: [
    { key: "rating_1", label: "Estrutura física" },
    { key: "rating_2", label: "Serviços estudantis" },
    { key: "rating_3", label: "Transparência administrativa" },
    { key: "rating_4", label: "Atendimento institucional" },
    { key: "rating_5", label: "Inclusão e acessibilidade" },
  ],
  COURSE: [
    { key: "rating_1", label: "Organização curricular" },
    { key: "rating_2", label: "Integração teoria e prática" },
    { key: "rating_3", label: "Infraestrutura dedicada" },
    { key: "rating_4", label: "Suporte acadêmico" },
    { key: "rating_5", label: "Atualização de conteúdos" },
  ],
  PROFESSOR: [
    { key: "rating_1", label: "Didática" },
    { key: "rating_2", label: "Clareza na avaliação" },
    { key: "rating_3", label: "Disponibilidade para dúvidas" },
    { key: "rating_4", label: "Feedbacks construtivos" },
    { key: "rating_5", label: "Atualização do conteúdo" },
  ],
  SUBJECT: [
    { key: "rating_1", label: "Clareza do conteúdo" },
    { key: "rating_2", label: "Carga de trabalho" },
    { key: "rating_3", label: "Relevância para o curso" },
    { key: "rating_4", label: "Material de apoio" },
    { key: "rating_5", label: "Integração com outras disciplinas" },
  ],
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

const ratingRange = { min: 1, max: 5 } as const;

type DuplicateStatus = "idle" | "checking" | "duplicate" | "unique" | "error";

function createInitialRatings(): RatingsState {
  return {
    rating_1: 3,
    rating_2: 3,
    rating_3: 3,
    rating_4: 3,
    rating_5: 3,
  };
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.detail) {
      return error.detail;
    }
    if (typeof error.payload === "string" && error.payload.trim().length > 0) {
      return error.payload;
    }
    if (error.status === 401) {
      return "Sua sessão expirou ou você não está autenticado.";
    }
    if (error.status === 403) {
      return "Você não tem permissão para realizar esta ação.";
    }
    return `Erro ao comunicar com a API (status ${error.status}).`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Ocorreu um erro inesperado. Tente novamente.";
}

export default function ReviewCreatePage() {
  const [targetType, setTargetType] = useState<TargetType>("INSTITUTION");
  const [ratings, setRatings] = useState<RatingsState>(() => createInitialRatings());
  const [reviewText, setReviewText] = useState("");

  const [targetOptions, setTargetOptions] = useState<TargetOption[]>([]);
  const [selectedTargetId, setSelectedTargetId] = useState("");
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [loadingOptions, setLoadingOptions] = useState(false);

  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [authMessage, setAuthMessage] = useState<string | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const [duplicateStatus, setDuplicateStatus] = useState<DuplicateStatus>("idle");
  const [duplicateMessage, setDuplicateMessage] = useState<string | null>(null);

  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const criteria = useMemo(() => CRITERIA_BY_TARGET[targetType], [targetType]);

  const fetchCurrentUser = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      setCurrentUser(null);
      setAuthMessage("É necessário entrar na plataforma para enviar avaliações.");
      setLoadingUser(false);
      return;
    }

    setLoadingUser(true);
    try {
      const user = await apiFetch<UserProfile>("/users/me");
      setCurrentUser(user);
      if (user.role !== "STUDENT") {
        setAuthMessage(
          "Apenas estudantes podem criar avaliações. Utilize uma conta de estudante para continuar.",
        );
      } else {
        setAuthMessage(null);
      }
    } catch (error) {
      console.error("Failed to load current user", error);
      setCurrentUser(null);
      setAuthMessage(getErrorMessage(error));
    } finally {
      setLoadingUser(false);
    }
  }, []);

  useEffect(() => {
    void fetchCurrentUser();
  }, [fetchCurrentUser]);

  const loadTargetOptions = useCallback(async (type: TargetType): Promise<TargetOption[]> => {
    switch (type) {
      case "INSTITUTION": {
        const institutions = await apiFetch<InstitutionResponse[]>(
          `/institutions${buildQuery({ limit: 200 })}`,
        );
        return institutions.map((institution) => ({ id: institution.id, label: institution.name }));
      }
      case "COURSE": {
        const courses = await apiFetch<CourseResponse[]>("/courses/");
        return courses.map((course) => ({ id: course.id, label: course.name }));
      }
      case "PROFESSOR": {
        const professors = await apiFetch<ProfessorResponse[]>("/professors");
        return professors.map((professor) => ({ id: professor.id, label: professor.name }));
      }
      case "SUBJECT": {
        const subjects = await apiFetch<SubjectResponse[]>("/subjects");
        return subjects.map((subject) => ({ id: subject.id, label: subject.name }));
      }
      default:
        return [];
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    setLoadingOptions(true);
    setOptionsError(null);
    setSelectedTargetId("");
    setDuplicateStatus("idle");
    setDuplicateMessage(null);

    loadTargetOptions(targetType)
      .then((options) => {
        if (!isMounted) {
          return;
        }
        setTargetOptions(options);
        if (options.length === 1) {
          setSelectedTargetId(String(options[0]?.id ?? ""));
        }
      })
      .catch((error) => {
        if (!isMounted) {
          return;
        }
        console.error("Failed to load target options", error);
        setTargetOptions([]);
        setOptionsError(getErrorMessage(error));
      })
      .finally(() => {
        if (isMounted) {
          setLoadingOptions(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [loadTargetOptions, targetType]);

  const checkDuplicate = useCallback(
    async (userId: number, type: TargetType, targetId: number): Promise<boolean> => {
      const query = buildQuery({
        target_type: type,
        target_id: targetId,
        user_id: userId,
        include_pending: true,
        limit: 1,
      });
      const reviews = await apiFetch<ReviewSummary[]>(`/reviews${query}`);
      return reviews.length > 0;
    },
    [],
  );

  useEffect(() => {
    if (!currentUser || currentUser.role !== "STUDENT" || selectedTargetId === "") {
      setDuplicateStatus("idle");
      setDuplicateMessage(null);
      return;
    }

    let isActive = true;
    setDuplicateStatus("checking");
    const targetId = Number(selectedTargetId);

    checkDuplicate(currentUser.id, targetType, targetId)
      .then((exists) => {
        if (!isActive) {
          return;
        }
        if (exists) {
          setDuplicateStatus("duplicate");
          setDuplicateMessage(
            "Você já enviou uma avaliação para este alvo. Aguarde a moderação ou solicite revisão se necessário.",
          );
        } else {
          setDuplicateStatus("unique");
          setDuplicateMessage(null);
        }
      })
      .catch((error) => {
        if (!isActive) {
          return;
        }
        console.error("Failed to check duplicate review", error);
        setDuplicateStatus("error");
        setDuplicateMessage(
          "Não foi possível verificar duplicidade agora. Tente novamente antes de enviar.",
        );
      });

    return () => {
      isActive = false;
    };
  }, [checkDuplicate, currentUser, selectedTargetId, targetType]);

  const handleRatingChange = useCallback((key: RatingKey, value: number) => {
    setRatings((previous) => ({ ...previous, [key]: value }));
  }, []);

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setFormError(null);
      setSuccessMessage(null);

      if (loadingUser) {
        setFormError("Carregando informações do usuário. Aguarde um instante.");
        return;
      }

      if (!currentUser) {
        setFormError("Faça login como estudante para enviar uma avaliação.");
        return;
      }

      if (currentUser.role !== "STUDENT") {
        setFormError("Somente estudantes podem criar avaliações no OpenCampus.");
        return;
      }

      if (!selectedTargetId) {
        setFormError(`Selecione uma ${TARGET_LABELS[targetType].toLowerCase()} para avaliar.`);
        return;
      }

      const numericTargetId = Number(selectedTargetId);
      if (Number.isNaN(numericTargetId)) {
        setFormError("Alvo selecionado inválido. Escolha novamente na lista.");
        return;
      }

      const trimmedText = reviewText.trim();
      if (trimmedText.length === 0) {
        setFormError("Descreva sua experiência antes de enviar a avaliação.");
        return;
      }

      setIsSubmitting(true);

      try {
        const duplicate = await checkDuplicate(currentUser.id, targetType, numericTargetId);
        if (duplicate) {
          setDuplicateStatus("duplicate");
          setFormError(
            "Já existe uma avaliação sua para este alvo. Consulte a moderação para ajustes se necessário.",
          );
          return;
        }

        const payload: Record<string, number | string | null> = {
          target_type: targetType,
          rating_1: ratings.rating_1,
          rating_2: ratings.rating_2,
          rating_3: ratings.rating_3,
          rating_4: ratings.rating_4,
          rating_5: ratings.rating_5,
          text: trimmedText,
          institution_id: targetType === "INSTITUTION" ? numericTargetId : null,
          course_id: targetType === "COURSE" ? numericTargetId : null,
          professor_id: targetType === "PROFESSOR" ? numericTargetId : null,
          subject_id: targetType === "SUBJECT" ? numericTargetId : null,
        };

        await apiFetch("/reviews", {
          method: "POST",
          body: JSON.stringify(payload),
        });

        setSuccessMessage(
          "Avaliação enviada com sucesso! Ela ficará pendente de moderação e só aparecerá publicamente após aprovação de um moderador.",
        );
        setReviewText("");
        setRatings(createInitialRatings());
        setSelectedTargetId("");
        setDuplicateStatus("idle");
        setDuplicateMessage(null);
      } catch (error) {
        console.error("Failed to submit review", error);
        setFormError(getErrorMessage(error));
      } finally {
        setIsSubmitting(false);
      }
    },
    [
      checkDuplicate,
      currentUser,
      loadingUser,
      ratings.rating_1,
      ratings.rating_2,
      ratings.rating_3,
      ratings.rating_4,
      ratings.rating_5,
      reviewText,
      selectedTargetId,
      targetType,
    ],
  );

  const isSubmitDisabled = useMemo(() => {
    if (loadingUser || isSubmitting) {
      return true;
    }
    if (!currentUser || currentUser.role !== "STUDENT") {
      return true;
    }
    if (!selectedTargetId) {
      return true;
    }
    if (duplicateStatus === "checking" || duplicateStatus === "duplicate") {
      return true;
    }
    return false;
  }, [currentUser, duplicateStatus, isSubmitting, loadingUser, selectedTargetId]);

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Enviar avaliação moderada</h1>
        <p className="text-sm text-slate-600">
          Escolha o tipo de alvo, preencha os critérios obrigatórios e compartilhe sua experiência. Todas as avaliações são
          anônimas para o público e começam como pendentes até a moderação concluir a análise.
        </p>
      </header>

      {authMessage && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {authMessage}
        </div>
      )}

      {formError && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {formError}
        </div>
      )}

      {successMessage && (
        <div className="space-y-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          <p>{successMessage}</p>
          <p>
            Enquanto a moderação analisa o conteúdo, ele não impactará métricas públicas. Você poderá visualizar sua submissão
            marcada como pendente sempre que ativar o filtro específico na área autenticada.
          </p>
        </div>
      )}

      <form className="space-y-6" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700">Tipo de alvo</label>
          <select
            value={targetType}
            onChange={(event) => {
              setTargetType(event.target.value as TargetType);
              setSuccessMessage(null);
              setFormError(null);
            }}
            className={fieldClasses}
          >
            {TARGET_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-slate-500">
            O backend garante que cada estudante envie apenas uma avaliação por alvo associado. A checagem local ajuda a evitar
            duplicidades acidentais antes do envio.
          </p>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700">
            {`Selecione a ${TARGET_LABELS[targetType].toLowerCase()} que deseja avaliar`}
          </label>
          <select
            value={selectedTargetId}
            onChange={(event) => {
              setSelectedTargetId(event.target.value);
              setSuccessMessage(null);
              setFormError(null);
            }}
            className={fieldClasses}
            disabled={loadingOptions || targetOptions.length === 0}
          >
            <option value="">Selecione uma opção</option>
            {targetOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
          {loadingOptions && <p className="text-xs text-slate-500">Carregando opções disponíveis...</p>}
          {optionsError && (
            <p className="text-xs text-red-600">
              {optionsError} Tente novamente mais tarde ou contate a moderação se o problema persistir.
            </p>
          )}
          {!loadingOptions && targetOptions.length === 0 && !optionsError && (
            <p className="text-xs text-slate-500">
              Nenhum registro foi encontrado para este tipo. Solicite cadastro via pedido de alteração se necessário.
            </p>
          )}
          {duplicateStatus === "checking" && (
            <p className="text-xs text-slate-500">Verificando se já existe uma avaliação sua para este alvo...</p>
          )}
          {duplicateMessage && duplicateStatus !== "checking" && (
            <p className="text-xs text-red-600">{duplicateMessage}</p>
          )}
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Critérios obrigatórios</h2>
          {criteria.map((criterion) => (
            <div key={criterion.key} className="space-y-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium text-slate-900">{criterion.label}</span>
                  {criterion.helper && <p className="text-xs text-slate-500">{criterion.helper}</p>}
                </div>
                <span className="inline-flex items-center rounded-full bg-slate-900 px-2 py-0.5 text-xs font-semibold text-white">
                  {ratings[criterion.key]}
                </span>
              </div>
              <input
                type="range"
                min={ratingRange.min}
                max={ratingRange.max}
                value={ratings[criterion.key]}
                onChange={(event) => handleRatingChange(criterion.key, Number(event.target.value))}
                className="w-full accent-slate-900"
              />
              <div className="flex justify-between text-[11px] text-slate-500">
                <span>1</span>
                <span>2</span>
                <span>3</span>
                <span>4</span>
                <span>5</span>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700">Relato detalhado</label>
          <textarea
            rows={6}
            className={fieldClasses}
            placeholder="Conte como foi sua experiência. Dados pessoais nunca são exibidos publicamente."
            value={reviewText}
            onChange={(event) => setReviewText(event.target.value)}
          />
          <p className="text-xs text-slate-500">
            Ao enviar você confirma que suas informações são verdadeiras e compreende que o conteúdo passará por moderação antes
            de qualquer publicação.
          </p>
        </div>

        <button type="submit" className={submitButtonClasses} disabled={isSubmitDisabled}>
          {isSubmitting ? "Enviando avaliação..." : "Enviar avaliação para moderação"}
        </button>
      </form>
    </div>
  );
}
