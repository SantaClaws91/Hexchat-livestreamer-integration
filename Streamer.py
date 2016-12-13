import hexchat
import livestreamer
import subprocess
import requests
import os
import sys

__module_name__ = "HexChat Twitch Streamer"
__module_author__ = "SantaClaws"
__module_version__ = "0.9a"
__module_description__ = "Launch a TwitchTV stream via Livestreamer on the corresponding channel where script is launched"


path = os.path.join(hexchat.get_info("configdir"), "addons")
if path not in sys.path:
    sys.path.append(path)

from vlc import vlc_path
if vlc_path:
    if not vlc_path.endswith('vlc.exe'):
                if not vlc_path.endswith('/') and not vlc_path.endswith('\\'):
                    vlc_path += '\\'
                vlc_path += 'vlc.exe'


client_id = "91yc6gwdiju5sae40wjqf0pvx4v97hu"		## I believe this is for biteybot

def get_twitch_info(channel):
    url = "https://api.twitch.tv/kraken/streams?"
    params = {
    	"channel": channel,
    	"client_id": client_id
    	}
    r = requests.get(url, params=params)
    data = r.json()
    return data

def livestreamer_cb(word, word_eol, userdata):
    word = [(word[i] if len(word) > i else "") for i in range(3)]

    channel = word[1]

    url = "http://www.twitch.tv/{}".format(channel)
    
    data = get_twitch_info(channel)

    if not 'streams' in data:
        format(channel + " is not live on twitch.tv/" + channel, onoff=False)
        return hexchat.EAT_ALL

    streams = livestreamer.Livestreamer()

    streams.set_option("http-query-params", "client_id=" + client_id)

    streams = streams.streams(url)

    if not 'best' in streams:
        format(channel + " is not live on twitch.tv/" + channel, onoff=False)
        return hexchat.EAT_ALL
    
    data = data['streams'][0]
    
    uploader = data["channel"]["display_name"]
    game = data["channel"]["game"]
    title = data["channel"]["status"]
    viewers = str(data["viewers"])
        
    stream = streams['best']
    format(uploader + " is streaming " + game + " for " + viewers + " viewers on " + url, onoff=True)

    subprocess.Popen([
        vlc_path,
        '--file-caching',
        '10000',
        stream.url,
        ":meta-title={}".format(title)
        ],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
        )

def stream_cb(word, word_eol, userdata):
    stream()
 
def stream(Quality='best'):
    CHANNEL = hexchat.get_info("channel")
    USER = CHANNEL.strip('#')

    hexchat.command("LIVESTREAMER " + USER)
    
        
def format(string, onoff=False):
    
    if (onoff == False):
        string = '\002\035\00301,04' + string
           
    else:
        string = '\002\035\00301,09' + string
           
    hexchat.prnt(string)

hexchat.hook_command("LIVESTREAMER", livestreamer_cb)
 
hexchat.hook_command("STREAM", stream_cb)
 
hexchat.prnt(__module_name__ + " version " + __module_version__ + " loaded")
