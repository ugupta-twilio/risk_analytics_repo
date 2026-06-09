# Skill Inventory

Tracks analytical skills, models, and tools available across the GM Risk Analytics team —
useful for onboarding new analysts and identifying reusable work.

> **Folder location:** `projects/GM/project_releases/skill_inventory/`
> This folder is **outside** the per-ticket analyst hierarchy. Only the GM ticket lead can merge changes here.

---

## Who can create folders / files here

| Action | Who can do it |
|---|---|
| Add or update files in `skill_inventory/` | **Ticket lead only** (`@ugupta-twilio`) |
| Create new subfolders | **Ticket lead only** — open a PR on `update/skill-inventory-<description>` |

Analysts cannot write here — the `path-check` CI enforces this.

---

## How to update

1. Branch: `update/skill-inventory-<date-or-description>`
2. Add or update entries in this folder
3. Open a PR — the GM ticket lead (`@ugupta-twilio`) is auto-assigned as reviewer
4. Merge once approved

---

## Structure convention

Group entries by skill type:

```
skill_inventory/
├── models/        # ML models and scoring approaches
├── features/      # Feature engineering methods
├── tools/         # Shared libraries and utility scripts
└── processes/     # Standard analytical workflows
```

Create a subfolder only if it doesn't already exist and its scope is clearly distinct.
