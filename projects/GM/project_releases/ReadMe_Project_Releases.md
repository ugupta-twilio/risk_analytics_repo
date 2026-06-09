# GM Project Releases

This folder tracks released projects and the skill inventory for the GM area of Risk Analytics.

> **Note:** This folder sits **outside** the standard `projects/<area>/<TICKET-ID>/<username>/` hierarchy.
> It is a shared area maintained by the GM ticket lead — individual analysts do not have write access here.

---

## Folder Structure

```
project_releases/
└── skill_inventory/    # Inventory of analytical skills and tools across GM projects
```

---

## Who can create folders here

| Folder | Who can create | How |
|---|---|---|
| `project_releases/` | **Repo admin only** | Already created; do not rename |
| `project_releases/<subfolder>/` | **Ticket lead** (`@ugupta-twilio`) | Open a PR on branch `update/project-releases-<description>` |

Analysts cannot create folders here — the `path-check` CI will block any PR that touches `project_releases/` unless the author is the ticket lead.

---

## Contents

| Folder | Description |
|---|---|
| `skill_inventory/` | Inventory of skills and capabilities across GM projects |

---

## Adding or updating content

1. Branch: `update/project-releases-<short-description>`
2. Make your changes inside this folder
3. Open a PR — the GM ticket lead (`@ugupta-twilio`) is auto-assigned as reviewer
4. Merge once approved
