apt update && apt upgrade -y
apt install -y build-essential git

# install docker
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do apt remove $pkg; done
apt update
apt install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
cd ~/etp_parsing
uv sync

cp .env.example .env
docker compose -f docker-compose.dev.yml up -d

# install playwright
uv run playwright install chromium --with-deps