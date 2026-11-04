# competition ledger: re:Invent event catalog API hackathon

scratch pad, started 2026-11-04. reads all ten public rival entries against
our cli (`README.md`, `docs/mcp-approach.md`). each entry: what they built,
the one or two ideas worth stealing, and the verdict for us.
out-of-scope and deferred items live at the bottom with reasons, so we stop
re-litigating them.

multilanguage support is out of scope: english speaker, cannot judge quality
in japanese, chinese, korean, spanish, or portuguese. no machine-translated
ship.

## rivals

### 1. re:Invent planner (yukiogw) — the multilanguage + travel-model one

- whole ui in english, japanese, simplified chinese, korean, spanish,
  portuguese. bedrock ai summary per session per language, cached and shared;
  english users see raw abstracts, no ai call.
- natural-language search becomes visible filter chips.
- travel model: comfortable / tight / too late per gap, with walking speed,
  venue familiarity, time-of-day traffic, the 10-minute reserved-seat rule,
  and in-venue floors and areas (encore side vs wynn side, promenade south at
  caesars). route map per day on a campus map. full repeat of a session
  suggested when a gap is too late. recorded lectures go to a watch-later
  list so room time goes to chalk talks and workshops.
- deterministic core, model only picks and explains: code enforces overlaps,
  travel, venue limits (claude sonnet 4.6 on bedrock). ai spend capped at
  $3/day, $60/month, rule-based fallback above the cap.
- local companion on localhost:8484 reads and writes the official schedule
  (favorites, reservations, personal time, lunch included in travel checks).
- room-string parsing from the real catalog: two formats handled, areas added
  after counting rooms per venue. only the venetian value is published
  guidance (~10 min hotel to expo); wynn/encore and caesars values are
  labeled estimates.
- social layer: ogp share cards, 10-minute signed qr exchange, nearest-venue
  name only (no coordinates), 11 quests plus a world map of countries met.
- steal: in-venue areas and floors in the travel model; estimate labeling
  (published vs estimated); ai-cost cap with rule-based fallback; watch-later
  split for recorded sessions. skip the rest: multilanguage (out of scope),
  quests and qr (social app, not a planner).
- gap vs us: our gaps are 0 / 30 / 60 with no in-venue component, no
  10-minute-rule buffer, no area parsing, no estimate labels.

### 2. reinvent:match (jose antonio) — the swipe-and-reasons one

- five-step profile: up to 8 topics, level per topic (basic to 200,
  intermediate to 300, advanced to 300-400), vendor platforms, ai background,
  formats. existing favorites can seed the profile.
- swipe cards in three groups (reinforce, broaden, learn new), each with a
  match percentage from five scores: relevance, level, format, architecture
  depth, coverage. two hearts on a niche tech moves similar sessions up.
- real-week capacity per day with 60-minute lunch and walks included.
  hourly calendar shows walks between venues (orange when unreachable).
  clash click offers keep one, move to a repeat, or keep both.
- fill-my-week: maybes first, then best matches at your level, never
  sponsored, never under 65%.
- two-way favorites sync (portal-only favorites untouched), import-what-
  changed from the portal, lunch/walks/free time as personal time, .ics
  download. reservations in booking order (single-time first, then hands-on,
  then score) with live seat checks and one-click backup booking.
- steal: per-card reason plus score (our shortlist prints no why);
  booking order scarcest-first (our fill orders by format, not scarcity);
  .ics export (cheap, real user value); repeat-time move as a clash fix.
- gap vs us: no explanations on picks, no scarcity ordering, no .ics,
  no two-way sync diff.

### 3. ai agent + two mcp servers (alexander smirnoff) — the guide, not an app

- verified read-only recipe: codex cli plus aws events mcp plus a local
  google calendar mcp. documented but untested setups for claude code, kiro,
  desktop.
- planning rules worth copying verbatim: favorites are preferences while
  reservations, mandatory sessions, and busy intervals are constraints;
  isreservable=false is not seat evidence; a matching title is not identity,
  verify ids and times; unknown venue and empty-after-error mean unknown,
  not free.
