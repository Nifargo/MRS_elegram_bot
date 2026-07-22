#!/usr/bin/env node

/**
 * PreToolUse hook for Read|Grep operations.
 * Blocks reading of sensitive, secret, and credential files.
 *
 * Exit 2 = block the action (with structured JSON for Claude Code hooks API)
 * Exit 0 = allow
 */

async function main() {
    const chunks = [];
    for await (const chunk of process.stdin) {
        chunks.push(chunk);
    }

    const toolArgs = JSON.parse(Buffer.concat(chunks).toString());

    const readPath =
        toolArgs.tool_input?.file_path ||
        toolArgs.tool_input?.path ||
        toolArgs.tool_input?.nameSubstring ||
        "";

    if (!readPath) {
        process.exit(0);
    }

    // ── Sensitive file patterns ──────────────────────────────────────
    const blockedPatterns = [
        // Environment & config secrets
        '.env',
        '.env.local',
        '.env.production',
        '.env.staging',
        '.env.development',

        // Java / Spring
        'application.properties',
        'application-prod.properties',
        'application-local.properties',
        'application-dev.properties',
        'application-staging.properties',
        'database.properties',
        'hibernate.cfg.xml',

        // Keystores & certificates
        'keystore.jks',
        'truststore.jks',
        '.p12',
        '.pfx',
        '.pem',
        '.key',
        '.crt',
        'id_rsa',
        'id_ed25519',

        // Credentials & tokens
        'credentials.json',
        'service-account.json',
        'secrets.yml',
        'secrets.yaml',
        '.npmrc',
        '.pypirc',
        '.netrc',
        '.docker/config.json',

        // CI/CD secrets
        '.github/secrets',
        'vault.yml',
        'vault.yaml',
    ];

    // ── Sensitive directories ────────────────────────────────────────
    const blockedDirs = [
        'secrets/',
        '.git/',
        '.claude/hooks/',
    ];

    // Check file patterns
    for (const pattern of blockedPatterns) {
        if (readPath.endsWith(pattern) || readPath.includes(`/${pattern}`)) {
            deny(`Cannot read sensitive file matching "${pattern}"`);
        }
    }

    // Check directory patterns
    for (const dir of blockedDirs) {
        if (readPath.includes(dir)) {
            deny(`Cannot read files inside "${dir}"`);
        }
    }

    process.exit(0);
}

function deny(reason) {
    const output = {
        hookSpecificOutput: {
            hookEventName: "PreToolUse",
            permissionDecision: "deny",
            permissionDecisionReason: reason,
        },
    };
    console.log(JSON.stringify(output));
    process.exit(2);
}

main().catch((err) => {
    // Fail closed — if hook crashes, block the action
    const output = {
        hookSpecificOutput: {
            hookEventName: "PreToolUse",
            permissionDecision: "deny",
            permissionDecisionReason: `Hook error: ${err.message}`,
        },
    };
    console.log(JSON.stringify(output));
    process.exit(2);
});