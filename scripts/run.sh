#!/bin/sh
set -x
version=$(ls -1 /Users/jeff/Library/Python | sort | tail -1)
dir=$(dirname $(python3 -m site --user-base))
#$dir/$version/bin/manim -pql main.py MusicAnimation
/opt/homebrew/bin/manim -pql main.py MusicAnimation
# /Library/Frameworks/Python.framework/Versions/3.11/bin/manim -pql main.py MusicAnimation