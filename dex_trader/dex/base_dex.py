from abc import ABC, abstractmethod


class BaseDex(ABC):

    @abstractmethod
    def get_quote(self, from_token: str, to_token: str, amount: float) -> dict:
        """
        Retrive a price quote for swapping tokens.
        :param from_token:
        :param to_token:
        :param amount:
        :return:
        """
        pass

    @abstractmethod
    def place_order(self, order: "Order") -> str:
        """
        Place an order on the Dex and return an order ID
        :param order:
        :return:
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order given its order ID
        :param order_id:
        :return:
        """
        pass
