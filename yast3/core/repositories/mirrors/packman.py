from yast3.core.repositories.mirrors.mirror import Mirror

packman_mirrors = [
    Mirror(url='https://mirrors.aliyun.com/packman/', organization='Alibaba Cloud', location='China', sync_frequency='24h'),
    Mirror(url='https://mirror.karneval.cz/pub/linux/packman/', organization='Karneval (Vodafone)', location='Czech', sync_frequency='1h'),
    Mirror(url='https://ftp.fau.de/packman/', organization='Friedrich-Alexander University', location='Germany', sync_frequency='1h'),
    Mirror(url='https://ftp.halifax.rwth-aachen.de/packman/', organization='RWTH Aachen University', location='Germany', sync_frequency='1h'),
    Mirror(url='https://ftp.gwdg.de/pub/linux/misc/packman/', organization='GWDG', location='Germany', sync_frequency='4h')
]