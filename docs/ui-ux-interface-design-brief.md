# UI/UX Interface Design Brief: Adaptive Practice Workspace

## Design Goal

Design the entire application as a Claude/Codex/NotebookLM-inspired workspace wrapped around the current PracDaGo practice UI. The product should feel like a serious local-first learning cockpit for robotics and technical study, not a landing page, generic chatbot, or overloaded dashboard.

The current PracDaGo screen remains the core Practice Surface. The new shell adds project navigation, source/resource management, NotebookLM-style source selection, Claude-style project memory and files, Codex-style side/bottom docks, artifact workflows, graph/memory panels, and optional IDE/sandbox launching.

## Exact User Requirement To Preserve

"Current UI expanded or next to Codex UI interface left side navigation importantly and toggle buttons on extreme rights providing side and bottom toggle, ingestion and artifact creation or practice problems exercise lessons by subjects chapter topic domains selecting proper stuff to create like NotebookLM, Claude like project chat and resources management option for domain -> subject in that chapter -> topics, code and etc practice can be done by launching IDE and sandbox as per need or custom."

## Visual Direction

Use a dark Claude-like color scheme:

- Background: near-black charcoal, not pure black.
- Main surfaces: dark warm gray.
- Cards/panels: slightly lighter dark gray with subtle borders.
- Text: warm off-white for primary, muted gray for secondary.
- Accent: restrained teal/cyan from current PracDaGo for active learning/practice states.
- Secondary accents: soft purple/blue only for AI/workflow indicators, used sparingly.
- Avoid bright neon, heavy gradients, decorative blobs, and card-heavy marketing layouts.
- Use 6-8px radius for panels/cards, subtle borders, compact spacing, and readable typography.

The app should visually sit between Claude Projects and the current PracDaGo interface: calm, dense, technical, and focused.

## Core Layout

Use one persistent Workspace Shell:

```txt
--------------------------------------------------------------------------------+
| Top Bar: project title, active context, search/command, model/status, settings |
+----------+-----------------------------------------------------+---------------+
| Left Nav | Main Workspace                                      | Right Toggles |
|          |                                                     | Sources       |
| Projects | Practice / Source Notebook / Resource Manager       | Chat          |
| Domains  | Graph / Artifacts / Workflow Editor                 | Artifacts     |
| Search   |                                                     | Memory        |
| Recent   |                                                     | Graph         |
+----------+-----------------------------------------------------+---------------+
| Bottom Dock: Output / Tests / Terminal / Sandbox / Evals / Logs                |
+--------------------------------------------------------------------------------+
```

Everything must be collapsible:

- Left nav can collapse to icons.
- Right side panel is opened by vertical toggle buttons on the extreme right.
- Bottom dock opens only when output, terminal, tests, sandbox, evals, or logs are needed.
- Main workspace should resize fluidly when panels open.
- User should never see all panels expanded at once by default.

## What To Borrow From Each Reference Image

### Current PracDaGo

Keep these as the Practice Surface foundation:

- Exercise list and filters.
- Chapter/problem navigation.
- Lesson tabs: Explanation, How it works, Syntax, Problem, Solve.
- Outline inside lesson content.
- Editor/answer surface.
- Run, reset, submit/proof checklist actions.
- Output panel.
- Progress indicators.

Change the shell around it, not the entire practice primitive.

### Codex Home

Borrow:

- Persistent left sidebar with projects and recent work.
- Central command/input area for starting work.
- Project switcher.
- Sparse dark workspace with focused center.

Adapt:

- Replace "What should we work on?" with learning-focused actions:
  - Continue practice
  - Add sources
  - Create exercises
  - Ask project tutor
  - Review blind spots

### Codex Split/Dock UI

Borrow:

- Side tools such as files, side chat, browser, terminal.
- Right-side panel toggles.
- Bottom panel for terminal/output.
- Ability to open secondary tools without changing primary context.

Adapt:

- Tools become Sources, Tutor Chat, Artifacts, Memory, Graph, Context, Terminal, Sandbox.

### Claude Projects List

Borrow:

- Project list layout.
- Search and sort.
- Simple project cards.
- Left nav with New chat, Search, Chats, Projects, Artifacts, Code, Customize.

Adapt:

- Projects become learning workspaces such as Robotics Learning, Modern Robotics, CMU MRSD Prep, Perception, Control.

### Claude Project Detail

Borrow:

- Project chat as a central interaction.
- Right-side project resources: Memory, Instructions, Files.
- Recents/history list.
- Editable project instructions.

Adapt:

