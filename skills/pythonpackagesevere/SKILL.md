---
name: pythonpackagesevere
description: "Decompose a Python package into independent projects. Use when the user says 'pythonpackagesevere', 'split package', 'decompose python package', or asks to break a monolith into separate projects."
---

# Python Package Decomposition — Structural Split Methodology

You are performing a comprehensive structural decomposition of a Python package into multiple independent projects. Work through each phase sequentially, producing reports and awaiting user confirmation before modifying code.

## Setup

**Target package path:** Use the path provided by the user argument, or default to `.` (current directory).

Create the output directory for all reports:

```
./package-decomposition/
```

---

## Phase 0 — Build Dependency Model (Read-Only)

**Goal:** Produce a complete dependency map of the package without modifying anything.

### Steps

1. **Map directory tree and entry points**
   - Enumerate all `.py` files, `__init__.py` re-exports, and `pyproject.toml` / `setup.py` / `setup.cfg` entry points.
   - Identify console_scripts, GUI scripts, plugin entry points.

2. **Construct import graph**
   - Find all `import X` and `from X import Y` statements.
   - Find dynamic imports: `importlib.import_module`, `__import__`, `pkgutil`.
   - Find lazy imports inside functions/methods.
   - Find conditional imports (`TYPE_CHECKING`, `try/except ImportError`).
   - Detect circular import chains.

3. **Symbol-level cross-boundary analysis**
   - Find cross-subpackage subclassing (class in package A inherits from package B).
   - Shared type definitions used across multiple subpackages.
   - Registry patterns (decorators that register into a global dict).
   - Protocol/ABC implementations spanning packages.

4. **Runtime coupling detection**
   - Global mutable state (module-level dicts/lists, singletons).
   - Plugin/hook systems.
   - ORM model cross-references (SQLAlchemy relationships, Django ForeignKeys).
   - Task queue references (Celery `@task`, task name strings).
   - Serialization dependencies (pickle, JSON schema refs, Pydantic model_validator).

### Output

Write to `./package-decomposition/phase0-dependency-model.md`:
- Directory tree summary
- Import graph (text DAG)
- Circular import chains (if any)
- Cross-boundary symbols table
- Runtime couplings inventory
- Risk assessment for split

### Hard Constraints
- Do NOT modify any source files.
- Do NOT skip dynamic/runtime imports — they are often the hardest coupling to fix later.

### Completion Criteria
- Every `.py` file in the package is accounted for in the import graph.
- All circular chains are identified.
- Runtime couplings are inventoried with file:line references.

**Present the Phase 0 report to the user and ask for confirmation before proceeding.**

---

## Phase 1 — Design Target Architecture

**Goal:** Define the target project boundaries and public APIs.

### Steps

1. **Define project boundaries**
   - Group modules into coherent domains based on Phase 0 analysis.
   - Ensure the project dependency graph is an acyclic DAG.
   - Each project should have a clear single responsibility.
   - Minimize cross-project API surface.

2. **Public API definition**
   - For each proposed project, define `__all__` exports.
   - Mark internal modules with `_` prefix convention.
   - Identify what becomes the public interface vs. implementation detail.

3. **Type ownership map**
   - Assign every shared type/protocol/ABC to exactly one project.
   - Types used by multiple projects belong to the lowest-dependency project or a dedicated `*-types` package.
   - No circular type dependencies between projects.

4. **Migration path for runtime couplings**
   - For each runtime coupling from Phase 0, propose a decoupling strategy:
     - Global state -> dependency injection or config objects
     - ORM cross-refs -> interface/protocol at boundary
     - Task queues -> string-based task names with separate worker configs
     - Plugin systems -> entry_points-based discovery

### Output

Write to `./package-decomposition/phase1-target-architecture.md`:
- Project DAG (names, dependencies between them)
- Per-project module list
- Public API surface per project
- Type ownership map
- Runtime coupling migration strategies

### Hard Constraints
- Project DAG must be acyclic — no circular dependencies between projects.
- Every module must belong to exactly one project.
- No "grab bag" utility projects — each project has a coherent domain.

### Anti-Patterns to Avoid
- Creating a `common` or `utils` project that everything depends on (split further).
- Leaving shared types unowned.
- Planning for bidirectional dependencies "to be fixed later".

### Completion Criteria
- Project DAG is acyclic.
- Every source file is assigned to exactly one project.
- Public APIs are explicitly defined.
- All runtime couplings have a migration strategy.

**Present the Phase 1 report to the user and ask for confirmation before proceeding.**

---

## Phase 2 — Pre-Split Refactoring (Inside Monorepo)

**Goal:** Refactor the existing codebase to eliminate coupling, while keeping everything in the monorepo. Tests must pass after each step.

### Steps

