/**
 * Канонический пример для ЭТОГО репозитория: пара [START]/[END], полный контракт,
 * тот же ANCHOR_ID в logLine (см. `.cursor/rules/ai-logging.mdc` и `src/lib/log.ts`).
 * Файл вне `tsconfig` include — в реальном коде под `src/` используй `import { logLine } from "../lib/log.js";`.
 */

function logLine(
  ..._args: unknown[]
): void {
  /* заглушка: в проекте бери из src/lib/log.ts */
}

// === CHUNK: SEMANTIC_EXAMPLE [REFERENCE] ===
// Описание: Показ полного каркаса функции и согласованного логирования.
// Dependencies: (none)
// [START_REGISTER_USER]
/*
 * ANCHOR: REGISTER_USER
 * @PreConditions:
 * - username и password — непустые строки после trim
 * @PostConditions:
 * - при успехе возвращает true; иначе false без исключения
 * PURPOSE: Пример регистрации с трассировкой для агента.
 * @see: log.ts -> logLine()
 */
async function registerUser(username: string, password: string): Promise<boolean> {
  logLine("background", "DEBUG", "registerUser", "REGISTER_USER", "START_ANCHOR", {
    u_len: username.trim().length,
    p_len: password.length,
  });

  if (password.length < 8) {
    logLine("background", "WARN", "registerUser", "REGISTER_USER", "START_ANCHOR", {
      decision: "password_too_short",
      branch: "reject",
    });
    logLine("background", "DEBUG", "registerUser", "REGISTER_USER", "END_ANCHOR", {
      ok: false,
    });
    return false;
  }

  logLine("background", "INFO", "registerUser", "REGISTER_USER", "END_ANCHOR", {
    ok: true,
  });
  return true;
}
// [END_REGISTER_USER]
// === END_CHUNK: SEMANTIC_EXAMPLE ===
