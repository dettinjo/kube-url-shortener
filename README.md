<!-- portfolio:date=2023-12-15 -->

[English](README.md) · [Deutsch](README.de.md)

# Kubernetes URL Shortener

A production-grade URL shortening service built as a practical exercise in Kubernetes orchestration and cloud-native deployment patterns. The project goes beyond a simple web app — the primary focus is the full Kubernetes deployment stack, including persistent storage, TLS termination, and automated certificate management.

<p align="center">
  <img src="docs/docker.svg" alt="Docker" width="170" />
</p>

### Architecture

The application itself is a lightweight Python/Flask service, but the real work is in the Kubernetes infrastructure:

- **Deployment & Service**: The Flask application runs in a Kubernetes Deployment with replica management, exposed via a ClusterIP Service.
- **Nginx Ingress Controller**: Routes external HTTP/S traffic to the application, handling path-based routing and enforcing HTTPS redirects.
- **cert-manager + Let's Encrypt**: Automatically provisions and renews TLS certificates, enabling HTTPS without manual certificate management.
- **NFS Persistent Volume**: The URL database (SQLite) is stored on an NFS-backed Persistent Volume Claim, ensuring data survives pod restarts and rescheduling.
- **ConfigMaps & Secrets**: Application configuration and sensitive data are managed as Kubernetes-native resources, never hardcoded.

### Key Learnings

This project provided hands-on experience with the full Kubernetes networking stack — from understanding how Ingress controllers interact with Services, to configuring cert-manager ACME challenges behind a NAT router. The NFS storage setup required configuring both the NFS server and the Kubernetes StorageClass, giving practical insight into how persistent storage works in a self-hosted cluster.
