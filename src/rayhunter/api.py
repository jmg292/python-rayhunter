import io
import logging
import requests
import urllib.parse

from .manifest import QmdlManifest
from .system_stats import SystemStats


class RayhunterApi:

    @property
    def active_recording(self) -> bool:
        """
        Check the manifest file to determine if there's a recording in progress.
        :returns: True if there's a "current_entry" in the manifest, else False
        """
        manifest = self.get_manifest()
        return manifest.current_entry is not None

    def __init__(self, hostname: str, port: int):
        self._url = f"http://{hostname}:{port}/"

    def _get_file_content(self, api_endpoint: str) -> bytes:
        """
        Stream a file from the given API endpoint into memory. 
        :param api_endpoint: The endpoint from which to retrieve a file
        :returns: The contents of the file (bytes)
        """
        file_content = io.BytesIO()
        file_url = urllib.parse.urljoin(self._url, api_endpoint)
        logging.info(f"Downloading file from: {file_url}")
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=4096):
            file_content.write(chunk)
        file_content.seek(0)
        return file_content.read()

    def get_manifest(self) -> QmdlManifest:
        """
        Fetch a copy of the QMDL manifest, used to track the names of previous and active recordings.
        :returns: An instance of `QmdlManifest` populated from the target device
        """
        manifest_url = urllib.parse.urljoin(self._url, "/api/qmdl-manifest")
        logging.info(f"Fetching manifest from: {manifest_url}")
        response = requests.get(manifest_url)
        response.raise_for_status()
        return QmdlManifest.from_dict(response.json())
    
    def get_analysis_report_file(self, filename: str) -> bytes:
        """
        Fetch a copy of the analysis report for a given capture. Use `get_manifest` to identify capture names.
        :param filename: The capture file name
        :returns: The contents of the analysis report file (bytes)
        """
        logging.info(f"Fetching analysis report for capture: {filename}")
        api_endpoint = f"/api/analysis-report/{filename}"
        return self._get_file_content(api_endpoint)
    
    def get_pcap_file(self, filename: str) -> bytes:
        """
        Fetch a copy of the pcap file for a given capture. PCAP is dynamically generated from QMDL by the Rayhunter binary when this API is called.
        :param filename: The capture file name (found in manifest)
        :returns: The contents of the pcap file (bytes)
        """
        logging.info(f"Fetching PCAP file for capture: {filename}")
        api_endpoint = f"/api/pcap/{filename}"
        return self._get_file_content(api_endpoint)

    def get_qmdl_file(self, filename: str) -> bytes:
        """
        Fetch a copy of the given QMDL file. Use `get_manifest` to identify QMDL capture names.
        :param filenae: The QMDL file name (found in manifest)
        :returns: The contents of the QMDL file (bytes)
        """
        logging.info(f"Fetching QDML file for capture: {filename}")
        api_endpoint = f"/api/qmdl/{filename}"
        return self._get_file_content(api_endpoint)
    
    def start_recording(self):
        """
        Start a new recording. Stops the active recording and starts a new one if this device is already recording.
        """
        start_recording_url = urllib.parse.urljoin(self._url, "/api/start-recording")
        logging.info(f"Starting recording with POST request to: {start_recording_url}")
        response = requests.post(start_recording_url)
        response.raise_for_status()
    
    def stop_recording(self):
        """
        Stop an active recording. Throws a 500 error if there is no active recording.
        """
        stop_recording_url = urllib.parse.urljoin(self._url, "/api/stop-recording")
        logging.info(f"Stopping recording with POST request to: {stop_recording_url}")
        response = requests.post(stop_recording_url)
        response.raise_for_status()

    def system_stats(self):
        """
        Fetch disk and memory utilization stats from the API.
        :returns: An instance of `SystemStats` populated from the target device.
        """
        system_stats_url = urllib.parse.urljoin(self._url, "/api/system-stats")
        logging.info(f"Fetching system stats from: {system_stats_url}")
        response = requests.get(system_stats_url)
        response.raise_for_status()
        return SystemStats.from_dict(response.json())
