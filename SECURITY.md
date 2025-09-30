# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Notepad++ MCP Server, please help us by reporting it responsibly.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
- **security@sandraschi.dev** (preferred)
- Or create a private security advisory on GitHub

### What to Include

When reporting a vulnerability, please include:

1. **Description**: A clear description of the vulnerability
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Impact**: What an attacker could achieve by exploiting this vulnerability
4. **Affected Versions**: Which versions are affected
5. **Environment**: Your operating system, Python version, and Notepad++ version
6. **Proof of Concept**: If possible, include a proof of concept

### Response Timeline

We will acknowledge your report within **48 hours** and provide a more detailed response within **7 days** indicating our next steps.

We will keep you informed about our progress throughout the process of fixing the vulnerability.

### Disclosure Policy

- We follow a **90-day disclosure timeline** from the initial report
- We will credit you (if desired) in our security advisory
- We will not disclose vulnerability details until a fix is available
- We may delay disclosure for critical infrastructure vulnerabilities

## Security Considerations

### Windows API Integration
This MCP server integrates with Windows APIs through pywin32. Please be aware of:

- **Windows Permissions**: The server requires Windows API access
- **Process Isolation**: Runs in the context of the Claude Desktop process
- **File System Access**: Can read and modify files through Notepad++

### Data Handling
- **File Content**: The server can access and modify file contents
- **Clipboard Operations**: Uses Windows clipboard for text insertion
- **Process Information**: Can access system process information

### Network Communications
- **Local Only**: All operations are performed locally on the user's system
- **No External Communications**: The server does not send data to external services
- **MCP Protocol**: Communications follow the Model Context Protocol over stdio

## Security Best Practices

### For Users
1. **Install from Trusted Sources**: Only install from the official GitHub repository
2. **Keep Dependencies Updated**: Regularly update pywin32 and other dependencies
3. **Monitor File Access**: Be aware that the server can access your files
4. **Use in Trusted Environments**: Run only in environments you trust

### For Developers
1. **Input Validation**: All user inputs are validated and sanitized
2. **Error Handling**: Comprehensive error handling prevents information leakage
3. **Logging**: Sensitive information is not logged
4. **Dependency Scanning**: Regular security audits of dependencies

## Known Security Considerations

### Windows-Specific Risks
- **API Access**: Requires Windows API permissions
- **Process Manipulation**: Can interact with Notepad++ processes
- **File System**: Full file system access through Notepad++

### MCP Protocol Security
- **Local Communication**: All MCP communication happens locally
- **Stdio Protocol**: Uses standard input/output streams
- **No Authentication**: Relies on Claude Desktop's security model

## Security Updates

Security updates will be:
- **Released as patch versions** (e.g., 1.0.1, 1.0.2)
- **Documented in CHANGELOG.md** under "Security"
- **Announced through GitHub Security Advisories**
- **Automatically available through Dependabot**

## Contact

For security-related questions or concerns:
- **Email**: security@sandraschi.dev
- **GitHub**: Create a private security advisory
- **Response Time**: Within 48 hours

## Acknowledgments

We appreciate the security research community for helping keep our software safe. Security researchers who report valid vulnerabilities will be acknowledged in our security advisories (unless they prefer to remain anonymous).

---

**Last Updated**: September 30, 2025
**Version**: 1.1.0
