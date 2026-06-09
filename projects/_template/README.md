# <Project Name>

## What this project does

*Describe the business question or problem this project addresses.*

## How to run

*List the steps to execute the code: environment setup, input data location, how to run scripts/notebooks, expected output.*

## Owner

*Your GitHub username — must match the folder name this README lives in.*

## Ticket

*The JIRA/ticket ID this project is associated with (e.g. RISK-3016).*

## Last updated

*YYYY-MM-DD*

---

## Folder rules

- This folder must be named after your **exact GitHub username** (case-sensitive)
- Only you and your ticket lead can merge changes into this folder
- Do not create subfolders for other analysts — each analyst creates their own folder via a self-service PR
- Do not store raw data files here — use S3 and reference the path in your notebooks

## Required files in this folder

| File | Purpose |
|---|---|
| `README.md` | This file — describe the project and how to run it |
| `__init__.py` | Empty — marks the folder as a Python package |
| `.sync-branch` | One line: the target branch for SageMaker auto-sync (e.g. `feature/RISK-3016`) |

Create `.sync-branch` when you join a ticket:
```bash
echo "feature/RISK-XXXX" > .sync-branch
```

See [Folder Structure Rules](../../../README.md#folder-structure-rules) in the repo README for the full policy on who can create what folders.
