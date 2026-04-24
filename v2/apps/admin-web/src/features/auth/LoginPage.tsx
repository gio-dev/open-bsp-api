import { Button, Heading, Text, VStack } from "@chakra-ui/react";
import { Link, useSearchParams } from "react-router-dom";

export default function LoginPage() {
  const [search] = useSearchParams();
  const authError = search.get("auth_error");

  return (
    <VStack p={8} gap={4} align="stretch" data-testid="login-page">
      <Heading size="lg">Sign in</Heading>
      <Text color="fg.muted">
        OpenID Connect login for the admin console (Story 2.1).
      </Text>
      {authError ? (
        <Text color="red.fg" role="alert" data-testid="login-auth-error">
          Sign-in did not complete ({authError}). Try again or contact support.
        </Text>
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
