import {
  Button,
  Field,
  Heading,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useState, type FormEvent } from "react";

import { apiFetchInit } from "../../lib/consoleAuth";

export default function OrganizationSettingsPage() {
  const [displayName, setDisplayName] = useState("");
  const [timezone, setTimezone] = useState("");
  const [operationalEmail, setOperationalEmail] = useState("");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);

  const apiPath = (path: string) =>
    `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`;

  const parse422FieldErrors = (body: unknown): Record<string, string> => {
    const next: Record<string, string> = {};
    if (!body || typeof body !== "object") return next;
    const o = body as Record<string, unknown>;
    if (Array.isArray(o.errors)) {
      for (const e of o.errors) {
        if (
          e &&
          typeof e === "object" &&
          "field" in e &&
          "message" in e &&
          typeof (e as { field: unknown }).field === "string" &&
          typeof (e as { message: unknown }).message === "string"
        ) {
          const { field, message } = e as { field: string; message: string };
          next[field] = message;
        }
      }
    }
    if (Object.keys(next).length === 0 && Array.isArray(o.detail)) {
      for (const item of o.detail) {
        if (
          item &&
          typeof item === "object" &&
          "loc" in item &&
          "msg" in item
        ) {
          const loc = (item as { loc: string[] }).loc;
          const msg = String((item as { msg: string }).msg);
          const key = loc[loc.length - 1] ?? "form";
          next[key] = msg;
        }
      }
    }
    return next;
  };

  const load = useCallback(async () => {
    setLoadError(null);
    try {
      const init = apiFetchInit();
      const r = await fetch(apiPath("/v1/me/organization"), init);
      if (r.status === 401) {
        setLoadError("Not signed in (use Login or VITE_AUTH_MODE=stub for dev).");
        return;
      }
      if (r.status === 403) {
        setLoadError("Forbidden (check dev stub headers / org_admin).");
        return;
      }
      if (!r.ok) {
        setLoadError(`Load failed (${r.status}).`);
        return;
      }
      const body = (await r.json()) as Record<string, string>;
      setDisplayName(body.display_name ?? "");
      setTimezone(body.timezone ?? "");
      setOperationalEmail(body.operational_email ?? "");
    } catch {
      setLoadError("Network error while loading organization.");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaveError(null);
    setFieldErrors({});
    setSaving(true);
    try {
      const patchInit = apiFetchInit({
        "Content-Type": "application/json",
      });
      const r = await fetch(apiPath("/v1/me/organization"), {
        method: "PATCH",
        ...patchInit,
        body: JSON.stringify({
          display_name: displayName,
          timezone,
          operational_email: operationalEmail,
        }),
      });
      if (r.status === 422) {
        const body: unknown = await r.json();
        const next = parse422FieldErrors(body);
        setFieldErrors(next);
        if (Object.keys(next).length === 0) {
          const msg =
            body &&
            typeof body === "object" &&
            "message" in body &&
            typeof (body as { message: unknown }).message === "string"
              ? (body as { message: string }).message
              : "Validation failed.";
          setSaveError(msg);
        }
        setSaving(false);
        return;
      }
      if (!r.ok) {
        setSaveError(`Save failed (${r.status}).`);
        setSaving(false);
        return;
      }
      const body = (await r.json()) as Record<string, string>;
      setDisplayName(body.display_name ?? "");
      setTimezone(body.timezone ?? "");
      setOperationalEmail(body.operational_email ?? "");
    } catch {
      setSaveError("Network error while saving.");
    }
    setSaving(false);
  };

  return (
    <VStack align="stretch" gap={4} data-testid="org-settings-root">
      <Heading size="lg" data-testid="org-settings-heading">
        Organization settings
      </Heading>
      {loadError ? (
        <Text color="red.fg" role="alert">
          {loadError}
        </Text>
      ) : null}
      {saveError ? (
        <Text color="red.fg" role="alert">
          {saveError}
        </Text>
      ) : null}
      <form onSubmit={(e) => void onSubmit(e)}>
        <VStack align="stretch" gap={4}>
          <Field.Root invalid={!!fieldErrors.display_name}>
            <Field.Label>Display name</Field.Label>
            <Input
              data-testid="org-display-name"
              value={displayName}
              onChange={(ev) => setDisplayName(ev.target.value)}
            />
            {fieldErrors.display_name ? (
              <Field.ErrorText>{fieldErrors.display_name}</Field.ErrorText>
            ) : null}
          </Field.Root>
          <Field.Root invalid={!!fieldErrors.timezone}>
            <Field.Label>Timezone (IANA)</Field.Label>
            <Input
              data-testid="org-timezone"
              value={timezone}
              onChange={(ev) => setTimezone(ev.target.value)}
            />
            {fieldErrors.timezone ? (
              <Field.ErrorText>{fieldErrors.timezone}</Field.ErrorText>
            ) : null}
          </Field.Root>
          <Field.Root invalid={!!fieldErrors.operational_email}>
            <Field.Label>Operational email (optional)</Field.Label>
            <Input
              type="email"
              data-testid="org-operational-email"
              value={operationalEmail}
              onChange={(ev) => setOperationalEmail(ev.target.value)}
            />
            {fieldErrors.operational_email ? (
              <Field.ErrorText>
                {fieldErrors.operational_email}
              </Field.ErrorText>
            ) : null}
          </Field.Root>
          <Button
            type="submit"
            loading={saving}
            data-testid="org-save"
            alignSelf="flex-start"
          >
            Save
          </Button>
        </VStack>
      </form>
    </VStack>
  );
}
