import json, os, glob, statistics, argparse, pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("baseline_dir")
parser.add_argument("opt_dir")
parser.add_argument("--out", default="comparison.md")
args = parser.parse_args()

def read_metrics(dirpath):
    rows = []
    for fp in glob.glob(os.path.join(dirpath, "*.json")):
        try:
            with open(fp) as f:
                m = json.load(f)
            rows.append(m)
        except:
            pass
    return rows

b = read_metrics(args.baseline_dir)
o = read_metrics(args.opt_dir)

def stats(arr):
    elapsed = [x["elapsed_s"] for x in arr]
    cpu = [x["avg_cpu_percent"] for x in arr]
    mem = [x["peak_mem_bytes"] for x in arr]
    return {
        "n": len(arr),
        "elapsed_mean": statistics.mean(elapsed) if elapsed else None,
        "elapsed_std": statistics.pstdev(elapsed) if elapsed else None,
        "cpu_mean": statistics.mean(cpu) if cpu else None,
        "mem_mean": statistics.mean(mem) if mem else None
    }

sb = stats(b)
so = stats(o)

# markdown summary
with open(args.out, "w") as f:
    f.write("# Résumé comparatif\n\n")
    f.write("## Baseline\n")
    f.write(str(sb)+"\n\n")
    f.write("## Optimized\n")
    f.write(str(so)+"\n\n")
    if sb["elapsed_mean"] and so["elapsed_mean"]:
        reduction = (sb["elapsed_mean"] - so["elapsed_mean"]) / sb["elapsed_mean"] * 100
        f.write(f"Durée moyenne réduite de {reduction:.1f}%\n")
print("Wrote", args.out)

# plot
df = pd.DataFrame({
    "baseline_elapsed": [x["elapsed_s"] for x in b],
    "opt_elapsed": [x["elapsed_s"] for x in o]
})
df.plot(kind="box")
plt.title("Comparaison des durées (s)")
plt.savefig("duration_boxplot.png")
print("Wrote duration_boxplot.png")
