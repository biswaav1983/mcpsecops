# MCP DevSecOps CI/CD Security Pipeline

This project demonstrates a **DevSecOps CI/CD pipeline for an MCP (Model Context Protocol) application** using GitLab CI/CD.

The pipeline integrates multiple security controls into the software delivery lifecycle, including:

- Python dependency validation
- Bandit SAST scanning
- Semgrep SAST scanning
- Gitleaks secret detection
- Cisco AI MCP Security Scanner
- Integration stage
- Manual production deployment
- Security scan artifact collection

The pipeline uses a **GitLab Docker Runner** with **Docker-in-Docker (DinD)** for container-based security scanning.

---

# Pipeline Architecture

The pipeline follows the following workflow:

```text
                     GitLab Repository
                            |
                            v
                     +-------------+
                     |    BUILD    |
                     +------+------+
                            |
                            v
        +-------------------------------------------+
        |               TEST STAGE                  |
        |                                           |
        |  +---------+ +---------+ +-------------+ |
        |  | Bandit  | | Semgrep | |  Gitleaks   | |
        |  +---------+ +---------+ +-------------+ |
        |                                           |
        |          +---------------------+          |
        |          | MCP Security Scanner|          |
        |          +---------------------+          |
        +-------------------+-----------------------+
                            |
                            v
                    +---------------+
                    |  INTEGRATION  |
                    +-------+-------+
                            |
                            v
                    +---------------+
                    |  PRODUCTION   |
                    |    Manual     |
                    +---------------+
```

---

# Pipeline Stages

The GitLab pipeline contains the following stages:

```yaml
stages:
  - build
  - test
  - integration
  - prod
```

The overall pipeline flow is:

```text
Build
  |
  v
Security Testing
  |
  +-- Bandit
  |
  +-- Semgrep
  |
  +-- Gitleaks
  |
  +-- Cisco AI MCP Scanner
  |
  v
Integration
  |
  v
Production
```

---

# 1. Build Stage

The build stage uses:

```text
python:3.11
```

The job installs the project dependencies:

```bash
pip install -r requirements.txt
```

It then verifies that the MCP library can be imported successfully:

```bash
python -c "import mcp; print('mcp library imported ok')"
```

Finally, all installed Python packages and versions are recorded:

```bash
pip freeze > build-dependencies.txt
```

## Build Artifact

The following artifact is generated:

```text
build-dependencies.txt
```

This provides a snapshot of the Python dependencies installed during the pipeline build.

Artifact retention:

```text
7 days
```

---

# 2. Bandit SAST Scan

Bandit is used to perform **Static Application Security Testing (SAST)** against the Python source code.

The pipeline uses:

```text
hysnsec/bandit
```

The scanner executes:

```bash
bandit -r /src \
  -x /src/tests \
  -f json \
  -o /src/bandit-output.json
```

The scan recursively examines the project while excluding the test directory.

## Bandit Artifact

```text
bandit-output.json
```

The report is generated in JSON format and retained for:

```text
7 days
```

The job is configured with:

```yaml
allow_failure: true
```

Therefore, security findings do not stop the remaining pipeline stages.

---

# 3. Semgrep SAST Scan

Semgrep performs additional **static security analysis**.

The pipeline uses:

```text
returntocorp/semgrep:1.92.0
```

The following Semgrep rule sets are enabled:

```text
p/python
p/security-audit
```

The scanner executes:

```bash
semgrep \
  --config p/python \
  --config p/security-audit \
  --error \
  --json \
  --output /src/semgrep-output.json \
  /src
```

## Semgrep Artifact

The scan generates:

```text
semgrep-output.json
```

The artifact is retained for:

```text
7 days
```

The job is configured as:

```yaml
allow_failure: true
```

This allows the pipeline to continue while still preserving security findings for analysis.

---

# 4. Gitleaks Secret Detection

Gitleaks searches the repository for accidentally committed secrets and sensitive information.

Examples include:

- API keys
- Authentication tokens
- Passwords
- Private keys
- Cloud credentials
- Database credentials
- Other secret patterns

The pipeline uses:

```text
zricethezav/gitleaks:v8.30.1
```

The scanner executes:

```bash
gitleaks detect \
  --source /src \
  --report-format sarif \
  --report-path /src/gitleaks-output.sarif \
  --exit-code 1
```

