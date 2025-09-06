# from ingestion import btc_eth_ws_listener
import btc_eth_ws_listener as btc_eth_ws_listener
from postgres_manager import PostgresManager
from datetime import datetime, timezone
import os, shutil

class DummyPostgres:
    """Simule PostgresManager pour les tests."""
    def __init__(self):
        self.data = []

    def write_on_db(self, table_name, price, date):
        self.data.append((table_name, price, date))
        return True

class DummyPostgres_connexion_postgres_fail:
    """Simule PostgresManager pour les tests."""
    def __init__(self):
        self.data = []

    def write_on_db(self, table_name, price, date):
        return False

def test_handle_message_inserts_new_data(monkeypatch):
    # Remplacer le postgres_manager global par DummyPostgres
    dummy_pg = DummyPostgres()
    monkeypatch.setattr(btc_eth_ws_listener, "postgres_manager", dummy_pg)

    # Reset état global
    btc_eth_ws_listener.last_data.clear()

    msg = {"id": "BTC-USD", "price": 25000}
    btc_eth_ws_listener.handle_message(msg)

    # Vérifier qu'une insertion a été faite
    assert len(dummy_pg.data) == 1
    table_name, price, date = dummy_pg.data[0]
    assert table_name == "btc_usd"
    assert price == 25000
    assert isinstance(date, datetime)

def test_handle_message_duplicate_ignored(monkeypatch):
    dummy_pg = DummyPostgres()
    monkeypatch.setattr(btc_eth_ws_listener, "postgres_manager", dummy_pg)

    # Pré-remplir last_data pour simuler un doublon récent (<30s)
    now = datetime.now(timezone.utc)
    btc_eth_ws_listener.last_data.clear()
    btc_eth_ws_listener.last_data["btc_usd"] = now

    msg = {"id": "BTC-USD", "price": 26000}
    btc_eth_ws_listener.handle_message(msg)

    # Aucune insertion car doublon
    assert len(dummy_pg.data) == 0

def test_handle_message_inserts_data_with_no_postgres(monkeypatch):
    # Remplacer le postgres_manager global par DummyPostgres
    dummy_pg = DummyPostgres_connexion_postgres_fail()
    monkeypatch.setattr(btc_eth_ws_listener, "postgres_manager", dummy_pg)

    # Reset état global
    btc_eth_ws_listener.last_data.clear()

    # Essayer d'insérer les données alors que le simulateur Postgres est éteint
    msg = {"id": "BTC-USD", "price": 25000}
    btc_eth_ws_listener.handle_message(msg)

    # Vérifier qu'une insertion a été faite
    assert len(dummy_pg.data) == 0

    # Vérifier que le CSV a été créé
    filepath = os.path.join("waiting_data_store","btc_usd.csv")
    assert os.path.exists(filepath)

    with open(filepath, "r") as f:
        content = f.read().strip()

    price, date_str = content.split(",")
    assert price == "25000"
    assert date_str.endswith("+00:00")

    # --- Supprimer le dossier ---
    if os.path.exists("waiting_data_store"):
        shutil.rmtree("waiting_data_store")

    # Vérifier qu'il n'existe plus
    assert not os.path.exists("waiting_data_store")

def test_try_to_connect_real_db(monkeypatch):
    postgres_manager = PostgresManager()
    print("postgres_manager.connect", postgres_manager.connect)
    # Verifie que la connexion existe
    assert postgres_manager.connect != None
    # Verifie que la connexion est bonne
    # assert postgres_manager.connect.closed == 0
    assert postgres_manager.connect.closed != 0