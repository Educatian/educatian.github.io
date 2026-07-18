# Teacher Response Simulation - Design System

## 0. Research Log

### Embedded references

- Shortlist: `claude.md` for warm editorial authority, `notion.md` for research-document clarity, and `microsoft.md` for accessible education-product structure.
- Layer A selected: `soft-skill.md`. Its macro-whitespace, asymmetric editorial composition, concentric media framing, spring-like interaction timing, and mobile collapse rules fit a premium public research page.
- Layer B selected: `claude.md`. Its parchment canvas, warm neutrals, serif/sans hierarchy, restrained chromatic accent, and chapter-like light/dark rhythm support a sensitive education topic without making it feel clinical or futuristic.
- Adaptation: Claude's terracotta is secondary. Korean classroom green is the primary identity color, taken from chalkboards and the Unity prototype.

### Lazyweb real-product screens

- Queries run: `education research project landing page university` and `AI education product case study landing page` on desktop.
- Screens viewed: EdSurge Research, Polygence mentor/research, and Microsoft AI in Education.
- Harvested grammar: one decisive hero statement; real evidence image adjacent to purpose; compact sectional navigation; long-form reading rhythm; proof before methodology; clear transition from present evidence to future roadmap; generous final context and ethics section.
- Excluded: copied brand marks, exact layouts, stock imagery, and product-specific claims.

### Imagen concept drafts

- Editorial draft: `C:/Users/jewoo/.codex/generated_images/019f7285-d269-75f3-b6c7-b49ae0b9fb76/exec-4a89296e-1a0c-42c1-a6b4-e0ab42af76a5.png`
- Structural draft: `C:/Users/jewoo/.codex/generated_images/019f7285-f00a-7782-957c-a7d669284b56/exec-556c22a0-856b-4350-bfd1-0334e72b91aa.png`
- Selected contract: Editorial draft. It gives the research title and classroom evidence equal weight, uses the roadmap as a quiet horizontal measure, and avoids the busier collage/card treatment of the structural draft.
- Production constraint: generated classroom scenes and generated team portraits are reference-only. The public page ships real Unity captures and text-only team identities.

### Existing host context

- `educatian.github.io` is a static GitHub Pages repository with one root landing page and independent root-level subpages.
- The host has no repository-wide `DESIGN.md` or reusable component layer. This design system is intentionally scoped to `teacher-response-simulation/` so the existing site is preserved.

### Content jobs and decision path

1. Hook: name the urgent practice problem and show the Korean classroom prototype.
2. Orient: define classroom orchestration and the project's purpose.
3. Prove: show current Unity evidence and clearly dated prototype metrics.
4. Explain: connect the four research tracks and technical interaction loop.
5. Sequence: separate the three-year planned roadmap from completed prototype work.
6. Establish trust: identify the core and participating research team, roles, and institutions.
7. Bound claims: state research, privacy, safety, and non-clinical constraints.
8. Navigate: link back to Educatian and let readers jump to evidence or roadmap.

## 1. Atmosphere & Identity

The page should feel like a well-edited Korean education research dossier laid on warm archival paper. It is calm, serious, humane, and evidence-first. The visual identity comes from the classroom itself: deep chalkboard green, cream paper, honeyed wood, muted cabinet ochre, and one restrained terracotta marker for planned milestones.

- Vibe: editorial luxury with soft structuralism.
- Layout archetype: asymmetric editorial split, followed by single-purpose sections.
- Voice: precise, non-sensational, bilingual where useful, Korean-first.
- Realism: Unity screenshots are shown as evidence, never disguised as photography.
- Avoid: cold blue AI gradients, glass dashboards, medical red alerts, fake team photography, generic three-column feature grids, and decorative technology iconography.

## 2. Color

### Palette

