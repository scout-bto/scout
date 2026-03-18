# CI/CD Pipeline

## Workflow Sequence

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant GH as GitHub
    participant QG as Quality Gates
    participant IT as Integration Testing<br/>(Ubuntu)
    participant XP as Cross-Platform Testing<br/>(Windows + macOS)
    participant Cmp as Compare Results
    participant PR as PR Comment

    Dev->>GH: Push to master / Open PR to master
    GH->>QG: Trigger workflow

    par Quality Gates (gate integration tests)
        QG->>QG: flake8 + JSON validation
        QG->>QG: Documentation check
    end

    par Unit Tests (run in parallel, do not gate integration)
        QG->>QG: Unit tests (Python 3.10, 3.11, 3.12)
    end

    QG->>GH: Check PR status & profiler label

    par Integration + Cross-Platform
        GH->>IT: Start Ubuntu integration test
        IT->>IT: Setup Python 3.10.17 + pinned deps
        IT->>IT: Run Scout workflow (ecm_prep → run)

        opt run-profiler label or push to master
            IT->>IT: psrecord (memory + CPU tracking)
        end

        IT->>Cmp: Compare results vs master
        Note over Cmp: JSON: approx comparison<br/>(0.0001% threshold)
        Note over Cmp: PDFs: pixel-level comparison<br/>(rendered PNGs via pdftoppm + ImageMagick)
        Cmp->>IT: Upload artifacts

    and
        GH->>XP: Start Windows test
        XP->>XP: Setup Python 3.10 + pinned deps
        XP->>XP: Run Scout workflow
        XP->>Cmp: Compare JSON results vs master
        Note over XP: JSON: approx comparison<br/>(0.0001% threshold)
        XP->>XP: Upload artifacts + status

    and
        GH->>XP: Start macOS test
        XP->>XP: Setup Python 3.10 + pinned deps
        XP->>XP: Run Scout workflow
        XP->>Cmp: Compare JSON results vs master
        XP->>XP: Upload artifacts + status
    end

    alt Ubuntu results match master
        IT->>IT: No commit needed
    else Ubuntu plot images differ
        IT->>GH: Commit comparison PNGs to branch
    end

    alt Ubuntu results match master
        IT-->>PR: ✅ Pass
    else Ubuntu results differ
        alt update-baseline label present
            IT-->>PR: ⚠️ Warn (accept as new baseline)
        else No label
            IT-->>PR: ❌ Fail
        end
    end

    PR->>PR: Collect cross-platform artifacts
    PR->>GH: Save comment body + PR number as artifact

    Note over GH: workflow_run trigger<br/>(base repo context, write access)
    GH->>PR: Download comment artifact
    PR->>GH: Post PR comment
    Note over PR: Always posted, even on failure.<br/>Works for fork PRs (split workflow pattern).<br/>Includes:<br/>• Ubuntu status + comparison result<br/>• What changed (JSON diffs, pixel-level plot diffs, or both)<br/>• Cross-platform results table<br/>• Before/after plot table (if diffs)<br/>• Failure details (if applicable)

    opt Accepting expected changes
        Dev->>GH: Add update-baseline label
        GH->>IT: CI re-runs automatically
        IT-->>PR: ⚠️ Results accepted
        Dev->>GH: Merge PR
        Note over GH: Committed results become<br/>the new master baseline
    end