- Right-side project resources become Memory, Learning Rules, Sources, Generated Artifacts, Workflows.
- Project chat should know selected domain/subject/chapter/topic context.

### NotebookLM Home

Borrow:

- Notebook/project grid.
- Create new notebook/project.
- Search, grid/list toggle, sorting.
- Source count on each project.

Adapt:

- Cards show learning project status:
  - sources count
  - generated artifacts count
  - active subjects
  - practice progress
  - blind spots

### NotebookLM Notebook

Borrow:

- Left source panel with add/select sources.
- Central chat over selected sources.
- Right studio panel for artifact generation.
- Source selection checkboxes.
- Studio actions like quiz, mind map, report, flashcards.

Adapt:

- Studio actions become workflow templates:
  - Create exercises
  - Create lesson
  - Explain chapter
  - Extract concepts
  - Generate quiz
  - Create mind map
  - Create report
  - Create flashcards

## Primary Screens

### 1. Home / Command Center

Purpose: quick resume and project entry.

Layout:

- Left global nav.
- Main center area with a command input and quick actions.
- Recent projects and active learning threads below.
- Optional right dock closed by default.

Primary actions:

- Continue last practice.
- Add source.
- Create learning project.
- Open project chat.
- Review blind spots.
- Open graph.

Do not make this a marketing dashboard. It is an operational start screen.

### 2. Projects / Learning Workspaces

Purpose: manage major learning spaces.

Project card content:

- Project name.
- Short goal.
- Domains/subjects included.
- Source count.
- Artifact count.
- Practice progress.
- Last active time.

Actions:

- New project.
- Search.
- Sort by activity/domain/progress.
- Grid/list toggle.

### 3. Project Overview

Purpose: Claude Projects-like resource and memory management.

Main area:

- Project title and purpose.
- Central project chat or command input.
- Recent sessions.
- Active study threads.

Right resource panel:

- Memory.
- Instructions / learning rules.
- Sources.
- Artifacts.
- Workflows.

Important: project chat is not the whole product. It is one Study Tool.

### 4. Resource Manager

Purpose: organize sources and artifacts by domain hierarchy.

Hierarchy:

```txt
Domain
  Subject
    Chapter
      Topic
        Sources
        Lessons
        Exercises
        Quizzes
        Notes
        Graph nodes
```

Interactions:

- Add source.
- Assign source to domain/subject/chapter/topic.
- Select multiple sources.
- Run workflow on selected sources.
- View ingestion status.
- Open source citations.

This should feel like NotebookLM source management plus Claude project files, not a raw file explorer.

### 5. Source Notebook

Purpose: NotebookLM-style study over selected sources.

Layout:

- Left: selected sources with checkboxes and search.
- Center: chat over selected sources.
- Right: workflow studio.

Workflow studio actions:

- Create exercises.
- Create lesson.
- Explain chapter.
- Extract concepts.
- Generate quiz.
- Create mind map.
- Create report.
- Create flashcards.

When a workflow completes, output becomes an Artifact and can be opened, edited, approved, or sent to Practice.

### 6. Practice Surface

Purpose: current PracDaGo learning and solving flow.

Layout:

- Left inside main area: scoped exercise/topic list.
- Center: lesson/explanation with outline and tabs.
- Right within main area or launched panel: editor/answer workspace.
- Bottom dock: output/tests/sandbox.
- Right dock: tutor/source citations/memory/graph/context.

Tabs:

- Explanation.
- How it works.
- Syntax.
- Problem.
- Solve.

Optional later tabs:

- Sources.
- Related concepts.
- Mistakes.

Practice actions:

- Run.
- Submit.
- Ask hint.
- View source citations.
- Open related concept graph.
- Launch IDE/sandbox.
- Mark solved/manual review.

### 7. Artifact Viewer

Purpose: open generated lessons, exercises, quizzes, reports, mind maps, flashcards, tables, or diagrams.

Layout:

- Main artifact content.
- Metadata strip: source refs, workflow used, eval status, generated time.
- Actions: approve, edit, regenerate, send to practice, compare versions.
- Right dock: citations, graph links, prompt/template, eval result.

### 8. Graph View

Purpose: show domain knowledge and learner state.

Graph types:

- Learning Graph: domain -> subject -> chapter -> concept -> prerequisite.
- Source Graph: source -> section -> chunk -> artifact.
- Memory Graph: attempt -> blind spot -> mastery -> recommendation.

Interactions:

- Filter by domain/subject/chapter/topic.
- Click concept to view sources, exercises, lessons, attempts.
- Show blind spots and mastery color.
- Send concept to practice/workflow.

