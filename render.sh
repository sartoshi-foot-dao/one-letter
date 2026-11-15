#!/bin/sh
# One command for every deliverable. Runs inside the render image (Dockerfile):
#   sh render.sh [fps] [workers]
# For each format: frames -> contact sheets + poster -> mp4 with the synthesised soundtrack -> sync check.
set -eu
FPS=${1:-30}; NW=${2:-8}
mkdir -p out reviews
python3 src/audio.py out/one-letter.wav
for FMT in 16x9 9x16; do
  rm -rf "out/frames-$FMT"
  python3 src/film.py frames "$FMT" "out/frames-$FMT" "$FPS" "$NW"
  python3 src/film.py sheet "$FMT" "out/frames-$FMT" "$FPS"
  ffmpeg -y -loglevel error -framerate "$FPS" -i "out/frames-$FMT/%05d.png" -i out/one-letter.wav \
    -map 0:v -map 1:a -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -shortest -movflags +faststart "out/one-letter-$FMT.mp4"
  ffprobe -v error -show_entries format=duration -of csv=p=0 "out/one-letter-$FMT.mp4"
  python3 src/verify_sync.py out/one-letter.wav "$FPS" "out/one-letter-$FMT.mp4"
  cp reviews/sync-report.md "reviews/sync-report-$FMT.md"
  rm -rf "out/frames-$FMT"
done
