class Mirror:
    """
    Represents a mirror for a repository.
    """

    url: str = ''
    organization: str = ''
    location: str = ''
    sync_frequency: str = ''

    def __init__(self, url: str, organization: str = '', location: str = '', sync_frequency: str = ''):
        self.url = url
        self.organization = organization
        self.location = location
        self.sync_frequency = sync_frequency