from abc import abstractmethod


class ISecrets:
    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        pass


class IDynamoDBSecrets(ISecrets):
    @abstractmethod
    def get_table_name(self) -> str:
        pass
