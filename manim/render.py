"""Render every scene to site/media/<Scene>.mp4 plus a poster PNG (last frame).

Usage:  python manim/render.py            # all scenes
        python manim/render.py MirrorStep # one scene
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENES = ["ZerosOnTheLine", "PrimesFromZeros", "MirrorStep", "Multiplicity", "ThetaChain"]
BUILD = ROOT / "build" / "manim"
OUT = ROOT / "site" / "media"


def run(scene, *flags):
    cmd = [sys.executable, "-m", "manim", "render", "-qm", "--media_dir", str(BUILD),
           *flags, str(ROOT / "manim" / "scenes.py"), scene]
    subprocess.run(cmd, check=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for scene in sys.argv[1:] or SCENES:
        run(scene)
        run(scene, "-s")  # last frame as poster
        video = BUILD / "videos" / "scenes" / "720p30" / f"{scene}.mp4"
        poster = next((BUILD / "images" / "scenes").glob(f"{scene}*.png"))
        shutil.copy(video, OUT / f"{scene}.mp4")
        shutil.copy(poster, OUT / f"{scene}.png")
        print(f"ok {scene}")


if __name__ == "__main__":
    main()
