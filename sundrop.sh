DIR="$(dirname $(readlink /usr/local/bin/sundrop))"
fab -f $DIR/sundrop $@
