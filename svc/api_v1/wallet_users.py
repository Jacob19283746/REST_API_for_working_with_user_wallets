def get_wallet_users(
        user_id: int
) -> list:
    return [
        {
            "id": user_id,
            "name": "John Doe",
            "email": "johndoe@example.com",
            "wallet": {
                "balance": 1000 * user_id,
                "currency": "USD",
                "transactions": [],
                "history": []
            }
        }
        ]