```

## How It Works

### Triggers
- **Push to `master`**: Runs full pipeline including profiler
- **PR to `master`**: Runs on `opened`, `synchronize`, `reopened`, `ready_for_review`, `labeled`

### Pipeline Structure
- **Quality gates** (flake8, JSON validation, docs check) must pass before integration tests start
- **Unit tests** (Python 3.10, 3.11, 3.12) run in parallel with integration tests — they do **not** block the integration pipeline
- **Integration tests** start as soon as quality gates pass, without waiting for unit tests

### Comparison Strategy
- **JSON results**: Approximate comparison — values within `0.0001%` tolerance are treated as equal (handles floating-point platform noise)
- **PDF plots** (Ubuntu only): Rendered to PNG at 150 DPI and compared pixel-by-pixel — metadata-only differences (timestamps, version strings) are ignored
- **Summary Excel files**: Percent difference report generated for review
- **Cross-platform**: Windows and macOS run JSON-level comparison against master

### When Results Differ
1. Full results (JSON, PDFs, Excel) are uploaded as workflow artifacts (Ubuntu only)
2. If plot images differ (pixel-level), comparison PNGs are committed to the PR branch for embedding in the PR comment
3. JSON and PDF result files are **not** committed to avoid breaking GitHub's diff viewer
4. The failure message specifies what changed: JSON diffs, pixel-level plot diffs, or both
5. The integration test step fails with ❌

### PR Comment (Split Workflow Pattern)
- The integration test workflow saves the comment body + PR number as an artifact (no write access needed)
- A separate `post_pr_comment.yml` workflow, triggered by `workflow_run`, downloads the artifact and posts the comment in the **base repo context** with write access
- This pattern ensures PR comments work for **fork PRs**, where `GITHUB_TOKEN` is read-only on `pull_request` events
- The comment is **always posted** after every CI run, regardless of pass/fail status
- Includes an **Ubuntu (Baseline)** section with status, diff result, and artifact links
- Includes a **Cross-Platform Results** table with status and JSON diff results for each platform
- On failure, includes a "Failure Details" section explaining the cause and instructions to use the `update-baseline` label
- Changed plots are shown in a before/after table inside collapsible sections

### Accepting Expected Changes
1. Add the `update-baseline` label to the PR
2. CI re-runs automatically (via `labeled` trigger)
3. The failure step is skipped — results are accepted as the new baseline
4. When merged, the committed results become the master baseline

### Pinned Environment
- Python `3.10.17` on Ubuntu (baseline); Python `3.10` on Windows/macOS
- `.github/constraints.txt` with exact dependency versions for all platforms
- `SOURCE_DATE_EPOCH=0` for deterministic PDF timestamps

### Cross-Platform Testing
- Integration tests run in parallel on **Ubuntu** (baseline), **Windows**, and **macOS**
- All platforms compare JSON results against master using `compare_results.py` with `0.0001%` threshold
- Pixel-level PDF comparison, result commits, and PR comment logic only run on Ubuntu
- Cross-platform results are aggregated into the PR comment as a summary table

## How to Use CI Flags

### PR Labels

| Label | Effect |
|---|---|
| `run-profiler` | Enables memory and CPU profiling during the integration test |
| `update-baseline` | Accepts result diffs as expected changes (skips failure for unit tests and integration tests) |

### Adding a Label
1. Go to the PR page on GitHub
2. Click the **Labels** gear icon in the right sidebar
3. Select the desired label (create it first if it doesn't exist)
4. CI re-runs automatically when the label is added (via the `labeled` trigger)

### Profiler
When enabled (via `run-profiler` label or push to `master`), the profiler:
- Tracks memory and CPU usage via `psrecord`
- Runs each step (`ecm_prep`, `run`) individually with `--with_profiler`
- Generates `profile_*.csv` files with peak memory/CPU metrics
- Logs are included in the uploaded workflow artifacts

### update-baseline
Use this when code changes intentionally alter results:
1. Review the before/after plots in the PR comment
2. If the changes are expected, add the `update-baseline` label
3. CI re-runs and skips the failure step (emits a warning instead) — applies to both **unit tests** and **integration tests**
4. On merge, the committed results become the new master baseline

### Constraints File
To update pinned dependency versions:
1. Edit `.github/constraints.txt` with the new versions
2. Re-run CI to verify the integration test still produces matching results
3. If results differ, use `update-baseline` to accept the new baseline
