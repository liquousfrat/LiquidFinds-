from ..utils import parse_batch_response, make_http_socket, shutdown_socket
from orjson import loads as json_loads
from datetime import datetime, timezone
from time import time, sleep

GROUP_API = "groups.roblox.com"
# Pre-resolve to save DNS lookup time per worker
GROUP_API_ADDR = (__import__("socket").gethostbyname(GROUP_API), 443)

def group_scanner(log_queue, count_queue, proxy_iter, timeout,
                  gid_ranges, gid_cutoff, gid_chunk_size):
    
    # Optimization: Pre-generate GIDs as bytes to avoid encoding inside the loop
    gid_pool = [
        str(gid).encode()
        for gid_range in gid_ranges
        for gid in range(*gid_range)
    ]
    gid_len = len(gid_pool)
    idx = 0

    print(f"🚀 Scanner Started: Tracking {gid_len} IDs in Singapore Region")

    while True:
        proxy_auth, proxy_addr = next(proxy_iter)
        
        try:
            # make_http_socket should handle the SSL wrap
            sock = make_http_socket(
                GROUP_API_ADDR,
                timeout,
                proxy_addr,
                proxy_headers={"Proxy-Authorization": proxy_auth} if proxy_auth else {},
                hostname=GROUP_API)
        except Exception:
            continue

        # Worker Loop: Stay on one proxy as long as it's fast
        while True:
            # Grab the next chunk using modulo to wrap around
            gid_chunk = [gid_pool[(idx + i) % gid_len] for i in range(gid_chunk_size)]
            idx = (idx + gid_chunk_size) % gid_len

            try:
                # 2026 FIX: Using \r\n (CRLF) and Connection: keep-alive
                # Checking 100 IDs at once (/v2/groups)
                request = (
                    b"GET /v2/groups?groupIds=" + b",".join(gid_chunk) + b" HTTP/1.1\r\n"
                    b"Host: groups.roblox.com\r\n"
                    b"Accept-Encoding: deflate\r\n"
                    b"Connection: keep-alive\r\n\r\n"
                )
                
                sock.send(request)
                resp = sock.recv(1048576)

                # If proxy is rate-limited (429) or dead, kill this socket and rotate
                if b"HTTP/1.1 200" not in resp:
                    break 

                # Locate body after headers
                body_idx = resp.find(b"\r\n\r\n") + 4
                resp_body = resp[body_idx:]

                # Handle fragmented responses (ensure full JSON is read)
                while not resp_body.endswith(b"}]}"):
                    more = sock.recv(1048576)
                    if not more: break
                    resp_body += more

                # parse_batch_response should return a dict: {gid: has_owner_bool}
                owner_status = parse_batch_response(resp_body, gid_chunk_size)

                for gid_bytes, has_owner in owner_status.items():
                    if not has_owner:
                        # SCALE TIP: Don't do the v1 check here! 
                        # Just log it as a "Potential" and move on.
                        log_queue.put((
                            datetime.now(timezone.utc), 
                            {"id": gid_bytes.decode(), "status": "Potential Hit"}
                        ))
                
                # Update the CPM counter
                count_queue.put((time(), gid_chunk_size))

            except (ConnectionResetError, TimeoutError, Exception):
                # Socket died or timed out, break to get a new proxy
                break
        
        shutdown_socket(sock)
