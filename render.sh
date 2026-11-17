#!/bin/sh
# One command for every deliverable. Runs inside the render image (Dockerfile):
#   sh render.sh [fps] [workers]          (ARM=B sh render.sh ... renders the viewer-study control film)
# For each format: frames -> contact sheets + poster -> mp4 with the synthesised soundtrack -> sync check.
set -eu
FPS=${1:-30}; NW=${2:-8}
ARM=${ARM:-A}; export ARM
if [ "$ARM" = A ]; then SUF=""; else SUF="-$ARM"; fi
mkdir -p out reviews
python3 src/audio.py out/one-letter$SUF.wav
for FMT in 16x9 9x16; do
  rm -rf "out/frames$SUF-$FMT"
  python3 src/film.py frames "$FMT" "out/frames$SUF-$FMT" "$FPS" "$NW"
  python3 src/film.py sheet "$FMT" "out/frames$SUF-$FMT" "$FPS"
  ffmpeg -y -loglevel error -framerate "$FPS" -i "out/frames$SUF-$FMT/%05d.png" -i out/one-letter$SUF.wav \
    -map 0:v -map 1:a -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -shortest -movflags +faststart "out/one-letter$SUF-$FMT.mp4"
  ffprobe -v error -show_entries format=duration -of csv=p=0 "out/one-letter$SUF-$FMT.mp4"
  python3 src/verify_sync.py out/one-letter$SUF.wav "$FPS" "out/one-letter$SUF-$FMT.mp4"
  cp reviews/sync-report.md "reviews/sync-report$SUF-$FMT.md"
  rm -rf "out/frames$SUF-$FMT"
done
