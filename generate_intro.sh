#! /bin/bash

say -v Daniel -r 175 -o intro_911_line.flac "This is the Nine One One Distraction Line. What is your emergency?"
ffmpeg -y -i intro_911_line.flac intro_911_line.mp3
cp -af intro_911_line.mp3 intro_live.mp3
share intro_live.mp3
