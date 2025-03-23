from dataclasses import dataclass


def _size_str_to_int(size: str) -> int:
    """
    Convert string notation of megabytes (e.g. 214.7M) to an integer value representing bytes (e.g. 225129267).
    :param size: String notation, megabytes (e.g. 214.7M)
    :returns: An integer value representing bytes (e.g. 225129267)
    """
    if size[-1] != "M":
        raise ValueError(f"Unsupported size suffix: {size[-1]} ({size})")
    return int(float(size.rstrip("M")) * 1048576)


@dataclass
class DiskStats:

    """Disk usage statistics and information about the underlying filesystem, obtained from the Rayhunter API.

    Size and percentage values are converted from string (e.g. 214.7M) to bytes (e.g. 225129267) for programmatic ease of use.

    Attributes:
        partition (str): The partition Rayhunter is mounted on (e.g. ubi0:usrfs).
        total_size (int): Total size of the disk in bytes (e.g. 225129267).
        used_size (int): The amount of disk space currently in use in bytes (e.g. 18350080).
        available_size (int): The amount of disk space currently available in bytes (e.g. 206884044).
        used_percent (int): The percentage of disk space currently in use (e.g. 8).
        mounted_on (str): Rayhunter's mount point (e.g. /data).

    """

    partition: str
    total_size: int
    used_size: int
    available_size: int
    used_percent: int
    mounted_on: str

    @staticmethod
    def from_dict(disk_stats: dict):
        for size_key in ["total_size", "used_size", "available_size"]:
            disk_stats[size_key] = _size_str_to_int(disk_stats[size_key])
        disk_stats["used_percent"] = int(disk_stats["used_percent"].rstrip("%"))
        return DiskStats(**disk_stats)


@dataclass
class MemoryStats:

    """Memory usage statistics, obtained from the Rayhunter API.

    Size and percentage values are converted from string (e.g. 159.9) to bytes (e.g. 167667302) for programmatic ease of use.

    Attributes:
        total (int): Total size of memory in bytes (e.g. 167667302).
        used (int): The amount of memory currently in use in bytes (e.g. 149212364).
        free (int): The amount of memory currently available in bytes (e.g. 18454937)

    """

    total: int
    used: int
    free: int

    @staticmethod
    def from_dict(memory_stats):
        for key in ["total", "used", "free"]:
            memory_stats[key] = _size_str_to_int(memory_stats[key])
        return MemoryStats(**memory_stats)
    

@dataclass
class SystemStats:

    """Disk and memory utilization statistics for the underlying system, pulled from the Rayhunter API.
    
    Attributes:
        disk_stats (DiskStats): Information on the underlying disk
        memory_stats (MemoryStats): Information on system memory utilization

    """

    disk_stats: DiskStats
    memory_stats: MemoryStats

    @staticmethod
    def from_dict(system_stats: dict):
        return SystemStats(
            disk_stats=DiskStats.from_dict(system_stats["disk_stats"]),
            memory_stats=MemoryStats.from_dict(system_stats["memory_stats"])
        )
