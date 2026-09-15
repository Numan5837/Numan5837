<div align="center">
  <img src="assets/profile-graph-hero.gif" width="100%" alt="Numan S. — AI evaluation, verifier engineering, and reproducible infrastructure" />

  <br/>

  <p><strong>AI EVALUATION &nbsp;·&nbsp; VERIFIER ENGINEERING &nbsp;·&nbsp; REPRODUCIBLE INFRASTRUCTURE</strong></p>

  <p>I build containerized benchmarks that make agent failures measurable,<br/>reproducible, and useful for improving evaluation systems.</p>

  <br/>

  <p>
    <a href="https://www.linkedin.com/in/numan-s-b622bb250/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" height="29" alt="LinkedIn" /></a>&nbsp;
    <a href="https://github.com/harbor-framework/terminal-bench/pull/1969"><img src="https://img.shields.io/badge/Terminal--Bench_%231969-0B6477?style=for-the-badge&logo=gnometerminal&logoColor=white" height="29" alt="Terminal-Bench pull request 1969" /></a>&nbsp;
    <a href="https://github.com/search?q=is%3Apr+author%3ANuman5837&type=pullrequests"><img src="https://img.shields.io/badge/Open--source_PRs-24292F?style=for-the-badge&logo=github&logoColor=white" height="29" alt="Open-source pull requests" /></a>
  </p>
</div>

<br/>

## Selected work

<sub>BENCHMARK DESIGN &nbsp;·&nbsp; EVALUATION SYSTEMS &nbsp;·&nbsp; RELIABLE INFRASTRUCTURE</sub>

### Replica reconciliation

**Terminal-Bench** &nbsp;·&nbsp; <sub>OPEN TB5 CANDIDATE</sub>

I designed a database reliability task that asks an agent to recover exact record drift from compressed replica sketches, choose one retry, and stay within a strict transfer budget.

> **Validation** &nbsp; [Docker passed](https://github.com/harbor-framework/terminal-bench/actions/runs/34815816471) &nbsp;·&nbsp; Oracle `1.0` &nbsp;·&nbsp; No-op `0.0` &nbsp;·&nbsp; GPT-5.6 Sol `0/5` with Terminus-2 via OpenRouter

**[View the pull request →](https://github.com/harbor-framework/terminal-bench/pull/1969)** &nbsp;&nbsp; [Read the failure analysis](https://github.com/harbor-framework/terminal-bench/pull/1969#issuecomment-5661777651)

<details>
<summary><strong>Model-run notes</strong></summary>

<br/>

All five trials completed without infrastructure errors. In the two trajectories analyzed in detail, the agent reused one global retry multiplier. That under-sized routed transition cases and overspent when the two routes drifted in opposite directions.

</details>

---

### Enterprise grading

**Infinity Megatron** &nbsp;·&nbsp; <sub>PRIVATE R&amp;D</sub>

I built the enterprise grading layer for **Infinity Megatron**, a private AI-agent evaluation platform. The pipeline covers rubric-based artifact scoring, verifier audits, Docker calibration, Pass@k trials, mutation testing, and structured reports.

<br/>

<p align="center">
  <img src="assets/infinity-grading-flow.gif" width="100%" alt="Infinity Megatron grading pipeline from task intake through evidence" />
</p>

<p align="center"><sub>Private implementation &nbsp;·&nbsp; The animation presents the workflow at a high level</sub></p>

---

### Evaluator reliability

**Gandalf the Grader** &nbsp;·&nbsp; <sub>OPEN-SOURCE ENGINEERING</sub>

I submitted targeted patches for cross-platform process launching, UTF-8-safe I/O, Python 3.12 CI, and safe handling of malformed trajectories and judge responses.

**[View the submitted patches →](https://github.com/Handshake-AI-Research/gandalf-the-grader/pulls?q=is%3Apr+author%3ANuman5837)**

## How I work

- **Build from controlled state.** Derive expected results from data held by the verifier.
- **Test both sides.** Prove the oracle passes and shortcut solutions fail.
- **Protect the evaluation.** Isolate agent code from fixtures, answers, and rewards.
- **Study the failures.** Use trajectories to separate capability gaps from task defects.

## Technical toolkit

<p align="center">
  <img src="https://skillicons.dev/icons?i=py,docker,kubernetes,aws,githubactions,linux,bash,powershell&theme=dark&perline=8" alt="Python, Docker, Kubernetes, AWS, GitHub Actions, Linux, Bash, and PowerShell" />
</p>

## Contribution activity

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Numan5837/Numan5837/output/github-contribution-grid-snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Numan5837/Numan5837/output/github-contribution-grid-snake.svg" />
    <img src="https://raw.githubusercontent.com/Numan5837/Numan5837/output/github-contribution-grid-snake-dark.svg" width="100%" alt="Animated contribution graph" />
  </picture>
</p>
