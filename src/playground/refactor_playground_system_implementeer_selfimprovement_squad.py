from loguru import logger
import os
import time
import subprocess
import json
from typing import Dict, Any, List


class SystemRefactor:
    """
    Refactor van een complex Python script met behulp van 'Extract Method' om de leesbaarheid te verbeteren.
    """

    def __init__(self, config_file: str = "config.json"):
        """
        Initialiseert de SystemRefactor klasse.

        Args:
            config_file (str): Het pad naar het configuratiebestand.
        """
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Laadt de configuratie uit een JSON-bestand.

        Returns:
            Dict[str, Any]: De configuratie als een dictionary.
        """
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            logger.info(f"Configuratie succesvol geladen van {self.config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuratiebestand {self.config_file} niet gevonden.")
            return {}
        except json.JSONDecodeError:
            logger.error(
                f"Fout bij het parsen van configuratiebestand {self.config_file}."
            )
            return {}
        except Exception as e:
            logger.error(f"Onverwachte fout bij het laden van configuratiebestand: {e}")
            return {}

    def _execute_command(self, command: str) -> str:
        """
        Private helper to execute shell commands.  Centralizes error handling.
        """
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Fout bij het uitvoeren van commando '{command}': {e.stderr}")
            return ""
        except FileNotFoundError:
            logger.error(f"Commando '{command}' niet gevonden.")
            return ""
        except Exception as e:
            logger.error(
                f"Onverwachte fout bij het uitvoeren van commando '{command}': {e}"
            )
            return ""

    def _run_command(self, command: str) -> str:
        """
        Voert een shell commando uit en returned de output.

        Args:
            command (str): Het commando om uit te voeren.

        Returns:
            str: De output van het commando.
        """
        output = self._execute_command(command)
        if output:
            logger.debug(f"Commando '{command}' uitgevoerd met succes.")
        return output

    def get_system_info(self) -> Dict[str, str]:
        """
        Verzamelt basale system information.

        Returns:
            Dict[str, str]: Een dictionary met system informatie.
        """
        system_info: Dict[str, str] = {}
        try:
            system_info["os_name"] = self._run_command("uname -s")
            system_info["kernel_version"] = self._run_command("uname -r")
            system_info["hostname"] = self._run_command("hostname")
            system_info["cpu_info"] = self._run_command(
                "cat /proc/cpuinfo | grep 'model name' | head -n 1 | awk -F: '{print $2}'"
            )
            system_info["memory_info"] = self._run_command(
                "free -h | grep Mem | awk '{print $2}'"
            )
            logger.info("Systeem informatie succesvol opgehaald.")
        except Exception as e:
            logger.error(f"Fout bij het ophalen van systeem informatie: {e}")

        return system_info

    def get_disk_usage(self) -> List[Dict[str, str]]:
        """
        Verzamelt disk usage informatie.

        Returns:
            List[Dict[str, str]]: Een lijst met dictionaries, elk met disk usage info.
        """
        disk_usage: List[Dict[str, str]] = []
        try:
            df_output = self._run_command("df -h")
            if not df_output:
                return disk_usage  # handle the case where df fails.
            lines = df_output.splitlines()[1:]  # Skip header
            for line in lines:
                fields = line.split()
                if len(fields) >= 6:
                    disk_info: Dict[str, str] = {
                        "filesystem": fields[0],
                        "size": fields[1],
                        "used": fields[2],
                        "available": fields[3],
                        "use_percentage": fields[4],
                        "mounted_on": fields[5],
                    }
                    disk_usage.append(disk_info)
            logger.info("Disk usage informatie succesvol opgehaald.")
        except Exception as e:
            logger.error(f"Fout bij het ophalen van disk usage informatie: {e}")
        return disk_usage

    def monitor_cpu_usage(self, interval: int = 1, duration: int = 10) -> List[float]:
        """
        Monitort CPU usage over een bepaalde periode.

        Args:
            interval (int): Het interval tussen metingen in seconden.
            duration (int): De duur van de monitoring in seconden.

        Returns:
            List[float]: Een lijst met CPU usage percentages.
        """
        cpu_usage_percentages: List[float] = []
        try:
            for _ in range(duration // interval):
                cpu_output = self._run_command(
                    "top -bn1 | grep 'Cpu(s)' | awk '{print $8}'"
                )
                if not cpu_output:
                    continue  # Skip if the command fails.
                try:
                    cpu_percent = float(cpu_output.replace("%", ""))
                    cpu_usage_percentages.append(cpu_percent)
                except ValueError as e:
                    logger.error(f"Fout bij het parsen van CPU usage: {e}")
                time.sleep(interval)
            logger.info("CPU usage monitoring voltooid.")
        except Exception as e:
            logger.error(f"Fout bij het monitoren van CPU usage: {e}")

        return cpu_usage_percentages

    def perform_system_check(self) -> Dict[str, Any]:
        """
        Voert een systeemcheck uit en retourneert de resultaten.
        """
        system_check_results: Dict[str, Any] = {}
        try:
            system_check_results["system_info"] = self.get_system_info()
            system_check_results["disk_usage"] = self.get_disk_usage()
            system_check_results["cpu_usage"] = self.monitor_cpu_usage()
            logger.info("Systeemcheck voltooid.")
        except Exception as e:
            logger.error(f"Fout tijdens de systeemcheck: {e}")

        return system_check_results

    def process_system_check_results(self, results: Dict[str, Any]) -> None:
        """
        Verwerkt de resultaten van de systeemcheck en logt ze.

        Args:
            results (Dict[str, Any]): De resultaten van de systeemcheck.
        """
        try:
            logger.info("Resultaten van systeemcheck:")
            if results.get("system_info"):
                logger.info(f"Systeem informatie: {results['system_info']}")
            if results.get("disk_usage"):
                logger.info(f"Disk Usage: {results['disk_usage']}")
            if results.get("cpu_usage"):
                logger.info(f"CPU Usage: {results['cpu_usage']}")
            else:
                logger.warning("Geen CPU usage data beschikbaar.")
            logger.info("Verwerking van resultaten voltooid.")
        except Exception as e:
            logger.error(f"Fout bij het verwerken van de resultaten: {e}")