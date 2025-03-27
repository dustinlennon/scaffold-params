#!/bin/bash
#
# Create a pipenv in the provided directory, or use an existing pipenv if 
# available. Install the scaffold-params distribution from github.  Finally,
# link the samples and create a dotenv file that to run `basic.py` without 
# an explicit --config parameter.
#
# syntax:
#   gitpip.sh dest_dir
#

args=("$@")

if [ ${#args[@]} -ne 1 ]; then
	echo "syntax error:  ./gitpip.sh dest_dir"
	exit 1
fi

DEST=$1
DEST=${DEST:-.}
DEST=$(realpath $DEST)

echo creating $DEST
mkdir -p $DEST

pushd $DEST
if [ ! -f Pipfile ]; then
	pipenv --python /usr/bin/python3
fi

# pipenv install file://${HOME}/Workspace/Sandbox/scaffold-params#egg=scaffold
pipenv install git+https://github.com/dustinlennon/scaffold-params#egg=scaffold

# make samples easily available
scaffold_path=$(pipenv run python -c "import scaffold; print(scaffold.__path__[0])")

ln -s ${scaffold_path}/samples

cat << EOF > dotenv
BASIC_CONFIG_PATH=${scaffold_path}/samples/conf/basic.yaml
EOF

