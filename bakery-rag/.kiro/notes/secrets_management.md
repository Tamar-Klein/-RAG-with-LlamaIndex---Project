# Secrets and API Keys
**Security Rule:** API keys and sensitive tokens must **NEVER** be hardcoded in the project files. 
**Implementation:** All secrets must be dynamically loaded via AWS Secrets Manager during runtime.