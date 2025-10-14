# Kubernetes Deployment Guide

This guide explains how to **set up and deploy** the microservices on a **Kubernetes cluster** using the `.yaml` files and `setup.sh` script located in the `/kubernetes` folder.

---

## **📈 Step 1: Transfer Local Files to the VM**
Before running Kubernetes setup, transfer all required configuration files to the VM.

### **1️⃣ Transfer Kubernetes Files**
Run this from your **local machine**:
```bash
scp -r kubernetes student065@<vm-ip>:/home/student065/
```
💪 This transfers all Kubernetes YAML files and setup scripts to the VM.

### **2️⃣ SSH Into the VM**
```bash
ssh student065@<vm-ip>
```
Now, navigate to the folder:
```bash
cd /home/student065/kubernetes
```

---

## **📈 Step 2: Setup Kubernetes Cluster**
The provided **`setup.sh`** script automates the setup of Kubernetes on the VM.

### **1️⃣ Setup the Master Node**
Run this on the **VM**:
```bash
chmod +x setup.sh
./setup.sh master
```
💪 **This will:**
- Install **dependencies**.
- Configure **container runtime (`containerd`)**.
- Initialize Kubernetes and set up the control plane.

### **2️⃣ Setup Worker Nodes**
Run this on each **worker node**:
```bash
./setup.sh worker
```
💪 **This will:**
- Join the worker node to the Kubernetes cluster.

### **3️⃣ Verify Cluster is Ready**
After setup, ensure all nodes are `Ready`:
```bash
kubectl get nodes
```
💪 **Expected Output:**
```
NAME        STATUS   ROLES           AGE   VERSION
master      Ready    control-plane   10m   v1.29.14
worker-1    Ready    <none>          5m    v1.29.14
worker-2    Ready    <none>          5m    v1.29.14
```

---

## **📈 Step 3: Deploy Microservices**
### **1️⃣ Apply Kubernetes Secrets**
Ensure **JWT_SECRET_KEY** and other sensitive values are stored as secrets.
```bash
kubectl apply -f secrets.yaml
```

### **2️⃣ Deploy Persistent Storage**
```bash
kubectl apply -f db-pv.yaml
kubectl apply -f db-pvc.yaml
```

### **3️⃣ Deploy Microservices**
```bash
kubectl apply -f auth-deployment.yaml
kubectl apply -f auth-service.yaml
kubectl apply -f shortener-deployment.yaml
kubectl apply -f shortener-service.yaml
kubectl apply -f headlamp.yaml
```
Verify the pods are running:
```bash
kubectl get pods
```

### **4️⃣ (Optional) Deploy Ingress for External Access**
```bash
kubectl apply -f ingress.yaml
kubectl apply -f ingress-nginx.yaml
kubectl apply -f cert-manager/
```
Verify Ingress is active:
```bash
kubectl get ingress
```

---

## **📈 Step 4: Access the Microservices**
### **1️⃣ Using NodePort (Without Ingress)**
```bash
kubectl get services
```
💪 Example Output:
```
NAME                    TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)
auth-service            ClusterIP   10.100.177.197   <none>        8001/TCP
headlamp                ClusterIP   10.103.226.21    <none>        80/TCP
kubernetes              ClusterIP   10.96.0.1        <none>        443/TCP
url-shortener-service   ClusterIP   10.101.146.241   <none>        8000/TCP
```
Test:
```bash
curl http://<worker-node-ip>:30001
curl http://<worker-node-ip>:30002
```

### **2️⃣ Using Ingress**
Test:
```bash
curl http://assignment.897000.xyz/auth
curl http://assignment.897000.xyz/shortener
```

---

<!-- API ENDPOINTS -->
## API Endpoints

### Authentication Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/auth/users` | Retrieve all users (mainly for debugging) |
| `POST` | `/auth/users` | Create a new user (requires username & password) |
| `PUT` | `/auth/users` | Update an existing user’s password |
| `POST` | `/auth/users/login` | Log in user (returns JWT) or verify an existing one |

### URL Shortener Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/shortener` | Create a new short URL (can supply short_id for custom). Always creates a unique entry. |
| `GET` | `/shortener/<short_id>` | Retrieve original URL |
| `PUT` | `/shortener/<short_id>` | Update an existing URL |
| `DELETE` | `/shortener/<short_id>` | Delete a short URL |
| `GET` | `/shortener/stats/<short_id>` | Get the number of times a short URL was accessed |
| `GET` | `/shortener` | Retrieve all short IDs (owned by the authenticated user) |
| `DELETE` | `/shortener` | Delete all short IDs owned by the authenticated user |

#### Example Usage

1. **Obtain a JWT** (Authentication Service)
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"username": "alice", "password": "mypass"}' \
     https://assignment.897000.xyz/auth/users/login
# Returns: {"token": "<JWT>"}
```

2.	**Create a Short URL** (URL Shortener)
```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer <JWT>" \
     -d '{"url": "https://example.com"}' \
     https://assignment.897000.xyz/shortener
# Returns: {"id": "<generatedShortID>", "value": "https://example.com"}
```

3. **Create a Short URL with Custom ID**
```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer <JWT>" \
     -d '{"url": "https://example2.com", "short_id": "myCustomID"}' \
     https://assignment.897000.xyz/shortener
# Returns: {"id": "myCustomID", "value": "https://example2.com"}
```

4. **Retrieve & Redirect**
```bash
curl -X GET https://assignment.897000.xyz/shortener/<short_id>
# This performs an HTTP 301 redirect to the original link. 
```

5. **Get Stats**
```bash
curl -X GET -H "Authorization: Bearer <JWT>" \
     https://assignment.897000.xyz/shortener/stats/<short_id>
# Returns: {"short_id": "<short_id>", "clicks": 5}
```

---

## **📈 Step 5: Monitor and Manage Kubernetes**
### **Check Pod Logs**
```bash
kubectl logs -f <pod-name>
```
### **Restart Failing Pods**
```bash
kubectl delete pod --all
```
### **Check Cluster Health**
```bash
kubectl get all
kubectl get nodes
kubectl get services
kubectl get pods -o wide
```
