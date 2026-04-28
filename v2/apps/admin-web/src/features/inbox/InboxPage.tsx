import {
  Badge,
  Box,
  Button,
  Heading,
  HStack,
  Spinner,
  Stack,
  Text,
  VStack,
  Wrap,
  WrapItem,
} from "@chakra-ui/react";
import type { MutableRefObject } from "react";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import { apiFetchInit } from "../../lib/consoleAuth";

const listEnvironment = (): string =>
  import.meta.env.VITE_WABA_ENV ?? "production";

const phoneIdStorageKey = (environment: string) =>
  `open-bsp:inbox:phone_number_id:${environment}`;

function readStoredPhoneNumberId(environment: string): string | null {
  try {
    return sessionStorage.getItem(phoneIdStorageKey(environment));
  } catch {
    return null;
  }
}

type WabaLine = {
  id: string;
  waba_id: string;
  phone_number_id: string;
  display_phone_number: string;
  environment: string;
  status: string;
};

async function readErrorMessage(r: Response): Promise<string> {
  const t = await r.text();
  try {
    const j = JSON.parse(t) as { message?: string };
    if (j.message) {
      return j.message;
    }
  } catch {
    /* ignore */
  }
  return t.slice(0, 400) || r.statusText;
}

type DisambiguationOpts = {
  env: string;
  phoneNumberIdRef: MutableRefObject<string | null>;
  setPhoneNumberId: (v: string | null) => void;
  setLineChoices: (v: WabaLine[]) => void;
  apiPath: (path: string) => string;
  apiInit: () => ReturnType<typeof apiFetchInit>;
};

async function fetchWithInboxLineDisambiguation(
  doFetch: (phoneId: string | null) => Promise<Response>,
  opts: DisambiguationOpts,
): Promise<Response> {
  const pid = opts.phoneNumberIdRef.current;
  const r = await doFetch(pid);
  if (r.status !== 409) {
    return r;
  }
  let conflictMsg =
    "Varias linhas WhatsApp neste ambiente; escolha o numero de envio.";
  try {
    const body = (await r.json()) as { message?: string };
    if (body?.message) {
      conflictMsg = body.message;
    }
  } catch {
    /* ignore */
  }
  const wabaR = await fetch(
    opts.apiPath(
      `/v1/me/waba-phone-numbers?environment=${encodeURIComponent(opts.env)}&limit=100`,
    ),
    opts.apiInit(),
  );
  if (!wabaR.ok) {
    throw new Error(
      `${conflictMsg} (falha ao listar numeros WABA: HTTP ${wabaR.status}).`,
    );
  }
  const wabaData = (await wabaR.json()) as { items?: WabaLine[] };
  const lines = wabaData.items ?? [];
  if (lines.length === 1) {
    const onlyId = lines[0].phone_number_id;
    try {
      sessionStorage.setItem(phoneIdStorageKey(opts.env), onlyId);
    } catch {
      /* ignore */
    }
    opts.setPhoneNumberId(onlyId);
    opts.setLineChoices([]);
    return doFetch(onlyId);
  }
  if (lines.length > 1) {
    opts.setLineChoices(lines);
    throw new Error(conflictMsg);
  }
  throw new Error(
    `${conflictMsg} Nenhum numero WABA registado para listar.`,
  );
}

type InboxHeader = {
  tenant_display_name: string;
  environment: string;
  waba: {
    waba_id: string;
    phone_number_id: string;
    display_phone_number: string;
  } | null;
};

type TagBrief = {
  id: string;
  name: string;
};

type ConvItem = {
  id: string;
  title: string | null;
  contact_wa_id: string;
  waba_id: string;
  last_message_at: string | null;
  tags?: TagBrief[];
};

type ListResponse = {
  header: InboxHeader;
  items: ConvItem[];
  limit: number;
  next_cursor: string | null;
};

type ThreadMsg = {
  id: string;
  source_id: string;
  message_type: string;
  body: string | null;
  received_at: string | null;
};

type ThreadResponse = {
  conversation_id: string;
  header: InboxHeader;
  items: ThreadMsg[];
  tags?: TagBrief[];
};

