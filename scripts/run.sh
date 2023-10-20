#!/bin/sh

manim="${1:-manim}"

touch timidity.cfg

"$manim" -pql main.py MusicAnimation