## Gitleaks Artifact

The generated report is:

```text
gitleaks-output.sarif
```

The report uses the **SARIF (Static Analysis Results Interchange Format)** format.

Artifact retention:

```text
7 days
```

The job uses:

```yaml
allow_failure: true
```

so secret findings can be reviewed without automatically terminating the complete pipeline.

---

# 5. Cisco AI MCP Security Scanner

The pipeline includes security testing specifically for the **Model Context Protocol (MCP)** application.

The scanner is installed using:

```bash
pip install cisco-ai-mcp-scanner==4.6.0 mcp==1.29.1
```

The scanner is configured with:

```bash
export MCP_SCANNER_STDIO_TIMEOUT=180
```

The MCP server is launched using:

```text
mcp run challenges/challenge2/server_http.py:mcp
```

The security scan executes:

```bash
mcp-scanner \
  --log-level error \
  --analyzers yara \
  --format raw \
  stdio \
  --stdio-command mcp \
  --stdio-arg run \
  --stdio-arg challenges/challenge2/server_http.py:mcp
```

The output is captured using:

```bash
tee mcp-scan-output.json
```

The pipeline then searches the scanner output for:

```json
"is_safe": false
```

If this value is detected, the job reports:

```text
MCP findings detected
```

and exits with a non-zero status.

Because the job has:

```yaml
allow_failure: true
```

the finding is reported without blocking subsequent pipeline stages.

## MCP Scanner Artifact

```text
mcp-scan-output.json
```

Artifact retention:

```text
7 days
```

---

# 6. Integration Stage

After security testing, the pipeline executes the integration stage.

Currently, this is a demonstration step:

```bash
echo "This is an integration step." | tee integration-output.txt
```

## Integration Artifact

```text
integration-output.txt
```

The artifact is retained for:

```text
7 days
```

This stage can later be expanded to include:

- API integration testing
- MCP client/server testing
- Functional testing
- End-to-end testing
- Authentication testing
- Authorization testing

---

# 7. Production Stage

The final stage represents deployment to production.

The current demonstration command is:

```bash
echo "This is a deploy step." | tee prod-output.txt
```

## Manual Deployment

Production is configured with:

```yaml
when: manual
```

Therefore, production deployment does not execute automatically.

An authorized user must manually trigger the production job from the GitLab pipeline interface.

## Production Artifact

```text
prod-output.txt
```

The artifact is retained for:

```text
7 days
```

---

# Docker-in-Docker Architecture

The pipeline uses Docker-in-Docker for container-based security scanners.

The configuration is:

```yaml
services:
  - name: docker:27-dind
    alias: docker

variables:
  DOCKER_HOST: "tcp://docker:2375"
  DOCKER_TLS_CERTDIR: ""
```

The security scanner jobs use:

```text
docker:27-cli
```

as their job image.

The architecture is:

```text
GitLab Runner
      |
      v
+-----------------------+
| docker:27-cli         |
|                       |
| docker pull           |
| docker run            |
+----------+------------+
           |
           | TCP 2375
           v
+-----------------------+
| docker:27-dind        |
|                       |
| Docker Daemon         |
+----------+------------+
           |
           +------------------+
           |        |         |
           v        v         v
        Bandit   Semgrep   Gitleaks
```

---

# GitLab Runner Requirements

The pipeline requires a GitLab Runner using the Docker executor.

Example runner configuration:

```toml
[[runners]]
  name = "local-docker-runner"
  executor = "docker"

  [runners.docker]
    tls_verify = false
    image = "docker:27-cli"
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 0
```

The following setting is important for conventional Docker-in-Docker operation:

```toml
privileged = true
```

Restart GitLab Runner after modifying its configuration:

```bash
sudo systemctl restart gitlab-runner
```

Verify the runner:

```bash
sudo gitlab-runner verify
```

---

# Pipeline Artifacts

Each pipeline execution generates security and operational artifacts.

| Pipeline Job | Artifact | Format |
|---|---|---|
| Build | `build-dependencies.txt` | Text |
| Bandit | `bandit-output.json` | JSON |
| Semgrep | `semgrep-output.json` | JSON |
| Gitleaks | `gitleaks-output.sarif` | SARIF |
| MCP Scanner | `mcp-scan-output.json` | JSON/Raw |
| Integration | `integration-output.txt` | Text |
| Production | `prod-output.txt` | Text |

