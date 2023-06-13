What is it?
---

The custom_secrets_manager package is a powerful python utility that simplifies configuration management and secrets handling within Git repositories. With just a directory path, the package automatically scans for popular configuration file formats such as YAML, INI, and JSON. It encrypts and securely stores secrets in a dedicated secrets_registry.log file, ensuring sensitive information remains protected. Additionally, by specifying only key names in the configuration file, the package seamlessly loads corresponding secrets from environment variables. This eliminates the need for separate configuration loading utilities and streamlines the development process. custom_secrets_manager is a useful tool for secure and efficient configuration management in Git projects.

Installation
---
```pip install custom-secrets-manager```