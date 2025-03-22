#!/bin/bash

cleanup() {
	if [ -d "$tmpdir" ]; then
		echo removing $tmpdir
		rm -rf $tmpdir
	fi
}

trap cleanup EXIT

dest=$1
dest=${dest:-.}

echo $dest
mkdir -p $dest

echo creating $tmpdir
tmpdir=$(mktemp -d)

pushd $tmpdir
git clone https://github.com/dustinlennon/pyapp-scaffold .
popd 

cp -r $tmpdir/templates $dest
cp -r $tmpdir/conf $dest
cp $tmpdir/example.py $dest

full_path=$(realpath $dest)
cat << EOF > $dest/dotenv
EXAMPLE_CONFIG_PATH=${full_path}/conf/example.yaml
EOF

pushd $dest
pipenv --python /usr/bin/python3
pipenv install git+https://github.com/dustinlennon/pyapp-scaffold#egg=scaffold
popd