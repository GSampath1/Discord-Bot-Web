import os
from flask import Flask, redirect, url_for, render_template, request
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from threading import Thread
import requests
import json

app = Flask(__name__,
            template_folder="template", static_folder='assets', static_url_path="/assets")

with open("config.json", "r") as f:
    config = json.load(f)

app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
# !! Only in development environment.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = config["client_id"]
app.config["DISCORD_CLIENT_SECRET"] = "BEu_bVlzw-1DIX0eLpy3BBJhMrl-Ge1V"
app.config["DISCORD_BOT_TOKEN"] = config["client_token"]
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:4000/auth/callback"

discord = DiscordOAuth2Session(app)
HYPERLINK = '<a href="{}">{}</a>'


@app.route("/auth/login/")
async def login():
    return discord.create_session()


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))


@app.route("/auth/callback")
async def callback():
    data = discord.callback()
    redirect_to = data.get("redirect", "/")
    return redirect(redirect_to)

"""@app.errorhandler(404)
async def page_not_found(error):
    return redirect("/404")"""


@app.route("/logout/")
async def logout():
    discord.revoke()
    return redirect(url_for(".index"))
"""
@app.route("/404")
async def error404():
    return render_template('404.html'), 404"""


@app.route("/support")
async def support():
    return redirect('https://discord.gg/Z8JqBrpCh8')


@app.route("/auth/invite/<int:guild>")
async def invite(guild=None):
    if not guild == None:
        return discord.create_session(scope=["bot", "applications.commands"], permissions=8, guild_id=guild, disable_guild_select=True, redirect=f"/guild/{guild}")
    return redirect('')


@app.route("/")
async def index():
    if not discord.authorized:
        return render_template('index.html', authorized=False)

    user = discord.fetch_user()
    return render_template('index.html', authorized=True, user=user)


@app.route("/dashboard/")
def user_guilds():
    bot_guild = []
    if not discord.authorized:
        return redirect("/login")
    guilds = discord.fetch_guilds()
    user = discord.fetch_user()
    for g in guilds:
        if g.permissions.administrator:
            r = discord.bot_request(f"/guilds/{g.id}", "GET")
            try:
                r["code"]
                continue
            except:
                bot_guild.append(g)
                pass
    return render_template('dashboard.html', authorized=True, user=user, guild=guilds, bot_guild=bot_guild)


@app.route("/secret/")
@requires_authorization
async def secret():
    return os.urandom(16)


def run():
    app.run(port=4000)
