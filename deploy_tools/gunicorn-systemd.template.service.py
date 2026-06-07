[Unit]
Description=Gunicorn server for 123.57.141.186

[Service]
Restart=on-failure
User=fangkuai
WorkingDirectory=/home/fangkuai/sites/123.57.141.186/source
ExecStart=/home/fangkuai/sites/123.57.141.186/virtualenv/bin/gunicorn --bind unix:/tmp/123.57.141.186.socket notes.wsgi:application

[Install]
WantedBy=multi-user.target