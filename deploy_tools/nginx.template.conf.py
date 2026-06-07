server {
    listen 80;
    server_name 123.57.141.186;

    location /static {
        alias /home/fangkuai/sites/123.57.141.186/static;
    }

    location / {
        proxy_set_header Host $host;
        proxy_pass http://unix:/tmp/123.57.141.186.socket;
    }
}