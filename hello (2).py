import threading, time, subprocess, shutil, re

# Kill previous instances
subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
subprocess.run(['pkill', '-f', 'lt'], capture_output=True)

# Function to run Streamlit
def run_streamlit():
    subprocess.run(['streamlit', 'run', 'app.py', '--server.port', '8501', '--server.address', '0.0.0.0'])

# Start Streamlit in a separate thread
threading.Thread(target=run_streamlit, daemon=True).start()
print("🚀 Starting Streamlit...")
time.sleep(8)

# Locate the LocalTunnel executable
lt_path = shutil.which("lt")
if not lt_path:
    raise ValueError("LocalTunnel not found. Run `!npm install -g localtunnel` first.")

print("🌐 Starting LocalTunnel...")
p = subprocess.Popen([lt_path, '--port', '8501'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

for line in iter(p.stdout.readline, b''):
    decoded = line.decode()
    print(decoded.strip())
    match = re.search(r'(https://[^\s]+\.loca\.lt)', decoded)
    if match:
        print(f"\n✅ Your Streamlit app is live at: {match.group(1)}")
        break