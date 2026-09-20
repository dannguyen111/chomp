# Running this in the cloud

Your machine never has to stay open. Total infrastructure cost: $0. The only
money spent is the $30 of OpenRouter credit.

## Setup (about 10 minutes, once)

1. Create a **public** repo and push the contents of `chomp/` to it. Public is
   what makes Actions free and unmetered. Nothing here is sensitive: the API key
   lives in encrypted secrets, never in the tree. If you would rather keep it
   private, see the note at the bottom.

2. Add the key under Settings, Secrets and variables, Actions, New repository
   secret. Name it exactly `OPENROUTER_API_KEY`.

3. Under Settings, Actions, General, set Workflow permissions to
   **Read and write**. The workflows commit the ledger back to the repo, which
   is how state survives between runs.

4. Run Phase 0 from the Actions tab: select `phase0`, Run workflow. This builds
   and validates the solver and caches the binary. It spends nothing.

5. Read the Phase 0 commit. That is Stop 1.

6. Run `session` manually once, with `session_cap` at `3.00`. Read
   `runs/<id>/transcript.jsonl` in the repo. That is Stop 2.

7. Once the prompt looks right, enable the schedule:

       git commit --allow-empty -m "autopilot on" && touch runs/AUTOPILOT
       git add runs/AUTOPILOT && git commit -m "autopilot on" && git push

   Sessions now run every 8 hours, alternating islands, until the budget guard
   trips. Delete the file to stop.

## What the repo gives you for free

- **Every ledger append is a commit.** Full history of what each session
  believed and when, diffable, with no extra tooling.
- **Concurrency group replaces flock.** GitHub queues a second run instead of
  starting it alongside the first, so two sessions can never race the ledger.
- **The budget guard runs before Python starts.** A run with under $3 remaining
  exits immediately rather than starting a session it would cut off mid-proof.
- **Transcripts are browsable in the web UI.** You can do a Stop 2 autopsy from
  your phone.

## Why every 8 hours

Three sessions a day at $3 each spends the whole budget in roughly four days,
which is the right pace for something you want to supervise at three checkpoints.
Going faster removes your ability to intervene before the money is gone. If you
want it slower, change the cron to `0 12 * * *` for one a day.

GitHub skips scheduled runs on repos with no activity for 60 days. Your sessions
commit on every run, so that will not trigger here.

## If you want a persistent box instead

**Oracle Cloud Always Free** gives a permanent ARM VM with 4 cores and 24GB RAM,
which beats the runners on memory and lets you keep large precomputed tables
resident between sessions. It is genuinely free forever. The catch is capacity:
the free ARM instances are hard to provision in popular regions, so budget an
afternoon of retrying or pick an unfashionable one. Run the harness there with
the original `run.sh` and a normal crontab. `flock` already handles the locking.

**Hetzner CX22** is about €3.79/month for 2 vCPU and 4GB. Reliable and instant,
and 4GB constrains how far the census can reach in one pass.

Free tier details move around, so confirm current limits before committing.

## Private repo note

Private repos get 2,000 free Actions minutes per month. Ten sessions at roughly
3 hours each comes to about 1,800 minutes, so it nearly fits, with no headroom
for Phase 0 or reruns. Public is the cleaner choice, and for a research project
you may want the history public anyway if something lands.
