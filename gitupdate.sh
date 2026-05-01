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
    "diagnostics")
        df -hl
        echo ">>> CRON"
        crontab -u pi -l | grep ^[^#]
        echo ">>> ERRORS"
        tail /var/log/apache2/error.log
        echo ">>> DIRS"
        ls -l $FW_PATH
        ls -l $FW_PATH/logs
        ls -l $FW_PATH/photos
        echo ">>> GIT"
        echo $FW_PATH
        cd $FW_PATH
        git status
        git log -1
        echo $WEB_PATH
        cd $WEB_PATH
        git status
        git log -1
    ;;
    "reset")
        echo ">>> PERMISSIONS"
        sudo chown -R pi:pi $FW_PATH/.git
        sudo chown -R pi:pi $FW_PATH/logs
        sudo chown -R pi:pi $FW_PATH/photos
        ls -l $FW_PATH
        ls -l $FW_PATH/logs
        ls -l $FW_PATH/photos
        chmod u+w $FW_PATH/logs/*
        echo ">>> GIT"
        echo $FW_PATH
        cd $FW_PATH
        git reset --hard HEAD
        rm -r .git/refs/remotes/origin
        git pull
        echo $WEB_PATH
        cd $WEB_PATH
        git reset --hard HEAD
    ;;
    *)
        echo "no command; did you mean versions, uptodate, settz, diagnostics, reset?"
        exit 1
    ;;
esac


