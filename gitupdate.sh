#!/bin/sh
case "$1" in
    "pull")
        cd /home/pi/Desktop/Mothbox/Web
        git pull
        ./postupdate.sh

        cd /home/pi/Desktop/Mothbox
        git pull
    ;;
    "versions")
        FIRMWARE=$(cd ../ && git describe)
        WEB=$(git describe)
        echo "Fw-$FIRMWARE Web-$WEB"
    ;;
    "uptodate")
        cd /home/pi/Desktop/Mothbox/Web
        git remote update > /dev/null


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
    ;;
    *)
        echo "no command; did you mean versions or uptodate?"
        exit 1
    ;;
esac


