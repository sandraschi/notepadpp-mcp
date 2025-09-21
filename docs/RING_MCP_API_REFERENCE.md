# 🏠 Ring MCP Server - API Reference

**Last Updated**: September 20, 2025
**Version**: 2.12.0 (Production)
**Framework**: FastMCP 2.12.3
**Status**: ✅ **PRODUCTION READY**

---

## 🎯 Overview

The Ring MCP Server provides comprehensive integration with Ring security devices through the Message Control Protocol (MCP). This server enables Claude Desktop to control and monitor Ring cameras, doorbells, security systems, and fire safety devices using real Ring API calls.

### 🚀 **Key Features**

- **Real-Time Device Control** - Direct communication with Ring devices
- **Live Streaming** - Access to camera feeds and doorbell video
- **Security System Management** - Arm/disarm, status monitoring, alerts
- **Health Monitoring** - Device connectivity, battery levels, maintenance alerts
- **Event History** - Comprehensive activity logs and visitor tracking

### 🐍 **Python Snippets Usage Guide**

**📖 Complete Guide**: [PYTHON_SNIPPETS_USAGE_GUIDE.md](PYTHON_SNIPPETS_USAGE_GUIDE.md)
- **How to use Python snippets** from this documentation
- **Step-by-step instructions** for creating MCP servers
- **Common issues and solutions** for debugging
- **Best practices** for FastMCP 2.12 development

**Quick Reference:**
- **Copy snippets** to `.py` files
- **Install dependencies**: `pip install fastmcp pydantic`
- **Test with MCPJam**: `mcpjam test --server "python my_server.py"`
- **Debug issues** using comprehensive troubleshooting guide
- **Multi-Transport Support** - Both stdio and HTTP transport options

---

## 📋 Prerequisites

### Required Environment Variables

```bash
# Ring API Credentials (choose one method)
RING_USERNAME=your_ring_email@example.com
RING_PASSWORD=your_ring_password

# OR
RING_TOKEN=your_oauth_token

# Server Configuration
HOST=0.0.0.0  # Default: 0.0.0.0
PORT=8123     # Default: 8123 (non-standard to avoid conflicts)

# Optional: Token Storage
RING_MCP_TOKEN_PATH=/path/to/tokens  # Default: ~/.ring-mcp/tokens.enc
```

### Installation

```bash
pip install fastmcp>=2.12.0
pip install python-ring-doorbell>=0.8.0
pip install aiofiles cryptography
```

---

## 🔐 Authentication

### OAuth 2.0 Flow

The server supports multiple authentication methods:

1. **Username/Password** (Recommended for initial setup)
2. **OAuth Token** (For production deployments)
3. **Token Refresh** (Automatic token renewal)

### Token Management

- **Automatic Storage**: Tokens are encrypted and stored locally
- **Refresh Logic**: Tokens are automatically refreshed before expiration
- **Secure Storage**: Uses AES encryption with PBKDF2 key derivation

---

## 🛠️ Available Tools

### 📹 Camera Management Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_camera_status` | Get comprehensive status of all Ring security cameras | None |
| `stream_all_cameras` | Start live streams from all available Ring cameras | None |

**Example Usage:**
```python
# Get camera status
result = await get_camera_status()
print(f"Total cameras: {result['total_cameras']}")
print(f"Online cameras: {result['online_cameras']}")

# Start camera streams
streams = await stream_all_cameras()
for stream in streams['camera_streams']:
    print(f"Camera: {stream['camera_name']} - Stream: {stream['stream_url']}")
```

### 🔔 Doorbell Management Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_doorbell_live_stream` | Get live video stream from Ring doorbell | `doorbell_id`, `quality`, `duration_seconds` |
| `answer_doorbell_call` | Answer an active doorbell call with two-way audio | `doorbell_id`, `enable_two_way_audio`, `auto_record` |
| `get_visitor_history` | Get comprehensive visitor history with snapshots | `hours`, `include_snapshots`, `motion_only` |
| `configure_motion_detection` | Configure motion detection settings | `doorbell_id`, `sensitivity`, `motion_zones`, `smart_alerts` |

**Example Usage:**
```python
# Get live doorbell stream
stream = await get_doorbell_live_stream(quality="high", duration_seconds=60)
print(f"Doorbell stream URL: {stream['stream_url']}")

# Configure motion detection
config = await configure_motion_detection(
    sensitivity="high",
    smart_alerts=True,
    motion_zones=[{"x": 0.2, "y": 0.2, "width": 0.6, "height": 0.6}]
)
```

