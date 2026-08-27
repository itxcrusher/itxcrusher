<!-- theme: ember | mode: daily | date: 2026-08-27 -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/themes/ember/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/themes/ember/hero-light.svg">
  <img src="./assets/themes/ember/hero-light.svg" width="100%" alt="Muhammad Hassaan Javed, GitHub handle @itxcrusher. Ember theme." />
</picture>

<p align="center">
  <a href="https://muhammadhassaanjaved.com"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/link-muhammadhassaanjaved-com.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/link-muhammadhassaanjaved-com.svg"><img src="./assets/badges/ember/light/link-muhammadhassaanjaved-com.svg" height="28" alt="muhammadhassaanjaved.com" /></picture></a> <a href="https://infraforge.agency"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/link-infraforge-agency.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/link-infraforge-agency.svg"><img src="./assets/badges/ember/light/link-infraforge-agency.svg" height="28" alt="infraforge.agency" /></picture></a> <a href="https://github.com/itxcrusher?tab=repositories&type=source&sort=pushed"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/link-repositories.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/link-repositories.svg"><img src="./assets/badges/ember/light/link-repositories.svg" height="28" alt="repositories" /></picture></a>
</p>

<picture><source media="(prefers-color-scheme: dark) and (max-width: 479px)" srcset="./assets/panels/ember/intro-xs-dark.svg"><source media="(max-width: 479px)" srcset="./assets/panels/ember/intro-xs-light.svg"><source media="(prefers-color-scheme: dark) and (max-width: 767px)" srcset="./assets/panels/ember/intro-sm-dark.svg"><source media="(max-width: 767px)" srcset="./assets/panels/ember/intro-sm-light.svg"><source media="(prefers-color-scheme: dark) and (max-width: 1199px)" srcset="./assets/panels/ember/intro-md-dark.svg"><source media="(max-width: 1199px)" srcset="./assets/panels/ember/intro-md-light.svg"><source media="(prefers-color-scheme: dark)" srcset="./assets/panels/ember/intro-lg-dark.svg"><img src="./assets/panels/ember/intro-lg-light.svg" width="100%" alt="Opening statement: I build infrastructure and bounded automation for other people's production systems. Most of that work is in private client and product repositories, so what is public here is a sample rather than the volume. If infrastructure feels exciting, something is probably wrong; the goal is systems that are quiet, predictable, and uninteresting in production." /></picture>

<details><summary><sub>the same three lines as plain text</sub></summary>

I build infrastructure and bounded automation for other people's production systems. Terraform, Kubernetes, CI/CD, and lately agents that act on evidence they can prove instead of guessing.

Most of that work is in private client and product repositories, so what is public here is a sample rather than the volume. The contribution graph counts it. The repository list cannot show it.

If infrastructure feels exciting, something is probably wrong. The goal is systems that are quiet, predictable, and uninteresting in production.

</details>