- steal: google calendar busy-interval input (we plan against our schedule
  only, never against the rest of life); the constraints-vs-preferences
  split stated as a rule our fill already follows but never writes down.
- gap vs us: no outside-calendar awareness. note the oauth warning inside:
  the local calendar package asks for full calendar scope while tool
  filtering only hides tools. read-only claims need scope-level proof.

### 4. sessionmind (maria-alexandra radu) — the before/during/after one

- pre-session briefings on a 15-minute eventbridge tick: real abstract plus
  taxonomy plus aws knowledge mcp grounding, 3-bullet prep card.
- one-tool note capture bound to a real session id, optional recording link.
- post-conference: markdown trip report, linkedin draft, builder center
  draft from notes plus real metadata, with opinion slots left as editable
  placeholders the system refuses to invent.
- steal: the whole after-half is missing from our repo. our
  `docs/full-but-interesting.md` tracks no-seat topics, not what we learned.
  cheapest version: a notes file per reserved session plus a report command
  that stitches notes to real abstracts with explicit [you fill this] slots.
- gap vs us: no notes, no briefings, no trip report.

### 5. riv (akifumi niida) — the sessions-as-code one

- wanted state in yaml at the end of a spec file (reserved, favorite,
  none). `riv plan` diffs intent vs live schedule and writes nothing;
  `riv apply --plan <id>` runs exactly that diff; `riv verify` rechecks.
- safety rules: never touches reservations it did not make; replacing a
  reservation cancels first and says so, needs an explicit flag; unknown
  outcome stops instead of resending, `--resume` re-reads and sends only
  what is missing; no seat-polling grabber on principle.
- local sqlite catalog, 0.6 ms median search, ai sees a few result lines.
  measured rest at 1.34 s/page vs mcp at 1.64 s/page on the same 317 kb.
  mock server for no-signin tries. japanese search admitted weak (no
  morphological analysis).
- steal: plan-before-apply as a named artifact (our `--dry-run` prints but
  leaves no re-runnable plan id); `--resume` semantics for unknown outcomes
  (we reconcile deletes via getschedule, but reserves have no resume path);
  the no-polling stance as a stated policy.
- gap vs us: no declarative spec, no plan ids, no resume on reserve timeouts.

### 6. re:invent pathfinder (julian luna) — the learning-journey one

- starts from what you are building, not topics. knowledge profile, ranked
  knowledge gaps, learning path in three tiers (primary, alternatives,
  exploratory), every pick explained against the gaps it addresses.
- availability heatmap: color-coded bands (available, limited, unavailable,
  walk-up, unknown) across day, time, venue, with filters and personal
  schedule context. preserves bands, never invents counts.
- adaptive loop: post-session reflections re-rank gaps and later picks.
  learning report export (markdown): gaps covered, pending, takeaways,
  next actions. demo mode with simulated catalog, live mode with builder id
  plus bedrock. deterministic scheduling under the ai ranking.
- steal: heatmap thinking (our open-windows table in `docs/mcp-approach.md`
  is the same data in text form; a day-by-time grid would read faster);
  reflection-driven re-rank as a possible `fill` input later.
- gap vs us: no visual availability grid, no goal-driven pathing, no
  reflections. all three are real but each is a project, not a patch.

### 7. autonomous concierge (bhawesh kumar) — the safety-engineering one

- hybrid search under 150 ms: sqlite filters plus keyword plus semantic
  vectors (sqlite-backed, numpy cosine), reciprocal rank fusion.
- immutable plan alternatives with deterministic scores and per-session
  include/exclude reasons; explicit approval (short-lived, tied to plan and
  schedule state) before any write; journaled and re-verified against aws.
- transit on a networkx venue graph with inside-venue walking, floor and
  zone crossings, a profile transit multiplier, arrive-10-minutes buffer,
  tight-but-feasible flag, and `transit: a to b` personal-time blocks.
  unknown venue lowers confidence (estimate_quality low), never blocks.
- venue parsed from the room string (registry plus floor and repeat group);
  unknown first segment becomes a zone with venue unknown.