| Token | Value | Role |
|---|---:|---|
| `--paper` | `#F4F1E8` | Page canvas |
| `--paper-raised` | `#FBFAF6` | Cards and inner media cores |
| `--paper-deep` | `#E8E3D7` | Outer shells and inactive controls |
| `--ink` | `#14231F` | Primary text and dark sections |
| `--ink-soft` | `#42524C` | Body and secondary text |
| `--ink-muted` | `#6F7974` | Captions and metadata |
| `--green` | `#173F35` | Primary identity, navigation, headings |
| `--green-2` | `#24594B` | Interactive hover and section emphasis |
| `--teal` | `#18796D` | Current-prototype status and focus accents |
| `--teal-soft` | `#D6E9E4` | Status chips and selected tabs |
| `--clay` | `#B75E3E` | Planned roadmap milestones only |
| `--clay-soft` | `#F0DDD4` | Planned-state chip background |
| `--line` | `#D7D1C4` | Warm separators and rings |
| `--focus` | `#156FCE` | Accessible keyboard focus ring |
| `--white` | `#FFFFFF` | Maximum contrast text/surfaces only |

### Rules

- Current, verified prototype evidence uses teal. Future and planned work uses clay.
- No gradients. Depth comes from nested warm surfaces, rings, and light/dark chapter changes.
- The chalkboard green is used in large areas only with paper or white text.
- Semantic meaning never relies on color alone. Every status includes visible text.

## 3. Typography

### Scale

| Token | Desktop | Mobile | Use |
|---|---:|---:|---|
| `--step-display` | `clamp(3.6rem, 7vw, 7.4rem)` | fluid | Hero Korean title |
| `--step-h2` | `clamp(2.4rem, 4.4vw, 4.7rem)` | fluid | Section heading |
| `--step-h3` | `clamp(1.45rem, 2vw, 2rem)` | fluid | Card/track heading |
| `--step-lede` | `clamp(1.05rem, 1.5vw, 1.35rem)` | fluid | Introductory prose |
| `--step-body` | `1rem` | `1rem` | Body text |
| `--step-small` | `0.875rem` | `0.875rem` | Captions and metadata |
| `--step-micro` | `0.75rem` | `0.75rem` | Eyebrows and labels |

### Font stack

- Display: `"Noto Serif KR", "Nanum Myeongjo", Georgia, serif`
- Body/UI: `"Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif`
- Numeric labels: body stack with tabular numerals, never monospace decoration.

### Rules

- Korean display text uses weight 500 and line-height `1.08` to retain editorial authority.
- Body copy uses weight 400 to 500 and line-height `1.75` for long-form readability.
- UI and captions are never smaller than 12px; body copy remains 16px or larger.
- Uppercase English eyebrows use `0.14em` tracking; Korean labels do not use wide tracking.
- Text columns cap at 68 characters or roughly 42rem.

## 4. Spacing & Layout

### Base unit

- Base unit: `4px`.
- Space scale: `4, 8, 12, 16, 24, 32, 48, 64, 88, 120, 160`.
- Section padding: `clamp(5rem, 10vw, 9rem)`.
- Content max width: `1280px`; reading max width: `720px`.

### Grid

- Desktop hero: 5/7 asymmetric split with the title slightly overlapping the media shell's visual plane.
- Desktop evidence: 7/5 split with a large proof frame and vertical evidence selector.
- Research tracks: alternating 5/7 rows, not a symmetric card grid.
- Team: three calm columns only because the content is genuinely parallel.
- Below 768px: every asymmetric section becomes one column; negative offsets and rotations disappear; section padding reduces to 64px and inline gutters to 20px.
- No fixed viewport-height sections. Hero uses content-driven minimum height.

### Rules

- Each section has one job and one dominant visual gesture.
- Section-to-section rhythm alternates dense proof with open explanatory space.
- Media always preserves its aspect ratio and declares intrinsic width and height.
- Touch targets are at least 44px by 44px with 8px minimum separation.

## 5. Components

### Floating project navigation

- Detached pill, maximum width 1180px, dark green surface, 18px outer radius.
- Desktop links are direct anchors. Mobile uses a two-line morph button and full-width paper menu island.
- States: default, hover, keyboard focus, active section, menu-open.

### Eyebrow and status chip

- Eyebrow: English utility label, micro size, green or muted ink.
- Status chip: pill with text plus a 6px dot. Teal means current snapshot; clay means planned.
- States: current, planned, neutral.

### Nested action button

- Fully rounded outer button with a trailing circular island containing a typographic arrow.
- Primary uses green/paper; secondary uses paper/green ring.
- States: default, hover translate, active scale `0.98`, focus ring, disabled opacity `0.45`.