### 🔒 Security System Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_security_system_status` | Get comprehensive status of the entire Ring security system | None |
| `arm_security_system` | Arm the Ring security system with specified mode | `mode`, `bypass_sensors`, `delay_minutes` |
| `disarm_security_system` | Disarm the Ring security system safely | `force_disarm`, `disarm_code` |
| `get_security_history` | Get comprehensive security system history | `hours`, `event_types`, `include_video` |

**Security Modes:**
- `home` - Perimeter protection, interior motion off
- `away` - Full perimeter and interior protection
- `disarmed` - All protection disabled

**Example Usage:**
```python
# Check security system status
status = await get_security_system_status()
print(f"System status: {status['system_status']['mode']}")
print(f"Armed: {status['system_status']['armed']}")

# Arm system for away mode
arm_result = await arm_security_system("away", delay_minutes=30)
print(f"Arming result: {arm_result['success']}")

# Get security history
history = await get_security_history(hours=24)
print(f"Recent events: {len(history['events'])}")
```

### 🚨 Fire Safety Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_fire_alarm_status` | Get comprehensive status of all fire alarms and smoke detectors | None |
| `test_fire_safety_system` | Perform comprehensive test of fire safety system | None |

**Example Usage:**
```python
# Check fire alarm status
fire_status = await get_fire_alarm_status()
print(f"Total alarms: {fire_status['total_alarms']}")
print(f"System health: {fire_status['system_health']}")

# Test fire safety system
test_result = await test_fire_safety_system()
print(f"Test status: {test_result['overall_status']}")
```

### 📊 Monitoring Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `monitor_system_health` | Perform comprehensive health check of entire Ring security system | None |
| `get_real_time_activity` | Get real-time activity feed from all Ring devices | None |

**Example Usage:**
```python
# System health check
health = await monitor_system_health()
print(f"Overall health score: {health['overall_health_score']}")
print(f"Devices with issues: {health['devices_with_issues']}")

# Real-time activity
activity = await get_real_time_activity()
print(f"Live activities: {len(activity['live_activity'])}")
```

### 🤖 Automation Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_security_automation` | Create custom security automation rule | `trigger_type`, `trigger_conditions`, `response_actions`, `automation_name` |
| `trigger_emergency_protocol` | Activate emergency security protocol | None |
| `schedule_security_modes` | Configure time-based security mode scheduling | `schedule_config`, `timezone` |

**Trigger Types:**
- `motion` - Motion detection events
- `doorbell` - Doorbell press events
- `schedule` - Time-based triggers
- `alarm` - Security alarm events

**Example Usage:**
```python
# Create motion-triggered automation
automation = await create_security_automation(
    trigger_type="motion",
    trigger_conditions={"device_type": "camera"},
    response_actions=[{"action": "record_video", "duration": 30}],
    automation_name="Front Door Motion Recording"
)

# Schedule security modes
schedule = await schedule_security_modes({
    "modes": ["away", "home"],
    "timeframes": [
        {"start": "08:00", "end": "17:00", "mode": "away", "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]},
        {"start": "17:00", "end": "08:00", "mode": "home", "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]}
    ]
})
```

---

## 📡 HTTP API Endpoints

### Server Configuration

```bash
# Start HTTP server
python -m ring_mcp.server

# Server will be available at:
# http://localhost:8000
```

### MCP Transport

The server supports both transport methods:

1. **stdio** (Default for Claude Desktop)
2. **HTTP** (For web clients and API access)

### Tool Discovery

```bash
# List available tools via HTTP
curl http://localhost:8000/tools

# Call a specific tool
curl -X POST http://localhost:8000/tools/get_camera_status \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## ⚠️ Error Handling

### Exception Types

| Exception | Description | HTTP Status |
|-----------|-------------|-------------|
| `AuthenticationError` | Invalid credentials or expired token | 401 |
| `DeviceNotFoundError` | Device not found or inaccessible | 404 |
| `RateLimitError` | API rate limit exceeded | 429 |
| `StreamingError` | Video streaming failed | 500 |
| `RingError` | General Ring API error | 500 |

### Error Response Format

```json
{
  "success": false,
  "error": "Error description",
  "error_type": "authentication|device|rate_limit|streaming|general",
  "timestamp": "2025-01-20T10:30:00Z",
  "request_id": "req-123456"
}
```

---

## 📊 Monitoring & Metrics

### Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `ring_api_calls_total` | Counter | Total Ring API calls |
| `ring_api_duration_seconds` | Histogram | API call duration |
| `ring_device_status` | Gauge | Device status |
| `ring_device_battery` | Gauge | Battery levels |
| `ring_device_online` | Gauge | Device connectivity |
| `ring_security_armed` | Gauge | Security system status |
| `ring_tool_calls_total` | Counter | MCP tool calls |
| `ring_tool_duration_seconds` | Histogram | Tool execution time |

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:30:00Z",
  "version": "2.12.0",
  "uptime": 3600,
  "active_connections": 1
}
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RING_USERNAME` | - | Ring account email |
| `RING_PASSWORD` | - | Ring account password |
| `RING_TOKEN` | - | OAuth access token |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8123` | Server port (non-standard to avoid conflicts) |
| `RING_MCP_TOKEN_PATH` | `~/.ring-mcp/tokens.enc` | Token storage path |
| `RING_MCP_ENCRYPTION_KEY` | Auto-generated | Encryption key |
| `RING_MCP_ENCRYPTION_SALT` | Auto-generated | Encryption salt |

### Advanced Configuration

```python
# Custom token storage path
RING_MCP_TOKEN_PATH=/secure/path/tokens.enc

