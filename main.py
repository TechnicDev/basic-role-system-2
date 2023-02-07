
# Some imports
from datetime import datetime
from interactions import discord_interactions, message
from discord.ext import commands
import discord
import json
import requests

config_file = open("bot_config.json", "r")
config_data = json.load(config_file)
config_file.close()

intents = discord.Intents()
intents.message_content=True
intents.messages=True
intents.members=True
intents.guilds=True

bot = commands.Bot(command_prefix=config_data['bot_prefix'], intents=intents,enable_debug_events=True)
bot.remove_command("help")

inter=discord_interactions.interactions(config_data['bot_token'], config_data['client_id'])

@bot.event
async def on_ready():
    print("Bot is ready")


@bot.event
async def on_socket_raw_receive(msgs):
    msg=json.loads(msgs)
    if msg['t']=="INTERACTION_CREATE":
        data=msg['d']
        ctx=inter.interaction_response(data, inter, bot)

        # print(msg)

        if ctx.type==3: # Buttons, the only one we actually need
            ctx.interact.load(64)

            roles = ctx.raw['data']['values']
            guild = bot.get_guild(int(ctx.raw['guild_id']))
            member = guild.get_member(int(ctx.raw['member']['user']['id']))

            if ctx.custom_id=='audiophile_and_producer':
                s_roles=[]
                for i in config_data['audiophile_and_producer']['roles']:s_roles.append(str(i['id']))
                for r in s_roles:
                    role = guild.get_role(int(r))
                    if r in roles:await member.add_roles(role)
                    else:await member.remove_roles(role)


            ctx.interact.edit_response(f"Your roles have been updated!")

@bot.group(name="load")
@commands.has_permissions(administrator=True)
async def load_waitlist(ctx):
    return

@load_waitlist.command(name="waitlist_notifications")
async def waitlist_notifications(ctx):
    """Loads the waitlist message"""
    comp = []
    for role in config_data['audiophile_and_producer']['roles']:
        comp.append(message.components.select_option(
            label=role['title'],
            value=str(role['id']),
            description=""
        ))
    msg = {
        "content": config_data['audiophile_and_producer']['message_content'], 
        "components": message.components.action_row([
            message.components.select(
                config_data['audiophile_and_producer']['place_holder'],
                f"audiophile_and_producer",
                comp,
                max=len(comp),
                min=0
            )
        ]).data
    }
    re = requests.post(
        f"https://discord.com/api/channels/{ctx.channel.id}/messages",
        json=msg,
        headers={"Authorization": f"Bot {config_data['bot_token']}"}
    )
    try: re.raise_for_status()
    except:
        await ctx.send(f"There was an error while sending the message\n`{re.text}`")
        return
    await ctx.message.delete()

@bot.command(name="help")
@commands.has_permissions(administrator=True)
async def help(ctx):
    """Get a list of my commands"""
    cnt=""
    for cmd in bot.commands:
        cnt += f"\n{config_data['bot_prefix']}{cmd.name:<15} | {cmd.help}"
    
    await ctx.send(f"My Commands:```{cnt}```")


@bot.event
async def on_command_error(err, err1):return

bot.run(config_data['bot_token'])