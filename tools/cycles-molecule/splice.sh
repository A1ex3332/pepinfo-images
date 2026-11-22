#!/bin/bash
# Splice the Cycles molecule shot into the kisspeptin Reel (9.87-14.10 s) keeping its caption cards and audio.
set -e
cd ~/work/mol
O=/mnt/project-files/automation/growth/test-reel/kiss-zoom/kpreg-v1.mp4
A=9.87; B=14.10; D=$(python3 -c "print(round($B-$A,3))")
ffmpeg -loglevel error -y -framerate 30 -i clip/f%04d.png -vf "scale=1080:1920:flags=lanczos,minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1,trim=duration=$D" -c:v libx264 -crf 12 -pix_fmt yuv420p mol60.mp4
ffmpeg -loglevel error -y -ss $A -t $D -i $O -an -c:v libx264 -crf 12 -pix_fmt yuv420p orig_mid.mp4
ffmpeg -loglevel error -y -i mol60.mp4 -i orig_mid.mp4 -filter_complex \
 "[1]crop=980:304:50:166[c1];[1]crop=980:256:50:166[c2];[0][c1]overlay=50:166:enable='lt(t,1.41)'[v1];[v1][c2]overlay=50:166:enable='gte(t,1.41)'" \
 -c:v libx264 -crf 12 -pix_fmt yuv420p mid.mp4
ffmpeg -loglevel error -y -i $O -i mid.mp4 -filter_complex \
 "[0:v]trim=0:$A,setpts=PTS-STARTPTS[a];[0:v]trim=$B,setpts=PTS-STARTPTS[c];[1:v]setpts=PTS-STARTPTS[b];[a][b][c]concat=n=3:v=1:a=0[v]" \
 -map "[v]" -map 0:a -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -c:a copy -movflags +faststart kpreg-cycles-molecule.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 kpreg-cycles-molecule.mp4
