sudo apt update -y && sudo apt upgrade -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get install python3.10 python3.10-venv python3.10-dev
export PATH=$PATH:$HOME/.local/bin
curl --fail --silent --show-error https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install -U pip setuptools wheel
python3.10 -m venv venv
./venv/bin/pip install -U -r requirements.txt
