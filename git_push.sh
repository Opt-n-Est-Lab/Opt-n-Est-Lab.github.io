#!/bin/bash

# Default commit message if none provided
MESSAGE=${1:-"Quick commit"}

git status
git add .
git status
git commit -m "$MESSAGE"
git push origin main