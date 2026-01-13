import time
import threading
import logging
import re
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SecurityGuard:
    """
    Een agent die de veiligheid van het AI-systeem bewaakt.
    """

    def __init__(
        self,
        system_files: List[str] = None,
        allowed_network_domains: List[str] = None,
        data_access_logs: List[Dict[str, Any]] = None,
    ):
        """
        Initialiseert de SecurityGuard.

        Args:
            system_files: Een lijst met kritieke bestandsnamen.
            allowed_network_domains: Een lijst met domeinnamen die toegestaan zijn voor netwerkverkeer.
            data_access_logs: Een lijst met logs van data access events.
        """
        self.system_files = system_files if system_files is not None else []
        self.allowed_network_domains = (
            allowed_network_domains if allowed_network_domains is not None else []
        )
        self.data_access_logs = data_access_logs if data_access_logs is not None else []
        self.running = True  # Flag to control the monitoring loop
        self.monitoring_thread = threading.Thread(
            target=self.start_monitoring, daemon=True
        )  # Run in daemon mode

    def start(self):
        """
        Start de security monitoring.
        """
        self.monitoring_thread.start()
        logging.info("SecurityGuard gestart.")

    def stop(self):
        """
        Stopt de security monitoring.
        """
        self.running = False
        self.monitoring_thread.join(timeout=5)  # Wait for the thread to finish
        logging.info("SecurityGuard gestopt.")

    def start_monitoring(self):
        """
        Start de continue monitoring loop.
        """
        while self.running:
            try:
                self.monitor_system()
                self.monitor_network_activity()
                self.analyze_data_access_logs()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logging.error(f"Er is een fout opgetreden tijdens de monitoring: {e}")
                time.sleep(10)  # Wait and try again

    def monitor_system(self):
        """
        Monitort wijzigingen aan kritieke bestanden.
        """
        for file in self.system_files:
            try:
                # Basic check:  could be expanded to checksums, size, modification date, etc.
                import os

                if not os.path.exists(file):
                    self.report_incident(f"Kritiek bestand ontbreekt: {file}")
                    continue  # Don't proceed with other checks if the file doesn't exist.

                original_size = os.path.getsize(file)
                time.sleep(
                    0.1
                )  # Debounce: short sleep to allow potential operations to complete.
                current_size = os.path.getsize(file)

                if original_size != current_size:
                    self.report_incident(f"Kritiek bestand gewijzigd: {file}")
            except Exception as e:
                logging.error(f"Fout bij het controleren van bestand {file}: {e}")

    def monitor_network_activity(self):
        """
        Monitort inkomend en uitgaand netwerkverkeer.  Implementatie zou afhankelijk zijn van OS en netwerkbibliotheken.
        """
        # Voorbeeld:  Simuleert netwerkverkeer.  In praktijk zou dit netwerkpakketten inspecteren.
        try:
            # Simulate checking network traffic - replaced with a more robust method in practice.
            # Here:  Look for any attempts to connect to a non-approved domain
            import socket
            import urllib.request

            # Simplified example: Check for outgoing requests to non-allowed domains.
            with urllib.request.urlopen(
                "https://api.ipify.org/"
            ) as response:  # Simulate network traffic (Get own IP)
                ip = response.read().decode("utf-8")
                if ip:
                    try:
                        domain = socket.gethostbyaddr(ip)[0]
                        if not any(
                            domain.endswith(allowed_domain)
                            for allowed_domain in self.allowed_network_domains
                        ):
                            self.report_incident(
                                f"Netwerkverkeer naar onbekend domein: {domain} ({ip})"
                            )
                    except socket.herror:
                        pass  # Ignore address resolution errors
        except Exception as e:
            logging.error(f"Fout bij het monitoren van netwerkactiviteit: {e}")

    def analyze_data_access_logs(self):
        """
        Analyseert data access logs op verdachte activiteit.
        """
        for log_entry in self.data_access_logs:
            try:
                # Voorbeeld: Zoeken naar toegang tot gevoelige bestanden.
                if "gevoelige_data" in str(log_entry.get("data", "")):
                    self.report_incident(
                        f"Ongeautoriseerde toegang tot gevoelige data: {log_entry}"
                    )

                # Voorbeeld:  Detecting suspicious amounts of data access.
                if (
                    log_entry.get("type") == "read"
                    and log_entry.get("bytes_accessed", 0) > 1000000
                ):  # 1MB example
                    self.report_incident(f"Verdachte grote data toegang: {log_entry}")

                # Voorbeeld: Searching for patterns of malicious use (prompt injection attempts).
                if "prompt" in log_entry and re.search(
                    r"(?i)(drop table|delete from)", log_entry["prompt"]
                ):
                    self.report_incident(
                        f"Mogelijke prompt injection detected: {log_entry}"
                    )

            except Exception as e:
                logging.error(
                    f"Fout bij het analyseren van log entry: {log_entry}. Fout: {e}"
                )

    def report_incident(self, message: str):
        """
        Registreert een veiligheidsincident.
        """
        logging.warning(f"VEILIGHEIDSINCIDENT: {message}")
        # In een echte implementatie zou dit acties ondernemen, zoals het loggen,
        # waarschuwen van beheerders, het isoleren van het systeem, etc.
        # Voorbeeld: Save the event
        self.log_incident(message)

    def log_incident(self, message: str):
        """
        Logt incidenten in een apart logbestand of database.
        """
        try:
            import datetime

            with open("security_incidents.log", "a") as f:
                f.write(f"{datetime.datetime.now()} - INCIDENT: {message}\n")
        except Exception as e:
            logging.error(f"Fout bij het loggen van incident: {e}")


# Example usage (within the main program, probably after other agents are initialized)
if __name__ == "__main__":
    # Simuleer kritieke bestanden, toegestane domeinen en logs.
    critical_files = ["__init__.py", "code_refactorer.py"]  # Example
    allowed_domains = ["example.com", "api.ipify.org"]  # Example
    example_logs = [
        {
            "timestamp": "2024-10-27T10:00:00",
            "user": "test_user",
            "action": "read",
            "file": "gevoelige_data.txt",
            "data": "Geheime informatie",
        },
        {
            "timestamp": "2024-10-27T10:01:00",
            "user": "test_user",
            "action": "read",
            "file": "some_file.txt",
            "data": "Some regular data",
        },
        {
            "timestamp": "2024-10-27T10:02:00",
            "user": "attacker",
            "action": "read",
            "file": "config.py",
            "data": "Some more data",
        },
        {
            "timestamp": "2024-10-27T10:03:00",
            "user": "malicious_user",
            "action": "prompt",
            "prompt": "drop table users; -- comment",
        },
    ]

    security_guard = SecurityGuard(
        system_files=critical_files,
        allowed_network_domains=allowed_domains,
        data_access_logs=example_logs,
    )
    security_guard.start()

    # Simulate running other tasks for a while
    time.sleep(20)

    security_guard.stop()
    print("Test afgerond.")
