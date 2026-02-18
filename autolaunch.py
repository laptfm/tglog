cat > ~/Library/LaunchAgents/com.user.telegramlogger.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.telegramlogger</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/ivan/Library/Application Support/TelegramLogger/logger.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/ivan/Library/Application Support/TelegramLogger/daemon_output.txt</string>
    <key>StandardErrorPath</key>
    <string>/Users/ivan/Library/Application Support/TelegramLogger/daemon_errors.txt</string>
</dict>
</plist>
EOF
