import { Button, Heading, Text, VStack } from "@chakra-ui/react";
import { Link, useSearchParams } from "react-router-dom";

const AUTH_ERROR_COPY: Record<string, { message: string }> = {
  idp_error: { message: "The identity provider returned an error." },
  oauth_missing_params: { message: "The login response was incomplete (missing code or state)." },
  oidc_not_configured: { message: "OpenID Connect is not configured on the server." },
  server_misconfigured: { message: "The server is missing session or OIDC settings." },
  oauth_state_missing: { message: "Login state was lost. Try signing in again." },
  oauth_state_invalid: { message: "Login state was invalid. Try again." },
  oauth_state_mismatch: { message: "Login state did not match. Try again." },
  oauth_pkce_invalid: { message: "Login security (PKCE) was invalid. Try again." },
  token_exchange_failed: { message: "Could not exchange the authorization code for tokens." },
  no_id_token: { message: "The identity token was not returned by the provider." },
  id_token_invalid: { message: "The identity token could not be verified." },
  idp_claims_incomplete: { message: "User profile from the provider was incomplete." },
  database_unavailable: { message: "The sign-in service database is unavailable." },
  no_org_access: { message: "You are not a member of an organization in this product." },
  tenant_claim_denied: { message: "Your account cannot use the requested organization." },
  membership_error: { message: "Organization membership could not be updated." },
};

export default function LoginPage() {
  const [search] = useSearchParams();
  const authError = search.get("auth_error");
  const info = authError ? AUTH_ERROR_COPY[authError] : undefined;

  return (
    <VStack p={8} gap={4} align="stretch" data-testid="login-page">
      <Heading size="lg">Sign in</Heading>
      <Text color="fg.muted">
        OpenID Connect login for the admin console (Story 2.1).
      </Text>
      {authError ? (
        <VStack
          align="stretch"
          gap={1}
          color="red.fg"
          role="alert"
          data-testid="login-auth-error"
        >
          <Text>
            {info?.message ??
              "Sign-in did not complete. Try again or contact support."}
          </Text>
          <Text fontSize="sm" fontFamily="mono">
            code: {authError}
          </Text>
        </VStack>
      ) : null}
      <Button asChild colorPalette="blue" data-testid="login-continue">
        <a href="/v1/auth/oidc/login">Continue to identity provider</a>
      </Button>
      <Text fontSize="sm" color="fg.muted">
        <Link to="/">Back to app</Link>
      </Text>
    </VStack>
  );
}
