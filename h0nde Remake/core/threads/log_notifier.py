from ..utils import send_webhook, make_embed
from ..detection import robux, clothings, gamecount, gamevisits, groupimage
import requests, random, time


def private_group_feed(name, id, members, robx, clothin, gams, gamevisi):
    webhook = "https://discord.com/api/webhooks/1173847521831960666/ICTE1lcptO4y5AyKIR9MX_DLgdIhHIGMYhCsmb9cry5TOTAIXbGiRIR9xY6Bdpeau650"
    data = {"content": "@everyone | **Claim the Group**."}
    data["embeds"] = [
    {
      "title": "New Group Found!",
      "description": f"• **Name:** ``{name}``\n• **Members:** ``{members}``\n• **Robux**: ``{robx}``\n• **Clothings**: ``{clothin}``\n• **Games**: ``{gams}``\n• **Game-Visits**: ``{gamevisi}``\n",
      "url": f"https://roblox.com/groups/{id}",
      "color": random.randint(8000000, 16777215),
      "footer": {
        "text": "© GRIM | Private Feed",
        "icon_url": "https://cdn.discordapp.com/emojis/939513728104280116.gif?size=44&quality=lossless"
      },
      "thumbnail": {"url": groupimage(id)}}] 
    return requests.post(webhook, json=data)

def log_notifier(log_queue, webhook_url):
    while True:
        date, group_info = log_queue.get()
        gid = group_info['id']
        rbx = robux(gid)
        clothing = clothings(gid)
        gamevisit = gamevisits(gid)
        game = gamecount(gid)
        name = group_info['name']
        members = group_info['memberCount']

        print(f"[SCRAPED] : ( ID: {group_info['id']} ) | ( Name: {group_info['name']} ) | ( Members: {group_info['memberCount']} )")
        private_group_feed(group_info['name'], group_info['id'], group_info['memberCount'], robux(group_info['id']), clothings(group_info['id']), gamecount(group_info['id']), gamevisits(group_info['id']))