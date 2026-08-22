# Infinite Network Stats - Home Assistant Integration

A custom Home Assistant integration for monitoring Infinite Network internet usage and statistics.

## Table of Contents

- [Infinite Network Stats - Home Assistant Integration](#infinite-network-stats---home-assistant-integration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Method 1: HACS (Recommended)](#method-1-hacs-recommended)
    - [Method 2: Manual Installation](#method-2-manual-installation)
  - [Configuration](#configuration)
    - [Configuration via YAML (Legacy)](#configuration-via-yaml-legacy)
  - [Setting up a Secondary Account](#setting-up-a-secondary-account)
    - [Security Best Practices](#security-best-practices)
  - [Usage](#usage)
    - [Available Sensors](#available-sensors)
  - [Troubleshooting](#troubleshooting)
    - [Authentication Failed](#authentication-failed)
    - [No Data Updates](#no-data-updates)
    - [Integration Not Found](#integration-not-found)
  - [Support](#support)
    - [Getting Help](#getting-help)
    - [Contributing](#contributing)
    - [Debug Logging](#debug-logging)
  - [License](#license)
  - [Disclaimer](#disclaimer)
  - [Credits](#credits)

## Overview

This integration allows Home Assistant users to monitor their Infinite Network VDSL2 or G.FAST NTU details from their Home Assistant dashboard.

## Features

- Real-time NTU details
- Real-time DSL sync speeds

## Prerequisites

Before installing this integration, ensure you have:

- **Home Assistant** version 2023.1 or later
- An active **Infinite Network** account
- Access to your Infinite Network account credentials
- Created [secondary credentials](#setting-up-a-secondary-account) for this integration to use

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add the repository URL: `https://github.com/pearj/infinite-networks-stats`
6. Select category: "Integration"
7. Click "Add"
8. Search for "Infinite Network Stats" in HACS
9. Click "Download"
10. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [GitHub repository](https://github.com/pearj/infinite-networks-stats)
2. Extract the contents
3. Copy the `custom_components/infinite_network_stats` folder to your Home Assistant `custom_components` directory
   ```bash
   cp -r infinite_network_stats /config/custom_components/
   ```
4. Restart Home Assistant

## Configuration

After installation, configure the integration through the Home Assistant UI:

1. Navigate to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Infinite Network Stats"
4. Enter your configuration details: (don't use your primary because this integration no longer supports MFA)
   - **Username**: Your Infinite Network secondary account username (email address)
   - **Password**: Your Infinite Network secondary account password

### Configuration via YAML (Legacy)

Alternatively, you can configure via `configuration.yaml`:

```yaml
sensor:
  - platform: infinite_network_stats
    username: your_email@example.com
    password: your_password
    scan_interval: 300  # Optional: Update interval in seconds (default: 300)
```

## Setting up a Secondary Account

You need to setup a secondary account with "Tech View" access, so that MFA is not required.

1. **Log in to Infinite Network**
   - Go to the [Infinite Network customer portal](https://portal.infinite.net.au)
   - Sign in with your primary account credentials

2. **Set Up the Secondary Account**
   - Add a **Authorised User** (top menu "Users" button)
   - Complete the **Add User** process
   - Ensure the account has permissions that only contain **Tech View**
   - Find the authorisation email and click the link to **Complete Authorisation**
   - Complete the form including setting a strong, unique password

3. **Use Secondary Account in Home Assistant**
   - Configure Home Assistant with the secondary account credentials
   - This keeps your primary account's security unchanged

### Security Best Practices

1. **Monitor Access**: Regularly check your account activity logs
2. **Use Secondary Account**: Prefer using a secondary account for integrations when possible

## Usage

After successful configuration, the integration will create several sensors in Home Assistant:

### Available Sensors

- `sensor.actual_line_rate_down` - Maximum DSL sync speed - down channel
- `sensor.actual_line_rate_up` - Maximum DSL sync speed - up channel
- `sensor.attainable_line_rate_down` - Actual DSL sync speed - down channel
- `sensor.attainable_line_rate_up` - Actual DSL sync speed - up channel
- `sensor.ntu_cpe_firmware` - NTU firmware version
- `sensor.ntu_cpe_make` - NTU manufacturer
- `sensor.ntu_cpe_model` - NTU model
- `sensor.ntu_cpe_serial` - NTU serial number
- `sensor.ntu_cpe_mac` - NTU MAC address
- `sensor.router_cpu_mac` - Your Router MAC address
- `sensor.service_state` - Service status
- `sensor.last_status_change` - Last time the service change state (up/down)

## Troubleshooting

### Authentication Failed

**Symptoms**: Integration fails to authenticate, shows "Invalid credentials" error.

**Solutions**:
1. Verify your username and password are correct
2. Check that your Infinite Network account is active
3. Try resetting your password on the Infinite Network portal

### No Data Updates

**Symptoms**: Sensors show "unavailable" or don't update.

**Solutions**:
1. Check Home Assistant logs for error messages:
   ```
   Settings → System → Logs
   ```
2. Verify your internet connection is working
3. Check if Infinite Network's portal is accessible
4. Try removing and re-adding the integration
5. Verify the account has permission to view usage data

### Integration Not Found

**Symptoms**: Can't find "Infinite Network Stats" when adding integration.

**Solutions**:
1. Confirm the integration files are in the correct directory:
   ```
   /config/custom_components/infinite_network_stats/
   ```
2. Restart Home Assistant after installation
3. Check for any errors in the logs during startup
4. Verify file permissions are correct

## Support

### Getting Help

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/pearj/infinite-network-stats/issues)
- **Discussions**: Join the conversation on [Home Assistant Community Forum](https://community.home-assistant.io/)
- **Documentation**: Check the [Infinite Network Help Center](https://infinitenetwork.com.au/support)

### Contributing

Contributions are welcome! Please read the [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

### Debug Logging

To enable debug logging for troubleshooting:

```yaml
logger:
  default: info
  logs:
    custom_components.infinite_network_stats: debug
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially affiliated with or endorsed by Infinite Network. Use at your own risk. The developers are not responsible for any issues that may arise from using this integration.

## Credits

Developed by [@pearj](https://github.com/pearj)

---

**Version**: 1.0.0
**Last Updated**: November 2025
**Home Assistant Minimum Version**: 2023.1.0




