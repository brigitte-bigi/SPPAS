#!/bin/bash

echo "Push on SourceForge:master"
git push origin master

echo "Tag the release"
git tag -a "v$1" -m "Release $1"

echo "Push on github:main"
git checkout --orphan main
git add -A
git commit -m "Release $1"
git push github main --force
git checkout master
git branch -D main

