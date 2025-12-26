from __future__ import annotations
from typing import Self

import sqlite3
from models import emergency, user, enc_emergency


class DatabaseManager:
    __instance = None
    __allow_init = False

    def __init__(self, db_path: str) -> None:
        if not DatabaseManager.__allow_init:
            raise TypeError(
                "DatabaseManager singleton must be created using DatabaseManager.get_instance"
            )

        # NOTE: For multithreading
        # self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        # Enable Foreign Key constraints. It's disabled by default
        # See: https://sqlite.org/foreignkeys.html "Overview" and "2. Enabling Foreign Key Support"
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.__init_db()

    @classmethod
    def get_instance(cls: type[Self], db_path: str | None = None) -> Self:
        """
        Returns the singleton instance of DatabaseManager.

        This class method implements the Singleton pattern. On the first call,
        a database path must be provided to initialize the underlying SQLite
        connection. Subsequent calls will return the already-created instance
        and will ignore the `db_path` parameter.

        Args:
            db_path (str | None): Path to the SQLite database file. This parameter
                is required only on the first invocation.

        Returns:
            DatabaseManager: The singleton instance of the database manager.

        Raises:
            ValueError: If `db_path` is not provided on the first invocation.
        """

        if cls.__instance is None:
            if db_path is None:
                raise ValueError("'db_path' required on first initialization")

            cls.__allow_init = True
            cls.__instance = cls(db_path)
            cls.__allow_init = False

        return cls.__instance

    def __init_db(self) -> None:
        """
        Initialize the database by creating the schema.
        """

        schema: str = """
        CREATE TABLE IF NOT EXISTS user (
            uuid TEXT PRIMARY KEY,
            is_rescuer INTEGER NOT NULL,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            birthday DATE NOT NULL,
            blood_type INTEGER NOT NULL,
            health_info_json TEXT DEFAULT '',

            CHECK (blood_type IN ('ANEG', 'APOS', 'BPOS', 'BNEG', 'OPOS', 'ONEG', 'ABPOS', 'ABNEG'))
        );

        CREATE TABLE IF NOT EXISTS emergency (
            id INTEGER PRIMARY KEY,
            user_uuid TEXT NOT NULL,
            position TEXT NULL DEFAULT '0,0',
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            street_number INTEGER NOT NULL,
            place_description TEXT,
            photo_b64 TEXT,
            resolved INTEGER NOT NULL,
            details_json TEXT,

            FOREIGN KEY (user_uuid) REFERENCES user(uuid)
        );

        CREATE TABLE IF NOT EXISTS encrypted_emergency (
            id INTEGER PRIMARY KEY,
            user_uuid TEXT NOT NULL,
            routing_info_json TEXT NOT NULL,
            blob BLOB NOT NULL,

            /*
                In order to prevent the violation of
                the foreign key constraint, when the user
                receives an emergency from another user,
                the sender must also send their user details,
                and the receiver must insert them into the
                `user` table before inserting the newly
                received emergency.
            */
            FOREIGN KEY (user_uuid) REFERENCES user(uuid)
        );
        """

        for sub_query in schema.split(";"):
            self.conn.execute(sub_query)

        self.conn.commit()

    def insert_user(self, user: user.User) -> None:
        """
        Inserts a User into the database.

        The operation is wrapped in an explicit transaction:
        the transaction is committed on success and rolled back if an error
        occurs.

        Args:
            user (user.User): The User instance to be inserted into the database.

        Raises:
            sqlite3.Error: If the insertion fails, the transaction is rolled back
                and the original database error is re-raised.
        """

        insert_query: str = "INSERT INTO user(uuid, is_rescuer, name, surname, birthday, blood_type, health_info_json) VALUES(?, ?, ?, ?, ?, ?, ?)"

        # Begin transaction
        self.conn.execute("BEGIN")
        try:
            self.conn.execute(insert_query, user.to_db_tuple())
            self.conn.commit()
        except self.conn.Error as e:
            self.conn.rollback()
            raise e

    def insert_emergency(self, emergency: emergency.Emergency) -> None:
        """
        Inserts an Emergency into the database.

        The operation is wrapped in an explicit transaction:
        the transaction is committed on success and rolled back if an error
        occurs.

        Args:
            emergency (emergency.Emergency): The Emergency instance to be
                inserted into the database.

        Raises:
            sqlite3.Error: If the insertion fails, the transaction is rolled back
                and the original database error is re-raised.
        """

        insert_query: str = """
            INSERT INTO emergency (user_uuid, position, address, city, street_number, place_description, photo_b64, resolved, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Begin transaction
        self.conn.execute("BEGIN")
        try:
            # Skip the field `id`
            vales = emergency.to_db_tuple()[1:]
            self.conn.execute(insert_query, vales)
            self.conn.commit()
        except self.conn.Error as e:
            self.conn.rollback()
            raise e

    def insert_encrypted_emergency(
        self, enc_emergency: enc_emergency.EncryptedEmergency
    ) -> None:
        """
        Inserts an EncryptedEmergency into the database.

        The operation is wrapped in an explicit transaction:
        the transaction is committed on success and rolled back if an error
        occurs.

        Args:
            enc_emergency (emergency.Emergency): The EncryptedEmergency instance to be
                inserted into the database.

        Raises:
            sqlite3.Error: If the insertion fails, the transaction is rolled back
                and the original database error is re-raised.
        """

        insert_query = "INSERT INTO encrypted_emergency(user_uuid, routing_info_json, blob) VALUES (?, ?, ?)"

        # Begin transaction
        self.conn.execute("BEGIN")
        try:
            # Skip the field `id`
            values = enc_emergency.to_db_tuple()[1:]
            self.conn.execute(insert_query, values)
            self.conn.commit()
        except self.conn.Error as e:
            self.conn.rollback()
            raise e
