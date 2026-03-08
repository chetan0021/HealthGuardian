<div align="center">
  <h1>🛡️ Health Guardian</h1>
  
  <p><b>A market-ready, native Windows desktop application meticulously engineered to protect human health and mitigate ocular fatigue during extended PC sessions.</b></p>

  <img src="screenshot.png" alt="Health Guardian Dashboard" width="800">

  <br><br>

  <!-- Tech Stack Badges -->
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://riverbankcomputing.com/software/pyqt/intro"><img src="https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6"></a>
  <a href="https://microsoft.com/windows"><img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows Native"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License: MIT"></a>

</div>

<hr>

## 🌟 Overview
Health Guardian utilizes a mathematically drawn Cyber aesthetic, deep autonomous background architectures, and highly strict overlay notifications to ensure critical health protocols are strictly enforced.

By color-coding primary objectives—Ocular Rest (Cyan), Hydration (Blue), and Physical Movement (Magenta)—the dashboard provides clear, glanceable cognitive mapping for your health requirements.

### ✨ Key Features
* **Strict Operating System Overlays**: Takes total control of the display layer (`Qt.WindowStaysOnTopHint`), actively bypassing easily ignored standard Windows Toast Notifications or "Do Not Disturb" focus modes.
* **Localized Async Audio Alerts**: High-frequency recurring audio alerts utilizing asynchronous `winsound` native thread purging.

## ⚕️ The Science of Health Guardian
Prolonged PC usage introduces sustained, unnatural stress to human physiology. Health Guardian mitigates this through three distinct, scientifically-backed protocols:

1. **The 20-20-20 Rule (Ocular Rest)**: Every 20 minutes, the application demands you look at an object 20 feet away for exactly 20 seconds. This action physically relaxes the ciliary muscles inside the eyes, preventing Computer Vision Syndrome (digital eye strain), dryness, and long-term myopia.
2. **Hydration Protocol**: Every 60 minutes, the system enforces a water break. Chronic mild dehydration while focusing on screens leads to headaches, reduced cognitive performance, and noticeable facial fatigue (dark circles and dry skin).
3. **Deep Posture Break**: Every 2 hours, a strict 15-minute complete detachment from the screen is required. This resets the musculoskeletal system, preventing repetitive strain injuries (RSI) and mitigating severe postural degradation.

## 🧠 How It Works
The application abandons traditional notification systems in favor of strict, native disruption logic:
1. **Background Mathematics**: Three independent sub-threads calculate time continuously. They cannot be paused simply by ignoring a notification.
2. **Forced Context Switching**: When a protocol duration expires, PyQt6 physically intercepts the Windows Desktop Manager, spawning an un-ignorable, topmost, frameless overlay across all monitors.
3. **Auditory Conditioning**: Upon the completion of the required rest interval (e.g., 20 seconds of looking away), an asynchronous 2000Hz repeating audio alert engages, ensuring cognitive compliance until the user physically verifies completion by clicking `I'VE DONE IT`.

## 📊 Operational Block Diagram
```mermaid
flowchart TD
    Start[User Launches App] --> Init[Initialize PyQt6 Engine]
    Init --> Threads[Spawn 3 Autonomous Timer Threads]
    
    subgraph Background Processing
        Threads --> T1[20 Min: Ocular Rest]
        Threads --> T2[60 Min: Hydration]
        Threads --> T3[120 Min: Posture Break]
    end

    T1 -->|Timeout| Alert[Trigger Forced Top-Level Overlay]
    T2 -->|Timeout| Alert
    T3 -->|Timeout| Alert

    subgraph Overlay Intervention
        Alert --> DND[Bypass OS 'Do Not Disturb']
        DND --> Count[Independent Wait Countdown]
        Count -->|Wait Expires| Audio[Engage 2000Hz Async Alarm]
        Audio --> Click{"User Clicks 'I'VE DONE IT'"}
    end

    Click -->|Acknowledge| Purge[Purge Graphics & Audio Buffers]
    Purge -.->|Reset Thread| Threads
```

## ⚙️ Configuration
Access the **⚙ SYSTEM SETTINGS** menu natively within the dashboard to tailor the enforcement:
- `Enable Fullscreen Popups`
- `Play Alert Beeps`
- `Run in Background (Minimize to System Tray)`

## 🚀 Installation & Usage

### Prerequisites
- Python 3.9+
- Windows OS (Tested on Windows 10/11)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/chetan0021/HealthGuardian.git
   cd HealthGuardian
   ```
2. Install dependencies (PyQt6 Native Framework):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## 🏗️ Architectural Flow
```mermaid
sequenceDiagram
    participant OS as Windows OS Task Tray
    participant UI as Main Dashboard UI
    participant Timer as Independent PyQt Signals
    participant Overlay as Massive Forced Overlay

    OS->>UI: Launch & Minimize to Tray
    UI->>Timer: Instantiate Timers (Ocular, Hydration, Break)
    loop Continuous Tracking
        Timer->>Timer: Tick Down (Uninterrupted Background Thread)
        opt Reaches Zero
            Timer-->>Timer: Reset to Max immediately and Resume
            Timer->>Overlay: Fire custom `pyqtSignal` (Alert)
            Overlay->>OS: Generate Topmost Frameless Window
            Overlay->>Overlay: Localized popup countdown begins
            opt Popup Countdown Reaches Zero
                Overlay->>Overlay: Asynchronous Audio Beep Event Fired (2000Hz)
            end
            Overlay-->>UI: User clicks "I'VE DONE IT" - Window & Audio Purged!
        end
    end
```

## 🤝 Collaboration & Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any robust features you contribute to Health Guardian are **greatly appreciated**.

### How to Contribute
1. **Fork the Project**
2. **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the Branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

Please ensure that any new UI additions adhere closely to the established "Cyber" aesthetic blueprint.  

## 📄 License
Distributed under the MIT License. Use it to protect your health globally.
