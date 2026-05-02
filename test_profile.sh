#!/usr/bin/env bash
# Local test script that mirrors the profiler logic in the CI workflow.
# Runs ecm_prep and run steps for both the feature branch and master,
# back-to-back on the same machine, then reports relative performance.

set -e

cd "$(git rev-parse --show-toplevel)"

FEATURE_SHA=$(git rev-parse HEAD)
mkdir -p results

steps=("ecm_prep" "run")

# --- Profile FEATURE branch ---
echo "=== Profiling FEATURE branch ==="
# Clear ecm_prep cache so each branch starts from a cold cache
rm -rf generated/ecm_competition_data/*.pkl.gz
rm -f  generated/ecm_prep.json

for step in "${steps[@]}"; do
  log_file="memory_log_feature_${step}.txt"

  psrecord --log "$log_file" --include-children --interval 1 \
    "python tests/integration_testing/run_workflow.py \
      --run_step $step \
      --yaml tests/integration_testing/integration_test.yml \
      --with_profiler"

  # run_workflow.py writes cProfile stats to results/profile_${step}.csv — rename with branch suffix
  mv "results/profile_${step}.csv" "results/profile_${step}_feature.csv"

  # Build a one-row summary CSV from the memory log (last data row = total elapsed time)
  (
    echo "# Elapsed time (s),CPU (%),Real (MB),Virtual (MB)"
    grep -v "^#" "$log_file" | grep -v "^$" | tail -n 1 | awk '{printf "%.3f,%.3f,%.3f,%.3f\n",$1,$2,$3,$4}'
  ) > "results/memory_summary_${step}_feature.csv"

  mv "$log_file" "results/memory_log_${step}_feature.txt"
done

# --- Checkout master ---
echo "=== Switching to master branch ==="
git fetch --depth=1 origin master
# Stash any tracked changes only (-u would stash the profiling results we just wrote)
git stash --include-untracked=false -m "temp profiling stash" || true
git checkout origin/master -- .
pip install -c .github/constraints.txt ".[dev]" psrecord --quiet

# --- Profile MASTER branch ---
echo "=== Profiling MASTER branch ==="
# Clear ecm_prep cache so master also starts from a cold cache
rm -rf generated/ecm_competition_data/*.pkl.gz
rm -f  generated/ecm_prep.json

for step in "${steps[@]}"; do
  log_file="memory_log_master_${step}.txt"

  psrecord --log "$log_file" --include-children --interval 1 \
    "python tests/integration_testing/run_workflow.py \
      --run_step $step \
      --yaml tests/integration_testing/integration_test.yml \
      --with_profiler"

  mv "results/profile_${step}.csv" "results/profile_${step}_master.csv"

  (
    echo "# Elapsed time (s),CPU (%),Real (MB),Virtual (MB)"
    grep -v "^#" "$log_file" | grep -v "^$" | tail -n 1 | awk '{printf "%.3f,%.3f,%.3f,%.3f\n",$1,$2,$3,$4}'
  ) > "results/memory_summary_${step}_master.csv"

  mv "$log_file" "results/memory_log_${step}_master.txt"
done

# --- Restore feature branch ---
echo "=== Restoring feature branch ==="
git checkout "$FEATURE_SHA" -- .
pip install -c .github/constraints.txt ".[dev]" psrecord --quiet
git stash pop || true

# --- Comparison ---
echo ""
echo "=== Profiling Comparison ===" | tee results/profile_comparison.txt

for step in "${steps[@]}"; do
  echo "" | tee -a results/profile_comparison.txt
  echo "--- Step: $step ---" | tee -a results/profile_comparison.txt

  # Extract elapsed time from the last data row of each memory log (col 1)
  m_time=$(grep -v "^#" "results/memory_log_${step}_master.txt" | grep -v "^$" | tail -n 1 | awk '{print $1}')
  f_time=$(grep -v "^#" "results/memory_log_${step}_feature.txt" | grep -v "^$" | tail -n 1 | awk '{print $1}')

  echo "Master  elapsed time: ${m_time}s" | tee -a results/profile_comparison.txt
  echo "Feature elapsed time: ${f_time}s" | tee -a results/profile_comparison.txt

  if [[ -n "$m_time" && -n "$f_time" ]]; then
    abs_diff=$(awk "BEGIN {printf \"%.2f\", $m_time - $f_time}")
    pct=$(awk "BEGIN {printf \"%.2f\", ($m_time - $f_time) / $m_time * 100}")
    printf "Δ Time: %ss (%.2f%% improvement in feature vs master)\n" "$abs_diff" "$pct" \
      | tee -a results/profile_comparison.txt
  fi
done

echo ""
echo "Results saved in results/:"
ls results/profile_*.csv results/memory_log_*.txt results/memory_summary_*.csv results/profile_comparison.txt 2>/dev/null
