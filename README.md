Automatisierte Login- & Logout-Skripte mit GitHub Actions optimiert

Login- und Logout-Skripte:
   - Automatisierte Scripte

GitHub Actions Workflows erstellt:
   - `login.yml`: Automatische Anmeldung um 14:02 MEZ (Mo-Fr)
   - `logout.yml`: Automatische Abmeldung um 17:04 MEZ (Mo-Fr)
   - Chrome & WebDriver werden automatisch installiert
   - Unterstützung für manuelles Starten über `workflow_dispatch`

Sicherheit:
   - Alle sensiblen Daten über GitHub Secrets verwaltet

Das Projekt läuft jetzt vollständig automatisiert in GitHub Actions!