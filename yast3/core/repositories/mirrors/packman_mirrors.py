from yast3.core.repositories.mirrors.mirror import Mirror

packman_mirrors = [
    Mirror(url='mirrors.aliyun.com/packman/', organization='Alibaba Cloud', location='China', sync_frequency='24h', protocols=['https']),
    Mirror(url='mirror.karneval.cz/pub/linux/packman/', organization='Vodafone Czech', location='Czech', sync_frequency='1h', protocols=['http', 'rsync']),
    Mirror(url='ftp.fau.de/packman/', organization='Friedrich-Alexander University', location='Germany', sync_frequency='1h', protocols=['http', 'https', 'ftp']),
    Mirror(url='ftp.halifax.rwth-aachen.de/packman/', organization='RWTH Aachen University', location='Germany', sync_frequency='1h', protocols=['http', 'https', 'ftp', 'rsync']),
    Mirror(url='ftp.gwdg.de/pub/linux/misc/packman/', organization='GWDG', location='Germany', sync_frequency='4h', protocols=['http', 'https', 'ftp']),
]