#!/bin/bash

yum update -y

amazon-linux-extras install nginx1 python3.8 -y 

cat << 'EOF' >> /etc/nginx/conf.d/demo.conf
server {
        listen 80;
        access_log  /var/log/nginx/demo.log;
        location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
}
EOF

# Restart nginx to make it effect
systemctl start nginx
systemctl enable nginx

yum install python3-pip git -y

# Install flask
pip3 install flask gunicorn boto3

# Git clone to fetch the source
su - ec2-user -c "cd /home/ec2-user && git clone https://github.com/d2lee/quiz.git"

# Create the gunicorn config file
cat << 'EOF' >> /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/quiz
ExecStart=/usr/local/bin/gunicorn \
        --workers 3 \
        --bind 127.0.0.1:8000 \
        app:app

[Install]
WantedBy=multi-user.target
EOF

systemctl restart gunicorn
systemctl enable gunicorn