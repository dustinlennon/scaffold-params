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

# make samples easily available
scaffold_path=$(pipenv run python -c "import scaffold; print(scaffold.__path__[0])")

ln -s ${scaffold_path}/samples

cat << EOF > dotenv
BASIC_CONFIG_PATH=${scaffold_path}/samples/conf/basic.yaml
EOF

