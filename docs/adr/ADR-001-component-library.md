# ADR-001: Component Library

**Status:** Accepted
**Date:** 2026-03-12
**Deciders:** Project owner

## Decision

Use **shadcn/ui** as the component library.

## Rationale

- Tailwind CSS v4 native — no style conflicts
- Components are copied into the codebase (full ownership, no upgrade surprises)
- Built on Radix UI primitives — excellent accessibility out of the box
- Covers all needed primitives: Card, Button, Badge, Dialog, Sheet, DropdownMenu, Tabs, Tooltip, Skeleton, Slider, Popover, Command
- Large community and active maintenance
- Works with Next.js 15 App Router

## Consequences

- Must manually copy component updates when shadcn releases new versions
- Component code lives in `frontend/components/ui/` and is ours to modify
