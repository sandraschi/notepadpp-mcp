# 🌐 Universal Multi-Server MCP Monitoring & Visual Analytics

**Advanced Grafana Integration Guide for ALL MCP Servers**
**Pictorial Information, Multi-Server Architecture, Video Analytics**

---

## 🎯 **Works with ALL Your MCP Servers!**

This guide applies to **all 20+ MCP servers** in your collection:

- ✅ **nest-protect-mcp** - Nest Protect smoke/CO detector monitoring
- ✅ **tapo-camera-mcp** - TP-Link Tapo camera integration
- ✅ **ring-mcp** - Ring security system monitoring
- ✅ **homekit-mcp** - Apple HomeKit device control
- ✅ **smartthings-mcp** - Samsung SmartThings integration
- ✅ **And all others** - Any MCP server can use this system!

**Copy this monitoring setup to any MCP server!** 📁➡️🔄

---

## 📸 **Question 1: Can Grafana Show Pictorial/Video Information?**

**YES! Absolutely!** Grafana has excellent support for visual content, including:

### **🎯 Visual Display Options for ALL MCP Servers**

#### **1. Nest Protect Visual Monitoring**
```json
{
  "type": "image",
  "title": "Nest Protect Status",
  "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
  "targets": [{
    "datasource": { "type": "loki", "uid": "loki" },
    "expr": "{service=\"nest-protect\"} |~ \"smoke_alarm\" | json | line_format \"{{.status_image}}\"",
    "refId": "A"
  }],
  "options": {
    "url": "http://localhost:8124/status/nest_protect_123.jpg",
    "alt": "Nest Protect alarm status"
  }
}
```

#### **2. Tapo Camera Visual Feed**
```python
# tapo-camera-mcp server
logger.warning("Motion detected",
    camera_id="living_room",
    image_url="http://localhost:8125/stills/tapo_motion_12345.jpg",
    confidence=0.92,
    description="Person in living room"
)
```

#### **3. Ring Camera Integration**
```python
# ring-mcp server
logger.info("Person at door detected",
    camera_id="front_door",
    image_url="http://localhost:8123/stills/alert_12345.jpg",
    confidence=0.85,
    description="Person detected at front door"
)
```

#### **4. Base64 Image Annotations (Universal)**
```python
import base64

# Any MCP server can embed images
def log_with_image(service_name: str, device_id: str, image_path: str):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()

    logger.warning(f"{service_name} alert",
        device_id=device_id,
        image_data=image_data,
        event_type="visual_alert"
    )
```

### **🚨 Security Camera Alert Example**

#### **Detection → Image → Alert Flow**
```python
# In Ring MCP server - motion_tools.py
async def detect_motion(device_id: str) -> dict:
    """Detect motion and capture image for Grafana display."""

    # Detect motion using Ring API
    motion_detected = await ring_client.detect_motion(device_id)

    if motion_detected:
        # Capture video still
        still_image = await ring_client.get_video_still(device_id)

        # Save temporarily for Grafana access
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_{device_id}_{timestamp}.jpg"
        image_path = f"/tmp/stills/{filename}"

        with open(image_path, 'wb') as f:
            f.write(still_image)

        # Log with image URL for Grafana
        logger.warning("Motion detected",
            device_id=device_id,
            image_url=f"http://localhost:8123/stills/{filename}",
            confidence=0.87,
            event_type="motion_detection"
        )

        return {
            "detected": True,
            "image_url": f"http://localhost:8123/stills/{filename}",
            "confidence": 0.87
        }

    return {"detected": False}
```

#### **Grafana Dashboard Display**
- **Image Panel**: Shows the captured still
- **Alert**: Includes image URL in notification
- **Annotation**: Marks the detection event on timeline
- **Correlation**: Links to security system logs

---

## 🌐 **Question 2: Can Multiple MCP Servers Use Same Stack?**

**YES! The monitoring stack is designed for multi-tenancy!**

### **📊 Multi-Server Architecture for ALL Your MCP Servers**

```
All 20+ MCP Servers → Shared Monitoring Stack → Unified Grafana
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ nest-protect    │    │ tapo-camera     │    │ ring-mcp        │
│ Server          │    │ Server          │    │ Server          │
│                 │    │                 │    │                 │
│ • Smoke/CO      │    │ • Camera feeds  │    │ • Security      │
│ • Battery       │    │ • Motion detect │    │ • Doorbells     │
│ • Air quality   │    │ • Video stills  │    │ • Alarms        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ homekit-mcp     │    │ smartthings-mcp │    │ ...and 15 more │
│ Server          │    │ Server          │    │ Servers         │
│                 │    │                 │    │                 │
│ • Apple devices │    │ • Samsung dev   │    │ • Various IoT   │
│ • Lights/Sensors│    │ • Hub control   │    │ • integrations  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │ Shared Stack    │
                    │                 │
                    │ • Loki          │
                    │ • Prometheus    │
                    │ • Grafana       │
                    │ • Promtail      │
                    └─────────────────┘
```

