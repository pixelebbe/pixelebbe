# Pixelebbe Installation Guide

## Prerequisites

This guide assumes you have a computer system that meets the following requirements:

* Operating System: Ubuntu 22.04 LTS, 24.04 or similar
* Python 3.9 or newer
* Installed: APT and Git

## System Setup

### Create System User

First, create a system user for Pixelebbe:

```bash
sudo adduser pixelebbe
sudo usermod -G www-data pixelebbe
sudo mkdir /var/pixelebbe
sudo chown pixelebbe /var/pixelebbe -R
sudo chgrp www-data /var/pixelebbe -R
```

### Install Dependencies

Update package sources and install necessary dependencies:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx
```

## Database Setup

Install and secure MariaDB:

```bash
sudo apt install mariadb-server libmariadb3 libmariadb-dev
sudo mysql_secure_installation
```

Make sure to note down the password you set, as it will be needed for the Pixelebbe configuration.

Verify MariaDB is running:

```bash
sudo systemctl status mariadb
```

Create a database for Pixelebbe:

```bash
sudo mariadb
```

In the MariaDB console:

```sql
CREATE DATABASE pixelebbe;
CREATE USER 'pixelebbe'@'localhost' IDENTIFIED BY '<your_password>';
GRANT ALL PRIVILEGES ON pixelebbe.* TO 'pixelebbe'@'localhost';
FLUSH PRIVILEGES;
exit;
```

## Application Setup

### Download Pixelebbe

Switch to the Pixelebbe system user and navigate to the installation directory:

```bash
sudo su pixelebbe
cd /var/pixelebbe
```

Clone the Pixelebbe repository:

```bash
git clone https://github.com/yourusername/pixelebbe.git .
```

### Python Environment Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
pip install gunicorn mariadb
```

### Configure Pixelebbe

Create a configuration file `config.py`:

```python
SETTINGS = {
    'SECRET_KEY': '<generate_a_secure_random_key>',
    'SECURITY_PASSWORD_SALT': '<generate_a_secure_random_salt>',
    'SQL_URL': 'mariadb+mariadbconnector://pixelebbe:<your_password>@127.0.0.1:3306/pixelebbe',
}
```

### Initialize Database

Set up the database tables:

```bash
python3 setup.py
```

## Server Configuration

### Create Systemd Service

Create a systemd service file at `/etc/systemd/system/pixelebbe.service`:

```ini
[Unit]
Description=Pixelebbe Gunicorn Service
After=network.target

[Service]
User=pixelebbe
Group=www-data
WorkingDirectory=/var/pixelebbe
Environment="PATH=/var/pixelebbe/venv/bin"
ExecStart=/var/pixelebbe/venv/bin/gunicorn --workers 3 --bind unix:pixelebbe.sock -m 007 pixelebbe:app

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl start pixelebbe
sudo systemctl enable pixelebbe
```

### Configure Nginx

Create an Nginx configuration file at `/etc/nginx/sites-available/pixelebbe`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/pixelebbe/pixelebbe.sock;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/pixelebbe /etc/nginx/sites-enabled
sudo nginx -t
sudo nginx -s reload
```

Configure firewall if needed:

```bash
sudo ufw allow 'Nginx Full'
```

## Create the first admin user

Login as pixelebbe and prepare the venv:

```bash
su pixelebbe
cd /var/pixelebbe
source venv/bin/activate
```

Create the user:

```bash
flask users create your@email.address -u yourusername -a
flask roles add yourusername users
```

## SSL Setup (Optional)

If your server is publicly accessible, it's recommended to set up HTTPS using Let's Encrypt:

```bash
sudo apt install python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Troubleshooting

If you encounter any issues:

1. Check the system logs: `sudo journalctl -u pixelebbe`
2. Check the Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Ensure all services are running: `sudo systemctl status pixelebbe nginx mariadb`
