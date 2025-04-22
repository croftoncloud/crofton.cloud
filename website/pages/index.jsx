import Image from "next/image";
import Link from "next/link";

export default function Home() {
  const projects = [
    {
      title: "Security Hub Automation Framework",
      description:
        "Designed a triage and remediation pipeline integrating AWS Security Hub, EventBridge, Lambda, Jira, and Slack — enabling real-time incident workflows.",
    },
    {
      title: "Cloud Security Assessments",
      description:
        "Developed a repeatable assessment process using Observe, Plan, Report to identify misconfigurations, compliance gaps, and remediation strategies across AWS environments.",
    },
    {
      title: "Continuous Monitoring (ConMon)",
      description:
        "Authored ConMon methodology for AWS environments leveraging native services and third-party integrations to deliver real-time detection and alerting of issues.",
    },
    {
      title: "Infrastructure-as-Code (IaC) Framework",
      description:
        "Built scalable IaC libraries and hand-off frameworks to support secure, automated deployments including alarms, dashboards, and event pipelines.",
    },
    {
      title: "CI/CD Pipeline Modernization",
      description:
        "Migrated legacy Jenkins pipelines to GitHub Actions, incorporating automated testing, code linting, and security scans using Veracode, Snyk, and Prisma Cloud.",
    },
  ];

  const timeline = [
    {
      role: "Principal Cloud Security Architect",
      company: "InterVision Systems",
      dates: "2023 – Present",
    },
    {
      role: "Sr. Cloud Security Engineer",
      company: "Tanium",
      dates: "2022 – 2023",
    },
    {
      role: "Sr. Cloud Security Architect",
      company: "Kion (cloudtamer.io)",
      dates: "2020 – 2022",
    },
    {
      role: "Principal Security Engineer / Director of IT & Security",
      company: "Dragos",
      dates: "2018 – 2020",
    },
    {
      role: "Enterprise Security Architect",
      company: "T. Rowe Price",
      dates: "2009 – 2018",
    },
  ];

  return (
    <div className="flex min-h-screen">
      <aside className="w-48 bg-gray-100 p-4 text-sm text-gray-700 border-r">
        <nav className="flex flex-col space-y-2">
          <Link href="/" className="hover:underline">Home</Link>
          <Link href="/resume" className="hover:underline">Resume</Link>
        </nav>
      </aside>

      <main className="flex-1 p-8 bg-gray-50">
        <div className="text-center max-w-3xl mx-auto">
          <Image
            src="/securchitect.jpg"
            alt="Cartoon profile of William Brady"
            width={200}
            height={200}
            className="mx-auto rounded-full mb-6"
          />
          <h1 className="text-4xl font-bold mb-2">William Brady</h1>
          <p className="text-lg text-gray-700 mb-4">Principal Cloud Security Architect</p>
          <p className="text-md text-gray-600">
            I design secure, scalable systems in the cloud. From architecture to automation,
            I've built cloud security programs, CI/CD pipelines, IAM models, and compliance
            guardrails that work in the real world.

            I am currently learning react and next.js to build a personal website and portfolio.
            Please escuse this work in progress.
          </p>
          <div className="mt-4">
            <Link href="/resume" className="text-blue-600 underline font-medium">
              View My Resume
            </Link>
          </div>
        </div>

        <section className="mt-10 w-full max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold mb-4">Key Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.map((project, index) => (
              <div key={index} className="border rounded bg-white shadow p-4">

                  <h3 className="text-lg font-bold mb-2">{project.title}</h3>
                  <p className="text-sm text-gray-700">{project.description}</p>

              </div>
            ))}
          </div>
        </section>

        <section className="mt-12 w-full max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold mb-4">Career Highlights</h2>
          <ul className="space-y-2">
            {timeline.map((item, index) => (
              <li key={index} className="text-gray-700 text-md">
                <strong>{item.role}</strong> at {item.company} <span className="text-sm text-gray-500">({item.dates})</span>
              </li>
            ))}
          </ul>
        </section>

        <footer className="mt-12 text-center text-sm text-gray-500">
          <p>
            Connect with me: <a href="https://linkedin.com/in/wbrady" className="text-blue-600">LinkedIn</a> |{' '}
            <a href="https://github.com/williambrady" className="text-blue-600">GitHub</a>
          </p>
          <p className="mt-1">&copy; {new Date().getFullYear()} William Brady | crofton.cloud</p>
        </footer>
      </main>
    </div>
  );
}
