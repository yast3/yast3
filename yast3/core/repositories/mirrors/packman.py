from yast3.core.repositories.mirrors.mirror import Mirror

packman_mirrors = [
    Mirror(url='mirrors.aliyun.com/packman/', organization='Alibaba Cloud (阿里云)', location='China', sync_frequency='24h', protocols=['http', 'https']),
    Mirror(url='mirror.karneval.cz/pub/linux/packman/', organization='Karneval (Vodafone)', location='Czech', sync_frequency='1h', protocols=['http', 'https', 'rsync']),
    Mirror(url='ftp.fau.de/packman/', organization='Friedrich-Alexander University', location='Germany', sync_frequency='1h', protocols=['http', 'https', 'ftp']),
    Mirror(url='ftp.hal-aachen.de/p-aachen.de/packman/', organization='RWTH Aachen University', location='Germany', sync_frequency='1h', protocols=['http', 'https', 'ftp', 'rsync']),
    Mirror(url='ftp.gwdg.de/pub/linux/misc/packman/', organization='GWDG', location='Germany', sync_frequency='4h', protocols=['http', 'https', 'ftp'])
]