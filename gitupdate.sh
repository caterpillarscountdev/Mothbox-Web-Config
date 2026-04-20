#!/bin/sh

FW_PATH=/home/pi/Desktop/Mothbox
WEB_PATH=/home/pi/Desktop/Mothbox/Web

uptodate() {
    cd $WEB_PATH
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
}

case "$1" in
    "pull")
        cd $WEB_PATH
        git pull
        ./postupdate.sh

        cd $FW_PATH
        git pull
    ;;
    "versions")
        FIRMWARE=$(cd $FW_PATH && git describe)
        WEB=$(cd $WEB_PATH && git describe)
        echo "Fw-$FIRMWARE Web-$WEB"
    ;;
    "uptodate")
        uptodate
    ;;
    "settz")
        sudo timedatectl set-timezone $2
        echo "TZ set to $2"
    ;;
    *)
        echo "no command; did you mean versions or uptodate?"
        exit 1
    ;;
esac


