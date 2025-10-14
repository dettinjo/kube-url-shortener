#!/bin/bash

set -e # Exit on error

# ========================
# CONFIGURABLE VARIABLES
# ========================
MASTER_USER=""    # Username for connecting to the master node
MASTER_IP=""  # Master node IP address
PASSWORD="" # ⚠️ Not recommended in production
K8S_VERSION="1.29.2"
POD_CIDR="192.168.0.0/16"

# Function to install dependencies
install_dependencies() {
    echo "[Step 1] Updating system and installing dependencies..."
    sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl gpg lsb-release net-tools expect
}

# Function to install Docker and containerd
install_docker_containerd() {
    echo "[Step 2] Installing Docker and containerd..."

    sudo apt-get install -y ca-certificates curl gnupg lsb-release

    # Add Docker GPG key and repository
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo tee /etc/apt/keyrings/docker.asc >/dev/null
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

    # Install Docker components
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Enable and configure Docker
    sudo systemctl enable docker
}

# Function to configure containerd for Kubernetes
configure_containerd() {
    echo "[Step 3] Configuring containerd for Kubernetes..."

    # Generate default config
    sudo containerd config default >config.toml

    # Modify SystemdCgroup setting
    sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' config.toml

    # Move configuration and restart containerd
    sudo mv config.toml /etc/containerd/config.toml
    sudo systemctl restart containerd
}

# Function to install Kubernetes
install_kubernetes() {
    echo "[Step 4] Installing Kubernetes (v$K8S_VERSION)..."

    # Add Kubernetes repository
    sudo mkdir -p -m 755 /etc/apt/keyrings
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list

    # Install Kubernetes components
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
}

# Function to configure networking and hostname resolution
configure_networking() {
    echo "[Step 5] Configuring networking settings..."

    # Fix hostname resolution
    HOSTNAME=$(hostname)
    IP=$(hostname -I | awk '{print $1}')
    echo -e "$IP\t$HOSTNAME" | sudo tee -a /etc/hosts

    # Enable br_netfilter
    sudo modprobe br_netfilter
    echo "br_netfilter" | sudo tee /etc/modules-load.d/k8s.conf

    # Configure sysctl settings for networking
    sudo tee /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF

    # Apply settings
    sudo sysctl --system
}

# Function to initialize the Kubernetes master node
initialize_master() {
    echo "[Step 6] Initializing Kubernetes Control Plane..."

    # Run kubeadm init
    sudo kubeadm init --pod-network-cidr=$POD_CIDR

    # Setup kubeconfig
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config

    echo "[INFO] Master node setup complete. Save this command for worker nodes:"
    kubeadm token create --print-join-command
}

# Function to deploy Calico networking plugin
deploy_calico() {
    echo "[Step 7] Deploying Calico networking plugin..."

    # Ensure the directory exists
    sudo mkdir -p /etc/NetworkManager/conf.d/

    # Apply Calico configuration
    echo "[keyfile]
unmanaged-devices=interface-name:cali*;interface-name:tunl*;interface-name:vxlan.calico;interface-name:vxlan-v6.calico;interface-name:wireguard.cali;interface-name:wg-v6.cali" | sudo tee /etc/NetworkManager/conf.d/calico.conf >/dev/null

    # Restart NetworkManager
    sudo systemctl restart NetworkManager

    # Install Calico
    curl -O https://raw.githubusercontent.com/projectcalico/calico/v3.27.2/manifests/calico.yaml
    kubectl apply -f calico.yaml

    echo "[INFO] Calico installation complete. Wait until all pods are running."
}

# Function to join a worker node to the cluster
join_worker() {
    echo "[Step 8] Joining worker node to cluster..."

    # Use expect to handle password-based SSH and retrieve join command
    JOIN_COMMAND=$(expect -c "
        spawn ssh $MASTER_USER@$MASTER_IP kubeadm token create --print-join-command
        expect \"password:\"
        send \"$PASSWORD\r\"
        expect eof
    " | grep 'kubeadm join')

    # Validate the retrieved join command
    if [[ -z "$JOIN_COMMAND" ]]; then
        echo "[ERROR] Failed to retrieve join command from master node."
        exit 1
    fi

    # Ensure proper formatting
    JOIN_COMMAND=$(echo "$JOIN_COMMAND" | tr -d '\r' | xargs)

    # Debugging output
    echo "[INFO] Executing join command on worker node..."
    echo "Running: sudo bash -c \"$JOIN_COMMAND\""

    # Execute the join command correctly
    eval "sudo $JOIN_COMMAND"
}

# Main execution logic
if [ "$1" == "master" ]; then
    install_dependencies
    install_docker_containerd
    configure_containerd
    install_kubernetes
    configure_networking
    initialize_master
    deploy_calico
elif [ "$1" == "worker" ]; then
    install_dependencies
    install_docker_containerd
    configure_containerd
    install_kubernetes
    configure_networking
    join_worker
else
    echo "Usage: $0 {master|worker}"
    exit 1
fi
