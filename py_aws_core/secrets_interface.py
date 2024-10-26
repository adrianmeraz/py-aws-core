from abc import abstractmethod


class ISecrets:

    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        pass