> [!TIP]
> **Want to check whether any of this is real?**
> `ripple-proof` audits a full captured campaign offline in about a minute, with Python 3.11 and nothing else. No install, no account, no credential, no network call. It prints every point where it refused to act.
>
> ```
> git clone https://github.com/itxcrusher/ripple-proof
> cd ripple-proof
> PYTHONPATH=src python -S -m lineage_agent.cli demo
> ```
>
> Expect `CAMPAIGN AUDIT: PASSED`, 11 of 11 checks. The [walkthrough](https://itxcrusher.github.io/ripple-proof/) keeps one run that fails its dbt build on purpose rather than dropping it.

## <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/themes/ember/h-public-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/themes/ember/h-public-light.svg"><img src="./assets/themes/ember/h-public-light.svg" width="100%" alt="what is public" /></picture>

<!-- PUBLIC_SURFACE:START -->
21 original public repositories. Most of the work is not here: over the last 12 months, 5,408 of 6,509 contributions were in private repositories (client delivery, product builds, and security research).

Most recent public work:

- **[ripple-proof](https://github.com/itxcrusher/ripple-proof)** - Bounded PostgreSQL column-rename agent: turns DataHub lineage evidence into validated dbt repairs across repositories, refuses ambiguous or stale evidence, and stops at human-reviewed pull requests. Updated 2026-08-09. [Walkthrough](https://itxcrusher.github.io/ripple-proof/) <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/lang-python.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/lang-python.svg"><img src="./assets/badges/ember/light/lang-python.svg" height="28" alt="Python" /></picture>
- **[vision-ai-poc](https://github.com/itxcrusher/vision-ai-poc)** - Real-time people detection, per-zone counting and dwell tracking with YOLOv8, ByteTrack and OpenCV. Runs as a local GUI demo or headless against RTSP cameras with server-fetched zones and privacy masking. Updated 2026-08-26. <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/lang-python.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/lang-python.svg"><img src="./assets/badges/ember/light/lang-python.svg" height="28" alt="Python" /></picture>
- **[kind-cluster-recovery](https://github.com/itxcrusher/kind-cluster-recovery)** - Four-node KIND cluster provisioned onto a remote host with Terraform over SSH, then debugged: CoreDNS Corefile repair, crash-loop recovery, and a least-privilege NetworkPolicy expressed in Terraform. Updated 2026-08-26. <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/lang-hcl.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/lang-hcl.svg"><img src="./assets/badges/ember/light/lang-hcl.svg" height="28" alt="HCL" /></picture>
- **[k8s-gitops-platform](https://github.com/itxcrusher/k8s-gitops-platform)** - ArgoCD app-of-apps GitOps configuration for a 17-service Kubernetes platform: parameterised Helm charts, an ELK logging stack, and cert-manager across three environments. Generalised from production. Updated 2026-08-22.
- **[wordpress-fargate-deployment](https://github.com/itxcrusher/wordpress-fargate-deployment)** - AWS CloudFormation template and helper scripts to deploy a production-ready WordPress environment on AWS Fargate with RDS, EFS, and an Application Load Balancer. Updated 2025-08-08. <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/lang-shell.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/lang-shell.svg"><img src="./assets/badges/ember/light/lang-shell.svg" height="28" alt="Shell" /></picture>
- **[azure-devops-demo](https://github.com/itxcrusher/azure-devops-demo)** - End-to-end Terraform and GitHub Actions pipeline that deploys a containerized service to Azure, with six reusable Terraform modules. Updated 2025-05-16. <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/lang-hcl.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/lang-hcl.svg"><img src="./assets/badges/ember/light/lang-hcl.svg" height="28" alt="HCL" /></picture>

Evidence trail for ripple-proof runs across four public sibling dbt repositories: [analytics](https://github.com/itxcrusher/ripple-proof-dbt-analytics/pull/6), [finance](https://github.com/itxcrusher/ripple-proof-dbt-finance/pull/6), [growth](https://github.com/itxcrusher/ripple-proof-dbt-growth/pull/5), [operations](https://github.com/itxcrusher/ripple-proof-dbt-operations/pull/5). All open and review-only.

_Generated 2026-08-27 from the GitHub API._
<!-- PUBLIC_SURFACE:END -->

## <picture><source media="(prefers-color-scheme: dark)" srcset="./assets/themes/ember/h-stack-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/themes/ember/h-stack-light.svg"><img src="./assets/themes/ember/h-stack-light.svg" width="100%" alt="the stack" /></picture>

Everything in the operating stack below has a public artifact in this account. Work that does not is in private repositories and is not listed here.

<p><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/cloud.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/cloud.svg"><img src="./assets/badges/ember/light/cloud.svg" height="28" alt="cloud" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/aws.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/aws.svg"><img src="./assets/badges/ember/light/aws.svg" height="28" alt="AWS" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/azure.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/azure.svg"><img src="./assets/badges/ember/light/azure.svg" height="28" alt="Azure" /></picture></p>
<p><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/platform.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/platform.svg"><img src="./assets/badges/ember/light/platform.svg" height="28" alt="platform" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/kubernetes.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/kubernetes.svg"><img src="./assets/badges/ember/light/kubernetes.svg" height="28" alt="Kubernetes" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/docker.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/docker.svg"><img src="./assets/badges/ember/light/docker.svg" height="28" alt="Docker" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/terraform.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/terraform.svg"><img src="./assets/badges/ember/light/terraform.svg" height="28" alt="Terraform" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/helm.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/helm.svg"><img src="./assets/badges/ember/light/helm.svg" height="28" alt="Helm" /></picture></p>
<p><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/delivery.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/delivery.svg"><img src="./assets/badges/ember/light/delivery.svg" height="28" alt="delivery" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/github-actions.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/github-actions.svg"><img src="./assets/badges/ember/light/github-actions.svg" height="28" alt="GitHub Actions" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/ci-cd-pipelines.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/ci-cd-pipelines.svg"><img src="./assets/badges/ember/light/ci-cd-pipelines.svg" height="28" alt="CI/CD pipelines" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/argocd.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/argocd.svg"><img src="./assets/badges/ember/light/argocd.svg" height="28" alt="ArgoCD" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/gitops.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/gitops.svg"><img src="./assets/badges/ember/light/gitops.svg" height="28" alt="GitOps" /></picture></p>
<p><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/systems.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/systems.svg"><img src="./assets/badges/ember/light/systems.svg" height="28" alt="systems" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/linux.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/linux.svg"><img src="./assets/badges/ember/light/linux.svg" height="28" alt="Linux" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/networking.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/networking.svg"><img src="./assets/badges/ember/light/networking.svg" height="28" alt="networking" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/shell-automation.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/shell-automation.svg"><img src="./assets/badges/ember/light/shell-automation.svg" height="28" alt="shell automation" /></picture></p>
<p><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/ai.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/ai.svg"><img src="./assets/badges/ember/light/ai.svg" height="28" alt="ai" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/bounded-agents.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/bounded-agents.svg"><img src="./assets/badges/ember/light/bounded-agents.svg" height="28" alt="bounded agents" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/mcp.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/mcp.svg"><img src="./assets/badges/ember/light/mcp.svg" height="28" alt="MCP" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/llm-workflows.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/llm-workflows.svg"><img src="./assets/badges/ember/light/llm-workflows.svg" height="28" alt="LLM workflows" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/computer-vision.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/computer-vision.svg"><img src="./assets/badges/ember/light/computer-vision.svg" height="28" alt="computer vision" /></picture></p>
<p><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/languages.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/languages.svg"><img src="./assets/badges/ember/light/languages.svg" height="28" alt="languages" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/python.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/python.svg"><img src="./assets/badges/ember/light/python.svg" height="28" alt="Python" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/bash.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/bash.svg"><img src="./assets/badges/ember/light/bash.svg" height="28" alt="Bash" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/hcl.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/hcl.svg"><img src="./assets/badges/ember/light/hcl.svg" height="28" alt="HCL" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/badges/ember/dark/yaml.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/badges/ember/light/yaml.svg"><img src="./assets/badges/ember/light/yaml.svg" height="28" alt="YAML" /></picture></p>
<details><summary><sub>the same stack as plain text</sub></summary>

- **cloud** - AWS, Azure
- **platform** - Kubernetes, Docker, Terraform, Helm
- **delivery** - GitHub Actions, CI/CD pipelines, ArgoCD, GitOps
- **systems** - Linux, networking, shell automation
- **ai** - bounded agents, MCP, LLM workflows, computer vision
- **languages** - Python, Bash, HCL, YAML

</details>

Upstream, open: [skip_cache for get_lineage](https://github.com/acryldata/mcp-server-datahub/pull/190) in acryldata/mcp-server-datahub, and a [repair-boundary skill](https://github.com/datahub-project/datahub-skills/pull/125) in datahub-project/datahub-skills.

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/itxcrusher/itxcrusher/output/snake-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/itxcrusher/itxcrusher/output/snake-light.svg"><img src="https://raw.githubusercontent.com/itxcrusher/itxcrusher/output/snake-light.svg" width="100%" alt="Contribution snake: an animation eating this account's GitHub contribution squares, regenerated daily from the output branch in today's theme colours." /></picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/themes/ember/signoff-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/themes/ember/signoff-light.svg">
  <img src="./assets/themes/ember/signoff-light.svg" width="100%" alt="Closing line at the end of the page: stay lit" />
</picture>

Muhammad Hassaan Javed (@itxcrusher). Infrastructure recovery and platform work: [infraforge.agency](https://infraforge.agency). Personal site: [muhammadhassaanjaved.com](https://muhammadhassaanjaved.com)

Direct: <muhammadhassaanjaved99@gmail.com>

<sub>Today this page wears <b>Ember</b>, one of 47 looks it rotates through daily. <a href="assets/themes/README.md">See them all</a>.</sub>
