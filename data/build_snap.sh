#!/bin/bash

DIR=$(dirname "$(readlink -f "$0")")

echo "Copy snapcraft.yaml to base directory"
cd $DIR
cp snapcraft.yaml ..
cd ..
sed -i "s/version\: git/version\: $(python3 src/urh/version.py)/" snapcraft.yaml


SNAPCRAFT_BUILD_ENVIRONMENT_CPU=4 SNAPCRAFT_BUILD_ENVIRONMENT_MEMORY=6G snapcraft
sudo snap install --dangerous urh*.snap
urh
