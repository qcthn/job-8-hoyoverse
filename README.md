# Hoyoverse Account Management Tools

This repository contains two independent tools for managing Hoyoverse game accounts:

1. Automatic Account Registration Tool
2. Phone Number Verification Tool

## Features

### 1. Account Registration Tool (main3_new.py)

- Automated registration of Hoyoverse game accounts
- Email alias generation
- Proxy management for distributed access
- CAPTCHA solving integration
- Email verification handling
- Robust error handling and retry mechanisms
- Progress tracking and logging
- CSV export of registration results

### 2. Phone Verification Tool (main_new_tool2.py)

- Automated phone number verification for existing Hoyoverse accounts
- Multi-country phone number acquisition (supports Poland, England, Russia, and more)
- SMS code verification
- Proxy rotation system
- CAPTCHA solving integration
- Detailed logging and progress tracking
- CSV export of verification results

## Prerequisites

- Python 3.10 or higher
- Chrome WebDriver
- Active internet connection
- Required API keys:
  - 2captcha API key for CAPTCHA solving
  - 5sim API key for phone number services
  - Proxy service API key(s)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd hoyoverse-tools
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Required API Keys

- 2captcha API key for CAPTCHA solving
- 5sim API key for phone verification
- Proxy service API keys

### Email Configuration

- Gmail account with App Password enabled for email verification

## Usage

### Account Registration Tool

1. Start the registration tool:

```bash
python main3_new.py
```

2. Access the web interface at `http://localhost:8080`

3. Upload your configuration file containing:

- Email address
- Email app password
- Number of accounts to register
- API keys

4. Monitor progress through the web interface

### Phone Verification Tool

1. Start the verification tool:

```bash
python main_new_tool2.py
```

2. Access the web interface at `http://localhost:8080`

3. Upload your CSV/Excel file containing:

- Email
- Password
- App Password

4. Enter required API keys:

- Proxy API keys
- CAPTCHA API key
- Phone service API key

5. Monitor verification progress through the web interface

## File Formats

### Registration Input Format

```csv
Email,App Password
example@gmail.com,your_app_password
```

### Phone Verification Input Format

```csv
Email,Password,App Password
account@email.com,account_password,gmail_app_password
```

## Output

Both tools generate:

- Real-time progress updates
- Detailed logs
- Downloadable CSV results
- Success/failure statistics

## Error Handling

The tools include comprehensive error handling for:

- Network issues
- CAPTCHA failures
- SMS verification timeouts
- Proxy errors
- Email verification failures
- API rate limits

## Security Considerations

- Store API keys securely
- Use proxy rotation to avoid IP bans
- Implement reasonable delays between requests
- Handle sensitive data appropriately

## Limitations

- Depends on external services (2captcha, 5sim)
- Subject to Hoyoverse's terms of service
- Rate limits may apply
- Phone number availability varies by country

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]

## Disclaimer

This tool is for educational purposes only. Please ensure compliance with Hoyoverse's terms of service and relevant regulations when using these tools.