# Custom encryption
RING_MCP_ENCRYPTION_KEY=your_base64_key_here
RING_MCP_ENCRYPTION_SALT=your_base64_salt_here
```

---

## 📝 Usage Examples

### Basic Device Discovery

```python
# Get all devices
devices = await get_devices()
for device in devices['devices']:
    print(f"{device['name']} ({device['type']}) - {device['online']}")

# Get specific device details
device = await get_device_details("device_123")
print(f"Battery: {device['battery_life']}%")
```

### Security Monitoring

```python
# Continuous monitoring loop
while True:
    health = await monitor_system_health()
    if health['overall_health_score'] < 80:
        print(f"⚠️ System health degraded: {health['overall_health_score']}")
        # Send alert or take corrective action

    activity = await get_real_time_activity()
    if activity['live_activity']:
        print(f"📊 Recent activity: {len(activity['live_activity'])} events")

    await asyncio.sleep(60)  # Check every minute
```

### Emergency Response

```python
# Emergency protocol activation
emergency = await trigger_emergency_protocol()
if emergency['success']:
    print("🚨 Emergency protocol activated")
    for measure in emergency['activated_measures']:
        print(f"✅ {measure}")
else:
    print(f"❌ Emergency activation failed: {emergency['error']}")
```

### Camera Surveillance

```python
# Multi-camera monitoring
streams = await stream_all_cameras()
for stream in streams['camera_streams']:
    print(f"🎥 {stream['camera_name']}: {stream['status']}")
    # Process stream URL for monitoring dashboard
```

---

## 🚨 Security Considerations

### Authentication Security

- **Never commit credentials** to version control
- **Use environment variables** for all sensitive data
- **Enable token refresh** for production deployments
- **Monitor token usage** through logging

### Network Security

- **Use HTTPS** for production deployments
- **Restrict API access** to trusted networks
- **Monitor rate limits** to prevent abuse
- **Implement proper firewall rules**

### Data Privacy

- **Video streams** are accessed directly from Ring
- **Event data** is cached locally for performance
- **No permanent storage** of sensitive video content
- **GDPR compliance** through minimal data retention

---

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Failed**
   ```bash
   # Check credentials
   export RING_USERNAME=your_email@example.com
   export RING_PASSWORD=your_password

   # Or use token
   export RING_TOKEN=your_oauth_token
   ```

2. **Device Not Found**
   ```bash
   # Verify device connectivity
   # Check Ring app for device status
   # Ensure proper permissions in Ring account
   ```

3. **Rate Limiting**
   ```bash
   # Implement exponential backoff
   # Monitor API call frequency
   # Use caching for non-critical data
   ```

### Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable FastMCP debug mode
export FASTMCP_DEBUG=1
```

---

## 📚 References & Resources

- [FastMCP Documentation](https://fastmcp.dev)
- [Ring API Documentation](https://developer.ring.com)
- [Python Ring Doorbell Library](https://github.com/tchellomello/python-ring-doorbell)
- [Message Control Protocol Specification](https://spec.modelcontextprotocol.io)

---

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/ring-mcp.git
cd ring-mcp

# Install dependencies
pip install -e .

# Run tests
python -m pytest

# Start development server
python -m ring_mcp.server
```

### Code Standards

- **Type hints** required for all functions
- **Docstrings** required for all public APIs
- **Error handling** with proper exception types
- **Logging** with structured format
- **Tests** for all new functionality

---

**🔗 For more information, see:**
- [Technical Architecture](TECHNICAL_ARCHITECTURE.md)
- [Development Guidelines](AI_DEVELOPMENT_RULES.md)
- [Troubleshooting Guide](TROUBLESHOOTING_FASTMCP_2.12.md)

---

*This API reference is automatically generated and kept in sync with the implementation. Last updated: September 20, 2025*
