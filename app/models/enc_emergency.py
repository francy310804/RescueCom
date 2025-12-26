class EncryptedEmergency:
    id: int
    user_uuid: str
    routing_info_json: str
    blob: bytes

    def __init__(
        self, user_uuid: str, routing_info_json: str, blob: bytes, id: int = 0
    ) -> None:
        self.user_uuid = user_uuid
        self.routing_info_json = routing_info_json
        self.blob = blob
        self.id = id

    def to_db_tuple(self) -> tuple:
        """
        Converts the encrypted_emergency instance into a tuple suitable for SQLite insertion.

        The returned tuple contains the emergency attributes in a fixed order,
        matching the expected parameter order of the insert query.

        Returns:
            tuple: A tuple containing the following values, in order:
                - id (int): Unique identifier of the emergency.
                - user_uuid (str): UUID of the user who created the emergency.
                - routing_info_json (str): Serialized routing informations.
                - blob (bytes): encrypted values
        """
        return (
            self.id,
            self.user_uuid,
            self.routing_info_json,
            self.blob,
        )
