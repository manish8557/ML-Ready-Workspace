# Custom bash configuration for ML workspace

# Colorful prompt
export PS1='\[\033[01;32m\]\u@ml-workspace\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# Useful aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias jupyter-lab='jupyter lab --ip=0.0.0.0 --port=8888 --no-browser'
alias jupyter-notebook='jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser'
alias tensorboard='tensorboard --logdir=./logs --host=0.0.0.0 --port=6006'
alias python='python3'
alias pip='pip3'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'

# TensorBoard status check
alias tb-status='ps aux | grep -q "[t]ensorboard" && echo "TensorBoard: RUNNING (port 6006)" || echo "TensorBoard: NOT RUNNING"'
alias tb-start='mkdir -p logs && nohup tensorboard --logdir=./logs --host=0.0.0.0 --port=6006 --reload_interval 5 > tensorboard.log 2>&1 &'
alias tb-stop='pkill -f tensorboard'
alias tb-logs='tail -f tensorboard.log'

# Network tools
alias ports='netstat -tulpn'
alias myip='hostname -I'

# Welcome message
echo "=== ML Workspace ==="
echo "Project directory: $(pwd)"
echo "Python path: $(which python)"
echo "Conda environment: ml-env"
echo "Jupyter Lab: http://localhost:8888"
echo "TensorBoard: http://localhost:6006"
tb-status
echo "Use 'tb-start' to start TensorBoard if not running"
echo "Use 'tb-status' to check TensorBoard status"