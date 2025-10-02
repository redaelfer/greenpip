# tools/measure_and_test.py
# Mesure CPU/mémoire pendant un run pytest et écrit metrics.json + junit report
import subprocess
import time
import json
import sys
import psutil
import os

def run_and_sample(junit_path="report.xml", sample_interval=0.5):
    # utilise la forme --junitxml=<file>
    cmd = ["pytest", f"--junitxml={junit_path}"]
    print("Running:", " ".join(cmd))
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + (os.pathsep + env.get("PYTHONPATH","") if env.get("PYTHONPATH") else "")
    proc = subprocess.Popen(cmd, env=env)
    time.sleep(0.05)

    samples = []
    start_time = time.time()

    try:
        while proc.poll() is None:
            stamp = time.time()
            # somme CPU + mémoire des processus Python actifs dans le repo (heuristique)
            cpu_total = 0.0
            mem_total = 0
            procs = []
            for p in psutil.process_iter(['pid','name','cmdline']):
                try:
                    name = (p.info.get('name') or '').lower()
                    cmdline = ' '.join(p.info.get('cmdline') or [])
                    # heuristique: processus python / pytest qui appartiennent au workspace
                    if 'python' in name or 'pytest' in cmdline or 'pytest' in name:
                        procs.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # initial call to cpu_percent to prime
            for p in procs:
                try:
                    p.cpu_percent(interval=None)
                except Exception:
                    pass

            # sleep interval to get meaningful cpu %
            time.sleep(sample_interval)

            for p in procs:
                try:
                    cpu_total += p.cpu_percent(interval=None)
                    mem = p.memory_info().rss if p.is_running() else 0
                    mem_total += mem
                except Exception:
                    pass

            samples.append({"t": stamp, "cpu_percent": cpu_total, "mem_rss": mem_total})

    except KeyboardInterrupt:
        proc.terminate()
    proc.wait()
    end_time = time.time()

    if samples:
        avg_cpu = sum(s["cpu_percent"] for s in samples) / len(samples)
        peak_mem = max(s["mem_rss"] for s in samples)
    else:
        avg_cpu = 0.0
        peak_mem = 0

    metrics = {
      "elapsed_s": end_time - start_time,
      "avg_cpu_percent": avg_cpu,
      "peak_mem_bytes": peak_mem,
      "samples": samples,
      "returncode": proc.returncode
    }

    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Wrote metrics.json")
    return proc.returncode

def main():
    import argparse
    parser = argparse.ArgumentParser(prog="measure_and_test.py")
    parser.add_argument("--junit", default="report.xml", help="Path for junit xml output")
    parser.add_argument("--interval", type=float, default=0.5, help="Sampling interval (seconds)")
    args = parser.parse_args()

    # run and sample
    rc = run_and_sample(junit_path=args.junit, sample_interval=args.interval)
    if rc != 0:
        print(f"pytest failed (returncode {rc})")
        sys.exit(rc)
    else:
        print("pytest finished successfully")

if __name__ == "__main__":
    main()
