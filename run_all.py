# run_all.py
import subprocess
import sys
import time

def main():
    print("🚀 Starting Advanced Cookie Analyzer System...")
    print("-------------------------------------------------")
    
    processes = []

    try:
        # 1. Start the API (FastAPI)
        print("🟢 Starting API Server (FastAPI)...")
        api_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api:app", "--port", "8000"])
        processes.append(api_process)
        time.sleep(2) # Take some time to ensure the port is ready

        # 2. Start the Background Scheduler
        print("🟢 Starting Background Audit Scheduler...")
        scheduler_process = subprocess.Popen([sys.executable, "scheduler.py"])
        processes.append(scheduler_process)
        time.sleep(1)

        # 3. Start the UI (Streamlit)
        print("🟢 Starting User Interface (Streamlit)...")
        ui_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])
        processes.append(ui_process)

        print("-------------------------------------------------")
        print("✅ All services are running successfully!")
        print("Press Ctrl+C to safely shut down all services.")
        
        # Keep the main script running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services safely...")
        for p in processes:
            p.terminate()
        print("✅ All services stopped.")

if __name__ == "__main__":
    main()