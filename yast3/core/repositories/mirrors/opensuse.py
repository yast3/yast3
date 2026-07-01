from yast3.core.repositories.mirrors.mirror import Mirror

opensuse_mirrors = [
    Mirror(url='download.opensuse.org/', organization='openSUSE', location='Global', sync_frequency='1h', protocols=['http', 'https']),
    Mirror(url='mirrors.aliyun.com/opensuse/', organization='Alibaba Cloud', location='China', sync_frequency='24h', protocols=['http', 'https']),
    Mirror(url='mirror.karneval.cz/pub/linux/opensuse/', organization='Karneval (Vodafone)', location='Czech', sync_frequency='1h', protocols=['http', 'https']),
    Mirror(url='ftp.fau.de/opensuse/', organization='Friedrich-Alexander University', location='Germany', sync_frequency='1h', protocols=['http', 'https', 'ftp']),
    Mirror(url='ftp.halifax.rwth-aachen.de/opensuse/', organization='RWTH Aachen University', location='Germany', sync_frequency='1h', protocols=['http', 'https', 'ftp']),
    Mirror(url='ftp.gwdg.de/pub/linux/misc/opensuse/', organization='GWDG', location='Germany', sync_frequency='4h', protocols=['http', 'https', 'ftp'])
]