import { Button, Heading, Table, Text, VStack } from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";

import { apiFetchInit } from "../../lib/consoleAuth";
import { VALID_TENANT_ROLES } from "../../lib/tenantRoles";

type MemberRow = { user_id: string; email: string; role: string };

export default function MembersPage() {
  const [items, setItems] = useState<MemberRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [draftRoles, setDraftRoles] = useState<Record<string, string>>({});
  const [savingId, setSavingId] = useState<string | null>(null);

  const apiPath = useCallback(
    (path: string) =>
      `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`,
    [],
  );

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const init = apiFetchInit();
      const r = await fetch(apiPath("/v1/me/members"), init);
      if (r.status === 403) {
        setError("You need org_admin to manage team roles (Story 2.2).");
        setItems([]);
        return;
      }
      if (r.status === 401) {
        setError("Sign in required.");
        setItems([]);
        return;
      }
      if (!r.ok) {
        setError(`Could not load members (${r.status}).`);
        setItems([]);
        return;
      }
      const data = (await r.json()) as { items?: MemberRow[] };
      const list = data.items ?? [];
      setItems(list);
      setDraftRoles(
        Object.fromEntries(list.map((row) => [row.user_id, row.role])),
      );
    } catch {
      setError("Network error while loading members.");
    }
    setLoading(false);
  }, [apiPath]);

  useEffect(() => {
    void load();
  }, [load]);

  const updateRole = useCallback(
    async (userId: string) => {
      const newRole = draftRoles[userId];
      if (newRole === undefined) return;
      setSavingId(userId);
      setError(null);
      try {
        const init = apiFetchInit();
        const r = await fetch(apiPath(`/v1/me/members/${userId}`), {
          method: "PATCH",
          ...init,
          headers: {
            "Content-Type": "application/json",
            ...init.headers,
          },
          body: JSON.stringify({ role: newRole }),
        });
        if (r.status === 403) {
          setError("Cannot change that role (e.g. last org_admin) or no access.");
          return;
        }
        if (!r.ok) {
          setError(`Update failed (${r.status}).`);
          return;
        }
        await load();
      } catch {
        setError("Network error while saving role.");
      } finally {
        setSavingId(null);
      }
    },
    [apiPath, draftRoles, load],
  );

  return (
    <VStack align="stretch" gap={4} data-testid="members-page">
      <Heading size="lg">Team &amp; roles</Heading>
      <Text color="fg.muted">
        Tenant memberships (RBAC). Only org_admin can list or change roles via API
        (Story 2.2).
      </Text>
      {error ? (
        <Text color="red.fg" role="alert">
          {error}
        </Text>
      ) : null}
      {loading ? (
        <Text color="fg.muted">Loading?</Text>
      ) : (
        <Table.Root size="sm" variant="outline" data-testid="members-table">
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader>Email</Table.ColumnHeader>
              <Table.ColumnHeader>Role</Table.ColumnHeader>
              <Table.ColumnHeader>User id</Table.ColumnHeader>
              <Table.ColumnHeader>Actions</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {items.map((row) => (
              <Table.Row key={row.user_id}>
                <Table.Cell>{row.email}</Table.Cell>
                <Table.Cell>
                  <select
                    aria-label={`Role for ${row.email}`}
                    data-testid={`role-select-${row.user_id}`}
                    value={draftRoles[row.user_id] ?? row.role}
                    onChange={(e) =>
                      setDraftRoles((d) => ({
                        ...d,
                        [row.user_id]: e.target.value,
                      }))
                    }
                  >
                    {VALID_TENANT_ROLES.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                </Table.Cell>
                <Table.Cell fontFamily="mono" fontSize="sm">
                  {row.user_id}
                </Table.Cell>
                <Table.Cell>
                  <Button
                    size="sm"
                    data-testid={`save-role-${row.user_id}`}
                    disabled={
                      (draftRoles[row.user_id] ?? row.role) === row.role ||
                      savingId === row.user_id
                    }
                    onClick={() => void updateRole(row.user_id)}
                  >
                    {savingId === row.user_id ? "Saving?" : "Update role"}
                  </Button>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      )}
    </VStack>
  );
}
