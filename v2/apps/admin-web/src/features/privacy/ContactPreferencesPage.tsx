import {
  Button,
  Checkbox,
  Heading,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { apiFetchInit } from "../../lib/consoleAuth";

type PrefsPayload = {
  contact_id: string;
  marketing_opt_in: boolean;
  transactional_allowed: boolean;
  disclosure_copy_slug: string;
  updated_at: string | null;
};

async function readErrorMessage(r: Response): Promise<string> {
  const t = await r.text();
  try {
    const j = JSON.parse(t) as { message?: string };
    if (j.message) return j.message;
  } catch {
    /* ignore */
  }
  return t.slice(0, 400) || r.statusText;
}

/** Story 6.3: preferencias LGPD por contacto; microcopy separa marketing vs transacional (UX-DR4). */
export default function ContactPreferencesPage() {
  const { contactId = "" } = useParams<{ contactId: string }>();
  const [data, setData] = useState<PrefsPayload | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [slugInput, setSlugInput] = useState("");

  const load = useCallback(async () => {
    setLoadError(null);
    const base = import.meta.env.VITE_API_BASE_URL ?? "";
    try {
      const r = await fetch(
        `${base}/v1/me/contacts/${encodeURIComponent(contactId)}/preferences`,
        apiFetchInit(),
      );
      if (!r.ok) {
        throw new Error(await readErrorMessage(r));
      }
      const body = (await r.json()) as PrefsPayload;
      setData(body);
      setSlugInput(body.disclosure_copy_slug);
    } catch (e) {
      setLoadError((e as Error).message);
    }
  }, [contactId]);

  useEffect(() => {
    if (contactId) void load();
  }, [contactId, load]);

  const save = async () => {
    if (!data) return;
    const base = import.meta.env.VITE_API_BASE_URL ?? "";
    setSaveError(null);
    setSaving(true);
    const init = apiFetchInit();
    const hdr =
      typeof init.headers === "object" && !(init.headers instanceof Headers)
        ? ({ ...(init.headers as Record<string, string>) })
        : ({} as Record<string, string>);
    try {
      const r = await fetch(
        `${base}/v1/me/contacts/${encodeURIComponent(contactId)}/preferences`,
        {
          ...init,
          method: "PATCH",
          headers: {
            ...hdr,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            marketing_opt_in: data.marketing_opt_in,
            transactional_allowed: data.transactional_allowed,
            disclosure_copy_slug: slugInput.trim() || data.disclosure_copy_slug,
          }),
        },
      );
      if (!r.ok) {
        throw new Error(await readErrorMessage(r));
      }
      const body = (await r.json()) as PrefsPayload;
      setData(body);
      setSlugInput(body.disclosure_copy_slug);
    } catch (e) {
      setSaveError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const previewEffect =
    data == null
      ? ""
      : !data.marketing_opt_in && data.transactional_allowed
        ? "O contacto deixa de receber campanhas promocionais; continua a receber mensagens transacionais (confirmacoes, codigos, alertas)."
        : data.marketing_opt_in && data.transactional_allowed
          ? "O contacto pode receber promocoes e mensagens transacionais."
          : !data.transactional_allowed
            ? "Transacional desligado: envios com preference_kind transactional serao bloqueados na API. Use apenas com base legal clara."
            : "Revise as combinacoes antes de gravar.";

  return (
    <VStack gap={4} align="stretch" data-testid="contact-preferences-root">
      <Heading size="lg" data-testid="contact-preferences-heading">
        Preferencias do contacto ({contactId || "?"})
      </Heading>
      <Text fontSize="sm" color="fg.muted" data-testid="contact-preferences-intro">
        Marketing e transacional sao categorias distintas. Os requisitos legais ficam por
        conta do tenant; esta pagina regista o estado tecnico usado pelo gate de envio.
      </Text>
      {loadError ? (
        <Text color="red.fg" role="alert" data-testid="contact-preferences-load-error">
          {loadError}
        </Text>
      ) : null}
      {data ? (
        <VStack align="stretch" gap={4}>
          <VStack align="stretch" gap={1}>
            <Checkbox.Root
              checked={data.marketing_opt_in}
              onCheckedChange={(d) => {
                const on = d.checked === true;
                setData((prev) => (prev ? { ...prev, marketing_opt_in: on } : prev));
              }}
              data-testid="contact-prefs-marketing"
            >
              <Checkbox.HiddenInput />
              <Checkbox.Control />
              <Checkbox.Label>
                <Text fontWeight="medium">Campanhas e promocoes (marketing)</Text>
                <Text fontSize="sm" color="fg.muted">
                  Inclui newsletters e ofertas. Envios com{" "}
                  <code>preference_kind: marketing</code> exigem esta opcao ligada.
                </Text>
              </Checkbox.Label>
            </Checkbox.Root>
          </VStack>
          <VStack align="stretch" gap={1}>
            <Checkbox.Root
              checked={data.transactional_allowed}
              onCheckedChange={(d) => {
                const on = d.checked === true;
                setData((prev) => (prev ? { ...prev, transactional_allowed: on } : prev));
              }}
              data-testid="contact-prefs-transactional"
            >
              <Checkbox.HiddenInput />
              <Checkbox.Control />
              <Checkbox.Label>
                <Text fontWeight="medium">Mensagens transacionais</Text>
                <Text fontSize="sm" color="fg.muted">
                  Confirmacoes, OTP, alertas de servico. Predefinicao do sistema: ligado.
                  Envios <code>transactional</code> e automacao do motor 5.5 usam este
                  sinal.
                </Text>
              </Checkbox.Label>
            </Checkbox.Root>
          </VStack>
          <Text fontSize="sm" borderWidth="1px" rounded="md" p={2} bg="bg.muted" data-testid="contact-prefs-preview">
            {previewEffect}
          </Text>
          <VStack align="stretch" gap={1}>
            <Text fontSize="sm" fontWeight="medium">
              Versao de copy / disclosure (slug)
            </Text>
            <Text fontSize="xs" color="fg.muted">
              Identificador curto escolhido pelo tenant (ex. baseline-v1). Texto legal
              completo via politica interna ou CMS futuro.
            </Text>
            <Input
              aria-label="Disclosure copy slug"
              value={slugInput}
              onChange={(e) => setSlugInput(e.target.value)}
              data-testid="contact-prefs-slug-input"
            />
          </VStack>
          {saveError ? (
            <Text color="red.fg" role="alert" data-testid="contact-preferences-save-error">
              {saveError}
            </Text>
          ) : null}
          <Button
            variant="solid"
            disabled={saving}
            onClick={() => void save()}
            data-testid="contact-prefs-save"
          >
            Gravar preferencias
          </Button>
        </VStack>
      ) : null}
    </VStack>
  );
}