### **🔧 Configuration for Multi-Server**

#### **1. Promtail Configuration for ALL MCP Servers**
```yaml
# monitoring/promtail/promtail-config.yml
scrape_configs:
  # Universal multi-server configuration
  - job_name: multi-mcp-logs
    static_configs:
      - targets:
          - localhost
        labels:
          service: "{{inventory_hostname}}"  # Server identifier
          log_type: application
          environment: production
          team: home-automation

  # Specific configurations for each MCP server
  - job_name: nest-protect-logs
    static_configs:
      - targets:
          - localhost
        labels:
          service: "nest-protect-mcp"
          device_type: "smoke_detector|co_detector"
          location: "home"
          manufacturer: "nest"
          __path__: ./logs/nest_protect_*.log
    pipeline_stages:
      - json:
          expressions:
            device_id: device_id
            battery_level: battery_level
            smoke_level: smoke_level
            co_level: co_level
            status: status

  - job_name: tapo-camera-logs
    static_configs:
      - targets:
          - localhost
        labels:
          service: "tapo-camera-mcp"
          device_type: "camera"
          location: "home"
          manufacturer: "tp-link"
          __path__: ./logs/tapo_camera_*.log
    pipeline_stages:
      - json:
          expressions:
            camera_id: camera_id
            motion_detected: motion_detected
            image_url: image_url
            confidence: confidence

  - job_name: ring-mcp-logs
    static_configs:
      - targets:
          - localhost
        labels:
          service: "ring-mcp-server"
          device_type: "camera|doorbell|security"
          location: "home"
          manufacturer: "ring"
          __path__: ./logs/ring_mcp_*.log

  - job_name: homekit-logs
    static_configs:
      - targets:
          - localhost
        labels:
          service: "homekit-mcp"
          device_type: "light|sensor|appliance"
          location: "home"
          manufacturer: "apple"
          __path__: ./logs/homekit_*.log
```

#### **2. Prometheus Configuration**
```yaml
# monitoring/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'mcp-servers'
    static_configs:
      - targets: ['ring-mcp:8123', 'homekit:8124', 'smartthings:8125']
    labels:
      service: mcp-server
      instance: '{{ $labels.instance }}'
    metrics_path: '/metrics'

  - job_name: 'ring-mcp-metrics'
    static_configs:
      - targets: ['ring-mcp:8123']
    labels:
      service: ring-mcp-server
      device_category: security
```

#### **3. Grafana Data Sources**
```yaml
# monitoring/grafana/provisioning/datasources/loki.yml
datasources:
  - name: Loki (Multi-Server)
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
    editable: true

  - name: Prometheus (Multi-Server)
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: false
    editable: true
```

### **📈 Multi-Server Benefits**

#### **1. Centralized Logging**
- **All servers** log to same Loki instance
- **Unified search** across all services
- **Correlated events** between different systems
- **Shared retention** policies

#### **2. Unified Dashboards**
- **Single pane of glass** for all home automation
- **Cross-service correlations** (Ring + HomeKit + SmartThings)
- **Shared alerting rules** and notification channels
- **Comparative analytics** between services

#### **3. Cost Effective**
- **Single monitoring stack** instead of multiple
- **Shared resources** (CPU, memory, storage)
- **Centralized management** and maintenance
- **Unified backup** and disaster recovery

#### **4. Advanced Analytics**
```python
# Cross-service event correlation
logger.info("Security event",
    source="ring-mcp",
    target="homekit",
    event_type="motion_to_light",
    description="Ring camera motion triggered HomeKit lights"
)

# Multi-server metrics aggregation
logger.info("System health",
    services=["ring-mcp", "homekit", "smartthings"],
    status="all_healthy",
    response_time=245
)
```

---

## 🎯 **Implementation Example: Security Camera with Images**

