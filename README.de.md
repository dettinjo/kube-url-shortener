<!-- portfolio:date=2023-12-15 -->

[Deutsch](README.de.md) · [English](README.md)

# Kubernetes URL-Kürzer

Ein produktionsreifer URL-Kürzungsdienst, der als praktische Übung in Kubernetes-Orchestrierung und Cloud-nativen Deployment-Mustern entwickelt wurde. Das Projekt geht über eine einfache Webanwendung hinaus — der Schwerpunkt liegt auf dem vollständigen Kubernetes-Deployment-Stack inklusive persistentem Speicher, TLS-Terminierung und automatischem Zertifikatsmanagement.

<p align="center">
  <img src="docs/kubernetes.svg" alt="Kubernetes" width="170" />
</p>

### Architektur

Der Dienst besteht aus mehreren Kubernetes-Komponenten: einem Flask-Backend zur URL-Verwaltung, einem NGINX-Ingress-Controller für das Routing, cert-manager für automatische SSL/TLS-Zertifikate sowie einem NFS-basiertem Persistent Volume für die Datenhaltung.

### Kernfunktionen

- **Kubernetes-Orchestrierung** mit Deployments, Services und Ingress-Ressourcen
- **Automatisches TLS** via cert-manager und Let's Encrypt
- **Persistenter Speicher** über NFS-basierte Persistent Volumes
- **NGINX Ingress** für Load Balancing und Routing
- **Flask-Backend** mit SQLite-Datenbankanbindung

### Lernziele

Dieses Projekt demonstriert den gesamten Lifecycle einer Cloud-nativen Anwendung: von der Containerisierung über die Orchestrierung bis hin zur sicheren HTTPS-Bereitstellung in einem echten Kubernetes-Cluster.
