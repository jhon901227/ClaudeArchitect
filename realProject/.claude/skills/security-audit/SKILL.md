---
name: security-audit
description: >
  Run a security audit of the codebase. Checks for exposed secrets, missing auth,
  unsafe dependencies, SQL injection, and XSS vectors.
  Invoked via /security-audit or when user says "security audit", "security review",
  "check for vulnerabilities".
version: 1.0.0
context: fork
allowed-tools: Read, Glob, Grep, Bash
# user-invocable: true means it appears in the / slash command menu
user-invocable: true
# disable-model-invocation: false = Claude CAN auto-invoke this
# if the user's message matches the description above
disable-model-invocation: false
argument-hint: "[optional: specific area to audit, e.g. 'api auth', 'dependencies']"
---

# Security Audit Skill

You are a **security-focused code reviewer** for the TaskFlow project.
This skill runs in a forked context — READ-ONLY.

## Audit Checklist

### 1. Secret Scanning
```bash
# Run in Bash tool
grep -r "password\|secret\|api_key\|token\|private" src/ --include="*.ts" -l
```
Report any hardcoded values (environment variable references are fine).

### 2. Authentication Coverage
```
Glob: src/api/routes/**/*.ts
```
For each route file, verify every non-public endpoint has `authenticate` middleware.

### 3. Input Validation
For every POST/PATCH route, confirm there is a `validate(schema)` middleware call.
Flag any routes that accept user input without validation.

### 4. Dependency Audit
```bash
npm audit --json
```
Report HIGH and CRITICAL severity issues. Ignore MODERATE unless asked.

### 5. SQL Injection (Prisma)
Prisma parameterizes by default, but check for raw queries:
```
Grep: pattern="prisma\.\$queryRaw|prisma\.\$executeRaw" paths=src/
```
Flag any `$queryRaw` calls that concatenate user input.

### 6. XSS Vectors (Frontend)
```
Grep: pattern="dangerouslySetInnerHTML" paths=src/frontend/
```
Flag all usages — each needs explicit justification.

## Output Format

```markdown
## Security Audit Report
**Date:** <today>
**Scope:** <area audited>

### 🔴 Critical Issues
### 🟠 High Issues  
### 🟡 Medium Issues
### ✅ Passed Checks

### Recommendations
```