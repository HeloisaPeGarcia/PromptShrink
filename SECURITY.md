# Security Policy — PromptShrink 🛡️

## Supported Versions

Below are the versions of PromptShrink currently supported with security updates:

| Version | Supported | Notes |
| ------- | --------- | ----- |
| `0.2.x` | :white_check_mark: | Current active release |
| `0.1.x` | :white_check_mark: | Critical security patches only |
| `< 0.1` | :x: | End of life |

---

## 🔒 Security Scope & Design Considerations

PromptShrink is designed to act as a **local pre-processor** and API proxy. Please note the following security guarantees and scope boundaries:

1. **Data Privacy & Transmission:** PromptShrink processes text locally or on your self-hosted server. It does **not** send prompt data to third-party servers outside of your direct environment.
2. **PII Masking (`pii_detector.py`):** PII masking uses deterministic regex patterns for common Brazilian & global identifier formats (CPF, CNPJ, Email, Phone, Credit Cards). It is intended as a privacy shield layer and should be combined with enterprise DLP rules where strict compliance is required.
3. **Prompt Injection Risk Detector (`injection_detector.py`):** The threat detector checks for common jailbreak and instruction override patterns (`risk_score`). It provides defense-in-depth, but applications should still enforce model-level system instructions.

---

## 📩 Reporting a Vulnerability

If you discover a security vulnerability or security flaw in PromptShrink, please report it responsibly:

### How to Report
- **Email:** Send details to `security@promptshrink.dev` (or open a GitHub Private Vulnerability Report).
- **Do NOT open a public GitHub issue** for undisclosed security vulnerabilities.

### What to Include in Your Report
1. A clear description of the vulnerability and potential impact.
2. Step-by-step instructions or proof-of-concept (PoC) script to reproduce the issue.
3. Affected module/endpoint (e.g. `pii_detector`, `api/routes/optimize.py`).

### Response Expectations
- **Initial Acknowledgment:** Within **48 hours**.
- **Status & Triage Update:** Within **5 business days**.
- **Fix & Disclosure Schedule:** Fixes are prioritized and published in a patch release (`0.2.x`).

Thank you for helping keep PromptShrink safe!
