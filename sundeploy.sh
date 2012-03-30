DIR="$(dirname $(readlink /usr/local/bin/sundeploy))"
fab -f $DIR/sundeploy $@
