#!/bin/sh

git remote update

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Latest Updates"
elif [ $LOCAL = $BASE ]; then
    echo "Update Available"
elif [ $REMOTE = $BASE ]; then
    echo "Local Changes"
else
    echo "Diverged"
fi
