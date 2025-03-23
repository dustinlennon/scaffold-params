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

cleanup() {
	if [ -d "$tmpdir" ]; then
		echo removing $tmpdir
		rm -rf $tmpdir
	fi
}

trap cleanup EXIT

echo creating $DEST
mkdir -p $DEST

# echo creating $tmpdir
# tmpdir=$(mktemp -d)

# pushd $tmpdir
# git clone https://github.com/dustinlennon/scaffold .
# popd 

# cp -r $tmpdir/samples $DEST

pushd $DEST
cat << EOF > dotenv
BASIC_CONFIG_PATH=${DEST}/samples/conf/basic.yaml
EOF

if [ ! -f Pipfile ]; then
	pipenv --python /usr/bin/python3
fi
pipenv install git+https://github.com/dustinlennon/scaffold#egg=scaffold
popd
