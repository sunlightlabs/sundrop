DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fab -f $DIR/sundeploy $@
