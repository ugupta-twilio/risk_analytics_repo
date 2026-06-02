# Risk Analytics

Code repository for the Twilio Risk Analytics (RA) team.

## Adding a New Project

1. Copy `projects/_template/` to `projects/<your-project-name>/`
2. Update the copied `README.md` with what your project does and how to run it
3. Open a PR — RA leads are auto-assigned as reviewers

## SageMaker Studio Setup

If you work in SageMaker Studio, see [sagemaker/README.md](sagemaker/README.md) for one-time setup instructions to connect your Studio environment to this repo.

## Shared Utilities

Reusable helper code lives in `shared/utils/`. Import from there rather than copying code across projects.

## Team

| Role | Contact |
|---|---|
| RA Lead | *<add name>* |
| Repo admin | *<add name>* |

## Contributing

- All changes to `main` require a PR with at least 1 RA team member approval
- Do not commit data files, credentials, or `.env` files (see `.gitignore`)
- Run your code before merging — no broken notebooks on `main`
