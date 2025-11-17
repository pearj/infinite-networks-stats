# Infinite Network Stats - Home Assistant Integration

A custom Home Assistant integration for monitoring Infinite Network internet usage and statistics.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Acquiring the MFA Shared Secret](#acquiring-the-mfa-shared-secret)
  - [Option 1: Using Your Primary Account](#option-1-using-your-primary-account)
  - [Option 2: Creating a Secondary Account](#option-2-creating-a-secondary-account-recommended)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

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
- **MFA Shared Secret** (see detailed instructions below)

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add the repository URL: `https://github.com/pearj/infinite-network-stats`
6. Select category: "Integration"
7. Click "Add"
8. Search for "Infinite Network Stats" in HACS
9. Click "Install"
10. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [GitHub repository](https://github.com/pearj/infinite-network-stats)
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
4. Enter your configuration details:
   - **Username**: Your Infinite Network account username (email address)
   - **Password**: Your Infinite Network account password
   - **MFA Shared Secret**: The TOTP shared secret (see below for instructions)

### Configuration via YAML (Legacy)

Alternatively, you can configure via `configuration.yaml`:

```yaml
sensor:
  - platform: infinite_network_stats
    username: your_email@example.com
    password: your_password
    mfa_secret: YOUR_MFA_SHARED_SECRET
    scan_interval: 300  # Optional: Update interval in seconds (default: 300)
```

## Acquiring the MFA Shared Secret

**IMPORTANT:** The MFA Shared Secret is NOT the 6-digit code from your authenticator app. It is the secret key used to generate those codes.

Infinite Network requires Multi-Factor Authentication (MFA) for account access. You have two options for obtaining the required MFA shared secret:

### Option 1: Using Your Primary Account

1. **Retrieve your MFA Secret from your Password vault or similar**

2. **Use the Secret in Home Assistant**
   - Use the captured MFA Shared Secret in your Home Assistant configuration
   - Format: Usually 16 characters, may contain uppercase letters and numbers (e.g., `JBSWY3DPEHPK3PXP`)

### Option 2: Creating a Secondary Account (Recommended)

✅ **Recommended:** This method is safer as it doesn't require modifying your primary account's security settings.

1. **Log in to Infinite Network**
   - Go to the [Infinite Network customer portal](https://portal.infinite.net.au)
   - Sign in with your primary account credentials

2. **Set Up the Secondary Account**
   - Add a **Authorised User** (left hand side menu)
   - Complete the **Authorise New Individual** process
   - Ensure the account has permissions of at least **Technical View**
   - Find the authorisation email and click the link to **Complete Authorisation**
   - Complete the form including setting a strong, unique password

3. **Enable MFA on Secondary Account**
   - Log in to the Infinite Network portal with the secondary account
   - Click **Set up two factor authentication**
   - Scan the QR code using a password vault app that enables you to retrieve the MFA Shared Secret (Laspass Authenticator or 1Password Authenticator)

4. **Capture the MFA Shared Secret**
   - Look for "Manual Entry Key" or "Secret Key" in your password vault
   - Copy this secret (e.g., `JBSWY3DPEHPK3PXP`)
   - Save it securely - you'll need this for Home Assistant

5. **Complete MFA Setup**
   - Enter the 6-digit verification code

6. **Use Secondary Account in Home Assistant**
   - Configure Home Assistant with the secondary account credentials
   - Use the secondary account's MFA Shared Secret
   - This keeps your primary account's security unchanged

### Understanding the MFA Shared Secret Format

The MFA Shared Secret (also called TOTP secret key) is typically:
- **Length**: 16-32 characters
- **Format**: Base32 encoded (A-Z, 2-7)
- **Example**: `JBSWY3DPEHPK3PXP` or `KRMVATZVJRGXI3LHMV2GS4Y=`
- **Not**: The 6-digit code from your authenticator app
- **Not**: Your password or username

### Security Best Practices

1. **Store Securely**: Keep your MFA shared secret in a password manager
2. **Never Share**: Don't share your MFA secret with anyone
3. **Backup**: Save backup codes provided during MFA setup
4. **Monitor Access**: Regularly check your account activity logs
5. **Use Secondary Account**: Prefer using a secondary account for integrations when possible

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
2. Ensure you're using the MFA Shared Secret (not the 6-digit code)
3. Check that your Infinite Network account is active
4. Try resetting your password on the Infinite Network portal

### MFA Token Invalid

**Symptoms**: Error message about invalid MFA token or TOTP.

**Solutions**:
1. Verify you copied the complete MFA Shared Secret (no spaces or extra characters)
2. Check the secret is in Base32 format (A-Z, 2-7)
3. Ensure your Home Assistant server's clock is synchronized (NTP)
4. Try reconfiguring MFA on your Infinite Network account

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




