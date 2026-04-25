# Security Policy

## Supported Versions

We currently support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Democracy Desk seriously. If you believe you have found a security vulnerability, please report it to us by following these steps:

1.  **Do NOT open a public issue.**
2.  Email the vulnerability details to `security@democracydesk.ai` (Mock for Demo).
3.  Include a brief description, steps to reproduce, and potential impact.

## Security Hardening in this Project

Democracy Desk implements several military-grade security features:
- **Cloud Armor Simulation**: Rate limiting and IP-based filtering via middleware.
- **reCAPTCHA Enterprise**: Bot and credential stuffing protection.
- **Content Security Policy (CSP)**: Strict origin control.
- **Data Encryption**: All telemetry in BigQuery and Firestore is encrypted at rest by Google Cloud.
- **Secret Management**: API Keys are managed via environment variables and Cloud Secret Manager.
