sudo apt update -y && sudo apt upgrade -y

sudo apt-get install build-essential libffi-dev -y

sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get install python3.10 python3.10-venv python3.10-dev -y
export PATH=$PATH:$HOME/.local/bin
curl --fail --silent --show-error https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install -U pip setuptools wheel

python3.10 -m venv venv
./venv/bin/pip install -U pip setuptools wheel
./venv/bin/pip install -U -r requirements.txt

sudo apt-get install libsndfile1 ffmpeg sox -y

VERSION=$(uname -i)
if [ "$version" = "x86_64" ]; then
    FILE="google-cloud-cli-406.0.0-linux-x86_64.tar.gz"
elif [ "$version" = "aarch64" ]; then
    FILE="google-cloud-cli-406.0.0-linux-arm.tar.gz"
else
    FILE="google-cloud-cli-406.0.0-linux-x86.tar.gz"
fi
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/$FILE
tar -xf $FILE
./google-cloud-sdk/install.sh -q

sudo apt-get install nginx -y
sudo cp ./core/setup/nginx.conf /etc/nginx/conf.d/yodaapi.conf

chmod +x ./run.bash

sudo cp ./core/setup/systemd.service /etc/systemd/system/API.service
sudo systemctl daemon-reload
sudo systemctl enable API

sudo systemctl start API

source ~/.bashrc
