#
---

````markdown
# 🧭 Installation Guide

Follow this guide to set up your **ML Workspace** on macOS, Windows, or Linux.

---

## ⚙️ System Requirements

### Minimum
- **RAM:** 8 GB  
- **Storage:** 20 GB free space  
- **Docker Desktop** (or Docker Engine for Linux)  
- **Python 3.8+** (for the launcher script)

### Recommended
- **RAM:** 16 GB or more  
- **Storage:** 50 GB+ free space  
- **CPU:** Multi-core processor  
- **Internet:** Stable connection for initial setup  

---

## 🚀 Step-by-Step Setup

### 🧩 Step 1: Install Docker

#### macOS
1. Download [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/).  
2. Install the `.dmg` file.  
3. Launch Docker Desktop from **Applications**.  
4. Wait for Docker to start (whale icon appears in the menu bar).

#### Windows
1. Download [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/).  
2. Run the installer.  
3. Enable **WSL2** when prompted.  
4. Restart your computer if required.

#### Linux (Ubuntu/Debian)
```bash
# Install Docker Engine
sudo apt update
sudo apt install docker.io
sudo systemctl enable docker
sudo systemctl start docker

# Add your user to the Docker group
sudo usermod -aG docker $USER

# Log out and back in for changes to take effect
````

---

### 🧾 Step 2: Verify Docker Installation

Run the following in your terminal:

```bash
docker --version
docker-compose --version
```

✅ You should see version numbers for both.

---

### 📥 Step 3: Get the ML Workspace

```bash
# Clone the repository
git clone https://github.com/yourusername/ml-workspace.git
cd ml-workspace
```

---

### ⚙️ Step 4: First-Time Setup

```bash
# Launch the workspace
python launch.py
```

> 🕐 The first run may take **10–30 minutes** as it builds the environment and downloads base Docker images.

---

## 💻 Platform-Specific Notes

### 🍎 macOS (Apple Silicon M1/M2)

* ✅ Fully optimized for **ARM64** architecture
* ✅ Uses **native ARM64** Docker images
* ✅ No manual configuration required
* ⚡ Better performance than Intel-based Macs

### 🍏 macOS (Intel)

* ✅ Fully supported
* ✅ Uses **x86_64** Docker images
* ✅ No special setup required

### 🪟 Windows

* ✅ Requires **WSL2** enabled
* ✅ Use **PowerShell** or **WSL Terminal**
* ✅ Ensure Docker Desktop **WSL integration** is turned on
* ⚙️ Virtualization may need to be enabled in BIOS

### 🐧 Linux

* ✅ Ensure your user is in the `docker` group
* ✅ Optionally enable Docker to start on boot
* 🧩 Some distributions may require extra dependencies

---

## ✅ Verification Steps

After installation completes, verify your setup:

### Check running containers

```bash
docker-compose ps
```

You should see `ml-workspace` in the running list.

### Access services

* **Jupyter Lab:** [http://localhost:8888](http://localhost:8888)
* **TensorBoard:** [http://localhost:6006](http://localhost:6006)

### Test the Python environment

```bash
docker-compose exec ml-workspace python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
```

---

## ⚠️ Common Installation Issues

### 🐳 Docker Not Starting

* **macOS / Windows:** Ensure Docker Desktop is running.
* **Linux:** Check status with:

  ```bash
  sudo systemctl status docker
  ```
* Restart Docker if necessary.

---

### 🔌 Port Conflicts

If ports **8888** or **6006** are in use:

```bash
lsof -i :8888
lsof -i :6006
```

Or edit `docker-compose.yml` to assign different ports.

---

### 💾 Insufficient Disk Space

Free up space or remove unused Docker images:

```bash
docker system prune -a
```

---

### 🌐 Network Issues

If downloads fail:

* Use a **stable internet connection**
* Try a **VPN** if behind a firewall
* Configure Docker proxy settings if needed

---

## 🚀 Next Steps

After successful installation:

1. Read [`USAGE.md`](USAGE.md) for daily usage instructions.
2. Explore the **example notebooks**.
3. Start building your ML projects! 🎯

---

## 🆘 Getting Help

If you encounter issues:

* Check logs:

  ```bash
  docker-compose logs ml-workspace
  ```
* Search or report issues on the **GitHub repository**.
* When creating a new issue, include:

  * Your OS and hardware details
  * Docker and Python versions
  * Relevant error messages or logs

---

> 💡 **Tip:** Once installed, the ML Workspace can be launched anytime with
>
> ```bash
> python launch.py
> ```
>
> It’s that simple!
