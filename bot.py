import discord
from discord.ext import commands, tasks
import logging
import random
import io
import aiohttp
from bs4 import BeautifulSoup
import urllib
from urllib.request import Request, urlopen
import time
from itertools import cycle
from asyncio import sleep as sleep_asyncio
import regex as re
import math
from werkzeug.urls import url_fix
from discord.utils import get




intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '.', intents = intents)
logging.basicConfig(level=logging.INFO)
messages_stats_path = (r"C:\Users\Uzivatel\Desktop\kodezy\discordbot\messages_stats.txt")
duels_stats_path = (r"C:\Users\Uzivatel\Desktop\kodezy\discordbot\duels_stats.txt")



@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(".commands"))
    print("bot is ready")
    print(discord.__version__)



global chanels_for_duel
global duel2_move_options_message
global duel2_chalenges
chanels_for_duel = ("duel", "duels")
duel2_chalenges = []
@client.command() #bude mít strenght, armor, speed podle rovnice: x=\frac{\left(r\ -\left(\sqrt{a}\cdot\sqrt{r}\right)\ -\ \frac{\left(\left(\sqrt{s}-\sqrt{a}\right)\cdot r^{3}\right)}{100000}\right)}{5}
async def duel(message, strenght = None, armor = None, speed = None, member:discord.User = None):

    async def duel2_start(duel2_invitation_info):
        global duel2_move_options_message
        global duel2_duelist_who_invited
        global duel2_duelist_who_accepted
        global duel2_round
        duel2_round = 0
        duel2_duelist_who_invited, duel2_duelist_who_accepted, duel2_duelist_who_invited_strenght, duel2_duelist_who_invited_armor, duel2_duelist_who_invited_speed = duel2_invitation_info.split("*")
        duel2_duelist_who_accepted_strenght = strenght
        duel2_duelist_who_accepted_armor = armor
        duel2_duelist_who_accepted_speed = speed
        duel2_duelist_who_invited_health = duel2_duelist_who_accepted_health = 100
        duel2_duelist_who_invited_name, duel2_duelist_who_invited_discriminator = duel2_duelist_who_invited.split("#")
        duel2_duelist_who_invited_mentionable = discord.utils.get(message.guild.members, name = duel2_duelist_who_invited_name, discriminator = duel2_duelist_who_invited_discriminator)


        duel2_starting_duel_embed = discord.Embed(title = "starting duel:", color = 9044739)
        duel2_starting_duel_embed.add_field(name = "chalanger:", value = f"{duel2_duelist_who_invited_mentionable.mention}\nstrenght:\n{duel2_duelist_who_invited_strenght}\narmor:\n{duel2_duelist_who_invited_armor}\nspeed:\n{duel2_duelist_who_invited_speed}", inline = True)
        duel2_starting_duel_embed.add_field(name = "oponent:", value = f"{message.author.mention}\nstrenght:\n{strenght}\narmor:\n{armor}\nspeed:\n{speed}", inline = True)
        duel2_starting_duel_embed.set_thumbnail(url = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/microsoft/209/crossed-swords_2694.png")
        await message.channel.send(embed = duel2_starting_duel_embed)
        await sleep_asyncio(3)

        while duel2_duelist_who_invited_health >= 1 and duel2_duelist_who_accepted_health >= 1 and duel2_round <= 16:
            duel2_round += 1
            duel2_move_options_embed = discord.Embed(title = "choose your move:", description = "you only have 5 seconds to chose!", color = 9044739)
            duel2_move_options_embed.add_field(name = "strenght", value = "by clicking at 💪 you will strike with all your power and that will result in dobleing your strenght")
            duel2_move_options_embed.add_field(name = "armor", value = "by clicking at 🛡 you will try to block and that will result in dobleing your armor")
            duel2_move_options_embed.add_field(name = "speed", value = "by clicking at 🦶 you will try to dodge and that will result in dobleing your speed")
            duel2_move_options_message = await message.channel.send(embed = duel2_move_options_embed)
            await duel2_move_options_message.add_reaction("💪")
            await duel2_move_options_message.add_reaction("🛡")
            await duel2_move_options_message.add_reaction("🦶")

            duel2_time_for_adding_reactions = 5
            while duel2_time_for_adding_reactions != 0:
                duel2_time_reamaining_for_adding_reactions_message = await message.channel.send(f"{duel2_time_for_adding_reactions}")
                duel2_time_for_adding_reactions -= 1

                await sleep_asyncio(1)
                await duel2_time_reamaining_for_adding_reactions_message.delete()
            

            async def from_reactions_change_stats_duel2(message, duelist, strenght, armor, speed):
                for r in message.reactions:
                    async for user in r.users():
                        if str(user) == duelist:
                            if str(r) == "💪":
                                strenght = int(strenght) * 2
                                return strenght, armor, speed
                            
                            if str(r) == "🛡":
                                armor = int(armor) * 2
                                return strenght, armor, speed
                            
                            if str(r) == "🦶":
                                speed = int(speed) * 2
                                return strenght, armor, speed

                return strenght, armor, speed
            
            duel2_move_options_message = await duel2_move_options_message.channel.fetch_message(duel2_move_options_message.id)
            duel2_duelist_who_invited_strenght, duel2_duelist_who_invited_armor, duel2_duelist_who_invited_speed = await from_reactions_change_stats_duel2(message=duel2_move_options_message, duelist=duel2_duelist_who_invited, strenght=duel2_duelist_who_invited_strenght, armor=duel2_duelist_who_invited_armor, speed=duel2_duelist_who_invited_speed)
            duel2_duelist_who_accepted_strenght, duel2_duelist_who_accepted_armor, duel2_duelist_who_accepted_speed = await from_reactions_change_stats_duel2(message=duel2_move_options_message, duelist=duel2_duelist_who_accepted, strenght=duel2_duelist_who_accepted_strenght, armor=duel2_duelist_who_accepted_armor, speed=duel2_duelist_who_accepted_speed)
 
            
            async def duel2_hit_calculation(calculator_strenght, calculator_armor, calculator_speed):
                hit_dmg = int(calculator_strenght)
                hit_dmg -= (int(calculator_armor)**(1/2))*(int(calculator_strenght)**(1/3))
                hit_dmg -= (((int(calculator_speed)**(1/2))-(int(calculator_armor)**(1/3)))*(int(calculator_strenght)**3))/100000
                hit_dmg /= 1.5
                hit_dmg += random.random() * hit_dmg / 5
                return hit_dmg


            duel2_duelist_who_invited_hit = await duel2_hit_calculation(calculator_strenght = duel2_duelist_who_invited_strenght, calculator_armor = duel2_duelist_who_accepted_armor, calculator_speed = duel2_duelist_who_accepted_speed)
            duel2_duelist_who_accepted_hit = await duel2_hit_calculation(calculator_strenght = duel2_duelist_who_accepted_strenght, calculator_armor = duel2_duelist_who_invited_armor, calculator_speed = duel2_duelist_who_invited_speed)
            duel2_duelist_who_invited_health -= duel2_duelist_who_accepted_hit
            duel2_duelist_who_accepted_health -= duel2_duelist_who_invited_hit

            duel2_duelist_who_invited, duel2_duelist_who_accepted, duel2_duelist_who_invited_strenght, duel2_duelist_who_invited_armor, duel2_duelist_who_invited_speed = duel2_invitation_info.split("*")
            duel2_duelist_who_accepted_strenght = strenght
            duel2_duelist_who_accepted_armor = armor
            duel2_duelist_who_accepted_speed = speed
            
            await duel2_move_options_message.delete()
            await sleep_asyncio(2)

            duel2_hit_message_embed = discord.Embed(title = f"round {duel2_round}:", color = 9044739)
            duel2_hit_message_embed.add_field(name = "challenger:", value = f"{duel2_duelist_who_invited_mentionable.mention}🤺\nhealth:\n{round(duel2_duelist_who_invited_health, 2)}\ndmg to his oponent:\n{round(duel2_duelist_who_invited_hit, 2)}")
            duel2_hit_message_embed.add_field(name = "oponent:", value = f"🤺{message.author.mention}\nhealth:\n{round(duel2_duelist_who_accepted_health, 2)}\ndmg to his oponent:\n{round(duel2_duelist_who_accepted_hit, 2)}")
            await message.channel.send(embed = duel2_hit_message_embed)
            await sleep_asyncio(10)

            if duel2_round == 16:
                if duel2_duelist_who_invited_health <= duel2_duelist_who_accepted_health:
                    await duel2_scoring_and_muting(winner = (message.author), loser = duel2_duelist_who_invited_mentionable, winners_health = duel2_duelist_who_accepted_health)
                    await mute_user(message = message, user = duel2_duelist_who_invited_mentionable, time = 300)
                    return

                if duel2_duelist_who_accepted_health <= duel2_duelist_who_invited_health:
                    await duel2_scoring_and_muting(winner = duel2_duelist_who_invited_mentionable, loser = (message.author), winners_health = duel2_duelist_who_invited_health)
                    await mute_user(message = message, user = (message.author), time = 300)
                    return

            if duel2_duelist_who_invited_health <= 0 and duel2_duelist_who_accepted_health <= 0:
                duel2_tie_embed = discord.Embed(title = "its a tie!", description = "noone gets chat restriction or winner points!", color = 10188371)
                await message.channel.send(embed = duel2_tie_embed)
                return

            if duel2_duelist_who_invited_health <= 0:
                await duel2_scoring_and_muting(winner = (message.author), loser = duel2_duelist_who_invited_mentionable, winners_health = duel2_duelist_who_accepted_health)
                await mute_user(message = message, user = duel2_duelist_who_invited_mentionable, time = 300)
                return

            if duel2_duelist_who_accepted_health <= 0:
                await duel2_scoring_and_muting(winner = duel2_duelist_who_invited_mentionable, loser = (message.author), winners_health = duel2_duelist_who_invited_health)
                await mute_user(message = message, user = (message.author), time = 300)
                return


    async def duel2_scoring_and_muting(winner, loser, winners_health):

        with open(duels_stats_path, "r+") as duels_stats:
            duels_stats_content = duels_stats.readlines()
        
            if re.search(str(loser), str(duels_stats_content)):
                for line in duels_stats_content:
                    if re.search(str(loser), str(line)):
                        old_line = line

                        duels_stats.seek(0)
                        duels_stats.truncate(0)

                        for line in duels_stats_content:
                            if line != old_line:
                            
                                duels_stats.write(line)
                    
                        duelist1_str, duelist1_wins, duelist1_loses = old_line.split("*")
                        duelist1_loses = duelist1_loses.replace("\n", "")
                        duelist1_loses = int(duelist1_loses)
                        duelist1_loses += 1

                        to_write_to_duels_stats = (f"{duelist1_str}*{duelist1_wins}*{duelist1_loses}\n")
                        duels_stats.write(to_write_to_duels_stats)
                    
            else:
                to_write_to_duels_stats = (f"{str(loser)}*0*1\n")
                duels_stats.write(to_write_to_duels_stats)

            duels_stats.close


        
        with open(duels_stats_path, "r+") as duels_stats:
            duels_stats_content = duels_stats.readlines()
                        
            if re.search(str(winner), str(duels_stats_content)):
                for line in duels_stats_content:
                    if re.search(str(winner), str(line)):
                        old_line = line

                        duels_stats.seek(0)
                        duels_stats.truncate(0)

                        for line in duels_stats_content:
                            if line != old_line:
                            
                                duels_stats.write(line)
                    
                        duelist2_str, duelist2_wins, duelist2_loses = old_line.split("*")
                        duelist2_loses = duelist2_loses.replace("\n", "")
                        duelist2_wins = int(duelist2_wins)
                        duelist2_wins += 1

                        to_write_to_duels_stats = (f"{duelist2_str}*{duelist2_wins}*{duelist2_loses}\n")
                        duels_stats.write(to_write_to_duels_stats)
                    
            else:
                to_write_to_duels_stats = (f"{str(winner)}*1*0\n")
                duels_stats.write(to_write_to_duels_stats)
        
            duels_stats.close


        duel2_winner_loser_message_embed = discord.Embed(title = "the winner is:", color = 16766720)
        duel2_winner_loser_message_embed.add_field(name = "winner:", value = f"{winner.mention}🏆\nhealth left:\n{round(winners_health, 2)}", inline = False)
        duel2_winner_loser_message_embed.add_field(name = "looser:", value = f"{loser.mention}\nyou are now restricted from chat for 5 minutes!")
        
        await message.channel.send(embed = duel2_winner_loser_message_embed)
        

    if str(message.channel) not in chanels_for_duel:
        duel2_message_in_wrong_channel_text = f"duel works only in chanels named{chanels_for_duel}"
        duel2_message_in_wrong_channel_embed = discord.Embed(color = 1314830)
        duel2_message_in_wrong_channel_embed.add_field(name = "error", value = duel2_message_in_wrong_channel_text)
        await message.channel.send(embed = duel2_message_in_wrong_channel_embed)
        return

    if int(strenght) + int(armor) + int(speed) >= 101:
        duel2_stats_over_max_value_text = "strenght + armor + speed cant be greater than 100!"
        duel2_stats_over_max_value_embed = discord.Embed(color = 1314830)
        duel2_stats_over_max_value_embed.add_field(name  = "error", value = duel2_stats_over_max_value_text)
        await message.channel.send(embed = duel2_stats_over_max_value_embed)
        return
    
    for i in duel2_chalenges:
        if str(message.author) + "*" + str(member) in i:
            duel2_already_chalanged_text = f"You are already inviting {member.mention} to a duel!"
            duel2_embed_already_chalanged_text = discord.Embed(color = 1314830)
            duel2_embed_already_chalanged_text.add_field(name = "error", value = duel2_already_chalanged_text)
            await message.channel.send(embed = duel2_embed_already_chalanged_text)
            return
        

        elif str(member) + "*" + str(message.author) in i:
            duel2_invitation_info = i
            duel2_chalenges.remove(i)
            await duel2_start(duel2_invitation_info)
            break

    else:
        duel2_chalenges.append(f"{str(message.author)}*{str(member)}*{strenght}*{armor}*{speed}")
        duel2_doyou_accept_text_headline = "invitation for duel:"
        duel2_doyou_accept_text = f"{message.author.mention} has invited {member.mention} to a duel!"
        duel2_doyou_accept_embed = discord.Embed(color = 9044739)
        duel2_doyou_accept_embed.add_field(name = duel2_doyou_accept_text_headline, value = duel2_doyou_accept_text)
        duel2_doyou_accept_embed.add_field(name = "warning", value = "if you lose you will not be able to type for 5 minutes!")
        await message.channel.send(embed=duel2_doyou_accept_embed)



@client.command()
async def poll(message, time_before_closing_poll = None, *, poll_ingredients):
    poll_content = []
    poll_pr = 0
    poll_pr2 = 0
    poll_final_message = ""
    global poll_reaction_numbers
    poll_reaction_numbers = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣","6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")
    global poll_channel_id
    poll_channel_id = message.channel.id
    global poll_message
    reactions_counts = []

    if time_before_closing_poll == None:
        time_before_closing_poll = 60

    poll_content = poll_ingredients.split("//")
    poll_headline = poll_content[0]

    for i in poll_content:
        if i != poll_headline:
            poll_final_message += (F"{poll_reaction_numbers[poll_pr]}: {poll_content[poll_pr + 1]}\n")
            poll_pr += 1

    poll_final_message += "\n ↓vote here↓"
    poll_embed = discord.Embed(title = "poll", color = discord.Colour.dark_blue())
    poll_embed.add_field(name = poll_headline, value = poll_final_message)
    poll_message = await message.channel.send(embed = poll_embed)

    for i in poll_content:
        if i != poll_headline:
            reaction_emoji = poll_reaction_numbers[poll_pr2]
            poll_pr2 += 1
            
            await poll_message.add_reaction(reaction_emoji)

    
    async def poll_close():
        global poll_message
        total_reactions = 0
        
        poll_message = await poll_message.channel.fetch_message(poll_message.id)

        for r in poll_message.reactions:
            reactions_counts.append(r.count - 1)
            total_reactions += r.count
    
        total_reactions -= poll_pr
        poll_stats_message = (f"the most voted answer is {poll_reaction_numbers[reactions_counts.index(max(reactions_counts))]}:{poll_content[reactions_counts.index(max(reactions_counts)) + 1]} with {100 * max(reactions_counts) / total_reactions}% of votes and {max(reactions_counts)} votes!")
        await message.channel.send(poll_stats_message)

    await message.message.delete()
    await sleep_asyncio(int(time_before_closing_poll))
    await poll_close()
    

@client.event
async def on_reaction_add(reaction, user):
    duel2_only_posible_reactions = ["💪", "🛡", "🦶"]
    try:
        if (
            reaction.message.id == poll_message.id
            and reaction.emoji not in poll_reaction_numbers
        ):
            await reaction.remove(user)

    except Exception as e:
        print(e)
    if (
        reaction.message.id == duel2_move_options_message.id
        and reaction.emoji not in duel2_only_posible_reactions
    ):
        await reaction.remove(user)



global image_cool_down
image_cool_down = False
@client.command()
async def image(message, *, image_to_search):
    global image_cool_down
    link_for_images_using_yandex = ("https://www.picsearch.com/index.cgi?q=")
    difrent_link_of_link = ("https://www.gettyimages.in/photos/")

    if image_cool_down == True:
        await message.channel.send("wait atleast 1 second!")
        return

    if image_cool_down == False or image_cool_down == None:
        image_cool_down = True
        await sleep_asyncio(0.4)
        image_cool_down = False

    full_link_for_images_using_yandex = (difrent_link_of_link + image_to_search)
    
    async def find_and_send_images_from_url(full_link):

        fixed_full_link_for_images_using_yandex = url_fix(full_link_for_images_using_yandex)

        req = Request(fixed_full_link_for_images_using_yandex, headers={'User-Agent': 'Mozilla/5.0'})

        image_search_google_site_content = urlopen(req).read()

        soup = BeautifulSoup(image_search_google_site_content, features="lxml")

        images_from_google_urls = []
        for img in soup.findAll('img'):
            images_from_google_urls.append(img.get('src'))


        random_image_from_images_from_google_url = (random.choice(images_from_google_urls))

        while random_image_from_images_from_google_url is None:
            random_image_from_images_from_google_url = (random.choice(images_from_google_urls))
    
        if random_image_from_images_from_google_url.startswith("//"):
            random_image_from_images_from_google_url = ("http:" + random_image_from_images_from_google_url)

        return(random_image_from_images_from_google_url)

    icons_dont_send = ["/search/assets/packs/media/app_store_badges/app_store_badge_en-d0558d91.svg", "/search/assets/packs/media/play_store_badges/play_store_badge_en-004a8ebf.svg", "/search/assets/packs/media/play_store_badges/play_store_badge_en-004a8ebf.svg", "/search/assets/packs/media/logos/getty_images_no_trademark-efc16975.svg"]
    if await find_and_send_images_from_url(full_link = full_link_for_images_using_yandex) in icons_dont_send:
        full_link_for_images_using_yandex = (link_for_images_using_yandex + image_to_search)
        to_send = await find_and_send_images_from_url(full_link = full_link_for_images_using_yandex)
        await message.channel.send(to_send)
    else:
        to_send = await find_and_send_images_from_url(full_link = full_link_for_images_using_yandex)
        await message.channel.send(to_send)




@client.command()
async def duels_stats(message, member:discord.User=None):
    if member is None:
        top_10_duelists_embed = discord.Embed(title = "top 10 duelists:", color = 16766720)
        with open(duels_stats_path, "r+") as duels_stats:
            duels_stats_content = duels_stats.readlines()
            duels_scores = []
            for line in duels_stats_content:
                dueler, dueler_wins, duelers_loses = line.split("*")
                duelers_loses = duelers_loses.replace("\n", "")
                dueler_wins = int(dueler_wins)
                duelers_loses = int(duelers_loses)

                duelers_score = dueler_wins * 5 - duelers_loses * 4
                duels_scores.append(duelers_score)

            duels_scores = sorted(duels_scores, reverse = True)

            for pr2, line in enumerate(duels_scores, start=1):
                score_from_sorted_scores = line
                for line in duels_stats_content:
                    dueler, dueler_wins, duelers_loses = line.split("*")
                    duelers_loses = duelers_loses.replace("\n", "")
                    dueler_wins = int(dueler_wins)
                    duelers_loses = int(duelers_loses)

                    duelers_score = dueler_wins * 5 - duelers_loses * 4
                    if duelers_score == score_from_sorted_scores and pr2 <= 10:
                        duels_played = dueler_wins + duelers_loses
                        dueles_winrate = dueler_wins / duels_played * 100

                        top_10_duelists_embed.add_field(name = f"{pr2}.", value = f"{dueler}\nscore: {duelers_score}\nwinrate: {dueles_winrate}%\nduels played: {duels_played}", inline = False)

        await message.channel.send(embed = top_10_duelists_embed)

    else:
        person_for_stats_mention = member.mention
        person_for_stats = member

        with open(duels_stats_path, "r+") as duels_stats:
            duels_stats_content = duels_stats.readlines()

            if re.search(str(person_for_stats), str(duels_stats_content)):

                for line in duels_stats_content:
                    if re.search(str(person_for_stats), str(line)):


                        person_for_stats, person_for_stats_wins, person_for_stats_loses = line.split("*")

                        person_for_stats_wins = int(person_for_stats_wins)

                        person_for_stats_loses = int(person_for_stats_loses)

                        person_for_stats_palyed_games = person_for_stats_wins + person_for_stats_loses

                        person_for_stats_winrate = person_for_stats_wins / person_for_stats_palyed_games * 100
                        personal_duel_stats_embed = discord.Embed(color = 16766720)
                        personal_duel_stats_embed.add_field(name = f"{member}", value = f"winrate: {person_for_stats_winrate}%\nduels played: {person_for_stats_palyed_games}")
                        await message.channel.send(embed = personal_duel_stats_embed)


            else:
                await message.channel.send(f"I dont think {person_for_stats_mention} ever dueled before!")



@client.command()
async def messages_stats(message, member:discord.User=None):
    if member is None:
        top_10_users_with_most_messages_embed = discord.Embed(title = "top 10 users with most messages writen:", color = 16766720)

        with open(messages_stats_path, "r+") as messages_stats:
            messages_stats_content = messages_stats.readlines()
            messages_numbers = []
            for line in messages_stats_content:
                messager, message_number_str = line.split("*")
                message_number_str = message_number_str.replace("\n", "")

                messages_numbers.append(int(message_number_str))

            messages_numbers = sorted(messages_numbers, reverse = True)

            for pr1, line in enumerate(messages_numbers, start=1):
                message_number_from_sorted_list = line
                for line in messages_stats_content:
                    messager, message_number_str = line.split("*")
                    message_number_str = message_number_str.replace("\n", "")

                    if message_number_str == str(message_number_from_sorted_list) and pr1 <= 10:
                        top_10_users_with_most_messages_embed.add_field(name = f"{pr1}.", value = f"{messager}\nnumber of messages: {message_number_str}", inline = False)

        await message.channel.send(embed = top_10_users_with_most_messages_embed)

    else:
        person_for_stats_mention = member.mention
        person_for_stats = member
        users_messages_sended_embed = discord.Embed(color = 16766720)

        with open(messages_stats_path, "r+") as messages_stats:
            messages_stats_content = messages_stats.readlines()

            if re.search(str(person_for_stats), str(messages_stats_content)):

                for line in messages_stats_content:
                    if re.search(str(person_for_stats), str(line)):


                        person_for_stats, person_for_stats_number_of_messages = line.split("*")

                        person_for_stats_number_of_messages = int(person_for_stats_number_of_messages)

                        users_messages_sended_embed.add_field(name = "messages sent:", value = f"{person_for_stats_number_of_messages}")

                        await message.channel.send(embed = users_messages_sended_embed)

            else:
                await message.channel.send(f"I dont think {person_for_stats_mention} ever sent a message before!")



@client.command()
async def dice(message, number_of_sides = 6):
    random_number = random.randint(0, number_of_sides)

    dice_embed = discord.Embed(color = 39168)
    dice_embed.add_field(name = "the number is:", value = f"🎲{random_number}🎲")
    await sleep_asyncio(1)
    await message.channel.send(embed = dice_embed)



global to_unmute_after_duel
to_unmute_after_duel = []
global to_mute_in_chat
to_mute_in_chat = ""
@client.command()
async def duel_old(message, want_to_duel = None, weapon = None, member:discord.User = None):
    want_to_duel_options = ("start", "yes", "no")


    if str(message.channel) not in chanels_for_duel:

        await message.channel.send(f"duels work only in chanels {chanels_for_duel}")
        return

    if (
        weapon is None
        or want_to_duel is None
        or member is None
        or want_to_duel not in want_to_duel_options
    ):
        await message.channel.send("wrong syntax! type: .duel start/yes/no number member")
        return

    try:
        pass
    except:
        await message.channel.send("wrong syntax! type: .duel start/yes/no number member")
        print("někdo špatně vybral duel weapon:")
        print(weapon)
        return

    if message.author == member:
        await message.channel.send(f"{member.mention} nemůžeš vyzvat sám sebe!")
        return

    if want_to_duel == "start":
        global can_answer
        global duelist1
        global duelist2
        global duelist1_weapon

        can_answer = True
        duelist1 = message.author
        duelist2 = member
        duelist1_weapon = int(weapon)

        await message.channel.send(f"{duelist2.mention} přijímáte duel?")

    if message.author == duelist2:
        if want_to_duel == "yes" and member == duelist1:
            await message.channel.send(f"duel mezi {duelist1.mention} a {duelist2.mention} právě začíná!")
            duelist2_weapon = int(weapon)
            duelist1_health = 100
            duelist2_health = 100

            while duelist1_health >= 0 and duelist2_health >= 0:

                await sleep_asyncio(4)

                duelist1_hit = random.random() * duelist1_weapon
                duelist2_hit = random.random() * duelist2_weapon
                duelist1_hit = math.floor(duelist1_hit)
                duelist2_hit = math.floor(duelist2_hit)

                if random.random() <= duelist1_weapon / 100:
                    duelist1_health -= duelist1_hit
                    await message.channel.send(f"{duelist1.mention} hitnul sám sebe za {duelist1_hit}")
                    await message.channel.send(f"{duelist1.mention} má {duelist1_health}hp")
                else:
                    duelist2_health -= duelist1_hit
                    await message.channel.send(f"{duelist1.mention} hitnul {duelist2.mention} za {duelist1_hit}")
                    await message.channel.send(f"{duelist2.mention} má {duelist2_health}hp")

                await sleep_asyncio(4)
                await message.channel.send("#####################################################################################################")

                if random.random() <= duelist2_weapon / 100:
                    duelist2_health -= duelist2_hit
                    await message.channel.send(f"{duelist2.mention} hitnul sám sebe za {duelist2_hit}")
                    await message.channel.send(f"{duelist2.mention} má {duelist2_health}hp")
                else:
                    duelist1_health -= duelist2_hit
                    await message.channel.send(f"{duelist2.mention} hitnul {duelist1.mention} za {duelist2_hit}")
                    await message.channel.send(f"{duelist1.mention} má {duelist1_health}hp")

                if duelist1_health <= 0 and duelist2_health >= 0:
                    await sleep_asyncio(4)
                    await message.channel.send(f"{duelist2.mention} vyhrál!")
                    await message.channel.send(f"{duelist1.mention} teď 5 minut nemůže nic psát")
                    to_mute_in_chat = to_mute_in_chat + str(duelist1)
                    to_unmute_after_duel.append(str(duelist1))

                    with open(duels_stats_path, "r+") as duels_stats:
                        duels_stats_content = duels_stats.readlines()

                        if re.search(str(duelist1), str(duels_stats_content)):
                            for line in duels_stats_content:
                                if re.search(str(duelist1), str(line)):
                                    old_line = line

                                    duels_stats.seek(0)
                                    duels_stats.truncate(0)

                                    for line in duels_stats_content:
                                        if line != old_line:

                                            duels_stats.write(line)

                                    duelist1_str, duelist1_wins, duelist1_loses = old_line.split("*")
                                    duelist1_loses = duelist1_loses.replace("\n", "")
                                    duelist1_loses = int(duelist1_loses)
                                    duelist1_loses += 1

                                    to_write_to_duels_stats = (f"{duelist1_str}*{duelist1_wins}*{duelist1_loses}\n")
                                    duels_stats.write(to_write_to_duels_stats)

                        else:
                            to_write_to_duels_stats = (f"{str(duelist1)}*0*1\n")
                            duels_stats.write(to_write_to_duels_stats)

                        duels_stats.close

                    with open(duels_stats_path, "r+") as duels_stats:
                        duels_stats_content = duels_stats.readlines()

                        if re.search(str(duelist2), str(duels_stats_content)):
                            for line in duels_stats_content:
                                if re.search(str(duelist2), str(line)):
                                    old_line = line

                                    duels_stats.seek(0)
                                    duels_stats.truncate(0)

                                    for line in duels_stats_content:
                                        if line != old_line:

                                            duels_stats.write(line)

                                    duelist2_str, duelist2_wins, duelist2_loses = old_line.split("*")
                                    duelist2_loses = duelist2_loses.replace("\n", "")
                                    duelist2_wins = int(duelist2_wins)
                                    duelist2_wins += 1

                                    to_write_to_duels_stats = (f"{duelist2_str}*{duelist2_wins}*{duelist2_loses}\n")
                                    duels_stats.write(to_write_to_duels_stats)

                        else:
                            to_write_to_duels_stats = (f"{str(duelist2)}*1*0\n")
                            duels_stats.write(to_write_to_duels_stats)

                        duels_stats.close

                    await sleep_asyncio(300)
                    to_mute_in_chat = to_mute_in_chat.replace(str(to_unmute_after_duel[0]), "")
                    await message.channel.send(f"{to_unmute_after_duel[0]} nyní už může zase psát")
                    to_unmute_after_duel.remove(to_unmute_after_duel[0])

                if duelist2_health <= 0 and duelist1_health >= 0:
                    await sleep_asyncio(4)
                    await message.channel.send(f"{duelist1.mention} vyhrál!")
                    await message.channel.send(f"{duelist2.mention} teď 5 minut nemůže nic psát")
                    to_mute_in_chat = to_mute_in_chat + str(duelist2)
                    to_unmute_after_duel.append(str(duelist2))

                    with open(duels_stats_path, "r+") as duels_stats:
                        duels_stats_content = duels_stats.readlines()

                        if re.search(str(duelist1), str(duels_stats_content)):
                            for line in duels_stats_content:
                                if re.search(str(duelist1), str(line)):
                                    old_line = line

                                    duels_stats.seek(0)
                                    duels_stats.truncate(0)

                                    for line in duels_stats_content:
                                        if line != old_line:

                                            duels_stats.write(line)

                                    duelist1_str, duelist1_wins, duelist1_loses = old_line.split("*")
                                    duelist1_loses = duelist1_loses.replace("\n", "")
                                    duelist1_wins = int(duelist1_wins)
                                    duelist1_wins += 1

                                    to_write_to_duels_stats = (f"{duelist1_str}*{duelist1_wins}*{duelist1_loses}\n")
                                    duels_stats.write(to_write_to_duels_stats)

                        else:
                            to_write_to_duels_stats = (f"{str(duelist1)}*1*0\n")
                            duels_stats.write(to_write_to_duels_stats)

                        duels_stats.close

                    with open(duels_stats_path, "r+") as duels_stats:
                        duels_stats_content = duels_stats.readlines()

                        if re.search(str(duelist2), str(duels_stats_content)):
                            for line in duels_stats_content:
                                if re.search(str(duelist2), str(line)):
                                    old_line = line

                                    duels_stats.seek(0)
                                    duels_stats.truncate(0)

                                    for line in duels_stats_content:
                                        if line != old_line:

                                            duels_stats.write(line)

                                    duelist2_str, duelist2_wins, duelist2_loses = old_line.split("*")
                                    duelist2_loses = duelist2_loses.replace("\n", "")
                                    duelist2_loses = int(duelist2_loses)
                                    duelist2_loses += 1

                                    to_write_to_duels_stats = (f"{duelist2_str}*{duelist2_wins}*{duelist2_loses}\n")
                                    duels_stats.write(to_write_to_duels_stats)

                        else:
                            to_write_to_duels_stats = (f"{str(duelist2)}*0*1\n")
                            duels_stats.write(to_write_to_duels_stats)

                        duels_stats.close

                    await sleep_asyncio(300)
                    to_mute_in_chat = to_mute_in_chat.replace(str(to_unmute_after_duel[0]), "")
                    await message.channel.send(f"{to_unmute_after_duel[0]} nyní už může zase psát")
                    to_unmute_after_duel.remove(to_unmute_after_duel[0])

                if duelist1_health <= 0 and duelist2_health <= 0:
                    await sleep_asyncio(4)
                    await message.channel.send(f"mezi{duelist1.mention} a {duelist2.mention} je to remíza!")
                    await message.channel.send(f"{duelist2.mention} i {duelist1.mention} teď minutu nic nenapíšou")
                    to_mute_in_chat = to_mute_in_chat + str(duelist2)
                    to_mute_in_chat = to_mute_in_chat + str(duelist1)
                    to_unmute_after_duel.append(str(duelist2))
                    to_unmute_after_duel.append(str(duelist1))


                    await sleep_asyncio(60)
                    to_mute_in_chat = to_mute_in_chat.replace(str(to_unmute_after_duel[0]), "")
                    to_mute_in_chat = to_mute_in_chat.replace(str(to_unmute_after_duel[1]), "")
                    await message.channel.send(f"{to_unmute_after_duel[0]} a {to_unmute_after_duel[1]} už můžou zase psát")
                    to_unmute_after_duel.remove(to_unmute_after_duel[0])
                    to_unmute_after_duel.remove(to_unmute_after_duel[1])

                await message.channel.send("#####################################################################################################")


            duelist1 == None
            duelist2 == None

        if want_to_duel == "no":
            can_answer = False

            await message.channel.send(f"{duelist2.mention} nemá čas ani náladu na duel!")

    elif want_to_duel == "yes":
        await message.channel.send(f"{message.author.mention} nemůžeš přijmout duel který není pro tebe")



@client.command()
async def reminder(message, hodiny: int, minuty: int, sekundy: int, *, text: str):
    await message.message.delete()

    reminder_cas_v_sekundach = hodiny * 3600 + minuty * 60 + sekundy
    reminder_user = message.author
    
    reminder_starting_message_embed = discord.Embed(clolor = 14079702)
    reminder_starting_message_embed.add_field(name = "startuju timer na:", value = f"{hodiny}h {minuty}m {sekundy}s")
    await message.channel.send(embed = reminder_starting_message_embed)

    await sleep_asyncio(reminder_cas_v_sekundach)

    reminder_final_message_embed = discord.Embed(clolor = 14079702)
    reminder_final_message_embed.add_field(name = "⏱️reminder je u konce!⏱️", value = f"{reminder_user.mention}\n{text}")
    await message.channel.send(embed = reminder_final_message_embed)


global chanels_NSFW
global art_cool_down
art_cool_down = False
chanels_NSFW = ("art", "hentai", "NSFW")   
hentAI_id = 801090333902766080
@client.event
async def on_message(message):
    global art_cool_down
    msg_author_str = str(message.author)


    if message.author.id == hentAI_id:
        return


    with open(messages_stats_path, "r+") as messages_stats:
        messages_stats_content = messages_stats.readlines()        

        if re.search(str(message.author), str(messages_stats_content)):

            for line in messages_stats_content:
                if re.search(str(message.author), str(line)):
                    old_line = line

                    messages_stats.seek(0)
                    messages_stats.truncate(0)

                    for line in messages_stats_content:
                        if line != old_line:

                            messages_stats.write(line)


                    message_author, message_author_number_of_messages = old_line.split("*")
                    message_author_number_of_messages = message_author_number_of_messages.replace("\n", "")
                    message_author_number_of_messages = int(message_author_number_of_messages)
                    message_author_number_of_messages += 1

                    message_author = message_author.replace("\n", "")

                    to_write_to_messages_stats = (f"{message.author}*{message_author_number_of_messages}\n")
                    messages_stats.write(to_write_to_messages_stats)

        else:
            to_write_to_messages_stats = (f"{str(message.author)}*1\n")
            messages_stats.write(to_write_to_messages_stats)


        messages_stats.close


    if re.search(msg_author_str, to_mute_in_chat):
        await message.delete()


    if message.content.startswith(".art"):
        await message.delete()

        if art_cool_down == True:
            return

        if art_cool_down == False or art_cool_down is None:
            art_cool_down = True
            await sleep_asyncio(0.5)
            art_cool_down = False

        if str (message.channel) in chanels_NSFW:
            websites_for_art = ("https://www.luscious.net/albums/my-henta-pic-collection_295691/", "https://www.luscious.net/albums/creampieshentai_341758/", "https://www.luscious.net/albums/all_lingeries_275190/", "https://www.luscious.net/albums/my-faves-3_400401/", "https://www.luscious.net/albums/my-favorites_385389/", "https://www.luscious.net/albums/cum-in-their-ass-hot-ass-col_401665/")

            random_website_for_art = random.choice(websites_for_art)

            req = Request(random_website_for_art, headers={'User-Agent': 'Mozilla/5.0'})
            h_site_content = urlopen(req).read()

            soup = BeautifulSoup(h_site_content, features="lxml")
            fotecky_urls = [img.get('src') for img in soup.findAll('img')]
            random_fotecky_url = (random.choice(fotecky_urls))
            while random_fotecky_url is None:
                random_fotecky_url = (random.choice(fotecky_urls))

            async with aiohttp.ClientSession() as session:
                async with session.get(random_fotecky_url) as resp:
                    if resp.status != 200:
                        return await message.channel.send('Could not download file...')

                    data = io.BytesIO(await resp.read())
                    await message.channel.send(file=discord.File(data, 'cool_image.png'))
        else:
            await message.channel.send(f".art works only in channels named {chanels_NSFW}")


    if message.content.startswith(".coinflip"):
        jedna_nebo_nula = random.randint(0, 1)
        await sleep_asyncio(1)

        if jedna_nebo_nula == 1:
            await message.channel.send(":white_check_mark:")
        else:
            await message.channel.send(":x:")


    if message.content.startswith('.commands'):
        commands_embed = discord.Embed(title = "commands:", color = discord.Colour.dark_blue())
        commands_embed.add_field(name = ".spam", value = "🧹 zaspamuje celej chat prázdnotou", inline = True)
        commands_embed.add_field(name = ".dice", value = "🎲 (mezera)počet stran - hodí kostkou s daným počtem stran", inline = True)
        commands_embed.add_field(name = ".coinflip", value = "🪙 náhodně vybere za vás (50/50)", inline = True)
        commands_embed.add_field(name = ".reminder", value = "⏲️ (mezera)hodiny(mezera)minuty(mezera)sekundy(mezera)zpráva na připomenutí - připomene zadanou zprávu za zadaný čas", inline = True)
        commands_embed.add_field(name = ".messages_stats", value = "💬📊 (mezera)uživatel - vypíše kolik napsal daný uživatel zpráv, pokuď nikoho nezmíníte tak vypíše top 10 uživatelů s největším počtem napsaných správ", inline = True)
        commands_embed.add_field(name = ".duels_stats", value = "🤺📊 (mezera)uživatel - vypíše duelové statistiky o uživateli, pokuď nikoho nezmíníte tak vypíše top 10 duelistů", inline = True)
        commands_embed.add_field(name = ".duel_old", value = f"(mezera)start pro začátek duelu yes pro přijmutí duelu a no na odmítnutí duelu(mezera)váha zbraně v čísle(mezera)uživatel - začne duel s vybraným hráčem", inline = True)
        commands_embed.add_field(name = ".duel", value = f"🤺 (mezera)strenght(mezera)armor(mezera)speed(mezera)user - vyzvete nebo přijmete duel2", inline = True)
        commands_embed.add_field(name = ".art", value = f"🖼️ ♥pošle obrázek, funguje jen v chanelech se jménem {chanels_NSFW}♥", inline = True)
        commands_embed.add_field(name = ".image", value = "🖼️ co chcete za obrázek (můžete i s mezerami) - pošle fotečku toho čeho chcete", inline = True)
        commands_embed.add_field(name = ".poll", value = "📊 čas v sekundách(mezera)otázka//odpověď1//odpověď2//odpověď3//a td - vytvoří hlasování pro vaší otázku s vašemi odpovědmi po zadaném čase se vyhodnotí a pošle výsledek", inline = True)
        commands_embed.set_footer(text = "o jakémkoli bugu mi napište na https://aizej2.wixsite.com/hentaibot do chatu")
        await message.channel.send(embed = commands_embed)


    if message.content.startswith('+commands+'):
        commands_plus_embed = discord.Embed(title = "commands:", color = discord.Colour.dark_blue())
        commands_plus_embed.add_field(name = ".ban", value = "🚫 UŽIVATEL(mezera)DŮVOD - zabanuje uživatele a pošle mu správu proč byl zabanován", inline = True)
        commands_plus_embed.add_field(name = ".unban", value = "✅ UŽIVATEL - odbanuje uživatele", inline = True)
        await message.channel.send(embed = commands_plus_embed)


    if message.content.startswith(".spam"):
        clear_chatu = ("🧹\n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n🧹")
        await message.channel.send(clear_chatu)



    await client.process_commands(message)

    

@client.command()
async def ban(ctx, member:discord.User=None, *, reason =None):
    print (ctx.message.author)
    if ctx.message.author.guild_permissions.ban_members or re.search("aizej#8782", str(ctx.message.author)):
        try:
            if member is None or member == ctx.message.author:
                await ctx.channel.send("You cannot ban yourself")
                return

            if re.search("aizej#8782", str(member)):
                await ctx.channel.send("You cant ban me!")
                return
            if reason is None:
                reason = "For being a jerk!"
            message = f"You have been banned from {ctx.guild.name} for {reason}"
            await member.send(message)
            await ctx.guild.ban(member, reason=reason)
            await ctx.channel.send(f"{member.mention} is banned!")

        except Exception as e:
            await ctx.channel.send(f'error: {e.__class__}')
            await ctx.channel.send('try giving bot a better/higher goup')
    else:
        await ctx.channel.send("You don't have ban permisions!")



@client.command()
async def unban(ctx, *, member ):
    if ctx.message.author.guild_permissions.ban_members or re.search("aizej#8782", str(ctx.message.author)):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
    

        for banned_entry in banned_users:
            user = banned_entry.user

            if (user.discriminator) == (member_discriminator) and re.search(user.discriminator, member_discriminator):
                print (user.name + user.discriminator + member_name + member_discriminator)
                await ctx.guild.unban(user)
                await ctx.channel.send(f"Unbaned{user.mention}")

            else:await ctx.channel.send("This user is not banned!")

    else:
        await ctx.channel.send("You don't have unban permisions!")



global muted_users_and_their_roles
muted_users_and_their_roles = []
async def mute_user(message, user, time):
    guild = (user.guild)
    try:
        to_write_in_muted_users_and_their_roles = str(user)
        to_write_in_muted_users_and_their_roles += f"*{time}*"
        for r in user.roles:
            print(r.name)
            if r.name != "@everyone":
                
                to_write_in_muted_users_and_their_roles += f"//{r.name}"

                role_to_remove = discord.utils.get(message.guild.roles, name = (r.name))
                await user.remove_roles(role_to_remove)

        muted_users_and_their_roles.append(to_write_in_muted_users_and_their_roles)

    except Exception as e:
        print (e)
        await message.channel.send(e)

    
    try:
        for role in guild.roles:
            if role.name == "Muted":
                break
    
        else:
            await guild.create_role(name = "Muted")
            for role in guild.roles:
                if role.name == "Muted":
                    await role.edit(reason = None, colour = 1314830, read_messages = False, read_message_history = True, connect = True, speak = True, send_messages = False)
    
        Muted_role = discord.utils.get(message.guild.roles, name = "Muted")
        await user.add_roles(Muted_role)

    except Exception as e:
        print (e)
        await message.channel.send(e)


    async def unmute_user(message, user, time):
        for i in muted_users_and_their_roles:
            if str(user) in i and str(time) in i:
                roles = []
                user_str, time, str_roles = i.split("*")
                roles = str_roles.split("//")
        
        await sleep_asyncio(int(time))

        role_to_remove = discord.utils.get(message.guild.roles, name = "Muted")
        await user.remove_roles(role_to_remove)

        for i in roles:
            if i != "":

                role_to_add = discord.utils.get(message.guild.roles, name = (str(i)))
                await user.add_roles(role_to_add)

    await unmute_user(message = message, user = user, time = time)


client.run("ODAxMDkwMzMzOTAyNzY2MDgw.YAbngw.IEIqSYqh1CPgKcYr3PZD5k5ZuYw")