- repeat_group: one offering selected at most once across `-r` repeats.
- booking with approval-gated swaps (conflict_detected plus proposed swap
  plus single-use token; must-attend never released). seat snapper polls
  the waitlist in priority order, reserves only, never cancels; clash keeps
  swap_proposed plus attendee review. per-operation rate limiters sized to
  published quotas; 429 retry-after honored.
- steal, in order: transit blocks as personal time (visible walks on the
  real schedule); must-attend pinning; estimate_quality labeling; repeat
  groups as one offering; per-operation quota buckets (we run workers=12
  with a probe timeout, no per-op limiters).
- gap vs us: no walk blocks, no pins, no repeat-group rule, no quota
  buckets, no approval tokens. this is the deepest engineering bar in the
  field and the most worth studying file by file.

### 8. session assistant (girish bhatia) — the strands serverless one

- strands agent on lambda (python) behind api gateway, s3 plus cloudfront
  spa, bedrock haiku 4.5, dynamodb sessions/history/oauth/state with ttl,
  kms plus secrets manager, cloudwatch without token logging.
- plain-english requests with conversational follow-ups
  ("how many of those are workshops?"), dark-mode cards showing live
  favorite and reservation state, per-day summary with conflict checks.
- serverless deploy-and-teardown daily: up when needed, down when not.
- steal: conversation memory for follow-up filtering (our cli is one-shot
  per invocation); teardown-by-default hosting posture.
- gap vs us: no conversational layer, no hosted demo. both imply an mcp
  server or hosted agent we have not built (see deferred).

### 9. hallway (mati santoro) — the phone-app plus groups one

- expo react native, whole catalog on the phone. phone-side localhost oauth
  (tiny http listener on 127.0.0.1:8484, keychain/keystore refresh).
  backend (api gateway, lambda, dynamodb, bedrock sonnet 4.6) never sees
  the user token: only goals, a 120-candidate shortlist, display names,
  session codes, and busy ranges. agent answers through a forced tool call;
  ids outside the shortlist are dropped. scheduler on the phone, llm ranks
  while code timetables.
- groups: 8-character invite codes, i'm-in reserves your own seat with your
  token, find-free-time from busy ranges only, share-schedule exposes
  session codes while personal blocks always show busy, team split-sessions
  covers more ground, meetups land as personal time on each phone.
- write-then-verify everywhere: read getschedule, send only what is
  missing, per-session results, unknown means re-read never resend, final
  getschedule is what the app shows. scarcest seats first (verylimited,
  then limited, then available). replace-full-sessions re-plans around
  what you hold.
- personal-time api traps documented from live fire: event-local las vegas
  time not utc, 5-minute steps, same-day start/end, full-entry replace,
  title/description/location charset bans `[]{}|\\^` plus backtick and
  emoji (400 with no field named, first failure was their own `[hallway]`
  tag).
- steal: busy-ranges-only group coordination (privacy-preserving and api-
  honest, since the api never shows another attendee); scarcest-first
  booking; the personal-time charset and timezone traps (check ours before
  we hit them); token-never-leaves-device as the architecture invariant.
- gap vs us: no groups, no scarcest-first, personal-time edge cases
  untested on our side.

### 10. autopilot (sumon m selim) — the seat-game control loop

- ranked targets plus a quota-aware loop: the reserve attempt is the
  availability test (no waitlist exists in the api), laddering upgrades a
  placeholder to a better same-slot target with cancel-then-reserve plus an
  explicit rollback that re-reserves the placeholder on failure, and a loud
  warning when even the rollback fails.
- pure decision function (grab, upgrade, hold with reasons), unit-tested
  against a fake client including double failure. per-operation token
  buckets; tick default 5 minutes down to seconds near the event.
- walkable-week check with a venue graph plus closer-alternative
  suggestions scored by walking saved. personal time as hard constraints.
  local dashboard with clash and tight-walk warnings, dry-run mode that
  narrates decisions before writing.
- response-shape traps caught by probing raw json, not docs: events under
  `items`, schedule nested under `schedule` with `reserved` (not
  reservations), reserve under `result.successful` / `result.failed` with
  a per-item code. an early run reported 0 reserved and 0 favorites on a
  non-empty account because of a decoding mismatch.
