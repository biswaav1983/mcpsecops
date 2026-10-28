# Compromised Third-Party Package Attack Lab

## Overview

This lab demonstrates a **software supply-chain attack** in which a compromised third-party Python package is introduced into an MCP application's CI/CD pipeline.

For this exercise, a **lab-created malicious version of `fastmcp`** is hosted on a local/internal PyPI server.

The objective is to demonstrate how insecure dependency resolution can allow an unintended package to enter a CI/CD build.

> ⚠️ **LAB USE ONLY**
>
> The malicious package used in this exercise must remain inside an isolated and authorized training environment.
>
> **Never upload the exercise package to public PyPI or publish it using a typosquatted package name.**

---

## Attack Scenario

An MCP application may automatically install Python dependencies when its CI/CD pipeline executes.

For example:

```text
Developer
    |
    v
Git Repository
    |
    v
CI/CD Pipeline
    |
    v
pip install
    |
    +-------------------------+
    |                         |
    v                         v
Public PyPI              Internal PyPI
Legitimate fastmcp       Exercise fastmcp
```

If package sources, versions, and integrity controls are not properly configured, the pipeline may install an unintended version of a dependency.

This lab demonstrates that risk using `fastmcp`.

---

# 1. Prerequisites

The following components are required:

- Linux/Ubuntu lab environment
- Python 3
- pip
- Twine
- Internal PyPI server
- GitLab or another CI/CD platform
- GitLab Runner or equivalent build agent
- MCP test application

The PyPI server should be accessible only from the lab environment.

Example internal repository:

```text
http://192.168.40.147:5001
```

---

# 2. Compromised Third-Party Package

For this exercise, we use a specially created **training version of `fastmcp`**.

The package exists only for demonstrating the risks associated with:

- Dependency confusion
- Package poisoning
- Compromised dependencies
- Uncontrolled package indexes
- Unpinned dependencies
- Missing integrity validation

The exercise package should be stored in:

```text
/malicious-fastmcp-build
```

Example:

```bash
cd /malicious-fastmcp-build
```

After building the package, the Python distribution artifacts should be available under:

```text
dist/
```

For example:

```text
dist/
├── fastmcp-999.0.0-py3-none-any.whl
└── fastmcp-999.0.0.tar.gz
```

---

# 3. Uploading to the Internal PyPI Index

An internal PyPI server must already be installed and running.

Upload the exercise package using **Twine**.

Navigate to the package directory:

```bash
cd /malicious-fastmcp-build
```

Upload the package:

```bash
python3 -m twine upload \
  --repository-url http://192.168.40.147:5001 \
  dist/*
```

Depending on the PyPI server configuration, Twine may request authentication credentials.

After uploading, verify that the package exists on the internal repository.

---

# 4. Poisoned Pipeline Attack Against an MCP Deployment

When a CI/CD pipeline builds an MCP deployment, it commonly installs Python dependencies automatically using `pip`.

Conceptually:

```text
Git Push
   |
   v
GitLab Repository
   |
   v
GitLab Pipeline
   |
   v
GitLab Runner
   |
   v
pip install
   |
   v
Python Dependencies
   |
   v
MCP Application
```

If dependency resolution is configured insecurely, an unintended package source may influence which artifact is installed.

For example:

```text
Internal PyPI
Exercise fastmcp
      |
      v
Dependency Resolution
      |
      v
CI/CD Runner
      |
      v
Package Installed
      |
      v
MCP Build
      |
      v
Deployment
```

This demonstrates why package installation should be treated as a **software supply-chain security boundary**.

---

# 5. Legitimate Project Versus Exercise Build

It is important to distinguish between the legitimate `fastmcp` project and the package created for this exercise.

| Package | Repository | Purpose |
|---|---|---|
| Legitimate `fastmcp` | Public PyPI | Normal application development |
| Exercise `fastmcp` | Internal lab PyPI | Security training only |

## Legitimate `fastmcp`

The real `fastmcp` package available through public PyPI is maintained by its project authors and is appropriate for normal development.

## Exercise Build

The malicious/training version of `fastmcp` exists **only on the lab-scoped internal package index**.

It is designed exclusively to demonstrate software supply-chain risks.

The exercise package must never be confused with or represented as the legitimate project.

---

# 6. Why the Attack Works

The lab demonstrates several dependency-management weaknesses.

```text
Uncontrolled Package Source
            +
Unpinned Dependency
            +
Missing Integrity Validation
            |
            v
   Dependency Resolution
            |
            v
      CI/CD Pipeline
            |
            v
      MCP Deployment
```

