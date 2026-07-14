# Mutual Fund FAQ Assistant — Frontend

The React frontend for the facts-only Mutual Fund FAQ Assistant. It is designed
to live inside the main `RAG/frontend` folder and can be opened directly in
Google Antigravity IDE.

## Prerequisites

- Node.js `>=22.13.0`

## Quick Start

```bash
npm ci
npm run dev:local
```

Open [http://localhost:3000](http://localhost:3000).

## Open in Antigravity

1. Open Google Antigravity IDE.
2. Choose **Open Folder** and select the `RAG/frontend` folder.
3. Open **Terminal → New Terminal**.
4. Run `npm ci` once, then run `npm run dev:local`.
5. Open `http://localhost:3000` in Antigravity's browser or Chrome.

Antigravity will automatically discover the project guidance in `.agents/`.
The `/run-local-frontend` workspace workflow can also be used from its agent
panel.

## Useful Commands

```bash
npm run dev:local  # Local development at localhost:3000
npm run build
npm test
```

## Workspace Auth Headers

OpenAI workspace sites can read the current user's email from
`oai-authenticated-user-email`.

SIWC-authenticated workspace sites may also receive
`oai-authenticated-user-full-name` when the user's SIWC profile has a non-empty
`name` claim. The full-name value is percent-encoded UTF-8 and is accompanied by
`oai-authenticated-user-full-name-encoding: percent-encoded-utf-8`.

Treat the full name as optional and fall back to email when it is absent:

```tsx
import { headers } from "next/headers";

export default async function Home() {
  const requestHeaders = await headers();
  const email = requestHeaders.get("oai-authenticated-user-email");
  const encodedFullName = requestHeaders.get("oai-authenticated-user-full-name");
  const fullName =
    encodedFullName &&
    requestHeaders.get("oai-authenticated-user-full-name-encoding") ===
      "percent-encoded-utf-8"
      ? decodeURIComponent(encodedFullName)
      : null;

  const displayName = fullName ?? email;
  // ...
}
```

## Optional Dispatch-Owned ChatGPT Sign-In

Import the ready-to-use helpers from `app/chatgpt-auth.ts` when the site needs
optional or required ChatGPT sign-in:

- Use `getChatGPTUser()` for optional signed-in UI.
- Use `requireChatGPTUser(returnTo)` for server-rendered pages that should send
  anonymous visitors through Sign in with ChatGPT.
- Use `chatGPTSignInPath(returnTo)` and `chatGPTSignOutPath(returnTo)` for
  browser links or actions.
- Pass a same-origin relative `returnTo` path for the destination after sign-in
  or sign-out. The helper validates and safely encodes it.
- Mark protected pages with `export const dynamic = "force-dynamic"` because
  they depend on per-request identity headers.

Dispatch owns `/signin-with-chatgpt`, `/signout-with-chatgpt`, `/callback`, the
OAuth cookies, and identity header injection. Do not implement app routes for
those reserved paths. Routes that do not import and call the helper remain
anonymous-compatible.

SIWC establishes identity only; it does not prove workspace membership. Use the
Sites hosting platform's access policy controls for workspace-wide restrictions,
or enforce explicit server-side membership or allowlist checks.

Use SIWC for account pages, user-specific dashboards, saved records, and write
actions tied to the current ChatGPT user. Leave public content anonymous.

## Project Notes

- The interface currently uses mock responses for frontend interaction testing.
- The Python RAG pipeline remains in the parent RAG project and is not modified
  by this frontend setup.
- Connect the frontend to a small JSON API around `src.pipeline.rag_chain.ask`
  when backend integration is ready.
