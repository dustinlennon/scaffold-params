#!/bin/bash

# gitpip.sh 
# 	clones the scaffold repo into a temporary directory;
#	creates a destination directory, `DEST`;
# 	copies the `./samples` directory from the repo into `DEST/sample`;
# 	dynamically creates `DEST/dotenv` for the "basic" sample;
# 	if missing, creates `DEST/Pipfile`--the pipenv virtual environment;
# 	installs "scaffold" into the pipenv

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

# pipenv install file://${HOME}/Workspace/Sandbox/scaffold#egg=scaffold
pipenv install git+https://github.com/dustinlennon/scaffold#egg=scaffold

# create a dotenv file
cat << EOF > dotenv
BASIC_CONFIG_PATH=${DEST}/samples/conf/basic.yaml
EOF

# copy samples out of site-package directory
venv=$(pipenv --venv)
site_packages=$(find $venv -type d -name "site-packages")
cp -r ${site_packages}/samples .

# remove any __pycache__ subdirectories
find ./samples -type d -name "__pycache__" | xargs rm -rf
popd
