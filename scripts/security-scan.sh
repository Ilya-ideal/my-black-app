#!/bin/bash
echo "🔒 Running Security Scans..."

# Scan for secrets in code
echo "Scanning for secrets..."
git secrets --scan

# Docker image security scan
echo "Scanning Docker image..."
trivy image ilia2014a/my-black-app:latest

# Dependency vulnerability scan
echo "Scanning Python dependencies..."
safety check

echo "✅ Security scans completed"