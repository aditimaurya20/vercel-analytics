from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# (region, latency_ms, uptime_pct)
DATA = [
    ("apac", 170.61, 98.162), ("apac", 203.76, 97.12), ("apac", 224.87, 98.132),
    ("apac", 149.57, 99.322), ("apac", 224.4, 97.835), ("apac", 168.26, 98.213),
    ("apac", 119.75, 98.858), ("apac", 190.28, 98.324), ("apac", 169.02, 97.602),
    ("apac", 192.02, 97.283), ("apac", 173.42, 98.901), ("apac", 221.73, 98.932),
    ("emea", 206.66, 98.762), ("emea", 209.57, 98.621), ("emea", 185.76, 98.6),
    ("emea", 198.56, 98.14), ("emea", 118.68, 98.782), ("emea", 127.84, 98.354),
    ("emea", 127.47, 97.861), ("emea", 172.97, 97.139), ("emea", 125.88, 98.081),
    ("emea", 183.47, 97.835), ("emea", 223.4, 99.199), ("emea", 133.58, 97.104),
    ("amer", 193.7, 98.079), ("amer", 205.39, 99.469), ("amer", 111.11, 97.112),
    ("amer", 181.69, 97.717), ("amer", 137.29, 97.233), ("amer", 137.16, 98.705),
    ("amer", 172.08, 98.472), ("amer", 169.72, 98.039), ("amer", 136.56, 98.932),
    ("amer", 158.69, 99.14), ("amer", 132.55, 99.12), ("amer", 115.99, 98.133),
]

class Query(BaseModel):
    regions: List[str]
    threshold_ms: float

def percentile(vals, p):
    s = sorted(vals)
    k = (len(s) - 1) * p / 100
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)

@app.post("/{full_path:path}")
def metrics(q: Query, full_path: str = ""):
    out = {}
    for region in q.regions:
        rows = [(l, u) for r, l, u in DATA if r == region.lower()]
        lat = [l for l, _ in rows]
        up = [u for _, u in rows]
        out[region] = {
            "avg_latency": sum(lat) / len(lat) if lat else None,
            "p95_latency": percentile(lat, 95) if lat else None,
            "avg_uptime": sum(up) / len(up) if up else None,
            "breaches": sum(1 for x in lat if x > q.threshold_ms),
        }
    return {**out, "regions": out}