### **1. Ring MCP Server Setup**
```python
# ring_mcp/tools/camera_tools.py
async def capture_motion_image(device_id: str, confidence: float) -> str:
    """Capture image when motion is detected."""

    # Get video still from Ring camera
    image_data = await ring_client.get_video_still(device_id)

    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"motion_{device_id}_{timestamp}.jpg"
    filepath = f"/tmp/stills/{filename}"

    with open(filepath, 'wb') as f:
        f.write(image_data)

    # Make available via HTTP
    image_url = f"http://localhost:8123/stills/{filename}"

    # Log with image URL for Grafana
    logger.warning("Motion detected with image",
        device_id=device_id,
        image_url=image_url,
        confidence=confidence,
        filename=filename,
        service="ring-mcp"
    )

    return image_url
```

### **2. Nest Protect Visual Status**
```python
# nest-protect-mcp/tools/smoke_detector_tools.py
def log_protect_status(device_id: str, status: str, battery_level: int):
    """Log Nest Protect status with visual indicators."""

    # Create status image showing alarm state
    status_colors = {
        "ok": "green",
        "warning": "yellow",
        "emergency": "red"
    }

    color = status_colors.get(status, "gray")
    status_image = create_status_image(device_id, status, color, battery_level)

    # Save status image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"status_{device_id}_{timestamp}.png"
    filepath = f"/tmp/status/{filename}"

    status_image.save(filepath)

    # Log with image for Grafana
    logger.info("Nest Protect status updated",
        device_id=device_id,
        status=status,
        battery_level=battery_level,
        status_image=f"http://localhost:8124/status/{filename}",
        service="nest-protect-mcp"
    )
```

### **3. Tapo Camera Motion Detection**
```python
# tapo-camera-mcp/tools/motion_tools.py
async def detect_and_log_motion(camera_id: str) -> dict:
    """Detect motion and log with visual evidence."""

    # Check for motion
    motion_detected = await tapo_client.detect_motion(camera_id)

    if motion_detected:
        # Capture image from camera
        image_data = await tapo_client.get_snapshot(camera_id)

        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_{camera_id}_{timestamp}.jpg"
        filepath = f"/tmp/motion/{filename}"

        with open(filepath, 'wb') as f:
            f.write(image_data)

        # Make available and log
        image_url = f"http://localhost:8125/motion/{filename}"

        logger.warning("Motion detected with image",
            camera_id=camera_id,
            image_url=image_url,
            confidence=0.89,
            service="tapo-camera-mcp"
        )

        return {
            "detected": True,
            "image_url": image_url,
            "confidence": 0.89
        }

    return {"detected": False}
```

### **2. Grafana Dashboard**
```json
{
  "title": "Security Camera - Live Feed",
  "panels": [
    {
      "type": "image",
      "title": "Front Door Camera",
      "gridPos": { "h": 8, "w": 12 },
      "targets": [{
        "expr": "{service=\"ring-mcp\"} |~ \"motion_detected\" | json | line_format \"{{.image_url}}\" | last()",
        "refId": "A"
      }],
      "options": {
        "url": "http://localhost:8123/stills/front_door_latest.jpg",
        "alt": "Front door camera feed"
      }
    }
  ]
}
```

### **3. Alert Configuration**
```json
{
  "name": "Security Camera Motion Alert",
  "condition": "B",
  "for": "0s",
  "rules": [
    {
      "type": "query",
      "query": "A",
      "evaluator": { "type": "gt", "params": [0] }
    }
  ],
  "annotations": {
    "summary": "Motion detected at front door",
    "description": "Camera captured image: {{ $values.A }}",
    "image_url": "{{ $values.A }}"
  }
}
```

---

## 📊 **Multi-Server Dashboard Examples**

### **1. Unified Home Automation Dashboard**
- **All server logs** in single view
- **Cross-service correlations** (Ring triggers HomeKit)
- **System-wide health** monitoring
- **Shared alerting** across all services

### **2. Service-Specific Dashboards**
- **Ring MCP**: Camera feeds, security events
- **HomeKit**: Light control, sensor data
- **SmartThings**: Device status, hub connectivity

### **3. Analytics Dashboard**
- **Usage patterns** across all services
- **Performance comparisons** between servers
- **Error correlation** between services
- **Resource utilization** trends

---

## 🚀 **Getting Started**

### **1. Start Monitoring Stack**
```bash
cd monitoring
docker-compose up -d
```

### **2. Configure Multiple Servers**
```bash
# Server 1 - Ring MCP
python -m ring_mcp

# Server 2 - HomeKit MCP
python -m homekit_mcp

# Server 3 - SmartThings MCP
python -m smartthings_mcp
```

### **3. Access Grafana**
- **URL**: http://localhost:3000
- **Dashboards**:
  - "Multi-Server MCP Monitoring"
  - "Ring Security Camera - Motion & Video"
  - Individual service dashboards

