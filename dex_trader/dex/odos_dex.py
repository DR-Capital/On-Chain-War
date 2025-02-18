from dex_trader.dex.base_dex import BaseDex
import aiohttp
import asyncio
from web3 import Web3

class OdosDex(BaseDex):

    def __init__(self):
        """
        Initializes the OdosDex instance with the base API URL.
        """
        self.base_url = "https://api.odos.xyz"

    async def get_quote(self, quote_params: dict) -> dict:
        """
        Generates a quote by sending a POST request to the Odos SOR API's /sor/quote/v2 endpoint.

        Args:
            quote_params (dict): A dictionary containing required parameters for the quote.
                Expected keys include:
                    - chainId: The chain ID for the quote.
                    - inputTokens: A list of token objects (each with tokenAddress and amount).
                    - outputTokens: A list of token objects (each with tokenAddress and proportion).
                    - slippageLimitPercent: The slippage tolerance (e.g., 0.3 for 0.3%).
                    - userAddr: The checksummed user address.
                Optional keys include:
                    - referralCode, disableRFQs, compact, etc.

        Returns:
            dict: The JSON response from the API, including the 'pathId' necessary for transaction assembly.

        Raises:
            Exception: If the API call fails or returns a non-200 status code.
        """

        url = f"{self.base_url}/sor/quote/v2"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, json=quote_params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.json()
                        raise Exception(f"Error in Quote: {error_data}")
        except Exception as e:
            raise Exception(f"Exception in get_quote: {str(e)}")

    async def assemble_transaction(self, user_addr: str, path_id: str, simulate: bool = False) -> dict:
        """
        Assembles an on-chain transaction by sending a POST request to the Odos SOR API's /sor/assemble endpoint.

        Args:
            user_addr (str): The checksummed user address (same as used in the quote).
            path_id (str): The pathId received from the quote response.
            simulate (bool, optional): If True, simulates the transaction. Defaults to False.

        Returns:
            dict: The JSON response from the API containing the assembled transaction details.

        Raises:
            Exception: If the API call fails or returns a non-200 status code.
        """

        url = f"{self.base_url}/sor/assemble"
        payload = {"userAddr": user_addr, "pathId": path_id, "simulate": simulate}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.json()
                        raise Exception(f"Error in Transaction Assembly: {error_data}")
        except Exception as e:
            raise Exception(f"Exception in assemble_transaction: {str(e)}")

    async def place_order(self, order: dict) -> dict:
        """
        Places an order by performing the following steps:
            1. Generates a quote using the provided quote parameters.
            2. Assembles the transaction using the quote's pathId.

        Args:
            order (dict): A dictionary containing order details. Must include:
                - 'quote_params': A dict with parameters for generating a quote.
                - 'simulate' (optional): A boolean indicating whether to simulate the transaction assembly.

        Returns:
            dict: The assembled transaction details.

        Raises:
            ValueError: If 'quote_params' is missing from the order dictionary.
            Exception: If any step in the process fails.
        """

        try:
            quote_params = order.get("quote_params")
            if not quote_params:
                raise ValueError("Order must include 'quote_params'")

            quote = await self.get_quote(quote_params=quote_params)
            print("Quote received:", quote)

            assembled_tx = await self.assemble_transaction(
                user_addr=quote_params["userAddr"],
                path_id=quote["pathId"],
                simulate=order.get("simulate", False)
            )
            print("Assembled transaction:", assembled_tx)
            return assembled_tx

        except Exception as e:
            raise Exception(f"Exception in place_order: {str(e)}")

    @staticmethod
    async def submit_to_chain(transaction, private_key:str, w3: Web3) -> str:
        """
        Submits the assembled transaction to the blockchain by signing it with a provided private key
        and broadcasting it using the chain defined by its chain id.

        Args:
            transaction (dict): The transaction data to be submitted. Must include a 'value' field.
            private_key (str): The private key used to sign the transaction.
            w3 (Web3): An initialized Web3 instance connected to the desired network.

        Returns:
            str: The transaction hash as a hexadecimal string.

        Raises:
            Exception: If signing or submitting the transaction fails.
        """

        try:

            transaction["value"] = int(transaction["value"])
            signed_tx = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash

        except Exception as e:
            raise Exception(f"Exception in submit_to_chain: {str(e)}")

    async def cancel_order(self, order_id: str) -> bool:
        try:
            print("Cancel order is not available")
            return False
        except Exception as e:
            raise Exception(f"Exception in cancel_order: {str(e)}")