### 9. Workflow Editor

Purpose: structured templates with editable prompts.

Fields:

- Workflow name.
- Artifact type.
- Input source types.
- Required context slots.
- Prompt template.
- Output schema.
- Eval checks.
- Example output.

This combines structured workflow templates with prompt-library flexibility.

## Right Dock Design

Use a vertical icon rail on the extreme right. Only one panel opens at a time.

Panels:

- Sources: selected source chunks and citations.
- Tutor: project-aware or exercise-aware chat.
- Artifacts: generated outputs.
- Memory: relevant learner memory and blind spots.
- Graph: related concepts/prerequisites.
- Context: current context slots and token usage.
- Inspector: workflow/eval/debug metadata.

Panel behavior:

- Opens over or beside main content depending on width.
- Resizable on desktop.
- Full-screen drawer on mobile.
- Close with escape/click toggle.

## Bottom Dock Design

Bottom dock is for execution and diagnostics.

Tabs:

- Output.
- Tests.
- Terminal.
- Sandbox.
- Evals.
- Logs.

Behavior:

- Closed by default.
- Auto-opens after Run/Submit.
- Can be pinned.
- Height resizable.
- On mobile, opens as full-screen sheet.

## End-To-End Workflow

### Flow A: Create A Learning Project

1. User opens app.
2. Home shows recent projects and command input.
3. User creates "Robotics Learning".
4. User adds domain "Robotics".
5. User adds subject "Modern Robotics".
6. User creates chapter/topic structure manually or from source extraction.

### Flow B: Add Sources

1. User opens Resource Manager or Source Notebook.
2. User clicks Add Source.
3. User uploads PDF/PPT/DOCX/transcript or links GitHub/docs.
4. User assigns domain, subject, chapter, topic.
5. Ingestion runs.
6. Source cards show status: extracting, chunking, indexed, graph-ready, artifact-ready.
7. User can inspect extracted chunks and citations.

### Flow C: Generate Practice Material

1. User selects sources.
2. User chooses workflow "Create practice pack".
3. UI asks scope: subject, chapter, topic, difficulty, exercise count, coding/manual.
4. Workflow creates lessons, explanations, exercises, tests, hints, examples.
5. Generated artifacts appear in Artifact Viewer.
6. User reviews and approves.
7. Approved exercises appear in Practice Surface.

### Flow D: Practice

1. User opens Practice.
2. Left list shows exercises scoped to current topic.
3. Center shows explanation and outline.
4. Editor appears for code tasks, or answer workspace appears for conceptual tasks.
5. User runs code or submits.
6. Bottom dock opens with output/tests.
7. Attempt is recorded in memory.
8. Graph/mastery updates.

### Flow E: Ask Tutor

1. User opens Tutor right dock.
2. Tutor receives current exercise, selected source chunks, graph facts, memory facts, and recent attempt.
3. Tutor gives Socratic hint, not answer.
4. Hint request is recorded.
5. Repeated struggle can create or strengthen a Blind Spot.

### Flow F: Review Learning State

1. User opens Graph or Memory.
2. UI shows weak topics, related prerequisites, and recommended next practice.
3. User clicks a concept.
4. App opens related lessons, sources, exercises, and generated artifacts.

## Anti-Bloat Rules

1. One primary task per screen.
2. Secondary tools live in collapsible docks.
3. Workflow actions are grouped, not scattered.
4. Chat is contextual, not the whole application.
5. Graph and memory are inspectable panels, not always-on clutter.
6. Advanced context/debug/eval panels are hidden by default.
7. Default screen should always answer: "What am I studying or practicing right now?"

## Responsive Behavior

Desktop:

- Left nav visible.
- Main area uses 2 or 3 columns depending on mode.
- Right dock and bottom dock resizable.

Tablet:

- Left nav collapses to icons.
- Right dock becomes overlay.
- Practice editor can stack below lesson.

Mobile:

- Bottom navigation replaces left sidebar.
- Panels become full-screen sheets.
- Practice mode shows one primary pane at a time: list, lesson, editor, output.

## Final Product Feel

The app should feel like:

- Claude Projects for project memory/resources.
- Codex for workspace shell, side tools, bottom terminal/output.
- NotebookLM for source selection and artifact workflows.
- PracDaGo for actual learning/practice.

The complete loop is:

```txt
Project -> Sources -> Ingestion -> Artifacts -> Practice -> Tutor -> Memory -> Graph -> Next Practice
```

Every interface decision should support that loop.
