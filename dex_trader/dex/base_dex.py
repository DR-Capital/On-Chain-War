from abc import ABC, abstractmethod


class BaseDex(ABC):

    @abstractmethod
    async def get_quote(self, quote_params: dict) -> dict:
        """
        Retrive a price quote for swapping tokens.
        :param quote_params:
        :return:
        """
        pass

    @abstractmethod
    async def place_order(self, order: dict) -> dict:
        """
        Place an order on the Dex and return an order ID
        :param order:
        :return:
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order given its order ID
        :param order_id:
        :return:
        """
        pass
