# Profile content standard

This profile uses a scan-first landing page with evidence-deep case studies.

## Visitor questions

The README must answer these questions in order:

1. Who is Ahmad, and what is his current academic context?
2. What kind of engineering work does he do?
3. Which three projects best prove it?
4. What is he actively building now?
5. What experience and recognition support the positioning?
6. Is the work active and inspectable?
7. Where can a reviewer explore more projects or make contact?

## README hierarchy

1. **Hero and positioning** — one student-engineer role statement, four focus labels, and primary links.
2. **Education** — current institution, D-IV program, department, location, and concise academic context.
3. **Selected engineering work** — exactly three flagship projects with problem, build, evidence, boundaries, and deep-dive links.
4. **Currently building** — exactly three active priorities; version and condition are kept separate.
5. **Experience and recognition** — trust signals before activity statistics.
6. **Engineering approach** — durable decision-making principles rather than another technology list.
7. **Engineering activity** — one bounded public/private aggregate and one local visualization.
8. **Project and case-study library** — one consolidated index for supporting work and recent public repositories.
9. **Contact** — a direct opportunity statement and external contact links.

## Education policy

Education appears directly after the hero because the profile represents an early-career student engineer. It provides current context without turning the README into an academic transcript.

The section contains only:

- institution and official English name;
- D-IV study program;
- department and location;
- current-student status;
- one concise sentence connecting study to practical engineering work.

It must not publish student identification numbers, temporary school email addresses, GPA, unverified graduation dates, or a complete course list. The official Polinema/JTI website is used as the institutional reference.

## Duplication policy

The README must not create separate top-level sections for:

- What I build;
- Additional case study;
- More projects;
- Public work recently updated;
- How I work.

Their useful content belongs in the hero, selected work, engineering approach, activity details, or project library.

## Selected-work policy

Selected work is limited to three projects. Each entry contains:

- the problem;
- what was built;
- a short technology line;
- three inspectable evidence points;
- collapsed engineering decisions, deep-dive topics, and current boundaries;
- repository and/or case-study links when safe.

Long architecture explanations remain in `case-studies/*/README.md`.

## Currently-building policy

Only three active priorities appear in the main table. The section communicates current direction, not a complete private-repository inventory.

Each row contains:

- project;
- source-derived version and editorial development condition;
- current engineering focus.

Commit dates remain in the activity index rather than the current-focus table.

## Metric policy

- Commit counts are context, not a quality score.
- Private activity is published only as one aggregate total for the selected portfolio set.
- Per-project private commit counts are queried transiently for aggregation and are never persisted or rendered.
- Activity labels state the time window and source so the numbers are not mistaken for lifetime totals.
- Versions and development conditions are separate fields; a version number does not imply production readiness.

## Table policy

Tables are reserved for compact, comparable metadata. Long engineering explanations belong in prose or case studies.

The collapsed private activity index contains only:

- project name;
- source-verified version;
- development condition;
- latest approved activity date.

Case-study navigation belongs in Selected Work or the Project and Case-Study Library, not in the activity table.

## Privacy boundary

Private projects use sanitized public labels and case studies. Tracked outputs must not reveal:

- private repository URLs;
- branch names;
- commit SHAs or messages;
- credentials;
- production data;
- confidential infrastructure details.

## GitHub alignment

GitHub places the profile README at the top of the profile and recommends using it to introduce professional background, skills, selected projects, experience, and achievements. GitHub also recommends highlighting roughly three to five best projects and supports up to six pinned items. The README therefore provides context and proof, while pinned repositories provide fast visual access to public work.

## References

- https://docs.github.com/en/account-and-profile/concepts/personal-profile
- https://docs.github.com/en/account-and-profile/tutorials/using-your-github-profile-to-enhance-your-resume
- https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- https://jti.polinema.ac.id/
- https://devel-www.polinema.ac.id/en/program-studi/d-iv-information-technology/