1. **Eliminate circular imports**
   - For each circular chain from Phase 0:
     - Move shared types to the lowest-level module.
     - Use `TYPE_CHECKING` guards for type-only imports.
     - Replace runtime circular imports with lazy imports or dependency injection.
   - Run tests after each change.

2. **Normalize import paths**
   - Replace relative imports with absolute imports where they cross future project boundaries.
   - Remove wildcard imports (`from X import *`).
   - Ensure all imports use the canonical path (no importing via re-exports that will disappear).

3. **Isolate global state**
   - Replace module-level mutable globals with:
     - Configuration objects passed explicitly.
     - Context variables (`contextvars`).
     - Dependency injection containers.
   - Run tests after each change.

4. **Decouple test utilities**
   - Move shared test fixtures to a dedicated test-utils location.
   - Remove test dependencies on internal implementation details.
   - Each future project's tests should only import from public APIs + test utils.

### Hard Constraints
- Tests MUST pass after every individual refactoring step.
- No behavioral changes — refactoring only.
- Do not move files between directories yet (that is Phase 3).
- Commit after each logical step with a descriptive message.

### Output

Write to `./package-decomposition/phase2-refactoring-log.md`:
- List of each refactoring performed with before/after.
- Test results after each step.
- Remaining risks or manual review items.

**Present the Phase 2 report to the user and ask for explicit confirmation before Phase 3 (which will restructure files).**

---

## Phase 3 — Execute Structural Split

**Goal:** Create the actual separate project directories and move code.

### Steps

1. **Scaffold each project**
   - For each project in the Phase 1 DAG, create:
     ```
     <project-name>/
       pyproject.toml          # with dependencies on sibling projects
       src/<package_name>/
         __init__.py
         py.typed               # PEP 561 marker
       tests/
       README.md
     ```
   - Use modern pyproject.toml (no setup.py).
   - Pin sibling project dependencies appropriately.

2. **Move files preserving git history**
   - Use `git mv` for all file moves.
   - Maintain the mapping from Phase 1 (source module -> target project).
   - Update `__init__.py` files in each new project.

3. **Rewrite imports**
   - Update all import statements to use new package names.
   - Fix string-based module paths (e.g., in Celery task names, entry_points, factory patterns).
   - Update any `__module__` or `__qualname__` references.

4. **Migrate entry points**
   - Move console_scripts, plugin entry_points to the correct project's pyproject.toml.
   - Update any path-based configuration files.

### Hard Constraints
- Use `git mv` for ALL file moves (preserves history).
- Never copy-and-delete (loses git history).
- String-based module paths are just as critical as import statements.
- Each project must be independently installable.

### Anti-Patterns to Avoid
- Leaving stale imports that happen to work because of transitive dependencies.
- Forgetting to update string references (task names, factory paths, serialized class paths).
- Creating circular pyproject.toml dependencies.

### Output

Write to `./package-decomposition/phase3-split-log.md`:
- Files moved per project.
- Import rewrites performed.
- String path updates.
- Entry point migrations.

**Ask user to review the split before proceeding to verification.**

---

## Phase 4 — Verification

**Goal:** Verify each project works independently and together.

### Steps

1. **Per-project isolated verification**
   For each project:
   - Create a fresh venv.
   - Install the project with its declared dependencies.
   - Run its test suite.
   - Run mypy / pyright type checking.
   - Run linter (ruff / flake8).
   - Verify `py.typed` marker works.

2. **Combined integration test**
   - Install all projects together in a single venv.
   - Run any integration / end-to-end tests.
   - Verify no import conflicts or shadowing.

3. **Runtime safeguards check**
   - Verify pickle/deserialization still resolves class paths.
   - Verify Celery task names resolve correctly.
   - Verify ORM model discovery works.
   - Verify serialized schemas (JSON Schema, OpenAPI) are correct.
   - Check any Docker/CI configurations reference correct paths.

### Output

Write to `./package-decomposition/phase4-verification-report.md`:
- Per-project test results.
- Type check results.
- Lint results.
- Integration test results.
- Runtime safeguards checklist.

### Completion Criteria
- All projects install and test independently.
- Combined installation has no conflicts.
- All runtime safeguards pass.
- CI pipeline (if present) passes.

---

## General Instructions

- **Be methodical.** Each phase builds on the previous one. Do not skip phases.
- **Be conservative.** When in doubt, do less and ask the user.
- **Preserve git history.** Use `git mv`, never copy-delete.
- **Tests are the safety net.** Run tests after every change in Phases 2-4.
- **Reports first, changes second.** Always produce the analysis report before making modifications.
- **Gate on user confirmation.** Never proceed from Phase 0 to 1 to 2 to 3 without user approval of the previous phase's output.
- **Handle edge cases:** namespace packages, compiled extensions (.so/.pyd), generated code, vendored dependencies.
