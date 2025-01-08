# Screenshot App

A web-based screenshot application that automatically captures screenshots from client devices.

## Features

- Automatic screenshot capture when opening the link
- Configurable capture interval (1-60 seconds)
- Real-time screenshot viewing
- Works on both mobile and desktop browsers
- No installation required on client devices

## Deployment with Cloudflare

1. Create a Cloudflare account at https://dash.cloudflare.com
2. Add your domain to Cloudflare
3. Update your domain's nameservers to Cloudflare's nameservers
4. Create a new Cloudflare Pages project:
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set build output directory: `templates`
   - Add environment variables:
     ```
     PYTHON_VERSION=3.9
     ```

## Environment Variables

Create a `.env` file with:
```
PORT=8080
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

3. Access the app:
- Local: http://localhost:5000
- Network: http://[your-ip]:5000

## Production Deployment

1. Push your code to GitHub
2. Connect to Cloudflare Pages
3. Configure your custom domain
4. Enable Cloudflare SSL/TLS
