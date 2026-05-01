# TaskFlow API

A task-management REST API built with Node.js, Express, and PostgreSQL.

## Stack

- **Runtime:** Node.js 20 LTS
- **Framework:** Express 4
- **ORM:** Prisma
- **Database:** PostgreSQL 16
- **Frontend:** React 18 + TypeScript + Tailwind
- **Tests:** Vitest (unit) + Playwright (e2e)

## Quick Start

```bash
cp .env.example .env
npm install
npx prisma migrate dev
npm run dev
```