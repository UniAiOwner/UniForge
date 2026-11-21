# ⚡ UniExec: Sovereign Sandboxed Code Mode Runtime

Pillar 5 of the **UniCortex Brain 2.0 Sovereign Mesh**.

Based on **arXiv:2611.19123** (*"Beyond Plain MCP: Do Decision Models and Code Mode Make Tool Use Cheaper and Faster?"*).

UniExec allows AI Developer Agents to write and execute programmatic micro-scripts against local UniCortex primitives (`unimemory`, `univerify`, `uniskill`, `git`) instead of invoking multiple serial JSON-RPC tool calls.

## 🚀 Key Capabilities
- **98% Token Reduction**: Eliminates verbose intermediate tool-calling JSON-RPC turns.
- **Sub-50ms Local Execution**: Evaluates scripts in high-performance local namespaces.
- **3-Tier Fail-Closed Security**:
  1. *Tier 1: Pre-Execution AST Guard*: Rejects forbidden destructive calls (`rm -rf`, raw sockets, `eval`) before spawning.
  2. *Tier 2: Linux Namespace Isolation*: Powered by Bubblewrap (`bwrap 0.11.0`) with `--unshare-all`, `--ro-bind / /`, and `--tmpfs /tmp`.
  3. *Tier 3: Hardware Resource Quotas*: Enforced via `prlimit` (15s CPU, 512MB RAM ceiling, 64 process limit).
- **Pre-Bound UniCortex Primitives**:
  - `memory_recall(query)`
  - `memory_store_fact(sub, pred, obj)`
  - `verify_code_gate(code, filename)`
  - `get_beacon()`
  - `consult_scientist(inquiry)`
  - `convene_council(council_name, topic, spec)`
  - `git_diff_summary(repo_path)`

## 💻 CLI Commands
```bash
# Execute a script in the sandbox
uniexec run script.py

# Evaluate an inline code snippet
uniexec eval "result = memory_recall('token economy')"

# Run self-diagnostic checks
uniexec doctor

# Measure Code Mode token & latency savings
uniexec benchmark
```