type HandoffResponse = {
  conversation_id: string;
  intent_summary: string | null;
  bot_last_output: string | null;
  handoff_state: string;
  queue_id: string | null;
  claimed_by_user_id: string | null;
  updated_at: string | null;
};

type AllTagsResponse = {
  items: TagBrief[];
};

export default function InboxPage() {
  const env = listEnvironment();
  const qc = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [mobilePane, setMobilePane] = useState<"list" | "thread">("list");
  const [phoneNumberId, setPhoneNumberId] = useState<string | null>(() =>
    typeof window !== "undefined" ? readStoredPhoneNumberId(listEnvironment()) : null,
  );
  const [lineChoices, setLineChoices] = useState<WabaLine[]>([]);
  const [queueInput, setQueueInput] = useState("");
  const phoneNumberIdRef = useRef(phoneNumberId);
  phoneNumberIdRef.current = phoneNumberId;

  const apiPath = useCallback(
    (path: string) => `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`,
    [],
  );

  const apiInit = useCallback(
    () =>
      apiFetchInit({
        "X-Console-Environment": env,
        "X-Environment": env,
      }),
    [env],
  );

  const disambiguationOpts = {
    env,
    phoneNumberIdRef,
    setPhoneNumberId,
    setLineChoices,
    apiPath,
    apiInit,
  } satisfies DisambiguationOpts;

  const allTagsQuery = useQuery({
    queryKey: ["inbox", "allTags"],
    queryFn: async (): Promise<AllTagsResponse> => {
      const r = await fetch(apiPath("/v1/me/inbox/tags"), apiInit());
      if (!r.ok) {
        throw new Error(await readErrorMessage(r));
      }
      return r.json() as Promise<AllTagsResponse>;
    },
  });

  const listQuery = useQuery({
    queryKey: ["inbox", "conversations", env, phoneNumberId],
    staleTime: 30_000,
    placeholderData: keepPreviousData,
    queryFn: async (): Promise<ListResponse> => {
      const doFetch = (pid: string | null) => {
        const q = new URLSearchParams({ environment: env });
        if (pid) {
          q.set("phone_number_id", pid);
        }
        return fetch(
          apiPath(`/v1/me/conversations?${q.toString()}`),
          apiInit(),
        );
      };
      const r = await fetchWithInboxLineDisambiguation(doFetch, disambiguationOpts);
      if (!r.ok) {
        throw new Error(await readErrorMessage(r));
      }
      setLineChoices([]);
      return r.json() as Promise<ListResponse>;
    },
  });

  const threadQuery = useQuery({
    queryKey: ["inbox", "thread", selectedId, env, phoneNumberId],
    enabled: Boolean(selectedId),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
    queryFn: async (): Promise<ThreadResponse> => {
      const doFetch = (pid: string | null) => {
        const q = new URLSearchParams({ environment: env });
        if (pid) {
          q.set("phone_number_id", pid);
        }
        return fetch(
          apiPath(
            `/v1/me/conversations/${encodeURIComponent(selectedId!)}/messages?${q.toString()}`,
          ),
          apiInit(),
        );
      };
      const r = await fetchWithInboxLineDisambiguation(doFetch, disambiguationOpts);
      if (!r.ok) {
        throw new Error(await readErrorMessage(r));
      }
      setLineChoices([]);
      return r.json() as Promise<ThreadResponse>;
    },
  });

  const handoffQuery = useQuery({
    queryKey: ["inbox", "handoff", selectedId, env],
    enabled: Boolean(selectedId),
    staleTime: 15_000,
    queryFn: async (): Promise<HandoffResponse> => {
      const q = new URLSearchParams({ environment: env });
      const r = await fetch(
        apiPath(
          `/v1/me/conversations/${encodeURIComponent(selectedId!)}/handoff?${q}`,
        ),
        apiInit(),
      );
      if (!r.ok) {
        throw new Error(await readErrorMessage(r));
      }
      return r.json() as Promise<HandoffResponse>;
    },
  });

  useEffect(() => {
    const d = handoffQuery.data;
    if (d) {
      setQueueInput(d.queue_id ?? "");
    }
  }, [handoffQuery.data]);

  const patchTags = useMutation({
    mutationFn: async (opts: { conversationId: string; tagIds: string[] }) => {
      const q = new URLSearchParams({ environment: env });
      if (phoneNumberId) {
        q.set("phone_number_id", phoneNumberId);
      }
      const base = apiInit();
      const r = await fetch(
        apiPath(
          `/v1/me/conversations/${encodeURIComponent(opts.conversationId)}/tags?${q}`,
        ),
        {
          ...base,
          method: "PATCH",
          headers: { ...base.headers, "Content-Type": "application/json" },
          body: JSON.stringify({ tag_ids: opts.tagIds }),
        },
      );
      if (!r.ok) {
        throw new Error(await readErrorMessage(r));
      }
      return r.json() as Promise<{ conversation_id: string; tags: TagBrief[] }>;
    },
    onMutate: async (opts) => {
      await qc.cancelQueries({
        queryKey: ["inbox", "conversations", env, phoneNumberId],
      });
      await qc.cancelQueries({
        queryKey: ["inbox", "thread", opts.conversationId, env, phoneNumberId],
      });
      const catalog = allTagsQuery.data?.items ?? [];
      const idSet = new Set(opts.tagIds);
      const newTags = catalog.filter((t) => idSet.has(t.id));

      const prevList = qc.getQueryData<ListResponse>([
        "inbox",
        "conversations",
        env,
        phoneNumberId,
      ]);
      const prevThread = qc.getQueryData<ThreadResponse>([
        "inbox",
        "thread",
        opts.conversationId,
        env,
        phoneNumberId,
      ]);

      if (prevList) {
        qc.setQueryData<ListResponse>(
          ["inbox", "conversations", env, phoneNumberId],
          {
            ...prevList,
            items: prevList.items.map((it) =>
              it.id === opts.conversationId ? { ...it, tags: newTags } : it,
            ),
          },
        );
      }
      if (prevThread) {
        qc.setQueryData<ThreadResponse>(
          ["inbox", "thread", opts.conversationId, env, phoneNumberId],
          { ...prevThread, tags: newTags },
        );
      }
      return { prevList, prevThread };
    },
    onError: (_err, vars, ctx) => {
      if (ctx?.prevList) {
        qc.setQueryData(
          ["inbox", "conversations", env, phoneNumberId],
          ctx.prevList,
        );
      }
      if (ctx?.prevThread && vars.conversationId) {
        qc.setQueryData(
          ["inbox", "thread", vars.conversationId, env, phoneNumberId],
          ctx.prevThread,
        );
      }
    },
    onSettled: (_data, _err, vars) => {
      qc.invalidateQueries({
        queryKey: ["inbox", "conversations", env, phoneNumberId],
      });
      if (vars?.conversationId) {
        qc.invalidateQueries({
          queryKey: ["inbox", "thread", vars.conversationId, env, phoneNumberId],
        });
      }
    },
  });

  const patchHandoff = useMutation({
    mutationFn: async (patch: { accept?: boolean; queue_id?: string | null }) => {
      if (!selectedId) {
        throw new Error("no conversation selected");
      }
      const q = new URLSearchParams({ environment: env });
      const base = apiInit();
      const r = await fetch(
        apiPath(
          `/v1/me/conversations/${encodeURIComponent(selectedId)}/handoff?${q}`,
        ),
        {
          ...base,
          method: "PATCH",
          headers: { ...base.headers, "Content-Type": "application/json" },
          body: JSON.stringify(patch),
        },
      );
      if (!r.ok) {
        throw new Error(await readErrorMessage(r));
      }
      return r.json() as Promise<HandoffResponse>;
    },
    onSuccess: (data) => {
      qc.setQueryData(["inbox", "handoff", selectedId, env], data);
      setQueueInput(data.queue_id ?? "");
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["inbox", "handoff", selectedId, env] });
    },
  });

  const header = listQuery.data?.header ?? threadQuery.data?.header;

  const selectConv = (id: string) => {
    setSelectedId(id);
    setMobilePane("thread");
  };

  const threadTags: TagBrief[] =
    threadQuery.data?.tags ??
    listQuery.data?.items.find((x) => x.id === selectedId)?.tags ??
    [];

  const addableTags =
    allTagsQuery.data?.items.filter(
      (t) => !threadTags.some((c) => c.id === t.id),
    ) ?? [];

  return (
    <VStack data-testid="inbox-root" align="stretch" gap={3}>
      {header ? (
        <Box
          data-testid="inbox-header"
          borderWidth="1px"
          rounded="md"
          p={3}
          bg="bg.subtle"
        >
          <Text fontWeight="medium">{header.tenant_display_name}</Text>
          <Text fontSize="sm" color="fg.muted">
            {header.environment}
            {header.waba
              ? ` · ${header.waba.display_phone_number} (${header.waba.waba_id})`
              : ""}
          </Text>
        </Box>
      ) : listQuery.isLoading ? (
        <HStack data-testid="inbox-header-skeleton">
          <Spinner size="sm" />
          <Text color="fg.muted">A carregar contexto...</Text>
        </HStack>
      ) : null}

      {phoneNumberId ? (
        <Text fontSize="xs" color="fg.muted" data-testid="inbox-phone-ref">
          Meta phone_number_id: {phoneNumberId}
        </Text>
      ) : null}

      {lineChoices.length > 1 ? (
        <VStack align="stretch" gap={2} data-testid="inbox-line-picker">
          <Text fontSize="sm" fontWeight="medium">
            Linha de envio (obrigatoria neste ambiente)
          </Text>
          <select
            aria-label="Escolher linha WhatsApp para inbox"
            value={phoneNumberId ?? ""}
            onChange={(e) => {
              const v = e.target.value;
              const next = v.length > 0 ? v : null;
              setPhoneNumberId(next);
              if (next) {
                try {
                  sessionStorage.setItem(phoneIdStorageKey(env), next);
                } catch {
                  /* ignore */
                }
              } else {
                try {
                  sessionStorage.removeItem(phoneIdStorageKey(env));
                } catch {
                  /* ignore */
                }
              }
            }}
          >
            <option value="">Selecione o numero...</option>
            {lineChoices.map((ln) => (
              <option key={ln.id} value={ln.phone_number_id}>
                {ln.display_phone_number} / {ln.waba_id}
              </option>
            ))}
          </select>
        </VStack>
      ) : null}

      {listQuery.isError ? (
        <Text color="red.fg" data-testid="inbox-list-error">
          {(listQuery.error as Error).message}
        </Text>
      ) : null}

      {patchTags.isError ? (
        <Text color="red.fg" data-testid="inbox-tags-error">
          {(patchTags.error as Error).message}
        </Text>
      ) : null}

      {patchHandoff.isError ? (
        <Text color="red.fg" data-testid="inbox-handoff-mutation-error">
          {(patchHandoff.error as Error).message}
        </Text>
      ) : null}

      {allTagsQuery.isError ? (
        <Text color="red.fg" role="alert" data-testid="inbox-catalog-error">
          Não foi possível carregar o catálogo de etiquetas:{" "}
          {(allTagsQuery.error as Error).message}
        </Text>
      ) : null}

      <Stack
        direction={{ base: "column", md: "row" }}
        gap={4}
        align="stretch"
      >
        <Box
          display={{ base: mobilePane === "list" ? "block" : "none", md: "block" }}
          minW={{ md: "280px" }}
          maxW={{ md: "360px" }}
          flexShrink={0}
          borderWidth="1px"
          rounded="md"
          p={2}
        >
          <Heading size="sm" mb={2}>
            Conversations
          </Heading>
          {listQuery.isLoading && !listQuery.data ? (
            <HStack data-testid="inbox-list-skeleton">
              <Spinner size="sm" />
              <Text fontSize="sm" color="fg.muted">
                A carregar conversas...
              </Text>
            </HStack>
          ) : (
            <VStack align="stretch" gap={1}>
              {listQuery.data?.items.map((c) => (
                <Button
                  key={c.id}
                  size="sm"
                  variant={selectedId === c.id ? "solid" : "ghost"}
                  justifyContent="flex-start"
                  onClick={() => selectConv(c.id)}
                  data-testid={`inbox-conv-${c.id}`}
                >
                  <VStack align="start" gap={1} w="full">
                    <Text fontWeight="medium">
                      {c.title ?? `+${c.contact_wa_id}`}
                    </Text>
                    <Text fontSize="xs" color="fg.muted">
                      {c.last_message_at ?? "?"}
                    </Text>
                    {(c.tags?.length ?? 0) > 0 ? (
                      <Wrap gap={1} w="full">
                        {(c.tags ?? []).map((t) => (
                          <WrapItem key={t.id}>
                            <Badge size="sm" variant="surface">
                              {t.name}
                            </Badge>
                          </WrapItem>
                        ))}
                      </Wrap>
                    ) : null}
                  </VStack>
                </Button>
              ))}
              {listQuery.data?.items.length === 0 ? (
                <Text fontSize="sm" color="fg.muted">
                  No conversations yet.
                </Text>
              ) : null}
            </VStack>
          )}
        </Box>

        <Box
          flex="1"
          display={{
            base: mobilePane === "thread" ? "block" : "none",
            md: "block",
          }}
          borderWidth="1px"
          rounded="md"
          p={3}
          minH={{ md: "320px" }}
        >
          <HStack mb={2} display={{ base: "flex", md: "none" }}>
            <Button
              size="xs"
              variant="ghost"
              onClick={() => {
                setMobilePane("list");
              }}
            >
              Lista
            </Button>
          </HStack>
          {!selectedId ? (
            <Text color="fg.muted" data-testid="inbox-thread-placeholder">
              Select a conversation.
            </Text>
          ) : threadQuery.isLoading ? (
            <HStack data-testid="inbox-thread-skeleton">
              <Spinner size="sm" />
              <Text fontSize="sm" color="fg.muted">
                A carregar mensagens...
              </Text>
            </HStack>
          ) : threadQuery.isError ? (
            <Text color="red.fg" data-testid="inbox-thread-error">
              {(threadQuery.error as Error).message}
            </Text>
          ) : (
            <VStack data-testid="inbox-thread" align="stretch" gap={2}>
              <Box
                data-testid="inbox-handoff-panel"
                borderWidth="1px"
                rounded="md"
                p={2}
                bg="bg.muted"
              >
                <Text fontSize="xs" color="fg.muted" mb={1}>
                  Handoff / automacao
                </Text>
                {handoffQuery.isLoading ? (
                  <HStack>
                    <Spinner size="sm" />
                    <Text fontSize="sm" color="fg.muted">
                      A carregar contexto de handoff...
                    </Text>
                  </HStack>
                ) : null}
                {handoffQuery.isError ? (
                  <Text color="red.fg" data-testid="inbox-handoff-error">
                    {(handoffQuery.error as Error).message}
                  </Text>
                ) : null}
                {handoffQuery.data ? (
                  <VStack align="stretch" gap={2}>
                    <HStack flexWrap="wrap" gap={2} align="center">
                      <Text fontSize="sm" fontWeight="medium">
                        Estado:
                      </Text>
                      <Badge
                        variant="surface"
                        data-testid="inbox-handoff-state"
                        colorPalette={
                          handoffQuery.data.handoff_state === "failed"
                            ? "red"
                            : "gray"
                        }
                      >
                        {handoffQuery.data.handoff_state}
                      </Badge>
                      {handoffQuery.data.handoff_state === "failed" ? (
                        <Text fontSize="xs" color="red.fg">
                          Pipeline ou automacao falhou; assuma ou reencamie.
                        </Text>
                      ) : null}
                    </HStack>
                    {handoffQuery.data.intent_summary ? (
                      <Box>
                        <Text fontSize="xs" color="fg.muted">
                          Intencao (resumo)
                        </Text>
                        <Text fontSize="sm" data-testid="inbox-handoff-intent">
                          {handoffQuery.data.intent_summary}
                        </Text>
                      </Box>
                    ) : null}
                    {handoffQuery.data.bot_last_output ? (
                      <Box>
                        <Text fontSize="xs" color="fg.muted">
                          Ultima saida do bot
                        </Text>
                        <Text fontSize="sm" data-testid="inbox-handoff-bot">
                          {handoffQuery.data.bot_last_output}
                        </Text>
                      </Box>
                    ) : null}
                    <HStack flexWrap="wrap" gap={2} align="flex-end">
                      <Box flex="1" minW="140px">
                        <Text fontSize="xs" color="fg.muted" mb={1}>
                          Fila (supervisao ? org_admin)
                        </Text>
                        <input
                          aria-label="Queue id para roteamento"
                          value={queueInput}
                          onChange={(e) => setQueueInput(e.target.value)}
                          style={{
                            width: "100%",
                            padding: "0.35rem 0.5rem",
                            borderRadius: "0.25rem",
                            border: "1px solid #ccc",
                          }}
                        />
                      </Box>
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={patchHandoff.isPending}
                        onClick={() =>
                          patchHandoff.mutate({
                            queue_id:
                              queueInput.trim() === ""
                                ? null
                                : queueInput.trim(),
                          })
                        }
                      >
                        Guardar fila
                      </Button>
                    </HStack>
                    {["pending_handoff", "queued", "failed"].includes(
                      handoffQuery.data.handoff_state,
                    ) ? (
                      <Button
                        size="sm"
                        data-testid="inbox-handoff-accept"
                        disabled={patchHandoff.isPending}
                        onClick={() => patchHandoff.mutate({ accept: true })}
                      >
                        Assumir conversa
                      </Button>
                    ) : null}
                  </VStack>
                ) : null}
              </Box>
              <Box data-testid="inbox-tags-row">
                <Text fontSize="xs" color="fg.muted" mb={1}>
                  Tags
                </Text>
                <HStack flexWrap="wrap" gap={1} align="center">
                  {threadTags.map((t) => (
                    <Badge
                      key={t.id}
                      variant="surface"
                      data-testid={`inbox-tag-chip-${t.id}`}
                    >
                      <HStack gap={1} align="center">
                        <Text fontSize="xs">{t.name}</Text>
                        <Button
                          aria-label={`remove ${t.name}`}
                          size="2xs"
                          variant="ghost"
                          minW={4}
                          h={4}
                          p={0}
                          disabled={patchTags.isPending}
                          onClick={() =>
                            patchTags.mutate({
                              conversationId: selectedId,
                              tagIds: threadTags
                                .filter((x) => x.id !== t.id)
                                .map((x) => x.id),
                            })
                          }
                        >
                          ×
                        </Button>
                      </HStack>
                    </Badge>
                  ))}
                  {addableTags.length > 0 ? (
                    <HStack gap={1} flexWrap="wrap">
                      {addableTags.slice(0, 6).map((t) => (
                        <Button
                          key={t.id}
                          size="2xs"
                          variant="outline"
                          disabled={patchTags.isPending}
                          onClick={() =>
                            patchTags.mutate({
                              conversationId: selectedId,
                              tagIds: [...threadTags.map((x) => x.id), t.id],
                            })
                          }
                        >
                          + {t.name}
                        </Button>
                      ))}
                      {addableTags.length > 6 ? (
                        <Text fontSize="xs" color="fg.muted">
                          +{addableTags.length - 6} mais
                        </Text>
                      ) : null}
                    </HStack>
                  ) : null}
                </HStack>
              </Box>
              {threadQuery.data?.items.map((m) => (
                <Box
                  key={m.id}
                  borderWidth="1px"
                  rounded="md"
                  p={2}
                  data-testid={`inbox-msg-${m.id}`}
                >
                  <Text fontSize="xs" color="fg.muted">
                    {m.received_at ?? m.source_id}
                  </Text>
                  <Text fontSize="sm">{m.body ?? `[${m.message_type}]`}</Text>
                </Box>
              ))}
              {threadQuery.data?.items.length === 0 ? (
                <Text fontSize="sm" color="fg.muted">
                  No messages in this thread.
                </Text>
              ) : null}
            </VStack>
          )}
        </Box>
      </Stack>
    </VStack>
  );
}
