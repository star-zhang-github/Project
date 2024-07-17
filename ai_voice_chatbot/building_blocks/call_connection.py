from pyngrok import ngrok
import os

#ngrok.set_auth_token(os.getenv("ngrok_token_key"))

http_tunnel = ngrok.connect(5000)
public_url = http_tunnel.public_url
print(f"Ngrok Tunnel URL: {public_url}")

# terminal command calls: ngrok http 5000