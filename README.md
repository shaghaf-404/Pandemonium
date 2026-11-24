<div align="center">
# ♟️ Pandemonium
 
### A living cyber-range where attack, defense, and governance play one long game of chess.
 
*Think like attackers. Engineer like defenders. Decide like risk owners.*
 
![track](https://img.shields.io/badge/track-integrated%20Red–Blue–GRC-6C4AB6)
![courses](https://img.shields.io/badge/CNC-418%20·%20411%20·%20419-1D9E75)
![lab](https://img.shields.io/badge/lab-EVE--NG-185FA5)
![containers](https://img.shields.io/badge/run-Docker%20Compose-0C447C)
![status](https://img.shields.io/badge/status-in%20development-BA7517)
 
</div>
---
 
## The idea
 
Most security stacks are three strangers: offense scales badly, defense drowns in alerts, and governance lives in a spreadsheet that never hears about the attack until it's over.
 
**Pandemonium puts all three on one board.** An AI **Red** agent attacks a synthetic enterprise. A **Blue** pipeline watches, detects, explains itself, and contains the threat. A **GRC** brain holds the enterprise context, recalculates risk live, and issues a treatment decision — which is pushed back as a real configuration change on the defenses.
 
So the attacker never plays the same board twice. Every round is a move. **That's the game.**
 
---
 
## ♟️ The loop
 
```
   GRC ──asset profiles──▶ RED ──attack + run_id──▶ BLUE
    ▲                                                 │
    │                                                 │  incident + metrics
    └──◀── config change ◀── risk + plan ◀────────────┘
                 ( the next move on the board )
```
 
Everything is stitched together by a shared `exercise_run_id`, and every record is tagged with its provenance: **AI-inferred**, **verified**, or **human-approved**.
 
---
 
## The three brains
 
| Brain | Course | What it does | Owner |
|-------|--------|--------------|-------|
| **Red** | CNC 418 | Plans, executes, and *verifies* multi-step attack chains against lab targets on a hard-coded allowlist | Shaghaf |
| **Blue** | CNC 411 | Vendor-agnostic SIEM/SOAR: detects, explains (XAI), and contains — with human-in-the-loop guardrails | Karim |
| **GRC** | CNC 419 | Standard-neutral governance: cross-framework mapping, ISRM scoring, budget optimizer, BIA | Safi |
 
Each brain is a standalone system — its own container, its own README, its own demo. The magic is that they talk.
 
---
 
## Repo layout
 
```
pandemonium/
├── contracts/      ★ shared schemas + IDs — the single source of truth
├── red/              CNC 418 — attack agent + verification
├── blue/             CNC 411 — detection + XAI + SOAR
├── grc/              CNC 419 — mapping + risk + BIA
├── integration/    ★ orchestrator + event bus + the closed loop
├── lab/              EVE-NG topology, firewalls, targets, synthetic enterprise
├── docs/             architecture, API, proposal, demo runbook
└── scripts/          up · seed · run-round · reset
```
 
> `contracts/` and `integration/` are what make this *one platform* instead of three dashboards behind one login.
 
---
 
## Quick start
 
```bash
# 1. clone + configure
cp .env.example .env        # fill in model keys / lab IPs
 
# 2. bring the platform up
make up                     # or: docker compose up -d
 
# 3. run one round of the game
make run-round              # GRC → Red → Blue → GRC → config change
 
# 4. reset the board to its golden state
make reset
```
 
---
 
## 🔌 How the brains talk
 
| Interface | Direction | Carries |
|-----------|-----------|---------|
| `GET /api/v1/assets/profile` | GRC → Red & Blue | `asset_id`, `criticality_tier`, `mtd_minutes`, `applicable_standards` |
| `POST /api/v1/findings` | Red → Blue & GRC | verified finding + `verified_poc`, as JSON & SARIF 2.1.0 |
| `POST /api/v1/incidents` | Blue → GRC | `mttd_sec`, `mttc_sec`, `mttr_sec`, `containment_action`, `residual_status` |
 
Full schemas live in [`contracts/`](contracts/).
 
---
 
## Safety & scope
 
This is an isolated war-game, and it stays that way:
 
- **Hard-coded allowlist** — the Red agent only ever touches approved lab targets (`localhost`, lab subnets). Anything else is refused in code.
- **Sandbox only** — all offense and automated containment run inside the EVE-NG lab, never against production or public infrastructure.
- **Synthetic data only** — no real corporate records or personal data ever touch an external model.
- **Human-in-the-loop** — disabling accounts, isolating critical hosts, and accepting risk all require a human sign-off.
---
 
## Team
 
| Member | Role |
|--------|------|
| **Shaghaf** | Red Team lead (CNC 418) |
| **Karim** | Blue Team lead (CNC 411) |
| **Alsafy** | GRC lead (CNC 419) |
 
All three own the integration layer together, and any member can defend any part of the codebase.
 
---
 
<div align="center">
Integrated Cybersecurity Capstone · Fall 2026
 
*Built for the lab. Kept in the lab.*
 
</div>
 
