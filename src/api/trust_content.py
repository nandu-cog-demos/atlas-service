"""Static content for the public Trust Center.

This is a prototype: the data below is curated content rather than
live-sourced. Compliance status, subprocessors, and metrics would be
wired to real systems (audit tracker, status page, vendor registry)
before production.
"""

from __future__ import annotations

from typing import Any

TRUST_CENTER: dict[str, Any] = {
    "overview": (
        "Atlas is committed to protecting the telemetry and operational data "
        "our customers entrust to us. This Trust Center summarizes our "
        "security program, compliance posture, and the subprocessors that "
        "help us deliver the service."
    ),
    "last_updated": "2026-07-01",
    "certifications": [
        {
            "name": "SOC 2 Type II",
            "status": "certified",
            "description": (
                "Independently audited controls for security, availability, "
                "and confidentiality. Report available under NDA."
            ),
        },
        {
            "name": "ISO/IEC 27001",
            "status": "certified",
            "description": "Certified information security management system (ISMS).",
        },
        {
            "name": "GDPR",
            "status": "compliant",
            "description": (
                "Data processing agreements, EU data residency options, and "
                "documented data-subject request workflows."
            ),
        },
        {
            "name": "HIPAA",
            "status": "in_progress",
            "description": "Controls assessment underway; BAA available on request.",
        },
    ],
    "security_practices": [
        {
            "category": "Data Protection",
            "items": [
                "TLS 1.2+ for all data in transit",
                "AES-256 encryption for data at rest",
                "Tenant-scoped data isolation",
            ],
        },
        {
            "category": "Access Control",
            "items": [
                "SSO and SAML for operator accounts",
                "Role-based access control and least-privilege defaults",
                "Mandatory MFA for all employee access",
            ],
        },
        {
            "category": "Infrastructure",
            "items": [
                "Hosted on hardened, continuously patched cloud infrastructure",
                "Network segmentation and private VPCs",
                "Automated secrets management and rotation",
            ],
        },
        {
            "category": "Monitoring & Response",
            "items": [
                "24/7 security monitoring and alerting",
                "Documented incident response plan with defined SLAs",
                "Annual third-party penetration testing",
            ],
        },
    ],
    "subprocessors": [
        {
            "name": "Amazon Web Services",
            "purpose": "Cloud hosting and storage",
            "location": "United States, EU",
        },
        {
            "name": "Datadog",
            "purpose": "Observability and monitoring",
            "location": "United States",
        },
        {
            "name": "Stripe",
            "purpose": "Payment processing",
            "location": "United States",
        },
    ],
    "service_status": {
        "state": "operational",
        "uptime_90d": 99.98,
        "status_page_url": "https://status.atlas.example.com",
    },
    "resources": [
        {"label": "Security Whitepaper", "url": "https://atlas.example.com/security"},
        {"label": "Privacy Policy", "url": "https://atlas.example.com/privacy"},
        {"label": "Report a Vulnerability", "url": "mailto:security@atlas.example.com"},
    ],
}
