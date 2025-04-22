
import { useState } from "react";
import Link from "next/link";

export default function Resume() {
  const experience = [
  {
    "company": "InterVision Systems, LLC.",
    "title": "Principal Cloud Security Architect",
    "dates": "Nov 2023 \u2013 Present",
    "details": [
      "Built the Professional Services Cloud Security Program Charter and supporting policies.",
      "Conducted client-facing Cloud Security Assessments using an Observe, Plan, Report methodology.",
      "Built reconnaissance automation to bootstrap Cloud Assessments for AWS.",
      "Designed and authored Continuous Monitoring (ConMon) for AWS environments.",
      "Authored security finding triage framework and remediation pipelines.",
      "Developed structured DevSecOps practices with Snyk, Veracode, Checkov, PrismaCloud.",
      "Mentored security engineers in Cloud Security, DevSecOps, threat modeling.",
      "Primary escalation for AWS Professional Services engineers and clients.",
      "Authored transition and handoff process for cloud deployment teams."
    ]
  },
  {
    "company": "Tanium, Inc.",
    "title": "Sr. Cloud Security Engineer",
    "dates": "Feb 2022 \u2013 Sep 2023",
    "details": [
      "Supported SaaS environments in commercial and Highly Regulated Environments.",
      "Developed and maintained Terraform, Python, PowerShell, and Bash scripts.",
      "Migrated Jenkins to GitHub Actions with security validation.",
      "Enhanced Continuous Monitoring with Tanium automation.",
      "Authored security runbooks, policies, and operational procedures."
    ]
  },
  {
    "company": "Kion (cloudtamer.io)",
    "title": "Sr. Cloud Security Architect",
    "dates": "Jun 2020 \u2013 Feb 2022",
    "details": [
      "Guided clients through AWS and Azure security best practices.",
      "Managed 650+ cloud accounts and security automation.",
      "Developed reusable reference architectures.",
      "Led IAM and governance integrations with SAML/SSO.",
      "Served on the Product Strategy Council influencing security direction.",
      "Automated CI/CD security integrations and supported Cloudtamer.io platform."
    ]
  }
];

  const sections = [
    {
      title: "Summary",
      content: "I’m a technologist who enjoys understanding every project or environment from concept through design, integration, and deployment..."
    },
    {
      title: "Certifications",
      content: "AWS Certifications: (Security, Database, Solutions Architect, DevOps, SysOps, Developer, Cloud Practitioner)\nMicrosoft Certification: Azure Fundamentals"
    },
    {
      title: "Experience",
      content: experience
    },
    {
      title: "Notable Skills",
      content: "Technical & Executive Documentation, Problem Solving, Automation, Mentorship, Project Leadership"
    },
    {
      title: "Security Services",
      content: "Defensive Network Design, Blue Team Operations, Cloud Security, System Hardening, Compliance Automation"
    },
    {
      title: "Cloud Services",
      content: "AWS, Azure, CNAPP Tools, Container Security, Cloud Security Assessments, Guardrails"
    },
    {
      title: "Identity Management",
      content: "RBAC, Entra ID, SAML, PIM, Federation, Hybrid IAM"
    },
    {
      title: "DevOps",
      content: "CI/CD Pipelines, Terraform, Secrets Management, GitOps, IaC Automation"
    },
    {
      title: "SaaS Integrations",
      content: "Jira, Confluence, M365, Microsoft Defender, Veracode, PrismaCloud, CrowdStrike"
    }
  ];

  return (
    <div className="flex min-h-screen">
      <aside className="w-48 bg-gray-100 p-4 text-sm text-gray-700 border-r">
        <nav className="flex flex-col space-y-2">
          <Link href="/" className="hover:underline">Home</Link>
          <Link href="/resume" className="hover:underline font-semibold">Resume</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8 bg-gray-50">
        <h1 className="text-3xl font-bold mb-4">Resume: William Brady</h1>
        <a href="/william_brady_resume_2025.pdf" className="text-blue-600 underline mb-6 inline-block" target="_blank" rel="noopener noreferrer">
          Download Resume PDF
        </a>
        <div className="space-y-4">
          {sections.map((section, idx) => (
            <Section key={idx} title={section.title} content={section.content} />
          ))}
        </div>
      </main>
    </div>
  );
}

function Section({ title, content }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border rounded bg-white shadow-sm">
      <button
        onClick={() => setOpen(!open)}
        className="w-full text-left px-4 py-3 bg-gray-100 hover:bg-gray-200 font-semibold"
      >
        {title}
      </button>
      {open && (
        <div className="px-4 py-3 text-sm text-gray-800 border-t">
          {Array.isArray(content) ? (
            <div className="space-y-3">
              {content.map((job, i) => (
                <NestedJob key={i} job={job} />
              ))}
            </div>
          ) : (
            <p className="whitespace-pre-line">{content}</p>
          )}
        </div>
      )}
    </div>
  );
}

function NestedJob({ job }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border rounded">
      <button
        onClick={() => setOpen(!open)}
        className="w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 font-medium text-sm"
      >
        {job.title} at {job.company} <span className="text-gray-500 text-xs">({job.dates})</span>
      </button>
      {open && (
        <ul className="list-disc pl-6 pr-4 py-2 text-sm text-gray-700 space-y-1">
          {job.details.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
