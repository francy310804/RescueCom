class Emergency:
    id: int
    user_uuid: str
    position: tuple[float, float]
    address: str
    city: str
    street_number: int
    place_description: str
    photo_b64: str
    resolved: bool
    # TODO: could be a new table
    details_json: str

    def __init__(
        self,
        id: int,
        user_uuid: str,
        address: str,
        city: str,
        street_number: int,
        resolved: bool,
        position: tuple[float, float] = (0.0, 0.0),
        place_description: str = "",
        photo_b64: str = "",
        details_json: str = "",
    ) -> None:
        self.id = id
        self.user_uuid = user_uuid
        self.position = position
        self.address = address
        self.city = city
        self.street_number = street_number
        self.place_description = place_description
        self.photo_b64 = photo_b64
        self.resolved = resolved
        self.details_json = details_json

    def to_db_tuple(self) -> tuple:
        """
        Converts the emergency instance into a tuple suitable for SQLite insertion.

        The returned tuple contains the emergency attributes in a fixed order,
        matching the expected parameter order of the insert query.
        The `position` tuple is serialized as a comma-separated string.

        Returns:
            tuple: A tuple containing the following values, in order:
                - id (int): Unique identifier of the emergency.
                - user_uuid (str): UUID of the user who created the emergency.
                - position (str): Serialized position as "x,y".
                - address (str): Street address of the emergency.
                - city (str): City where the emergency occurred.
                - street_number (int): Street number of the address.
                - place_description (str): Additional place description.
                - photo_b64 (str): Base64-encoded photo associated with the emergency.
                - resolved (bool): Whether the emergency has been resolved.
                - details_json (str): Serialized emergency details.
        """

        return (
            self.id,
            self.user_uuid,
            # NOTE: Saved in the db as: "x,y"
            f"{self.position[0]},{self.position[1]}",
            self.address,
            self.city,
            self.street_number,
            self.place_description,
            self.photo_b64,
            self.resolved,
            self.details_json,
        )
