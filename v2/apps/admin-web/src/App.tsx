import { Button, Heading, Spinner, Text, VStack } from "@chakra-ui/react";
import { lazy, Suspense } from "react";
import {
  BrowserRouter,
  Link,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";

import LoginPage from "./features/auth/LoginPage";
import EmbedPanelPage from "./features/embed/EmbedPanelPage";
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
const FlowEditorPage = lazy(() => import("./features/flows/FlowEditorPage"));
const ContactPreferencesPage = lazy(
  () => import("./features/privacy/ContactPreferencesPage"),
);

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

function ConsoleChromeLayout() {
  const sessionUi = import.meta.env.VITE_AUTH_MODE === "session";

  return (
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
        <Link to="/flows/editor">Flows</Link>
        {" · "}
        <Link to="/settings/integrations">Integrations</Link>
        {" · "}
        <Link to="/embed/panel">Embed (iframe)</Link>
        {" · "}
        <Link to="/privacy/contacts/15550009999/preferences">
          Contact prefs (LGPD)
        </Link>
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
        <Outlet />
      </Suspense>
    </VStack>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/embed/panel" element={<EmbedPanelPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ConsoleChromeLayout />}>
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
            <Route path="/flows/editor" element={<FlowEditorPage />} />
            <Route
              path="/privacy/contacts/:contactId/preferences"
              element={<ContactPreferencesPage />}
            />
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
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