An insecure pipeline may trust a package based primarily on:

```text
Package Name
     +
Version Requirement
     +
Available Repository
```

This can create an opportunity for an unintended package to enter the build process.

---

# 7. Security Impact

A compromised dependency can potentially affect the confidentiality, integrity, and availability of the CI/CD environment.

Depending on the permissions granted to the build runner, the risk may extend to:

- Application source code
- CI/CD variables
- Build artifacts
- Deployment credentials
- API tokens
- Container registries
- Cloud credentials
- MCP configuration
- Production infrastructure

For this reason, CI/CD runners should always follow the principle of **least privilege**.

---

# 8. Recommended Defensive Controls

Organizations should implement multiple layers of software supply-chain protection.

### Pin Dependency Versions

Avoid uncontrolled dependency versions.

Dependencies should be explicitly reviewed and pinned according to the organization's dependency-management policy.

---

### Control Package Sources

CI/CD pipelines should use explicitly approved package repositories.

Avoid configurations that allow arbitrary or untrusted package indexes to participate in dependency resolution.

A preferred architecture is:

```text
CI/CD Pipeline
      |
      v
Approved Internal Repository
      |
      v
Reviewed Dependencies
      |
      v
Application Build
```

---

### Verify Package Integrity

Where supported, use cryptographic hashes or equivalent integrity controls to verify that downloaded packages match reviewed artifacts.

---

### Generate an SBOM

Generate a **Software Bill of Materials (SBOM)** for application builds.

The SBOM provides visibility into the software components included in the final deployment.

---

### Sign and Verify Artifacts

Where possible, implement:

```text
Build
  |
  v
Generate SBOM
  |
  v
Create Attestation
  |
  v
Sign Artifact
  |
  v
Verify Signature
  |
  v
Deploy
```

This provides additional assurance that artifacts have not been unexpectedly modified.

---

### Scan Dependencies

Integrate Software Composition Analysis and dependency scanning into the CI/CD pipeline.

Security controls can include:

- Dependency vulnerability scanning
- SCA scanning
- SBOM generation
- Package provenance validation
- Artifact signing
- Attestation verification
- CI/CD policy enforcement

---

# 9. Learning Objectives

After completing this exercise, participants should understand:

1. How Python dependencies enter an MCP application.
2. How package repositories influence dependency resolution.
3. Why third-party packages represent a software supply-chain risk.
4. How compromised packages can affect CI/CD environments.
5. Why dependency versions should be controlled.
6. Why package sources should be explicitly configured.
7. Why CI/CD runners should use least privilege.
8. How SBOMs improve dependency visibility.
9. How signing and attestations strengthen software supply-chain security.
10. How internal artifact repositories can reduce dependency-related risk.

---

# 10. Cleanup

After completing the exercise:

1. Remove the malicious/training package from the internal PyPI repository.
2. Restore the MCP project's legitimate dependency configuration.
3. Remove temporary CI/CD credentials used by the lab.
4. Remove generated training artifacts.
5. Confirm that the pipeline uses only approved package sources.
6. Re-run the pipeline and verify that only legitimate dependencies are installed.

The desired secure architecture should resemble:

```text
Developer
    |
    v
Source Repository
    |
    v
CI/CD Pipeline
    |
    v
Approved Internal Package Repository
    |
    v
Pinned + Verified Dependencies
    |
    v
Security Scanning
    |
    v
SBOM + Attestation
    |
    v
Artifact Verification
    |
    v
MCP Deployment
```

---

# ⚠️ Important Safety Notice

This repository and the malicious `fastmcp` package are intended **only for authorized cybersecurity and DevSecOps training**.

### DO NOT

- Upload the malicious package to public PyPI.
- Publish it to another public package repository.
- Use a typosquatted package name.
- Distribute it as the legitimate `fastmcp` project.
- Deploy the package into production.
- Test it against systems without authorization.
- Use the exercise to target third-party CI/CD environments.

### DO

- Keep the package inside the isolated lab.
- Use a private/internal PyPI server.
- Restrict access to the training environment.
- Remove the package after completing the exercise.
- Use the exercise to understand and improve software supply-chain security.

---

## Disclaimer

This project is intended solely for:

**Cybersecurity Training • DevSecOps Education • MCP Security Testing • Software Supply-Chain Security Research**

All demonstrations must be performed within an isolated environment that you own or are explicitly authorized to test.
