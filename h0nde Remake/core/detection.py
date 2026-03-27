import requests
import json
from requests_futures.sessions import FuturesSession
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RequestException

roblox_cookie = {".ROBLOSECURITY": "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_B3742F633F2CC0EDB4C66AB8EC725C025A4EECD295F2E6E710004D86FFA2386B3D0749BA1FE65C12591F87926DB7152692E4006BDAC7E3016C5D7C022748D91BBD68F8ADCEA0E4EEA6A63238DE2177FDAE6F67670784276DC08C00C7BECD64EB34E12C1A3CEA4A161EF97780AA50C58DD73CC323955FA8170E849F33FD2D99F2D62F950B7301985FAEF2BB3DB3A81AE6699AA15AB01DBC1F33867D30DD34E6B2631923739EE8E4A4302F038400A029AD84F6772041A3DC317FA7BD8D91C108A03209A2339466B2BD66EDD00D597567049FFB2B083284796B012C3E653A35A2E46B8DEDE90983DB08E4A472FDC2F1E9A9C95F2234E5E5C0E803C34351B453DB6F1FD3DAFA961158DF80AD4CFF218E34FEBE581A1254BB007B67680F480464DE80CAD0AF73617610D73BA8E44BDFF9BF0E362C84EBDB0F0441CC76499A52410BC05567D1D3B013166716E69909B99317B7E97C1393CB795AB30CC265C56F5BFB7ED90E628B8EA205F5360725DCA2A80F7C3A64283E"}
def clothings(id):
  clothings = 0
  session = FuturesSession()
  retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
  session.mount('https://', HTTPAdapter(max_retries=retries))
  try:
    check = session.get(f"https://catalog.roblox.com/v1/search/items/details?Category=3&CreatorTargetId={id}&CreatorType=2&Limit=30").result()
    check = check.json()
  except RequestException as e:
    print(e)
    return 0

  def get_page(cursor=None):
      nonlocal check
      try:
        if cursor:
          url = f"https://catalog.roblox.com/v1/search/items/details?Category=3&CreatorTargetId={id}&CreatorType=2&Limit=30&cursor={cursor}"
        else:
          url = f"https://catalog.roblox.com/v1/search/items/details?Category=3&CreatorTargetId={id}&CreatorType=2&Limit=30"
        check = session.get(url).result().json()
      except RequestException as e:
        print(e)  
        return 0
      return check

  while True:
      if "data" in check:
          clothings += len(check['data'])
      if "nextPageCursor" not in check or not check['nextPageCursor']:
          break
      else:
          check = get_page(check['nextPageCursor'])
  return clothings

def robux(id):
  # Import Local Cookie Variable
  global roblox_cookie
  session = FuturesSession()
  retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
  session.mount('https://', HTTPAdapter(max_retries=retries))
  try:
      # Send the request asynchronously and return a Future object
      future = session.get(f'https://economy.roblox.com/v1/groups/{id}/currency', cookies=roblox_cookie, timeout=5)
  except RequestException as e:
    print(e)
    return 0
  try:
    response = future.result()
    data = json.loads(response.text)
    if "robux" in data:
      robux = data.get("robux", 0)
    else:
      robux = 0
  except RequestException as e:
    print(e)
    return 0
  return robux

def gamevisits(id):
  # Create a FuturesSession object
  session = FuturesSession()
  retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
  session.mount('https://', HTTPAdapter(max_retries=retries))

  # Make the API request asynchronously
  try:
    future = session.get(f'https://games.roblox.com/v2/groups/{id}/games?accessFilter=All&sortOrder=Asc&limit=100', timeout=5)
  except RequestException as e:
    print(e)
    return 0

  # Wait for the request to complete and load the response into a dictionary
  try:
    response = future.result()
    os = json.loads(response.text)
    if "data" in os:
      data = os["data"]
    else:
      data = 0
      
  except RequestException as e:
    print(e)
    return 0

  # If there are no games, return "None"
  if not data:
    return 0
  
  # Find the total number of visits for all games
  total_visits = 0
  for game in data:
    visits = game["placeVisits"]
    total_visits += visits
  return total_visits
  
def gamecount(id):
  session = FuturesSession()
  retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
  session.mount('https://', HTTPAdapter(max_retries=retries))
  try:
      # Send the request asynchronously and return a Future object
      future = session.get(f'https://games.roblox.com/v2/groups/{id}/games?accessFilter=All&sortOrder=Asc&limit=100', timeout=5)
  except RequestException as e:
    print(e)
    return 0
  try:
    response = future.result()
    os = json.loads(response.text)
    if "data" in os:
      data = os["data"]
    else:
      data = 0
  except RequestException as e:
    print(e)
    return 0
  if not data:
    return 0
  else:
    return len(data)

def groupimage(id):
  # Create a session with retries enabled
  session = FuturesSession()
  retry = Retry(connect=3, backoff_factor=0.5, status_forcelist=[502, 503, 504])
  adapter = HTTPAdapter(max_retries=retry)
  session.mount('https://', adapter)

  # Send the request asynchronously and return a Future object
  future = session.get(f'https://thumbnails.roblox.com/v1/groups/icons?groupIds={id}&size=150x150&format=Png&isCircular=false', timeout=5)

  # Wait for the request to complete and handle any errors that may occur
  try:
    response = future.result()
    icon_url = response.json()
    if "data" in icon_url and len(icon_url["data"]) > 0:
       image = icon_url["data"][0]["imageUrl"]
    else:
       image = ""

  except RequestException as e:
    print(e)
    image = ""
  return image 