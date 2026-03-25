# Tooling + Repo Use Cases

This map explains what each configured item is, how it is categorized (tool/repo/subagent/etc), and a concrete use case.

## Direct Tools (Installed/Verified)
| Item | Category | Type | What It Does | Example Use Case |
| --- | --- | --- | --- | --- |
| `gh` | GitHub operations | CLI tool | Manage PRs, issues, releases, workflows | Open a PR and trigger workflow checks from terminal |
| `task` | Task runner | CLI tool | Standard command entrypoint via `Taskfile.yml` | `task onboard` on a fresh machine |
| `mise` | Runtime manager | CLI tool | Pin and manage language/tool versions | Reproduce Python/Node versions on CI and local |
| `lefthook` | Quality gate | CLI tool | Fast pre-commit/pre-push hooks | Enforce lint/format before commit |
| `uv` | Python package/env | CLI tool | Fast venv and dependency install | `uv venv && uv pip install -r requirements.txt` |
| `ruff` | Python lint/format | CLI tool | Lint + format Python code quickly | Pre-commit linting and formatting |
| `biome` | JS lint/format | CLI tool | JS/TS formatter+linter | Standardize JS config/scripts formatting |
| `nx` | Monorepo orchestration | CLI tool | Task graph + project orchestration | Run/test multiple apps in one workspace |
| `supabase` | Backend platform | CLI tool | DB/auth/local stack workflows | Start local Supabase for auth+DB testing |
| `vercel` | Deployment | CLI tool | Deploy and inspect web projects | Preview deploy a frontend branch |
| `stripe` | Billing integration | CLI tool | Stripe event forwarding and testing | Test webhook events locally |
| `playwright-cli` | Browser automation | CLI/package | Browser automation runner package | Automate login flow regression checks |
| `notebooklm-py` | Research utility | Python package | NotebookLM scripting integration | Batch summarize source docs for research |
| `skills.sh` | Skills registry | URL resource | Skills discovery/reference site | Find reusable skill workflows |

## Agentic Workflow Repos
| Repo | Category | Type | What It Does | Example Use Case |
| --- | --- | --- | --- | --- |
| `VoltAgent/awesome-claude-code-subagents` | Subagents | Reference repo | Curated subagent patterns and examples | Pick a specialized subagent template per task type |
| `thedotmack/claude-mem` | Memory | Reference repo | Persistent memory approach for agents | Store durable project context across sessions |
| `vercel-labs/skills` | Skills | Reference repo | Skill patterns/templates | Reuse a proven skill layout for new workflows |
| `kcchien/skills-cli` | Skills | Reference repo | CLI around skills management | Script skill install/list/update operations |
| `automazeio/ccpm` | Project mgmt | Reference repo | Structured execution and ownership flow | Break roadmap work into owned execution units |
| `modelcontextprotocol/servers` | MCP | Reference repo | MCP server implementations | Add a new MCP server for an external system |
| `shanraisshan/claude-code-hooks` | Hooks | Reference repo | Hook patterns for quality/safety | Add a guard hook before running dangerous commands |
| `shanraisshan/claude-code-best-practice` | Playbook | Reference repo | Claude-code execution best practices | Align repo conventions with proven patterns |
| `affaan-m/everything-claude-code` | Knowledge base | Reference repo | Broad examples and references | Find implementation examples for uncommon flows |
| `obra/superpowers` | Agent capability | Reference repo | Extended capability patterns | Add an enhanced tool orchestration flow |
| `gsd-build/get-shit-done` | Execution ops | Reference repo | Completion-biased task execution patterns | Convert vague backlog into shippable tasks |
| `github/spec-kit` | Spec-first delivery | Reference repo | Spec templates and workflow | Define feature spec before implementation |

## Build/Runtime Foundation Repos
| Repo | Category | Type | What It Does | Example Use Case |
| --- | --- | --- | --- | --- |
| `go-task/task` | Task runner internals | Source repo | Source for go-task tool | Reference syntax/features for advanced Taskfiles |
| `jdx/mise` | Runtime manager internals | Source repo | Source for mise tool | Check exact behavior of runtime pinning |
| `evilmartians/lefthook` | Hook manager internals | Source repo | Source for lefthook tool | Validate hook config compatibility |
| `astral-sh/uv` | Python infra internals | Source repo | Source for uv tool | Confirm resolver/install behavior |
| `astral-sh/ruff` | Python static analysis internals | Source repo | Source for ruff tool | Confirm lint rule behavior with upstream docs |
| `biomejs/biome` | JS lint/format internals | Source repo | Source for biome tool | Check formatter/linter option support |
| `nrwl/nx` | Monorepo internals | Source repo | Source for nx tool | Validate target graph behavior for monorepo tasks |

## Platform + App CLI Repos
| Repo | Category | Type | What It Does | Example Use Case |
| --- | --- | --- | --- | --- |
| `supabase/cli` | Backend platform | Source repo | Supabase CLI source/docs | Confirm command behavior before infra rollout |
| `stripe/stripe-cli` | Billing platform | Source repo | Stripe CLI source/docs | Validate webhook/testing flags |
| `googleworkspace/cli` | Workspace integration | Source repo | Google Workspace CLI tooling | Automate workspace user/resource tasks |
| `HKUDS/CLI-Anything` | General automation | Reference repo | CLI orchestration ideas/tooling | Rapidly script cross-service operations |

## Automation / Testing / Research Repos
| Repo | Category | Type | What It Does | Example Use Case |
| --- | --- | --- | --- | --- |
| `microsoft/playwright-cli` | Browser automation | Source repo | Playwright CLI project | Investigate e2e automation capabilities |
| `teng-lin/notebooklm-py` | Research automation | Source repo | NotebookLM Python integration | Build automated literature digestion job |

## CI Action Repos
| Repo | Category | Type | What It Does | Example Use Case |
| --- | --- | --- | --- | --- |
| `astral-sh/setup-uv` | CI setup | GitHub Action repo | Install/configure `uv` in CI | Ensure reproducible Python setup in workflows |
| `astral-sh/ruff-action` | CI lint | GitHub Action repo | Run Ruff in GitHub Actions | Fast lint gate on pull requests |
| `go-task/setup-task` | CI setup | GitHub Action repo | Install/configure `task` in CI | Run Taskfile-based checks in Actions |
| `jdx/mise-action` | CI setup | GitHub Action repo | Install/configure `mise` in CI | Align CI runtime versions with local |

## How “Clone Once, Access All” Works
1. Clone this repo.
2. Run `bash scripts/onboard.sh`.
3. The script runs setup and bootstrap retry.
4. All reference repos are cloned into `.tools-cache/`.
5. The bootstrap report in `.bootstrap/latest_report.md` shows exact status and paths.
