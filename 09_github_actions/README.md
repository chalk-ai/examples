# GitHub Actions
Deploy feature pipelines in GitHub Actions.

Docs: https://docs.chalk.ai/docs/github-actions

CLI Step: https://github.com/chalk-ai/cli-action

Deploy Step: https://github.com/chalk-ai/deploy-action

## 1. Install Chalk CLI
Install the Chalk CLI in a GitHub Action.

**[1_install_chalk_cli.yaml](1_install_chalk_cli.yaml)**

```yaml
- uses: chalk-ai/cli-action@v1
  with:
    client-id: ${{secrets.CHALK_CLIENT_ID}}
    client-secret: ${{secrets.CHALK_CLIENT_SECRET}}
```
Docs: https://docs.chalk.ai/docs/github-actions

Step: https://github.com/chalk-ai/cli-action

## 2. Deploy with Chalk
Deploy to Chalk (either as a preview deployment or to production).

**[2_deploy_with_chalk.yaml](2_deploy_with_chalk.yaml)**

```yaml
- uses: chalk-ai/deploy-action@v1
  with:
    client-id: ${{secrets.CHALK_CLIENT_ID}}
    client-secret: ${{secrets.CHALK_CLIENT_SECRET}}
    await: true
```
Docs: https://docs.chalk.ai/docs/github-actions

Step: https://github.com/chalk-ai/deploy-action

## 3. Preview deployments
Set up preview deployments for all PRs.

**[3_deploy_preview.yaml](3_deploy_preview.yaml)**

```yaml
- uses: chalk-ai/deploy-action@v1
  with:
    client-id: ${{secrets.CHALK_CLIENT_ID}}
    client-secret: ${{secrets.CHALK_CLIENT_SECRET}}
    await: true
    no-promote: true
```
Docs: https://docs.chalk.ai/docs/github-actions

Step: https://github.com/chalk-ai/deploy-action
