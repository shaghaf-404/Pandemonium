# Pandemonium :: Red  

The AI-driven offensive agent. It plans, runs, and **verifies** multi-step
attacks against lab targets on a hard-coded allowlist, and reports verified
findings (JSON / SARIF) to the Blue and GRC systems.

> Lab-only. Every target passes through the allowlist before anything runs.

## What's here so far (foundation)

| File | What it is | Status |
|------|------------|--------|
| `pandemonium_red/allowlist.py` | default-deny target allowlist what Red is *allowed to attack*. Static, in our
 code, keeps the exercise inside the lab.
- **Blocklist** (Blue's firewall) (you're here)
1. HexStrike wired in as the executor (one tool, no AI)
2. first real verifier (proof-of-exploitation)
3. LLM planner its MCP
plumbing to the kali tools. The planning, verification, classification, and
chaining are ours.
