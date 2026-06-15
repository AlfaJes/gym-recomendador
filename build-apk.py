#!/usr/bin/env python3
"""Build the Gym Recomendador APK on Raspberry Pi."""
import subprocess, sys, os, time, json
from pathlib import Path

PROJECT = Path("/opt/data/projects/gym-recomendador")
BUILD_LOG = PROJECT / "build-log.txt"
PWA_DIR = PROJECT / "pwa"

def log(msg):
    with open(BUILD_LOG, "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)

def run(cmd, **kw):
    log(f"  → {' '.join(cmd[:5])}...")
    kw.setdefault("timeout", 600)
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

# ─── Phase 1: Detect environment ─────────────────────────────
log("="*60)
log("🏋️ GYM RECOMENDADOR — APK BUILDER")
log("="*60)
log(f"Arquitectura: {os.uname().machine}")
log(f"Proyecto: {PROJECT}")
log("")

# Check Java
java = run(["which", "java"])
log(f"Java: {'✅' if java.returncode == 0 else '❌'} {java.stdout.strip() or 'no encontrado'}")

# Check Node
node = run(["node", "--version"])
log(f"Node: {'✅' if node.returncode == 0 else '❌'} {node.stdout.strip() or 'no encontrado'}")

# Check Android SDK
android_home = os.environ.get("ANDROID_HOME", "")
log(f"ANDROID_HOME: {'✅' if android_home else '❌ no configurado'}")
print(f"PROGRESS:5", flush=True)
