"""
Tests for UniBus Unix Domain Socket Transport.
"""

import json
import asyncio
from pathlib import Path
from unibus.uds import UDSServer, publish_uds_sync, is_uds_server_alive


def test_uds_server_lifecycle_and_broadcast(tmp_path: Path):
    async def _async_runner():
        sock_path = tmp_path / "test_unibus.sock"
        server = UDSServer(sock_path)

        # Start server
        await server.start()
        assert sock_path.exists()
        assert is_uds_server_alive(sock_path) is True

        # Connect client receiver
        reader, writer = await asyncio.open_unix_connection(str(sock_path))
        # Yield control briefly so server registers client into subscribers
        await asyncio.sleep(0.05)

        # Broadcast event from server
        test_packet = {"topic": "test.broadcast", "payload": {"val": 42}}
        await server.broadcast(test_packet)

        # Receiver reads packet
        line = await asyncio.wait_for(reader.readline(), timeout=2.0)
        received = json.loads(line.decode("utf-8"))
        assert received["topic"] == "test.broadcast"
        assert received["payload"]["val"] == 42

        # Test sync publisher to server
        sync_ok = publish_uds_sync({"topic": "client.ping", "data": "hello"}, socket_path=sock_path)
        assert sync_ok is True

        # Cleanup receiver
        writer.close()
        await writer.wait_closed()

        # Stop server
        await server.stop()
        assert not sock_path.exists()
        assert is_uds_server_alive(sock_path) is False

    asyncio.run(_async_runner())
