from dataclasses import field


class Mirror:
    """
    Represents a mirror for a repository.
    """

    url: str = ''
    organization: str = ''
    location: str = ''
    sync_frequency: str = ''
    protocols: list[str] = field(default_factory=list)

    def __init__(
        self,
        url: str,
        organization: str = '',
        location: str = '',
        sync_frequency: str = '',
        protocols: list[str] | None = None,
    ):
        self.url = url
        self.organization = organization
        self.location = location
        self.sync_frequency = sync_frequency
        self.protocols = protocols or ['https']