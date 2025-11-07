import json
import logging
from typing import List, Dict, Any

import streamlit as st

from client import OnionClient


def get_client() -> OnionClient:
	if "onion_client" not in st.session_state:
		st.session_state["onion_client"] = OnionClient()
	return st.session_state["onion_client"]


def format_relays(relays: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
	return [
		{"#": idx + 1, "host": relay.get("host", ""), "port": relay.get("port", "")}
		for idx, relay in enumerate(relays)
	]


def main() -> None:
	st.set_page_config(page_title="Onion Client Dashboard", page_icon="🧅", layout="centered")
	st.title("🧅 Onion Routing Client")
	st.caption("Send messages through a simple onion route via available relays.")

	client = get_client()

	with st.sidebar:
		st.header("Directory Server")
		directory_host = st.text_input("Host", value=client.directory_host)
		directory_port = st.number_input("Port", min_value=1, max_value=65535, value=int(client.directory_port), step=1)
		update_dir = st.button("Save Directory Settings", use_container_width=True)
		if update_dir:
			client.directory_host = directory_host
			client.directory_port = int(directory_port)
			st.success("Directory settings updated.")

		st.divider()
		refresh_relays = st.button("Fetch Relays", use_container_width=True)

	if refresh_relays:
		with st.spinner("Contacting directory server..."):
			success = client.get_relays_from_directory()
			if success:
				st.toast(f"Fetched {len(client.relays)} relays", icon="✅")
			else:
				st.error("Failed to fetch relays from directory server.")

	st.subheader("Relays")
	if getattr(client, "relays", []):
		st.dataframe(format_relays(client.relays), use_container_width=True, hide_index=True)
	else:
		st.info("No relays loaded. Use 'Fetch Relays' from the sidebar to load available relays.")

	st.subheader("Send Message")
	message = st.text_area("Message", placeholder="Type your message to send through the onion route...")
	col1, col2 = st.columns([1, 1])
	with col1:
		send_clicked = st.button("Send via Onion Route", type="primary")
	with col2:
		build_only = st.button("Preview Built Onion Payload")

	response_placeholder = st.empty()
	debug_placeholder = st.expander("Debug Payload", expanded=False)

	if send_clicked:
		if not message.strip():
			st.warning("Please enter a message.")
		else:
			with st.spinner("Sending message through relays..."):
				try:
					resp = client.send_message(message.strip())
					response_placeholder.success(f"Response: {resp}")
				except Exception as exc:  # noqa: BLE001
					response_placeholder.error(f"Error: {exc}")

	if build_only:
		if not message.strip():
			st.warning("Please enter a message to build the payload.")
		else:
			try:
				payload_bytes, first_hop = client.create_onion_route(message.strip())
				with debug_placeholder:
					st.write("First hop:", first_hop)
					try:
						decoded = json.loads(payload_bytes.decode("utf-8"))
						st.json(decoded)
					except Exception:  # noqa: BLE001
						st.code(payload_bytes.decode("utf-8", errors="replace"))
			except Exception as exc:  # noqa: BLE001
				st.error(f"Error building onion payload: {exc}")


if __name__ == "__main__":
	# Keep logging noise minimal within Streamlit runs
	logging.getLogger("Client").setLevel(logging.INFO)
	main()


