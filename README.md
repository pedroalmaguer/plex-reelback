# Plex Reelback

A silly name for a hopefully silly "Wrapped" style app for Plex + Tautulli.
Powered by Flask, HTMX and AI (For now)

## Feature Creep
- View your Tautulli stats
- Display in a fun "wrapped" style.
- Excluded users list. (excluded_users.json)

## Getting Started

1. Grab Tautulli URL, Api Key and SQLite DB
    - Tautulli URL 
      -  http://localhost:8181
    - API Key
      - Settings->Web Interface-> API Key
    - DB
      - Settings->Imports & Backups->Under Directories select "Backup Database"
      - Once Backup is complete, SSH to your Tautulli server, navigate to the backup directory (Default /root/snap/tautulli/common/Tautulli/backups)
      - Copy latest backup created to your root project folder

2. TBD
3. TBD