- steal: rollback-with-loud-warning (our `--rebalance` rebooks on failure
  but never tests or reports the double-failure case); pure-function
  planner with reasons (ours is close: `fill` prints plans, but the
  decision function is not isolated and reason-coded); reserve-as-probe
  stated plainly; shape-probing before building.
- gap vs us: no background loop by design (we run by hand), double-failure
  path unhandled, planner reasons not machine-readable.

### 11. builder group planner (syed omer shah) — the smallest group tool

- one node file, zero dependencies: shared sessions (2+ members share a
  session), meetup slots (all-free windows, one-click personal time per
  calendar), group picks (group-topic sessions nobody holds, one-click
  group reservation).
- steal: meetup slots are the group version of our hallway-windows idea
  (see `docs/hallway-windows.md`); three group views are the right minimal
  shape if we ever do groups.
- gap vs us: no group views at all. single person to add if groups happen.

## where we stand (honest)

ahead or at parity: rest coverage of all write paths with write-then-verify
(getschedule confirms, deletes reconciled, `other` retried once); seat
sweeps with persisted timestamps; venue-gap planning with three tiers;
launch ledger (nobody else tracks launch signals); exclusion discipline
(bedrock except nova, frontier models) with a public record; stack-aware
pick from live resources; local-model rank path; no-polling by default.

behind, ranked by value over effort:

1. scarcity ordering plus per-card reasons (match, concierge, hallway).
   small change to `fill` ordering and `shortlist` output, visible daily.
2. repeat groups as one offering (concierge, hallway, planner).
   a `_base` strip exists in the mapper; planning does not enforce
   at-most-one across repeats.
3. in-venue areas, floors, and the 10-minute rule (planner, concierge).
   extends map-config, not a rewrite.
4. walk blocks as personal time (concierge, match, hallway).
   makes travel visible on the real schedule; needs the charset and
   timezone traps from hallway rechecked first.
5. plan ids plus resume on unknown reserve outcomes (riv).
   `--dry-run` output should be re-runnable, not just readable.
6. notes plus trip report (sessionmind). `docs/hallway-windows.md` covers
   where to meet; nothing covers what we learned.
7. availability grid (pathfinder). text tables first, graphics later.
8. quota buckets per operation (concierge, autopilot). fine at workers=12
   today; required before any loop or shared demo.
9. groups (hallway, group planner). needs the backend we do not have.
10. conversational layer and hosted demo (assistant, concierge, pathfinder).
    needs the mcp server decision below.

## out of scope (do not reopen without new facts)

- multilanguage ui and per-language ai summaries (planner). cannot judge
  quality in any second language; shipping unjudgeable output is worse
  than not shipping it.
- quests, qr exchange, world map, ogp cards (planner). social app, not a
  planner; no attendee demand stated.
- continuous seat polling and auto-snag (concierge, autopilot). polling
  against no waitlist looks like a bot; hand-run `fill` stays the default.
  revisit only if the api gains a real waitlist or availability feed.

## deferred (decided, not scheduled)

- mcp server for our planner. if on-demand functions are needed to support
  it, prefer rust on graviton lambdas (cost and cold start). no server
  design exists yet; the cli stays the interface until one does.
- webp animations of the mcp in action on bryanchasko.com/reinvent-26 with
  s3 hosting. blocked on the mcp server existing; brand recipe
  (`~/writing/brand.md`) is stills-first, so stills come before any motion
  in any case.
- groups, phone app, hosted demo, google calendar input. each needs either
  a backend holding other people's data or an oauth scope we have not
  justified. documented here, not started.

## coordination

- sumerian-signing-hosts (sibling repo, same org): checked 2026-11-04.
  their work is staged 3d-signing-host bakes, clean tree, no shared deploy
  path with this repo. no merge or deploy collision. recheck before any
  deploy that touches shared infra (budgets, asset buckets, site paths).
- bryanchasko.com/reinvent-26 page exists (`content/reinvent26/_index.md`).
  site edits stay in that repo with its own review; this repo links out,
  never duplicates.
