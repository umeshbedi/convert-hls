# GitHub Actions: run convert.py

This repository includes a GitHub Actions workflow to install the AWS CLI, configure AWS credentials, install Python dependencies (boto3), and run `convert-hls/convert.py`.

Required repository secrets (set these in GitHub > Settings > Secrets > Actions):

- `AWS_ACCESS_KEY_ID` — your AWS access key id
- `AWS_SECRET_ACCESS_KEY` — your AWS secret access key
- `AWS_DEFAULT_REGION` — e.g. `us-east-1`
- `AWS_DEFAULT_OUTPUT` — e.g. `json`

How to run the workflow:

1. Push to `main` or trigger manually from the Actions tab (workflow_dispatch).
2. The workflow will:
   - install AWS CLI v2
   - run `aws configure` (using the secrets)
   - install `boto3`
   - run `python convert-hls/convert.py`

Notes and security:

- Do NOT commit AWS credentials into the repo. Use GitHub Secrets as described above.
- The Action runs on `ubuntu-latest` runner.
