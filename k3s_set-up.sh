# Installling K3s
curl -sfL https://get.k3s.io | sh -
sudo systemctl status k3s

# Settting K3 as default kuberntes infrastructure
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown "$USER:$USER" ~/.kube/config
chmod 600 ~/.kube/config

# Import docker images to K3s
docker save marine_edge_platform-publisher:latest \
  marine_edge_platform-subscriber:latest \
  marine_edge_platform-sync-agent:latest \
  -o marine-edge-images.tar

sudo k3s ctr images import marine-edge-images.tar
sudo k3s ctr images list | grep marine