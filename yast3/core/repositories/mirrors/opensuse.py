from yast3.core.repositories.mirrors.mirror import Mirror

opensuse_mirrors = [
    Mirror(url='https://mirrors.aliyun.com/opensuse/', organization='Alibaba Cloud', location='China', sync_frequency='24h'),
    Mirror(url='https://mirror.karneval.cz/pub/linux/opensuse/', organization='Karneval (Vodafone)', location='Czech', sync_frequency='1h'),
    Mirror(url='https://ftp.fau.de/opensuse/', organization='Friedrich-Alexander University', location='Germany', sync_frequency='1h'),
    Mirror(url='https://ftp.halifax.rwth-aachen.de/opensuse/', organization='RWTH Aachen University', location='Germany', sync_frequency='1h'),
    Mirror(url='https://ftp.gwdg.de/pub/linux/misc/opensuse/', organization='GWDG', location='Germany', sync_frequency='4h')
]