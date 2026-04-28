import { Button, Heading, Spinner, Text, VStack } from "@chakra-ui/react";
import { lazy, Suspense } from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";

import LoginPage from "./features/auth/LoginPage";
import TenantShell from "./features/shell/TenantShell";

const OrganizationSettingsPage = lazy(
  () => import("./features/organization/OrganizationSettingsPage"),
);
const WabaPhoneNumberListPage = lazy(
  () => import("./features/waba/WabaPhoneNumberListPage"),
);
const MembersPage = lazy(() => import("./features/team/MembersPage"));
const IntegrationsPage = lazy(
  () => import("./features/integrations/IntegrationsPage"),
);
const MessageTemplatesPage = lazy(
  () => import("./features/templates/MessageTemplatesPage"),
);
const InboxPage = lazy(() => import("./features/inbox/InboxPage"));

async function logoutSession(): Promise<void> {
  const base = import.meta.env.VITE_API_BASE_URL ?? "";
  try {
    await fetch(`${base}/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch {
    /* ignore network errors on logout */
  }
  window.location.href = "/login";
}

export default function App() {
  const sessionUi = import.meta.env.VITE_AUTH_MODE === "session";

  return (
    <BrowserRouter>
      <VStack p={8} align="stretch" gap={4}>
        <Heading size="xl">Open BSP Admin</Heading>
        <Text color="fg.muted">
          <Link to="/settings/organization">Organization settings</Link>
          {" · "}
          <Link to="/settings/team">Team &amp; roles</Link>
          {" · "}
          <Link to="/channels/waba-numbers">WhatsApp numbers</Link>
          {" · "}
          <Link to="/channels/message-templates">Templates</Link>
          {" · "}
          <Link to="/inbox">Inbox</Link>
          {" · "}
          <Link to="/settings/integrations">Integrations</Link>
          {" · "}
          <Link to="/login">Login</Link>
          {sessionUi ? (
            <>
              {" · "}
              <Button
                size="xs"
                variant="ghost"
                onClick={() => void logoutSession()}
                data-testid="logout-button"
              >
                Log out
              </Button>
            </>
          ) : null}
        </Text>
        <Suspense fallback={<Spinner />}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<TenantShell />}>
              <Route
                path="/settings/organization"
                element={<OrganizationSettingsPage />}
              />
              <Route path="/settings/team" element={<MembersPage />} />
              <Route
                path="/settings/integrations"
                element={<IntegrationsPage />}
              />
              <Route
                path="/channels/message-templates"
                element={<MessageTemplatesPage />}
              />
              <Route path="/inbox" element={<InboxPage />} />
              <Route
                path="/channels/waba-numbers"
                element={<WabaPhoneNumberListPage />}
              />
              <Route
                index
                element={<Text color="fg.muted">Home</Text>}
              />
              <Route path="*" element={<Text color="fg.muted">Home</Text>} />
            </Route>
          </Routes>
        </Suspense>
      </VStack>
    </BrowserRouter>
  );
}