### **4. Example Multi-Server Log**
```json
{
  "timestamp": "2025-01-20T10:30:45.123Z",
  "level": "INFO",
  "service": "ring-mcp-server",
  "device_id": "front_door_camera",
  "event": "motion_detected",
  "confidence": 0.85,
  "image_url": "http://localhost:8123/stills/motion_12345.jpg",
  "correlated_services": ["homekit-server", "smartthings-server"],
  "actions_taken": ["lights_activated", "recording_started"]
}
```

---

## 🎯 **This is Production-Ready!**

### **✅ Pictorial Information**
- **Image panels** display camera stills
- **Base64 images** in log annotations
- **Dynamic URLs** for real-time feeds
- **Alert integration** with image attachments

### **✅ Multi-Server Support**
- **Shared monitoring stack** for cost efficiency
- **Proper labeling** for service separation
- **Cross-service correlation** for advanced analytics
- **Unified dashboards** with comprehensive visibility

**Ready for complex home automation setups with visual monitoring!** 🏠📹🔍

---

## 📋 **Copy to Your Other MCP Servers**

### **For nest-protect-mcp:**
```bash
# Copy monitoring folder to nest-protect-mcp
cp -r ring-mcp/monitoring nest-protect-mcp/

# Update promtail config
sed -i 's/ring-mcp/nest-protect-mcp/g' nest-protect-mcp/monitoring/promtail/promtail-config.yml
sed -i 's/camera|doorbell|security/smoke_detector|co_detector/g' nest-protect-mcp/monitoring/promtail/promtail-config.yml
```

### **For tapo-camera-mcp:**
```bash
# Copy monitoring folder to tapo-camera-mcp
cp -r ring-mcp/monitoring tapo-camera-mcp/

# Update for camera-specific labels
sed -i 's/ring-mcp/tapo-camera-mcp/g' tapo-camera-mcp/monitoring/promtail/promtail-config.yml
sed -i 's/camera|doorbell|security/camera/g' tapo-camera-mcp/monitoring/promtail/promtail-config.yml
```

### **For Any MCP Server:**
1. **Copy** `monitoring/` folder to your MCP server repo
2. **Update** service name in `promtail-config.yml`
3. **Update** device types and labels as needed
4. **Start** monitoring stack: `docker-compose up -d`
5. **Access** unified Grafana at `http://localhost:3000`

---

## 🎯 **Universal Benefits for All 20+ MCP Servers**

| Server | Visual Features | Multi-Server Benefits | Logs → Grafana |
|--------|-----------------|----------------------|---------------|
| **nest-protect-mcp** | Status indicators, battery levels | Smoke/CO correlation with cameras | Alarm events, battery warnings |
| **tapo-camera-mcp** | Motion stills, live feeds | Integration with security systems | Motion detection, video events |
| **ring-mcp** | Camera feeds, security alerts | Unified home security view | Device status, alarm events |
| **homekit-mcp** | Device status icons | Light/camera coordination | Automation triggers, device sync |
| **smartthings-mcp** | Hub status, sensor graphs | Cross-platform device control | Hub connectivity, device events |
| **And 15+ more** | Custom dashboards per server | Unified monitoring view | Structured logs for all |

**This monitoring system scales to your entire MCP server collection!** 🚀📊🔍

---

## 🔥 **Advanced: Cross-Server Event Correlation**

### **Nest Protect + Ring Camera Integration**
```python
# nest-protect-mcp detects alarm
logger.warning("Smoke detected",
    device_id="kitchen_protect",
    smoke_level=2.1,
    alarm_active=True,
    correlated_cameras=["front_door", "kitchen"],
    service="nest-protect-mcp"
)

# ring-mcp responds
logger.info("Recording triggered by smoke alarm",
    camera_id="kitchen",
    trigger_source="nest-protect-alarm",
    recording_duration=30,
    service="ring-mcp"
)
```

### **Tapo Camera + HomeKit Light Integration**
```python
# tapo-camera-mcp detects motion
logger.info("Motion detected in living room",
    camera_id="living_room",
    confidence=0.87,
    trigger_lights=True,
    service="tapo-camera-mcp"
)

# homekit-mcp activates lights
logger.info("Lights activated by camera motion",
    light_group="living_room",
    brightness=100,
    correlated_camera="living_room",
    service="homekit-mcp"
)
```

### **Grafana Cross-Service Dashboard**
- **Correlated Events**: Link smoke alarms to camera recordings
- **Causal Analysis**: Motion detection triggers light activation
- **Timeline View**: See events across all servers chronologically
- **Alert Correlation**: Multi-server alert patterns

**This creates a unified smart home monitoring system!** 🏠🤖🔗
