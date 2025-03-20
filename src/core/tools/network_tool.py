"""Network configuration and diagnostics tool module for Moinsy.

Like a digital cartographer mapping the invisible highways of packet transmission,
this module enables the user to navigate and manipulate their network configurations
with the quiet desperation of someone who just wants their internet to work.
"""

from PyQt6.QtCore import QObject, pyqtSignal
import subprocess
import logging
import socket
import ipaddress
import re
import json
import os
import time
from typing import List, Dict, Any, Optional, Tuple, Union, Set, cast

from utils.system_utils import execute_command


class NetworkTool(QObject):
    """Network configuration and management tool.

    This class provides functionality for network interface management,
    connection diagnostics, IP configuration, and network testing - all
    while silently contemplating the fragility of our digital connections
    in an indifferent universe.

    Like packets traversing the vast digital expanse only to be dropped
    without ceremony, this class sends forth its functions into the void
    of the operating system, hoping for acknowledgment but prepared for
    the inevitable timeout of its existence.
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    request_input = pyqtSignal(str, str)
    network_info_updated = pyqtSignal(dict)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize the network tool.

        Args:
            parent: Optional parent QObject

        Like all digital beginnings, we emerge into an uncertain network
        environment, armed only with signals and the capacity for disappointment.
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Store network interface data
        self.interfaces: Dict[str, Dict[str, Any]] = {}
        self.selected_interface: Optional[str] = None
        self.wireless_available: bool = False

        # Cache for DNS servers
        self.dns_servers: List[str] = []

        # Check for required tools
        self._check_required_tools()

        self.logger.debug("Network tool initialized - preparing to navigate the labyrinth of connectivity")

    def _check_required_tools(self) -> None:
        """Check for required network tools and commands."""
        try:
            required_tools = [
                "ip", "ping", "traceroute", "dig", "nmcli", "iwconfig", "ss"
            ]

            missing_tools = []
            for tool in required_tools:
                result = subprocess.run(
                    ["which", tool],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.returncode != 0:
                    missing_tools.append(tool)

            # Report missing tools but continue - we'll handle missing tools when needed
            if missing_tools:
                self.logger.warning(f"Missing network tools: {', '.join(missing_tools)}")
                self.log_output.emit(f"Note: Some network tools are not available: {', '.join(missing_tools)}")

        except Exception as e:
            self.logger.error(f"Error checking network tools: {str(e)}")
            # Non-fatal error, continue initialization

    def get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all network interfaces.

        Returns:
            Dictionary mapping interface names to their properties

        Like a census taker counting digital citizens, this method
        catalogs all the network interfaces yearning for connection
        in the void of your machine.
        """
        try:
            self.log_output.emit("Scanning network interfaces...")
            self.update_progress.emit(10)

            # Get interface list using 'ip' command
            result = execute_command(["ip", "-j", "addr", "show"], return_output=True)
            if not isinstance(result, str):
                raise Exception("Failed to execute ip addr command")

            # Parse JSON output
            interfaces_data = json.loads(result)

            # Process each interface
            self.interfaces = {}
            for interface in interfaces_data:
                # Skip loopback interface
                if interface.get("ifname") == "lo":
                    continue

                ifname = interface.get("ifname", "unknown")
                self.interfaces[ifname] = {
                    "name": ifname,
                    "type": self._determine_interface_type(ifname),
                    "mac_address": interface.get("address", ""),
                    "state": interface.get("operstate", "unknown"),
                    "addresses": [],
                    "wireless": False,
                    "wireless_info": {}
                }

                # Extract IP addresses
                for addr_info in interface.get("addr_info", []):
                    ip = addr_info.get("local", "")
                    prefix = addr_info.get("prefixlen", "")
                    family = addr_info.get("family", "")

                    if ip and prefix and family:
                        addr_type = "ipv4" if family == "inet" else "ipv6"
                        self.interfaces[ifname]["addresses"].append({
                            "address": ip,
                            "prefix": prefix,
                            "type": addr_type
                        })

            # Check which interfaces are wireless
            self._identify_wireless_interfaces()

            # Get additional interface information
            self._get_interface_details()

            # Get DNS server information
            self.dns_servers = self._get_dns_servers()

            self.update_progress.emit(100)
            self.log_output.emit(f"Found {len(self.interfaces)} network interfaces")

            # Notify about wireless capability
            wireless_interfaces = [name for name, data in self.interfaces.items()
                                 if data.get("wireless", False)]

            if wireless_interfaces:
                self.wireless_available = True
                self.log_output.emit(f"Wireless interfaces available: {', '.join(wireless_interfaces)}")

            # Emit signal with network info
            self.network_info_updated.emit(self.interfaces)

            return self.interfaces

        except json.JSONDecodeError as e:
            self.error_occurred.emit(f"Error parsing network interface data: {str(e)}")
            self.logger.error(f"JSON parse error in get_network_interfaces: {str(e)}")
            return {}
        except Exception as e:
            self.error_occurred.emit(f"Error getting network interfaces: {str(e)}")
            self.logger.error(f"Error in get_network_interfaces: {str(e)}")
            return {}

    def _determine_interface_type(self, ifname: str) -> str:
        """Determine the type of network interface based on name and properties.

        Args:
            ifname: Interface name

        Returns:
            Interface type string (ethernet, wireless, virtual, etc.)
        """
        # Common naming patterns
        if ifname.startswith("en") or ifname.startswith("eth"):
            return "ethernet"
        elif ifname.startswith("wl"):
            return "wireless"
        elif ifname.startswith("ww"):
            return "wwan"  # Wireless WAN (cellular)
        elif ifname.startswith("br"):
            return "bridge"
        elif ifname.startswith("tun") or ifname.startswith("tap"):
            return "tunnel"
        elif ifname.startswith("docker") or ifname.startswith("veth"):
            return "virtual"
        elif ifname.startswith("virbr"):
            return "virtual_bridge"
        else:
            return "other"

    def _identify_wireless_interfaces(self) -> None:
        """Identify which interfaces are wireless using multiple detection methods.

        Like an archaeologist attempting to decipher ancient hieroglyphs with multiple
        Rosetta stones, we employ various techniques to identify wireless interfaces,
        knowing full well that the universe's entropy ensures some systems will remain
        stubbornly inscrutable regardless of our efforts.
        """
        try:
            # Method 1: Use iwconfig (traditional but not always reliable)
            iwconfig_detected = set()
            result = execute_command(["iwconfig"], return_output=True)
            if isinstance(result, str):
                # Process output to identify wireless interfaces
                current_interface = None
                for line in result.split('\n'):
                    if not line.startswith(' '):
                        # This is a new interface line
                        parts = line.split()
                        if len(parts) > 0:
                            current_interface = parts[0]
                            # Check if it's a wireless interface (not "no wireless extensions")
                            if "no wireless extensions" not in line and current_interface in self.interfaces:
                                self.interfaces[current_interface]["wireless"] = True
                                iwconfig_detected.add(current_interface)

            # Method 2: Check for wireless interfaces by naming convention
            # Common wireless interface naming patterns
            wireless_patterns = ['wlan', 'wlp', 'wls', 'wifi', 'ath', 'wl']
            for ifname in self.interfaces:
                for pattern in wireless_patterns:
                    if ifname.startswith(pattern):
                        self.interfaces[ifname]["wireless"] = True
                        self.logger.debug(f"Interface {ifname} identified as wireless by naming pattern")

            # Method 3: Check /sys/class/net/{ifname}/wireless directory existence
            for ifname in self.interfaces:
                if os.path.exists(f"/sys/class/net/{ifname}/wireless"):
                    self.interfaces[ifname]["wireless"] = True
                    self.logger.debug(f"Interface {ifname} identified as wireless by sysfs")

            # Method 4: Use iw dev command as a fallback
            if not any(self.interfaces.get(ifname, {}).get("wireless", False) for ifname in self.interfaces):
                result = execute_command(["iw", "dev"], return_output=True)
                if isinstance(result, str):
                    current_interface = None
                    for line in result.split('\n'):
                        if "Interface" in line:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                ifname = parts[1]
                                if ifname in self.interfaces:
                                    self.interfaces[ifname]["wireless"] = True
                                    self.logger.debug(f"Interface {ifname} identified as wireless by iw dev")

            # Log the results of our archaeological expedition into interface taxonomy
            wireless_interfaces = [name for name, data in self.interfaces.items()
                                   if data.get("wireless", False)]

            if wireless_interfaces:
                self.logger.info(f"Identified wireless interfaces: {', '.join(wireless_interfaces)}")
            else:
                self.logger.warning("No wireless interfaces detected despite wireless connectivity being reported")
                # One last desperate attempt - log all interfaces for debugging
                self.logger.debug(f"All detected interfaces: {', '.join(self.interfaces.keys())}")

        except Exception as e:
            self.logger.warning(f"Error identifying wireless interfaces: {str(e)}")
            # Non-fatal error, continue without wireless identification
            # The digital void swallows our error silently, another small tragedy

    def _get_interface_details(self) -> None:
        """Get additional details about network interfaces."""
        # Get interface statistics
        for ifname in self.interfaces:
            try:
                # Get link statistics
                stats_result = execute_command(
                    ["ip", "-s", "link", "show", ifname],
                    return_output=True
                )

                if isinstance(stats_result, str):
                    # Parse the statistics
                    self.interfaces[ifname]["statistics"] = self._parse_interface_statistics(stats_result)

                # For wireless interfaces, get wireless details
                if self.interfaces[ifname].get("wireless", False):
                    self._get_wireless_details(ifname)

            except Exception as e:
                self.logger.warning(f"Error getting details for interface {ifname}: {str(e)}")
                continue

    def _parse_interface_statistics(self, stats_output: str) -> Dict[str, Any]:
        """Parse interface statistics from ip -s link output.

        Args:
            stats_output: Output from ip -s link command

        Returns:
            Dictionary of parsed statistics
        """
        stats = {
            "rx_bytes": 0,
            "rx_packets": 0,
            "rx_errors": 0,
            "tx_bytes": 0,
            "tx_packets": 0,
            "tx_errors": 0
        }

        lines = stats_output.split('\n')
        rx_line_idx = None
        tx_line_idx = None

        # Find RX and TX lines
        for i, line in enumerate(lines):
            if "RX:" in line:
                rx_line_idx = i
            elif "TX:" in line and rx_line_idx is not None:
                tx_line_idx = i
                break

        if rx_line_idx is not None and rx_line_idx + 1 < len(lines):
            # Parse RX statistics (bytes, packets, errors)
            rx_parts = lines[rx_line_idx + 1].strip().split()
            if len(rx_parts) >= 3:
                stats["rx_bytes"] = int(rx_parts[0])
                stats["rx_packets"] = int(rx_parts[1])
                stats["rx_errors"] = int(rx_parts[2])

        if tx_line_idx is not None and tx_line_idx + 1 < len(lines):
            # Parse TX statistics (bytes, packets, errors)
            tx_parts = lines[tx_line_idx + 1].strip().split()
            if len(tx_parts) >= 3:
                stats["tx_bytes"] = int(tx_parts[0])
                stats["tx_packets"] = int(tx_parts[1])
                stats["tx_errors"] = int(tx_parts[2])

        return stats

    def _get_wireless_details(self, ifname: str) -> None:
        """Get details about wireless interface.

        Args:
            ifname: Interface name
        """
        try:
            # Try using iwconfig for detailed wireless information
            result = execute_command(["iwconfig", ifname], return_output=True)

            if not isinstance(result, str):
                return

            wireless_info = {
                "ssid": "",
                "mode": "",
                "frequency": "",
                "access_point": "",
                "bit_rate": "",
                "signal_level": ""
            }

            # Extract SSID
            ssid_match = re.search(r'ESSID:"([^"]*)"', result)
            if ssid_match:
                wireless_info["ssid"] = ssid_match.group(1)

            # Extract Mode
            mode_match = re.search(r'Mode:(\S+)', result)
            if mode_match:
                wireless_info["mode"] = mode_match.group(1)

            # Extract Frequency
            freq_match = re.search(r'Frequency:(\S+)', result)
            if freq_match:
                wireless_info["frequency"] = freq_match.group(1)

            # Extract Access Point
            ap_match = re.search(r'Access Point: (\S+)', result)
            if ap_match:
                wireless_info["access_point"] = ap_match.group(1)

            # Extract Bit Rate
            bitrate_match = re.search(r'Bit Rate=(\S+)', result)
            if bitrate_match:
                wireless_info["bit_rate"] = bitrate_match.group(1)

            # Extract Signal Level
            signal_match = re.search(r'Signal level=(\S+)', result)
            if signal_match:
                wireless_info["signal_level"] = signal_match.group(1)

            # Store the wireless information
            self.interfaces[ifname]["wireless_info"] = wireless_info

            # Try to get list of available wireless networks
            self._scan_wireless_networks(ifname)

        except Exception as e:
            self.logger.warning(f"Error getting wireless details for {ifname}: {str(e)}")

    def _scan_wireless_networks(self, ifname: str) -> None:
        """Scan for available wireless networks.

        Args:
            ifname: Wireless interface name
        """
        try:
            # Only attempt if we have nmcli available
            which_result = subprocess.run(
                ["which", "nmcli"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if which_result.returncode != 0:
                self.logger.debug("nmcli not available, skipping wireless scan")
                return

            # Use nmcli to scan for networks
            self.log_output.emit(f"Scanning for wireless networks on {ifname}...")

            result = execute_command(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", "ifname", ifname],
                return_output=True
            )

            if not isinstance(result, str):
                return

            # Parse networks
            networks = []
            for line in result.split('\n'):
                if line.strip():
                    parts = line.split(':')
                    if len(parts) >= 3:
                        networks.append({
                            "ssid": parts[0],
                            "signal": parts[1],
                            "security": parts[2]
                        })

            # Store the available networks
            self.interfaces[ifname]["available_networks"] = networks

            self.log_output.emit(f"Found {len(networks)} wireless networks")

        except Exception as e:
            self.logger.warning(f"Error scanning wireless networks: {str(e)}")

    def _get_dns_servers(self) -> List[str]:
        """Get configured DNS servers.

        Returns:
            List of DNS server IP addresses

        Like archaeologists digging for the ancient guides of network navigation,
        we extract the DNS servers that translate human-readable domains into
        the numerical addresses machines understand.
        """
        dns_servers = []

        try:
            # Try reading from /etc/resolv.conf first
            if os.path.exists("/etc/resolv.conf"):
                with open("/etc/resolv.conf", 'r') as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                dns_servers.append(parts[1])

            # If that didn't work, try using nmcli
            if not dns_servers:
                result = execute_command(
                    ["nmcli", "-t", "-f", "IP4.DNS", "device", "show"],
                    return_output=True
                )

                if isinstance(result, str):
                    for line in result.split('\n'):
                        if line.startswith("IP4.DNS:"):
                            parts = line.strip().split(':')
                            if len(parts) >= 2:
                                dns_servers.append(parts[1])

            return dns_servers

        except Exception as e:
            self.logger.warning(f"Error getting DNS servers: {str(e)}")
            return []

    def select_interface(self, interface_name: str) -> bool:
        """Select a network interface for operations.

        Args:
            interface_name: Name of the interface to select

        Returns:
            True if interface was successfully selected

        Like choosing a champion for network jousting, this method
        selects one interface from many to be the focus of our attention.
        """
        try:
            if interface_name not in self.interfaces:
                self.error_occurred.emit(f"Interface {interface_name} not found")
                return False

            self.selected_interface = interface_name
            self.log_output.emit(f"Selected interface: {interface_name}")

            # Display interface details
            interface = self.interfaces[interface_name]
            interface_type = interface.get("type", "unknown")
            state = interface.get("state", "unknown")

            self.log_output.emit(f"Interface type: {interface_type}")
            self.log_output.emit(f"Status: {state}")

            # Show addresses
            addresses = interface.get("addresses", [])
            if addresses:
                self.log_output.emit("IP Addresses:")
                for addr in addresses:
                    self.log_output.emit(f"  {addr['address']}/{addr['prefix']} ({addr['type']})")
            else:
                self.log_output.emit("No IP addresses configured")

            # Show wireless details if applicable
            if interface.get("wireless", False):
                wireless_info = interface.get("wireless_info", {})
                if wireless_info.get("ssid"):
                    self.log_output.emit(f"Connected to wireless network: {wireless_info.get('ssid', '')}")
                    self.log_output.emit(f"Signal level: {wireless_info.get('signal_level', '')}")
                else:
                    self.log_output.emit("Not connected to any wireless network")

            return True

        except Exception as e:
            self.error_occurred.emit(f"Error selecting interface: {str(e)}")
            self.logger.error(f"Error in select_interface: {str(e)}")
            return False

    def get_connection_status(self, target: str = "1.1.1.1") -> Dict[str, Any]:
        """Get connectivity status by pinging a target.

        Args:
            target: IP address or hostname to ping

        Returns:
            Dictionary with connection status information

        Like tapping on a wall to check for hollow spaces, we ping
        distant hosts to see if our network tunnels are open.
        """
        if not self.selected_interface:
            self.error_occurred.emit("No interface selected")
            return {"success": False, "error": "No interface selected"}

        try:
            self.log_output.emit(f"Testing connection by pinging {target}...")
            self.update_progress.emit(10)

            # Ping with a specific interface
            result = execute_command(
                ["ping", "-c", "4", "-I", self.selected_interface, target],
                return_output=True
            )

            self.update_progress.emit(100)

            if not isinstance(result, str):
                return {"success": False, "error": "Ping command failed"}

            # Parse ping results
            packet_loss_match = re.search(r'(\d+)% packet loss', result)
            packet_loss = 100.0
            if packet_loss_match:
                packet_loss = float(packet_loss_match.group(1))

            rtt_match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)', result)
            rtt_avg = None
            if rtt_match:
                rtt_avg = float(rtt_match.group(2))

            success = packet_loss < 100

            if success:
                self.log_output.emit(f"Connection test successful. Packet loss: {packet_loss}%, Average RTT: {rtt_avg} ms")
            else:
                self.log_output.emit(f"Connection test failed. {packet_loss}% packet loss.")

            return {
                "success": success,
                "packet_loss": packet_loss,
                "rtt_avg": rtt_avg,
                "output": result
            }

        except Exception as e:
            error_msg = f"Error testing connection: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def run_traceroute(self, target: str = "1.1.1.1") -> Dict[str, Any]:
        """Run a traceroute to a target host.

        Args:
            target: IP address or hostname for traceroute

        Returns:
            Dictionary with traceroute results

        Like an explorer mapping the path through a digital jungle,
        we trace each hop along the route to our destination.
        """
        if not self.selected_interface:
            self.error_occurred.emit("No interface selected")
            return {"success": False, "error": "No interface selected"}

        try:
            self.log_output.emit(f"Running traceroute to {target}...")
            self.update_progress.emit(10)

            # Run traceroute (note: not all traceroute versions support -i for interface)
            result = execute_command(
                ["traceroute", "-m", "15", target],
                return_output=True
            )

            self.update_progress.emit(100)

            if not isinstance(result, str):
                return {"success": False, "error": "Traceroute command failed"}

            # Parse traceroute output
            hops = []
            for line in result.split('\n'):
                if not line.strip() or "traceroute to" in line:
                    continue

                # Extract hop information
                match = re.match(r'^\s*(\d+)(?:\s+\*\s+\*\s+\*|(?:\s+(?:(\d+.\d+) ms|\*)){1,3}(?:\s+([^\s]+)(?:\s+\(([\d.]+)\))?)?)$', line)
                if match:
                    hop_num = int(match.group(1))
                    hop_time = match.group(2)
                    hop_host = match.group(3)
                    hop_ip = match.group(4)

                    hops.append({
                        "hop": hop_num,
                        "time": float(hop_time) if hop_time else None,
                        "host": hop_host if hop_host else "*",
                        "ip": hop_ip
                    })

            self.log_output.emit(f"Traceroute completed with {len(hops)} hops")

            # Output formatted traceroute
            self.log_output.emit("\nTraceroute results:")
            for hop in hops:
                time_str = f"{hop['time']:.2f} ms" if hop['time'] else "*"
                host_str = hop['host'] if hop['host'] else "*"
                if hop['ip']:
                    host_str += f" ({hop['ip']})"
                self.log_output.emit(f"  {hop['hop']}: {time_str} {host_str}")

            return {
                "success": True,
                "hops": hops,
                "output": result
            }

        except Exception as e:
            error_msg = f"Error running traceroute: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def test_dns(self, domain: str = "www.google.com") -> Dict[str, Any]:
        """Test DNS resolution for a domain.

        Args:
            domain: Domain name to resolve

        Returns:
            Dictionary with DNS test results

        Like a translator interpreting ancient texts, DNS servers convert
        human-readable domain names into the IP addresses machines understand.
        """
        try:
            self.log_output.emit(f"Testing DNS resolution for {domain}...")
            self.update_progress.emit(10)

            # First try with Python's socket module
            start_time = time.time()
            try:
                ip_address = socket.gethostbyname(domain)
                resolution_time = time.time() - start_time

                self.log_output.emit(f"Resolved {domain} to {ip_address} in {resolution_time:.3f} seconds")

                result = {
                    "success": True,
                    "domain": domain,
                    "ip": ip_address,
                    "time": resolution_time
                }

            except socket.gaierror:
                self.log_output.emit(f"Failed to resolve {domain} using Python's DNS resolver")
                result = {"success": False, "error": "DNS resolution failed"}

            # Also try with dig for more detailed information
            if self._check_command_exists("dig"):
                dig_result = execute_command(
                    ["dig", "+short", domain],
                    return_output=True
                )

                if isinstance(dig_result, str) and dig_result.strip():
                    # Parse dig results (multiple IPs possible)
                    ips = [line for line in dig_result.strip().split('\n') if line]
                    result["all_ips"] = ips

                    self.log_output.emit(f"All resolved IPs: {', '.join(ips)}")

            self.update_progress.emit(100)
            return result

        except Exception as e:
            error_msg = f"Error testing DNS: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def get_routing_table(self) -> Dict[str, Any]:
        """Get the system's routing table.

        Returns:
            Dictionary with routing table information

        Like examining a map of all possible paths through the digital landscape,
        this method reveals how traffic is directed through the network topology.
        """
        try:
            self.log_output.emit("Retrieving routing table...")
            self.update_progress.emit(10)

            # Get routing table with 'ip route' command
            result = execute_command(
                ["ip", "-j", "route"],
                return_output=True
            )

            self.update_progress.emit(50)

            if not isinstance(result, str):
                return {"success": False, "error": "Failed to get routing table"}

            # Parse JSON output
            routes = json.loads(result)

            # Format for display
            self.log_output.emit("\nRouting Table:")

            # Group routes by destination
            for route in routes:
                dst = route.get("dst", "default")
                dev = route.get("dev", "unknown")
                gateway = route.get("gateway", "direct")

                self.log_output.emit(f"  {dst} via {gateway} dev {dev}")

            self.update_progress.emit(100)

            return {
                "success": True,
                "routes": routes
            }

        except json.JSONDecodeError as e:
            error_msg = f"Error parsing routing table: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error getting routing table: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def get_connection_statistics(self) -> Dict[str, Any]:
        """Get connection statistics and active connections.

        Returns:
            Dictionary with connection statistics

        Like a census taker counting digital inhabitants, this method
        tallies the active connections between your machine and others.
        """
        if not self.selected_interface:
            self.error_occurred.emit("No interface selected")
            return {"success": False, "error": "No interface selected"}

        try:
            self.log_output.emit("Retrieving connection statistics...")
            self.update_progress.emit(10)

            # Use 'ss' command to get statistics
            result = execute_command(
                ["ss", "-tuipn"],
                return_output=True
            )

            self.update_progress.emit(40)

            if not isinstance(result, str):
                return {"success": False, "error": "Failed to get connection statistics"}

            # Parse connections
            connections = {
                "tcp": [],
                "udp": []
            }

            lines = result.split('\n')
            for line in lines[1:]:  # Skip header
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 5:
                    proto = parts[0].lower()
                    if proto in ("tcp", "udp"):
                        # Extract local and remote addresses
                        local = parts[3]
                        remote = parts[4]

                        # Extract state for TCP
                        state = parts[1] if proto == "tcp" else "n/a"

                        connections[proto].append({
                            "local": local,
                            "remote": remote,
                            "state": state
                        })

            # Get interface stats
            if self.selected_interface in self.interfaces:
                stats = self.interfaces[self.selected_interface].get("statistics", {})
                tx_bytes = stats.get("tx_bytes", 0)
                rx_bytes = stats.get("rx_bytes", 0)

                # Format for human-readable output
                tx_mb = tx_bytes / (1024 * 1024)
                rx_mb = rx_bytes / (1024 * 1024)

                self.log_output.emit(f"\nNetwork Statistics for {self.selected_interface}:")
                self.log_output.emit(f"  Received: {rx_mb:.2f} MB ({stats.get('rx_packets', 0)} packets)")
                self.log_output.emit(f"  Sent: {tx_mb:.2f} MB ({stats.get('tx_packets', 0)} packets)")
                self.log_output.emit(f"  Errors - RX: {stats.get('rx_errors', 0)}, TX: {stats.get('tx_errors', 0)}")

            # Display connection counts
            tcp_count = len(connections["tcp"])
            udp_count = len(connections["udp"])

            self.log_output.emit(f"\nActive Connections:")
            self.log_output.emit(f"  TCP: {tcp_count} connections")
            self.log_output.emit(f"  UDP: {udp_count} connections")

            # Show some active connections as examples
            if tcp_count > 0:
                self.log_output.emit("\nSample TCP Connections:")
                for i, conn in enumerate(connections["tcp"][:5]):  # Show up to 5
                    self.log_output.emit(f"  {conn['local']} → {conn['remote']} ({conn['state']})")

                if tcp_count > 5:
                    self.log_output.emit(f"  ... and {tcp_count - 5} more")

            self.update_progress.emit(100)

            return {
                "success": True,
                "connections": connections,
                "tcp_count": tcp_count,
                "udp_count": udp_count,
                "stats": stats if self.selected_interface in self.interfaces else {}
            }

        except Exception as e:
            error_msg = f"Error getting connection statistics: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def configure_dhcp(self) -> bool:
        """Configure selected interface to use DHCP.

        Returns:
            True if configuration was successful

        Like surrendering to the chaotic whims of the network gods,
        we let DHCP assign our digital identity instead of crafting it ourselves.
        """
        if not self.selected_interface:
            self.error_occurred.emit("No interface selected")
            return False

        try:
            self.log_output.emit(f"Configuring {self.selected_interface} to use DHCP...")
            self.update_progress.emit(10)

            # Check if NetworkManager is available
            if self._check_command_exists("nmcli"):
                # Use NetworkManager
                result = execute_command(
                    ["sudo", "nmcli", "device", "modify", self.selected_interface, "ipv4.method", "auto"],
                    return_output=False
                )

                if isinstance(result, int) and result != 0:
                    self.error_occurred.emit("Failed to configure DHCP with NetworkManager")
                    return False

                # Apply changes
                execute_command(
                    ["sudo", "nmcli", "device", "reapply", self.selected_interface],
                    return_output=False
                )

                self.log_output.emit("DHCP configuration applied successfully")

            else:
                # Fallback to ifconfig/dhclient
                # Down the interface
                execute_command(
                    ["sudo", "ip", "link", "set", self.selected_interface, "down"],
                    return_output=False
                )

                # Remove any static IP addresses
                execute_command(
                    ["sudo", "ip", "addr", "flush", "dev", self.selected_interface],
                    return_output=False
                )

                # Up the interface
                execute_command(
                    ["sudo", "ip", "link", "set", self.selected_interface, "up"],
                    return_output=False
                )

                # Run dhclient
                result = execute_command(
                    ["sudo", "dhclient", "-v", self.selected_interface],
                    return_output=False
                )

                if isinstance(result, int) and result != 0:
                    self.error_occurred.emit("Failed to configure DHCP with dhclient")
                    return False

                self.log_output.emit("DHCP configuration applied successfully")

            self.update_progress.emit(100)

            # Update interface information
            self.get_network_interfaces()

            return True

        except Exception as e:
            error_msg = f"Error configuring DHCP: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            self.update_progress.emit(0)
            return False

    def configure_static_ip(self, ip_address: str, prefix_len: int,
                           gateway: str, dns_servers: List[str]) -> bool:
        """Configure static IP address for selected interface.

        Args:
            ip_address: Static IP address to set
            prefix_len: Network prefix length (e.g., 24 for /24)
            gateway: Gateway IP address
            dns_servers: List of DNS server IP addresses

        Returns:
            True if configuration was successful

        Like a digital hermit staking a permanent claim in the network wilderness,
        we assign ourselves a fixed address amidst the chaos of dynamic allocation.
        """
        if not self.selected_interface:
            self.error_occurred.emit("No interface selected")
            return False

        try:
            # Validate inputs
            try:
                # Check IP address
                ipaddress.ip_address(ip_address)

                # Check gateway
                ipaddress.ip_address(gateway)

                # Check prefix length
                if not (0 <= prefix_len <= 32):
                    raise ValueError("Prefix length must be between 0 and 32")

                # Check DNS servers
                for dns in dns_servers:
                    ipaddress.ip_address(dns)

            except ValueError as e:
                self.error_occurred.emit(f"Invalid network configuration: {str(e)}")
                return False

            self.log_output.emit(f"Configuring static IP {ip_address}/{prefix_len} on {self.selected_interface}...")
            self.update_progress.emit(10)

            # Use NetworkManager if available
            if self._check_command_exists("nmcli"):
                # Use NetworkManager
                cmds = [
                    ["sudo", "nmcli", "device", "modify", self.selected_interface,
                     "ipv4.method", "manual",
                     f"ipv4.addresses", f"{ip_address}/{prefix_len}",
                     "ipv4.gateway", gateway]
                ]

                # Add DNS servers
                if dns_servers:
                    dns_str = ",".join(dns_servers)
                    cmds.append(["sudo", "nmcli", "device", "modify", self.selected_interface,
                                "ipv4.dns", dns_str])

                # Execute commands
                for cmd in cmds:
                    result = execute_command(cmd, return_output=False)
                    if isinstance(result, int) and result != 0:
                        self.error_occurred.emit(f"Failed to configure static IP with NetworkManager")
                        return False

                # Apply changes
                execute_command(
                    ["sudo", "nmcli", "device", "reapply", self.selected_interface],
                    return_output=False
                )

            else:
                # Fallback to ip commands
                # Down the interface
                execute_command(
                    ["sudo", "ip", "link", "set", self.selected_interface, "down"],
                    return_output=False
                )

                # Remove any existing IP addresses
                execute_command(
                    ["sudo", "ip", "addr", "flush", "dev", self.selected_interface],
                    return_output=False
                )

                # Set the new IP address
                result = execute_command(
                    ["sudo", "ip", "addr", "add", f"{ip_address}/{prefix_len}", "dev", self.selected_interface],
                    return_output=False
                )

                if isinstance(result, int) and result != 0:
                    self.error_occurred.emit("Failed to set static IP address")
                    return False

                # Up the interface
                execute_command(
                    ["sudo", "ip", "link", "set", self.selected_interface, "up"],
                    return_output=False
                )

                # Set the default gateway
                execute_command(
                    ["sudo", "ip", "route", "add", "default", "via", gateway],
                    return_output=False
                )

                # Set DNS servers by writing to resolv.conf
                dns_content = "\n".join([f"nameserver {dns}" for dns in dns_servers])

                try:
                    # Write to a temporary file first
                    with open("/tmp/resolv.conf.tmp", "w") as f:
                        f.write(dns_content)

                    # Use sudo to move it to /etc/resolv.conf
                    execute_command(
                        ["sudo", "mv", "/tmp/resolv.conf.tmp", "/etc/resolv.conf"],
                        return_output=False
                    )
                except Exception as dns_error:
                    self.logger.warning(f"Failed to set DNS servers: {str(dns_error)}")

            self.log_output.emit(f"Static IP configuration applied successfully")
            self.log_output.emit(f"IP Address: {ip_address}/{prefix_len}")
            self.log_output.emit(f"Gateway: {gateway}")
            self.log_output.emit(f"DNS Servers: {', '.join(dns_servers)}")

            self.update_progress.emit(100)

            # Update interface information
            self.get_network_interfaces()

            return True

        except Exception as e:
            error_msg = f"Error configuring static IP: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            self.update_progress.emit(0)
            return False

    def connect_wireless(self, ssid: str, password: Optional[str] = None,
                        security_type: str = "wpa-psk") -> bool:
        """Connect to a wireless network.

        Args:
            ssid: Wireless network SSID to connect to
            password: Optional network password
            security_type: Network security type (wpa-psk, wpa-eap, etc.)

        Returns:
            True if connection was successful

        Like a digital courtship dance, we attempt to woo the wireless network
        with our credentials, hoping for a successful connection.
        """
        if not self.selected_interface:
            self.error_occurred.emit("No interface selected")
            return False

        # Check if interface is wireless
        if not self.interfaces.get(self.selected_interface, {}).get("wireless", False):
            self.error_occurred.emit(f"Interface {self.selected_interface} is not a wireless interface")
            return False

        try:
            self.log_output.emit(f"Connecting to wireless network: {ssid}...")
            self.update_progress.emit(10)

            # Check if NetworkManager is available
            if self._check_command_exists("nmcli"):
                # Use NetworkManager
                if password:
                    result = execute_command(
                        ["sudo", "nmcli", "device", "wifi", "connect", ssid, "password", password,
                         "ifname", self.selected_interface],
                        return_output=True
                    )
                else:
                    result = execute_command(
                        ["sudo", "nmcli", "device", "wifi", "connect", ssid,
                         "ifname", self.selected_interface],
                        return_output=True
                    )

                if not isinstance(result, str) or "successfully activated" not in result:
                    self.error_occurred.emit(f"Failed to connect to wireless network: {ssid}")
                    self.log_output.emit("Note: If the network is hidden or has unusual security, "
                                       "please use the system network settings.")
                    return False

                self.log_output.emit(f"Successfully connected to {ssid}")

            else:
                # Fallback to wpa_supplicant
                self.error_occurred.emit("NetworkManager not available. Please use the system network settings.")
                return False

            self.update_progress.emit(100)

            # Update interface information
            self.get_network_interfaces()

            return True

        except Exception as e:
            error_msg = f"Error connecting to wireless network: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            self.update_progress.emit(0)
            return False

    def scan_wireless_networks(self) -> List[Dict[str, Any]]:
        """Scan for available wireless networks.

        Returns:
            List of dictionaries with wireless network information

        Like a digital explorer surveying the ethereal landscape of radio waves,
        we scan for the invisible networks that permeate our physical space.
        """
        if not self.selected_interface:
            self.error_occurred.emit("No interface selected")
            return []

        # Check if interface is wireless
        if not self.interfaces.get(self.selected_interface, {}).get("wireless", False):
            self.error_occurred.emit(f"Interface {self.selected_interface} is not a wireless interface")
            return []

        try:
            self.log_output.emit(f"Scanning for wireless networks...")
            self.update_progress.emit(10)

            # Check if NetworkManager is available
            if self._check_command_exists("nmcli"):
                # Use NetworkManager to scan
                result = execute_command(
                    ["sudo", "nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,CHAN,BSSID", "device", "wifi", "list",
                     "--rescan", "yes", "ifname", self.selected_interface],
                    return_output=True
                )

                if not isinstance(result, str):
                    self.error_occurred.emit("Failed to scan for wireless networks")
                    return []

                # Parse networks
                networks = []
                seen_ssids = set()  # To handle duplicate SSIDs

                for line in result.split('\n'):
                    if line.strip():
                        parts = line.split(':')
                        if len(parts) >= 3:
                            ssid = parts[0]

                            # Skip empty SSIDs or already seen SSIDs
                            if not ssid or ssid in seen_ssids:
                                continue

                            seen_ssids.add(ssid)

                            signal = int(parts[1]) if parts[1].isdigit() else 0
                            security = parts[2] if len(parts) > 2 else ""
                            channel = parts[3] if len(parts) > 3 else ""
                            bssid = parts[4] if len(parts) > 4 else ""

                            networks.append({
                                "ssid": ssid,
                                "signal": signal,
                                "security": security,
                                "channel": channel,
                                "bssid": bssid
                            })

                # Sort by signal strength
                networks.sort(key=lambda x: x["signal"], reverse=True)

                self.log_output.emit(f"Found {len(networks)} wireless networks")

                # Display networks
                self.log_output.emit("\nAvailable Wireless Networks:")
                for i, network in enumerate(networks, 1):
                    signal_bars = self._signal_strength_bars(network["signal"])
                    security = " 🔒" if network["security"] else ""
                    self.log_output.emit(f"  {i}. {network['ssid']} {signal_bars}{security}")

                self.update_progress.emit(100)

                # Store in interface data
                self.interfaces[self.selected_interface]["available_networks"] = networks

                return networks
            else:
                # Fallback to iwlist
                result = execute_command(
                    ["sudo", "iwlist", self.selected_interface, "scanning"],
                    return_output=True
                )

                if not isinstance(result, str):
                    self.error_occurred.emit("Failed to scan for wireless networks")
                    return []

                # Parse the iwlist output (more complex)
                networks = self._parse_iwlist_scan(result)

                self.log_output.emit(f"Found {len(networks)} wireless networks")

                # Display networks
                self.log_output.emit("\nAvailable Wireless Networks:")
                for i, network in enumerate(networks, 1):
                    signal_bars = self._signal_strength_bars(network["signal"])
                    security = " 🔒" if network.get("encryption", False) else ""
                    self.log_output.emit(f"  {i}. {network['ssid']} {signal_bars}{security}")

                self.update_progress.emit(100)

                # Store in interface data
                self.interfaces[self.selected_interface]["available_networks"] = networks

                return networks

        except Exception as e:
            error_msg = f"Error scanning for wireless networks: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            self.update_progress.emit(0)
            return []

    def _signal_strength_bars(self, signal: Union[int, str]) -> str:
        """Convert signal strength to a bar representation with existential awareness.

        Args:
            signal: Signal strength percentage (0-100)

        Returns:
            String representation of signal bars

        Like an artist converting the invisible electromagnetic waves into a
        visual representation humans can comprehend, we transform arbitrary
        numeric values into a meaningful pattern of symbols - regardless
        of the signal's original encoding.
        """
        # Ensure signal is numeric despite whatever form the void has provided
        if isinstance(signal, str):
            try:
                signal = int(signal)
            except (ValueError, TypeError):
                # In the face of absurdity, we default to the lowest signal
                signal = 0
        elif not isinstance(signal, (int, float)):
            signal = 0

        # Convert numeric value to symbolic representation
        if signal >= 80:
            return "▮▮▮▮▮"
        elif signal >= 60:
            return "▮▮▮▮▯"
        elif signal >= 40:
            return "▮▮▮▯▯"
        elif signal >= 20:
            return "▮▮▯▯▯"
        else:
            return "▮▯▯▯▯"

    def _parse_iwlist_scan(self, scan_output: str) -> List[Dict[str, Any]]:
        """Parse the output of iwlist scanning.

        Args:
            scan_output: Output from iwlist scanning

        Returns:
            List of wireless networks
        """
        networks = []
        current_network = None

        for line in scan_output.split('\n'):
            line = line.strip()

            # New cell indicates new network
            if "Cell" in line and "Address:" in line:
                # Save previous network if exists
                if current_network and 'ssid' in current_network:
                    networks.append(current_network)

                # Start new network
                current_network = {
                    "bssid": line.split("Address:")[1].strip(),
                    "signal": 0,
                    "encryption": False,
                    "ssid": ""
                }

            # Skip if no current network
            if not current_network:
                continue

            # Extract SSID
            if "ESSID:" in line:
                essid = line.split("ESSID:")[1].strip('"')
                current_network["ssid"] = essid

            # Extract Signal level
            elif "Signal level=" in line:
                signal_str = line.split("Signal level=")[1].split()[0]

                # Handle different formats (dBm or percentage)
                if signal_str.endswith("dBm"):
                    # Convert dBm to percentage (-100 to -50 → 0 to 100%)
                    dbm = float(signal_str.rstrip("dBm"))
                    signal_percent = max(0, min(100, (dbm + 100) * 2))
                else:
                    # Already percentage
                    signal_percent = float(signal_str.rstrip("%"))

                current_network["signal"] = int(signal_percent)

            # Check encryption
            elif "Encryption key:on" in line:
                current_network["encryption"] = True

        # Add the last network
        if current_network and 'ssid' in current_network:
            networks.append(current_network)

        return networks

    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists on the system.

        Args:
            command: Command to check

        Returns:
            True if command exists and is executable
        """
        try:
            result = subprocess.run(
                ["which", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.returncode == 0
        except Exception:
            return False

    def start_monitoring(self, interval: int = 5) -> bool:
        """Start continuous monitoring of network interface statistics.

        Args:
            interval: Time between updates in seconds

        Returns:
            True if monitoring started successfully

        Like a vigilant sentinel standing watch over digital frontiers,
        this method initiates the endless cycle of observation, measuring
        the ebb and flow of data across our tenuous connections to the void.
        """
        if not self.selected_interface:
            self.error_occurred.emit("No interface selected for monitoring")
            return False

        try:
            from PyQt6.QtCore import QTimer

            # Store the initial statistics for calculating deltas
            if self.selected_interface in self.interfaces:
                self._initial_stats = self.interfaces[self.selected_interface].get("statistics", {}).copy()
            else:
                self._initial_stats = {}

            # Store the interval explicitly to avoid method/property confusion
            self._monitoring_interval = interval  # Store in seconds

            # Create monitoring timer if it doesn't exist
            if not hasattr(self, '_monitor_timer'):
                self._monitor_timer = QTimer()
                self._monitor_timer.timeout.connect(self._update_monitor_stats)

            # Set interval and start timer
            self._monitor_timer.setInterval(interval * 1000)  # Convert to milliseconds
            self._monitor_timer.start()

            self.log_output.emit(
                f"Started monitoring interface {self.selected_interface} (updates every {interval} seconds)")
            return True

        except Exception as e:
            error_msg = f"Failed to start network monitoring: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return False

    def stop_monitoring(self) -> None:
        """Stop network interface monitoring.

        Like a weary observer finally closing their eyes after a long vigil,
        this method terminates our ceaseless digital surveillance, allowing
        the network to flow unobserved once more.
        """
        if hasattr(self, '_monitor_timer') and self._monitor_timer.isActive():
            self._monitor_timer.stop()
            self.log_output.emit("Network monitoring stopped")

    def _update_monitor_stats(self) -> None:
        """Update network statistics during monitoring.

        Calculate and emit changes in network traffic since monitoring began,
        offering glimpses into the frenetic dance of packets traversing our
        digital nervous system - assuming, of course, that methods and integers
        can agree on their fundamental nature.
        """
        try:
            # Refresh interface data
            self.get_network_interfaces()

            if not self.selected_interface or self.selected_interface not in self.interfaces:
                self.stop_monitoring()
                self.error_occurred.emit("Selected interface is no longer available")
                return

            # Get current stats
            current_stats = self.interfaces[self.selected_interface].get("statistics", {})

            # Calculate deltas from initial stats
            if self._initial_stats:
                rx_bytes_delta = current_stats.get("rx_bytes", 0) - self._initial_stats.get("rx_bytes", 0)
                tx_bytes_delta = current_stats.get("tx_bytes", 0) - self._initial_stats.get("tx_bytes", 0)
                rx_packets_delta = current_stats.get("rx_packets", 0) - self._initial_stats.get("rx_packets", 0)
                tx_packets_delta = current_stats.get("tx_packets", 0) - self._initial_stats.get("tx_packets", 0)

                # Get interval in seconds - fixing the type confusion between method and property
                # A subtle reminder that in programming, as in life, identity matters
                if hasattr(self, '_monitoring_interval'):
                    # Use stored value if available
                    interval_seconds = self._monitoring_interval
                else:
                    # Fallback with defensive retrieval of timer interval
                    interval_seconds = 5  # Default to 5 seconds
                    if hasattr(self, '_monitor_timer'):
                        try:
                            # Handle both callable method and property cases
                            interval_ms = self._monitor_timer.interval() if callable(
                                self._monitor_timer.interval) else self._monitor_timer.interval
                            interval_seconds = interval_ms / 1000
                        except Exception:
                            self.logger.warning("Failed to get timer interval, using default")

                # Convert to KB/s
                rx_rate = rx_bytes_delta / (1024 * interval_seconds) if interval_seconds else 0  # KB/s
                tx_rate = tx_bytes_delta / (1024 * interval_seconds) if interval_seconds else 0  # KB/s

                # Create monitoring update
                monitor_data = {
                    "interface": self.selected_interface,
                    "rx_rate": rx_rate,
                    "tx_rate": tx_rate,
                    "rx_packets": rx_packets_delta,
                    "tx_packets": tx_packets_delta,
                    "state": self.interfaces[self.selected_interface].get("state", "unknown"),
                    "timestamp": time.time()
                }

                # Update the initial stats for the next interval
                self._initial_stats = current_stats.copy()

                # Emit monitoring update
                self.log_output.emit(
                    f"Network traffic: ↓ {rx_rate:.2f} KB/s ({rx_packets_delta} packets) | "
                    f"↑ {tx_rate:.2f} KB/s ({tx_packets_delta} packets)"
                )

                # Emit a signal with the monitoring data that the UI can use
                self.network_info_updated.emit({"monitor_data": monitor_data})

        except Exception as e:
            error_msg = f"Error updating network monitor: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)

    def export_traffic_data(self, filepath: str) -> bool:
        """Export network traffic data to a CSV file.

        Args:
            filepath: Path where the CSV file will be saved

        Returns:
            True if export was successful

        Like a digital archaeologist preserving artifacts of ephemeral transmissions,
        this method captures fleeting network statistics and entombs them in the
        structured sepulcher of a CSV file, a futile act of preservation in
        the face of the ever-flowing river of data.
        """
        if not self.selected_interface or self.selected_interface not in self.interfaces:
            self.error_occurred.emit("No valid interface selected for export")
            return False

        try:
            import csv
            from datetime import datetime

            # Get current interface stats
            interface = self.interfaces[self.selected_interface]
            stats = interface.get("statistics", {})
            addresses = interface.get("addresses", [])
            wireless_info = interface.get("wireless_info", {}) if interface.get("wireless", False) else {}

            # Format current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Prepare data for CSV
            header = [
                "Timestamp", "Interface", "Type", "State", "MAC Address",
                "IPv4 Addresses", "IPv6 Addresses", "RX Bytes", "TX Bytes",
                "RX Packets", "TX Packets", "RX Errors", "TX Errors"
            ]

            # Add wireless columns if applicable
            if interface.get("wireless", False):
                header.extend(["SSID", "Signal Level", "Frequency", "Bit Rate"])

            # Get IP addresses as comma-separated strings
            ipv4_addrs = []
            ipv6_addrs = []
            for addr in addresses:
                if addr.get("type") == "ipv4":
                    ipv4_addrs.append(f"{addr.get('address', '')}/{addr.get('prefix', '')}")
                elif addr.get("type") == "ipv6":
                    ipv6_addrs.append(f"{addr.get('address', '')}/{addr.get('prefix', '')}")

            # Prepare row data
            row = [
                timestamp,
                self.selected_interface,
                interface.get("type", "unknown"),
                interface.get("state", "unknown"),
                interface.get("mac_address", ""),
                ";".join(ipv4_addrs),
                ";".join(ipv6_addrs),
                stats.get("rx_bytes", 0),
                stats.get("tx_bytes", 0),
                stats.get("rx_packets", 0),
                stats.get("tx_packets", 0),
                stats.get("rx_errors", 0),
                stats.get("tx_errors", 0)
            ]

            # Add wireless info if applicable
            if interface.get("wireless", False):
                row.extend([
                    wireless_info.get("ssid", ""),
                    wireless_info.get("signal_level", ""),
                    wireless_info.get("frequency", ""),
                    wireless_info.get("bit_rate", "")
                ])

            # Write to CSV file
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                writer.writerow(row)

            self.log_output.emit(f"Network traffic data exported to: {filepath}")
            return True

        except Exception as e:
            error_msg = f"Failed to export traffic data: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return False

    # Add this method to create traffic monitoring log exports with multiple entries
    def export_monitoring_log(self, filepath: str, monitoring_data: List[Dict[str, Any]]) -> bool:
        """Export network monitoring log to a CSV file.

        Args:
            filepath: Path where the CSV file will be saved
            monitoring_data: List of monitoring data entries

        Returns:
            True if export was successful

        Like a historian meticulously recording the ebb and flow of digital tides,
        this method preserves the temporal patterns of network activity, creating
        a fossil record of our ephemeral connections to the void.
        """
        if not monitoring_data:
            self.error_occurred.emit("No monitoring data available for export")
            return False

        try:
            import csv
            from datetime import datetime

            # Prepare header
            header = [
                "Timestamp", "Interface", "State",
                "Download Speed (KB/s)", "Upload Speed (KB/s)",
                "Download Packets", "Upload Packets"
            ]

            # Create rows from monitoring data
            rows = []
            for entry in monitoring_data:
                timestamp = datetime.fromtimestamp(entry.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
                rows.append([
                    timestamp,
                    entry.get("interface", "unknown"),
                    entry.get("state", "unknown"),
                    entry.get("rx_rate", 0),
                    entry.get("tx_rate", 0),
                    entry.get("rx_packets", 0),
                    entry.get("tx_packets", 0)
                ])

            # Write to CSV file
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                writer.writerows(rows)

            self.log_output.emit(f"Network monitoring log exported to: {filepath}")
            return True

        except Exception as e:
            error_msg = f"Failed to export monitoring log: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return False

    def get_interface_names_by_type(self, interface_type: str = None) -> List[str]:
        """Get list of interface names, optionally filtered by type.

        Args:
            interface_type: Optional type to filter by (e.g., 'ethernet', 'wireless')

        Returns:
            List of interface names

        Like a census taker categorizing citizens by profession,
        this method groups our network interfaces by their digital vocations,
        allowing us to selectively communicate with those whose purpose
        aligns with our current needs.
        """
        try:
            # Get interfaces
            interfaces = self.interfaces

            # Filter by type if specified
            if interface_type:
                return [
                    name for name, data in interfaces.items()
                    if data.get("type", "") == interface_type
                ]

            # Return all interfaces
            return list(interfaces.keys())

        except Exception as e:
            error_msg = f"Error getting interface names: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return []