All artifacts are retained for:

```text
7 days
```

Artifacts can be downloaded from the corresponding GitLab pipeline job.

---

# Security Pipeline Summary

| Security Control | Tool | Purpose |
|---|---|---|
| Dependency Validation | pip | Validate application dependencies |
| SAST | Bandit | Detect Python security weaknesses |
| SAST | Semgrep | Detect insecure code patterns |
| Secret Detection | Gitleaks | Detect exposed credentials and secrets |
| MCP Security | Cisco AI MCP Scanner | Analyze MCP server security |
| Security Evidence | GitLab Artifacts | Preserve scanner results |

---

# Security Findings and Pipeline Behavior

The security scanning jobs use:

```yaml
allow_failure: true
```

This is intentional for a security demonstration or training environment.

It allows the pipeline to:

```text
Build
   |
   v
Security Scan
   |
   +---- Findings detected
   |
   +---- Report uploaded
   |
   v
Pipeline continues
```

For a production DevSecOps implementation, security gates can be introduced so that findings above an approved severity level prevent deployment.

---

# Running the Pipeline

Clone the repository:

```bash
git clone <repository-url>
```

Enter the project directory:

```bash
cd mcpdevsecops
```

After modifying the project or pipeline:

```bash
git add .
git commit -m "Update DevSecOps security pipeline"
git push origin main
```

The GitLab pipeline should start automatically after the push.

Pipeline execution can be monitored from:

```text
GitLab
  -> Project
  -> Build
  -> Pipelines
```

---

# Expected Pipeline Flow

A successful pipeline should show approximately:

```text
build                    PASSED

sast-bandit              PASSED / ALLOWED FAILURE
sast-semgrep             PASSED / ALLOWED FAILURE
secrets-gitleaks         PASSED / ALLOWED FAILURE
mcp-scanner              PASSED / ALLOWED FAILURE

integration              PASSED

prod                     MANUAL
```

The production stage remains pending until manually triggered.

---

# Troubleshooting

## `docker: not found`

If the pipeline reports:

```text
/bin/sh: docker: not found
```

verify that Docker-based jobs use:

```yaml
image: docker:27-cli
```

---

## Cannot Connect to Docker Daemon

If the pipeline reports that it cannot connect to Docker, verify:

```yaml
DOCKER_HOST: "tcp://docker:2375"
DOCKER_TLS_CERTDIR: ""
```

Also verify that the GitLab Runner is configured with:

```toml
privileged = true
```

---

## Artifact Not Found

An error similar to:

```text
WARNING: bandit-output.json: no matching files
ERROR: No files to upload
```

usually means the scanner failed before generating its report.

Check the scanner output earlier in the GitLab job log.

---

## Docker Connectivity Test

For troubleshooting Docker-in-Docker, add:

```bash
docker info
```

before:

```bash
docker pull
```

For example:

```yaml
script:
  - docker info
  - docker pull hysnsec/bandit
```

If `docker info` succeeds, the Docker CLI can communicate with the DinD Docker daemon.

---

# Important Security Considerations

This pipeline is suitable for **DevSecOps training, MCP security experimentation, and controlled lab environments**.

For production environments, consider additional controls such as:

- Pinning container images by digest
- Dependency vulnerability scanning
- Software Bill of Materials (SBOM) generation
- Container image scanning
- Signed artifacts
- Build provenance/attestation
- Protected production environments
- Branch protection
- Security approval gates
- Least-privilege runners
- Secure handling of CI/CD secrets

Never commit credentials, GitLab runner tokens, API keys, passwords, or private keys to the repository.

---

# Purpose

The primary purpose of this project is to demonstrate how traditional application security controls and AI/MCP-specific security testing can be incorporated into a GitLab CI/CD workflow.

The pipeline demonstrates a practical **DevSecOps security testing lifecycle**:

```text
CODE
 |
 v
BUILD
 |
 v
SAST
 |---- Bandit
 |---- Semgrep
 |
 v
SECRET SCANNING
 |---- Gitleaks
 |
 v
AI / MCP SECURITY
 |---- Cisco AI MCP Scanner
 |
 v
INTEGRATION
 |
 v
MANUAL PRODUCTION DEPLOYMENT
```

This provides multiple security checkpoints before an application reaches the production stage.
