# Design System — AIMeridian

**Version:** 1.0
**Phase:** 0 — Planning
**Last Updated:** 2026-03-12
**Component Library:** shadcn/ui (Radix UI primitives + Tailwind CSS v4)

---

## Design Principles

1. **Clarity first** — Information density is high; every pixel must earn its place
2. **Mobile-first** — Designed for 390px, enhanced for 1440px
3. **Readable at speed** — Users scan, not read; typography and spacing optimised for scanning
4. **Calm UI** — No aggressive animations; subtle transitions only
5. **Dark mode as default** — Primary users are developers working in dark environments

---

## Color Palette

### Light Mode

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| `background` | `#FAFAFA` | `neutral-50` | Page background |
| `surface` | `#FFFFFF` | `white` | Card, panel backgrounds |
| `surface-raised` | `#F5F5F5` | `neutral-100` | Hover states, subtle sections |
| `border` | `#E5E5E5` | `neutral-200` | Card borders, dividers |
| `text-primary` | `#171717` | `neutral-900` | Headings, body text |
| `text-secondary` | `#525252` | `neutral-600` | Subtext, metadata |
| `text-muted` | `#A3A3A3` | `neutral-400` | Placeholder, disabled |
| `accent` | `#7C3AED` | `violet-700` | Primary actions, active states |
| `accent-light` | `#EDE9FE` | `violet-100` | Accent backgrounds |
| `success` | `#16A34A` | `green-600` | Thumbs up, positive feedback |
| `danger` | `#DC2626` | `red-600` | Thumbs down, errors |
| `warning` | `#D97706` | `amber-600` | Warnings, trial source badges |
| `info` | `#2563EB` | `blue-600` | Info badges, links |

### Dark Mode

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| `background` | `#0A0A0A` | `neutral-950` | Page background |
| `surface` | `#171717` | `neutral-900` | Card, panel backgrounds |
| `surface-raised` | `#262626` | `neutral-800` | Hover states, subtle sections |
| `border` | `#404040` | `neutral-700` | Card borders, dividers |
| `text-primary` | `#FAFAFA` | `neutral-50` | Headings, body text |
| `text-secondary` | `#A3A3A3` | `neutral-400` | Subtext, metadata |
| `text-muted` | `#525252` | `neutral-600` | Placeholder, disabled |
| `accent` | `#A78BFA` | `violet-400` | Primary actions, active states |
| `accent-light` | `#2E1065` | `violet-950` | Accent backgrounds |
| `success` | `#4ADE80` | `green-400` | Thumbs up |
| `danger` | `#F87171` | `red-400` | Thumbs down, errors |
| `warning` | `#FCD34D` | `amber-300` | Warnings |
| `info` | `#60A5FA` | `blue-400` | Info badges, links |

---

## Typography

**Font family:** `Inter` (Google Fonts) — system fallback `ui-sans-serif, system-ui, sans-serif`

| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `text-xs` | 12px | 400 | 1.5 | Timestamps, source platform labels |
| `text-sm` | 14px | 400 | 1.5 | Card summary text, filter chips |
| `text-sm-medium` | 14px | 500 | 1.5 | Badge labels, button text |
| `text-base` | 16px | 400 | 1.6 | Body text |
| `text-base-medium` | 16px | 500 | 1.6 | Source names, card metadata |
| `text-lg` | 18px | 600 | 1.4 | Card titles |
| `text-xl` | 20px | 700 | 1.3 | Page headings (Sources, Settings) |
| `text-2xl` | 24px | 700 | 1.2 | Main page heading (Feed) |
| `text-3xl` | 30px | 800 | 1.1 | Hero/marketing text (if any) |

---

## Spacing Scale

Uses Tailwind's default 4px base scale. Commonly used values:

| Token | px | Usage |
|-------|-----|-------|
| `space-1` | 4px | Tight icon padding |
| `space-2` | 8px | Inner card padding (compact) |
| `space-3` | 12px | Gap between badge and text |
| `space-4` | 16px | Standard card padding |
| `space-5` | 20px | Section gaps |
| `space-6` | 24px | Card vertical padding |
| `space-8` | 32px | Between feed sections |
| `space-12` | 48px | Page top padding (desktop) |
| `space-16` | 64px | Large section gaps |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 4px | Badges, chips |
| `rounded-md` | 8px | Buttons, inputs |
| `rounded-lg` | 12px | Cards |
| `rounded-xl` | 16px | Dialogs, sheets |
| `rounded-full` | 9999px | Avatar, toggle switch |

---

## Shadows

| Token | Usage |
|-------|-------|
| `shadow-sm` | Card hover state |
| `shadow-md` | Dropdown menus, tooltips |
| `shadow-lg` | Modal dialogs |

---

## Component Inventory

All components use shadcn/ui as the base. Custom variants are documented below.

### Primitives (from shadcn/ui)

| Component | Source | Variants |
|-----------|--------|---------|
| `Button` | shadcn | `default`, `destructive`, `outline`, `ghost`, `link` |
| `Badge` | shadcn | `default`, `secondary`, `destructive`, `outline` |
| `Card` | shadcn | `CardHeader`, `CardContent`, `CardFooter` |
| `Input` | shadcn | — |
| `Textarea` | shadcn | — |
| `Dialog` | shadcn | Used for AddSource, confirm dialogs |
| `Sheet` | shadcn | Used for mobile FilterPanel bottom sheet |
| `DropdownMenu` | shadcn | Used for card actions menu |
| `Tabs` | shadcn | Used for Sources detail page |
| `Tooltip` | shadcn | Used for icon-only buttons |
| `Skeleton` | shadcn | Used for FeedCard loading state |
| `Switch` | shadcn | Used for source active/paused toggle |
| `Slider` | shadcn | Used for min_score filter |
| `Popover` | shadcn | Used for date range picker |
| `Command` | shadcn | Used for source picker in filter panel |
| `ScrollArea` | shadcn | Used for long lists |

