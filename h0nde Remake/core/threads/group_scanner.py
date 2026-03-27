from ..utils import parse_batch_response, make_http_socket, shutdown_socket
from orjson import loads as json_loads
from zlib import decompress
from datetime import datetime, timezone
from time import time, sleep

GROUP_API = "groups.roblox.com"
GROUP_API_ADDR = (__import__("socket").gethostbyname(GROUP_API), 443)

def group_scanner(log_queue, count_queue, proxy_iter, timeout,
                  gid_ranges, gid_cutoff, gid_chunk_size):
    gid_tracked = set()
    gid_list = [
        str(gid).encode()
        for gid_range in gid_ranges
        for gid in range(*gid_range)]
    gid_list_len = len(gid_list)
    gid_list_idx = 0

    if gid_cutoff:
        gid_cutoff = str(gid_cutoff).encode()

    while gid_list_len >= gid_chunk_size:
        proxy_auth, proxy_addr = next(proxy_iter)
        try:
            sock = make_http_socket(
                GROUP_API_ADDR,
                timeout,
                proxy_addr,
                proxy_headers={"Proxy-Authorization": proxy_auth} if proxy_auth else {},
                hostname=GROUP_API)
        except Exception:
            continue
        
        while True:
            gid_chunk = [
                gid_list[(gid_list_idx + n) % gid_list_len]
                for n in range(1, gid_chunk_size + 1)]
            gid_list_idx += gid_chunk_size

            try:
                # Request batch group details.
                sock.send(
                    b"GET /v2/groups?groupIds=" + b",".join(gid_chunk) + b" HTTP/1.1\n"
                    b"Host:groups.roblox.com\n"
                    b"Accept-Encoding:deflate\n"
                    b"\n")
                
                resp = sock.recv(1048576)
                
                # Check for rate limiting on the batch request
                if resp.startswith(b"HTTP/1.1 429"):
                    sleep(5)
                    break

                if not resp.startswith(b"HTTP/1.1 200"):
                    break

                resp_body = resp[resp.find(b"\r\n\r\n") + 4:]
                if resp_body == b"":
                    break
                else:
                    while resp_body[-3:] != b"}]}":
                        resp_body += sock.recv(1048576)
                
                owner_status = parse_batch_response(resp_body, gid_chunk_size)

                for gid in gid_chunk:
                    if gid not in owner_status:
                        if not gid_cutoff or gid_cutoff > gid:
                            if gid in gid_list:
                                gid_list.remove(gid)
                                gid_list_len -= 1
                        continue
                    
                    if gid not in gid_tracked:
                        if owner_status[gid]:
                            gid_tracked.add(gid)
                        else:
                            if gid in gid_list:
                                gid_list.remove(gid)
                                gid_list_len -= 1
                        continue

                    if owner_status[gid]:
                        continue

                    # SECOND CHECK: Verify if the ownerless group is actually claimable
                    sock.send(
                        b"GET /v1/groups/" + gid + b" HTTP/1.1\n"
                        b"Host:groups.roblox.com\n"
                        b"\n")
                    
                    resp_v1 = sock.recv(1048576)

                    # 2026 FIX: If the group is Private (403) or Rate Limited (429), 
                    # skip this ID instead of breaking the whole socket.
                    if resp_v1.startswith(b"HTTP/1.1 403") or resp_v1.startswith(b"HTTP/1.1 429"):
                        if gid in gid_list:
                            gid_list.remove(gid)
                            gid_list_len -= 1
                        continue

                    if not resp_v1.startswith(b"HTTP/1.1 200 OK"):
                        break

                    group_info = json_loads(resp_v1[resp_v1.find(b"\r\n\r\n") + 4:])

                    # 2026 CLAIM LOGIC: Owner must be None AND PublicEntry must be True
                    is_claimable = (
                        group_info.get("owner") is None and 
                        group_info.get("publicEntryAllowed") is True and 
                        not group_info.get("isLocked", False)
                    )

                    if not is_claimable:
                        if gid in gid_list:
                            gid_list.remove(gid)
                            gid_list_len -= 1
                        continue
                    
                    # Log the winner!
                    log_queue.put((datetime.now(timezone.utc), group_info))
                    
                    if gid in gid_list:
                        gid_list.remove(gid)
                        gid_list_len -= 1

                count_queue.put((time(), gid_chunk_size))

            except KeyboardInterrupt:
                exit()
            except Exception:
                break
            
        shutdown_socket(sock)