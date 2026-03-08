# Health Guardian (Iron Man / Jarvis Edition)

Native Windows desktop application designed to protect human health during long PC sessions. Health Guardian utilizes true 7-segment digital fonts, aggressive neon styling, zero-dependency background architectures, and highly strict overlay notifications to ensure the health protocols (20-20-20 Rule, Hydration, Long Screen Breaks) are followed.

![Health Guardian Dashboard](screenshot.png)

## Core Philosophy & Design
Rather than relying on Windows OS toast notifications—which are easily ignored and frequently blocked by "Do Not Disturb" (Focus Assist) modes—Health Guardian takes total control of the display layer. When a health interval is triggered, the application enforces a native, transparent, top-level system window (`Qt.WindowStaysOnTopHint`) directly in the center of the screen.

This overlay comes with its own independent localized countdown and high-frequency recurring audio alerts (via asynchronous `winsound` native threading) that refuse to stop until verbally acknowledged.

## Architectural Flow
```mermaid
sequenceDiagram
    participant OS as Windows OS Task Tray
    participant UI as Main Dashboard UI
    participant Timer as Independent Background Timers
    participant Overlay as Massive Forced Overlay

    OS->>UI: Launch & Minimize to Tray
    UI->>Timer: Instantiate Timers (20-rule, Hydration, Break)
    loop Continuous Tracking
        Timer->>Timer: Tick Down (Uninterrupted)
        opt Reaches Zero
            Timer-->>Timer: Reset to Max immediately and Resume
            Timer->>Overlay: Fire custom pyqtSignal (Alert)
            Overlay->>OS: Generate Topmost Frameless Window
            Overlay->>Overlay: Localized popup countdown begins
            opt Popup Countdown Reaches Zero
                Overlay->>Overlay: Asynchronous Audio Beep Event Fired (2000Hz)
            end
            Overlay-->>UI: User clicks "I'VE DONE IT" - Window & Audio Purged!
        end
    end
```

## Setup & Running
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt` (Installs PyQt6 Native Bindings).
3. Run the application: `python main.py`

*(Note: On first run, the app will ping github automatically to securely download and install the `DSEG-7_Classic` digital font for the Iron Man/Jarvis aesthetics).*

## Configuration
Access the `⚙ SYSTEM SETTINGS` menu natively within the dashboard to toggle:
- `Enable Fullscreen Popups`
- `Play Alert Beeps`
- `Run in Background (Minimize to System Tray)`