---

### Custom Components

#### `FeedCard`

```
┌─────────────────────────────────────────────────────────┐
│ [platform badge]  [content_type badge]    [date] [menu ⋮]│
│                                                          │
│ Title of the content item (text-lg, 2 lines max)         │
│                                                          │
│ Summary text goes here. Up to 3 lines of text before     │
│ truncating with ellipsis...                              │
│                                                          │
│ [author name] · [source name]                            │
│                                                          │
│ [↑ 0]  [↓]  [🔖]  [skip]          [→ Read more]         │
└─────────────────────────────────────────────────────────┘
```

- Card background: `surface`
- Border: 1px `border`
- Border radius: `rounded-lg`
- Padding: `p-4` (16px)
- Title: `text-lg font-semibold text-primary` (2-line clamp)
- Summary: `text-sm text-secondary` (3-line clamp)
- Platform badge: coloured per platform (arXiv=violet, GitHub=slate, Reddit=orange, HN=amber)
- Thumbs up/down: icon buttons, green/red on active state
- Hover: `shadow-sm`, subtle border darkening
- New item indicator: left border accent stripe (`border-l-4 border-accent`)

#### `FilterChip`

```
[label ×]
```

- Background: `accent-light`
- Text: `accent`
- Border radius: `rounded-full`
- Size: `text-sm px-3 py-1`
- Dismiss button: `×` icon, fades in on hover

#### `SourceRating`

Five-star component. Stars are filled/empty based on rating.
- Filled star: `accent` colour
- Empty star: `border` colour
- Interactive (clickable) on source edit page

#### `FeedCard Skeleton`

- Mirrors FeedCard layout
- Uses `Skeleton` (shadcn) for title, summary, and footer
- Animates with `animate-pulse`

---

## Layout

### Page Shell

```
┌────────────────────────────────────────────────────────┐
│  Header (sticky)                                       │
│  [AIMeridian logo]  [search]  [theme toggle] [settings]│
├────────────────────────────────────────────────────────┤
│  FilterBar (sticky below header, desktop only)         │
│  Showing: [Papers ×] [LLM ×]  [+ Add filter]           │
├─────────────────────┬──────────────────────────────────┤
│  Sidebar (desktop)  │  Main Content                    │
│  • Feed             │  FeedList (2-col grid ≥1024px,   │
│  • Saved            │           1-col below)           │
│  • Sources          │                                  │
│  • Settings         │                                  │
└─────────────────────┴──────────────────────────────────┘
```

### Mobile Layout (< 768px)

```
┌────────────────────────────────┐
│  Header (sticky)               │
│  [Logo]  [filter icon] [menu]  │
├────────────────────────────────┤
│  Feed (single column)          │
│  FeedCard                      │
│  FeedCard                      │
│  FeedCard                      │
│  ...                           │
├────────────────────────────────┤
│  Bottom nav                    │
│  [Feed] [Saved] [Sources] [⚙️] │
└────────────────────────────────┘
```

Filter panel opens as a bottom Sheet on mobile.

### Breakpoints

| Name | Width | Layout |
|------|-------|--------|
| `sm` | 640px | — |
| `md` | 768px | Bottom nav → sidebar nav |
| `lg` | 1024px | 1-col feed → 2-col feed |
| `xl` | 1280px | Wider sidebar |

---

## Motion

- **Card hover:** `transition-shadow duration-150` — shadow appears
- **Filter chip dismiss:** `transition-opacity duration-100` — chip fades out
- **Sheet / Dialog open:** Radix built-in — slide-up (mobile), fade (desktop)
- **Skeleton pulse:** `animate-pulse`
- **Thumb active state:** `transition-colors duration-100`
- **Page transitions:** None by default (avoid janky navigation)

All animations respect `prefers-reduced-motion`.

---

## Iconography

Use **Lucide React** (already included with shadcn/ui).

| Context | Icon |
|---------|------|
| Thumbs up | `ThumbsUp` |
| Thumbs down | `ThumbsDown` |
| Bookmark / Save | `Bookmark` |
| Skip | `ChevronsRight` |
| More like this | `Plus` |
| Less like this | `Minus` |
| Filter | `SlidersHorizontal` |
| Search | `Search` |
| Settings | `Settings` |
| Dark mode | `Moon` |
| Light mode | `Sun` |
| External link | `ExternalLink` |
| Card menu | `MoreHorizontal` |
| Add source | `PlusCircle` |
| Archive | `Archive` |
| Refresh / Trigger fetch | `RefreshCw` |
| Paper content type | `FileText` |
| Repo content type | `Github` |
| Post content type | `MessageSquare` |
| Model content type | `Cpu` |
| Video content type | `Video` |

---

## Platform Badge Colours

| Platform | Background | Text |
|----------|-----------|------|
| arXiv | `violet-100` / `violet-950` | `violet-700` / `violet-400` |
| GitHub | `slate-100` / `slate-900` | `slate-700` / `slate-400` |
| Reddit | `orange-100` / `orange-950` | `orange-700` / `orange-400` |
| Hacker News | `amber-100` / `amber-950` | `amber-700` / `amber-400` |
| HuggingFace | `yellow-100` / `yellow-950` | `yellow-700` / `yellow-400` |
| Papers w/ Code | `blue-100` / `blue-950` | `blue-700` / `blue-400` |
| RSS | `green-100` / `green-950` | `green-700` / `green-400` |
| X / Twitter | `sky-100` / `sky-950` | `sky-700` / `sky-400` |
| LinkedIn | `cyan-100` / `cyan-950` | `cyan-700` / `cyan-400` |
