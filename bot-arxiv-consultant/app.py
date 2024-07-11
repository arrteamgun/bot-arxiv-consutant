#!/usr/bin/env python3
import os
import telebot
import logging
import urllib
import urllib.request
import urllib.parse
from xml.etree import ElementTree as ET
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(filename='bot.log', level=logging.INFO)
logger = logging.getLogger('arxiv_consultant_bot')
logger.setLevel(logging.INFO)
logger.info('bot is started!')

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

bot.set_my_commands([
    telebot.types.BotCommand("/start", "main menu"),
    telebot.types.BotCommand("/help", "print usage"),
    telebot.types.BotCommand("/find", "finds sources")
])


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, 'hi')


@bot.message_handler(commands=['help'])
def help(message):
    commands = bot.get_my_commands()
    response = "Bot commands:\n"
    for command in commands:
        response += f"/{command.command} - {command.description}\n"
    bot.reply_to(message, response)


def xml_selector(xml_string) -> str:
    ns = {'atom': 'http://www.w3.org/2005/Atom',
          'arxiv': 'http://arxiv.org/schemas/atom'}
    root = ET.fromstring(xml_string)
    entries = root.findall(".//atom:entry", ns)
    results = ''
    for entry in entries:
        # get title/authors/pdf link
        title = entry.find(".//{*}title")
        title_text = title.text if title is not None else "No title"
        authors = entry.findall(".//{*}author")
        author_names = [author.find(
            ".//{*}name").text for author in authors if author.find(".//{*}name") is not None]
        pdf_link = None
        links = entry.findall(".//{*}link")
        for link in links:
            if link.get('title') == 'pdf':
                pdf_link = link.get('href')
                break
        # formatting
        results += f"*Title*: {title_text}\n*Authors*: {', '.join(
            author_names)}\n*Document's Link*: {pdf_link if pdf_link else 'No PDF link'}\n\n"
    return results


@bot.message_handler(commands=['find'])
def find(message):
    query = urllib.parse.quote_plus(message.text)
    url = f'http://export.arxiv.org/api/query?search_query={
        query}&start=0&max_results=5'
    data = urllib.request.urlopen(url).read().decode('utf-8')
    bot.reply_to(message, xml_selector(data))

bot.infinity_polling()