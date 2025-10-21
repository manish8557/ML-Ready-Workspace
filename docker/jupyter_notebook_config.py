# Jupyter Notebook Configuration File
# Jupyter configuration
c = get_config()

# Server configuration
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.token = 'ml123'
c.ServerApp.password = ''

# Notebook configuration
c.NotebookApp.allow_origin = '*'
c.NotebookApp.allow_remote_access = True
c.NotebookApp.tornado_settings = {
    'headers': {
        'Content-Security-Policy': "frame-ancestors 'self' http://localhost:*"
    }
}

# Extensions
c.NotebookApp.nbserver_extensions = {
    'jupyterlab': True,
    'nbdime': True
}

# Auto-save
c.NotebookApp.notebook_dir = '/home/mluser/ml-project'
c.FileContentsManager.delete_to_trash = False
EOF