### Double-bezel media frame

- Outer shell: paper-deep, 8px padding, 28px radius, warm ring.
- Inner core: paper-raised, 22px radius, overflow hidden, inset highlight.
- Image is never animated; only caption and selector states transition.
- States: default, selected gallery asset, focus-within.

### Evidence gallery

- One large responsive figure plus four semantic tab buttons.
- Selection updates image, alt text, title, description, and evidence label.
- States: selected, unselected, hover, focus, unavailable JavaScript fallback with all figures visible in `<noscript>`.

### Prototype metric strip

- Four facts with strong numeric value and precise qualifier.
- Current snapshot is dated. Numbers never animate as counters.

### Research track row

- Large two-digit index, serif title, short explanation, and a compact method line.
- Alternates text alignment only on desktop. No decorative icon.
- States: default, revealed on intersection, reduced-motion static.

### Roadmap chapter

- Three vertical plan cards connected by a quiet baseline on desktop.
- Each year shows dates, aim, methods, and explicitly planned output.
- Clay status label prevents future milestones from reading as completed.

### Team identity card

- Text-only identity with monogram, the verified supplied name (bilingual where available), affiliation, role, and contribution.
- No generated or inferred portrait.
- States: default and focus only when the affiliation link exists.

### Ethics boundary note

- Dark green chapter with four concise commitments: educational practice, non-clinical scope, privacy/IRB, and human oversight.
- Uses sentences, not warning-icon decoration.

## 6. Motion & Interaction

### Timing

| Token | Value | Use |
|---|---:|---|
| `--motion-fast` | `180ms` | Press and focus feedback |
| `--motion-base` | `420ms` | Hover and gallery state |
| `--motion-slow` | `760ms` | Section reveal |
| `--ease-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | Entrances and releases |
| `--ease-spring` | `cubic-bezier(0.32, 0.72, 0, 1)` | Navigation and buttons |

### Rules

- Animate only `transform`, `opacity`, and short `filter` transitions.
- IntersectionObserver reveals use 20px vertical travel and one stagger level only.
- Gallery changes cross-fade the image and caption; no carousel auto-play.
- The reading-progress bar uses `transform: scaleX()`.
- `prefers-reduced-motion: reduce` removes reveals, menu interpolation, and smooth scrolling while preserving all information and state changes.

## 7. Depth & Surface

### Strategy

- Level 0: flat paper canvas.
- Level 1: warm ring `0 0 0 1px rgba(20,35,31,.09)`.
- Level 2: nested bezel with inset white highlight.
- Level 3: whisper lift `0 18px 60px rgba(20,35,31,.10)` reserved for hero/evidence media.
- Level 4: dark chapter contrast, not a heavier shadow.

- Large cards use 24 to 32px radii; small controls use pills or 12 to 16px radii.
- No backdrop blur on scrolling content. The navigation may use an opaque dark surface, avoiding blur cost.
- No generic gray borders and no hard black drop shadows.

## 8. Accessibility Constraints & Accepted Debt

### Constraints

- WCAG AA contrast minimum for all text and meaningful controls.
- Full keyboard navigation for menu, anchors, gallery tabs, and image dialog.
- Focus is always visible with a 3px blue ring and 3px offset.
- Every Unity image has contextual Korean alt text, declared dimensions, and a nearby caption distinguishing prototype evidence from research plans.
- The page remains meaningful with JavaScript disabled; core content and at least the lead image stay visible.
- Navigation labels are explicit, skip link is first, headings remain hierarchical, and landmarks are named.
- No flashing, parallax, autoplay, forced horizontal scroll, or motion-dependent meaning.
- Team identities are text-based to avoid misleading or unauthorized portraits.
- Research plans, current prototype facts, and safety boundaries are linguistically separated.

### Accepted debt

- The page uses a system-first Korean and Latin font stack so school networks do not depend on external font delivery.
- The current Unity prototype images include development-stage geometry and interface details. Captions label them as a dated research prototype rather than a finished product.
- The public page does not embed a live Unity build because the verified build target is currently Windows. It documents the prototype with evidence captures instead.
- Funding award status is not asserted until an official public award source is available. The page identifies the content as a three-year research plan.
