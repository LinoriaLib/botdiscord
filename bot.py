import os
import discord
import requests
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))
API_URL = os.getenv("API_URL")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


def is_authorized(interaction: discord.Interaction) -> bool:
    return any(role.id == ALLOWED_ROLE_ID for role in interaction.user.roles)


class ConfirmActionView(View):

    def __init__(self, action, userid, reason, day, username,
                 interaction_user):
        super().__init__(timeout=60)
        self.action = action  # "ban", "kick", "unban"
        self.userid = userid
        self.reason = reason
        self.day = day
        self.username = username
        self.interaction_user = interaction_user

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "⛔ You are not the one who initiated this action.",
                ephemeral=True)
            return

        data = {
            "command": self.action,
            "userid": self.userid,
            "reason": self.reason
        }
        if self.day is not None:
            data["day"] = self.day

        requests.post(f"{API_URL}/send_command", json=data)

        await interaction.response.edit_message(content=(
            f"✅ `{self.username}` (ID: `{self.userid}`) has been `{self.action}`ed.\n"
            f"📌 **Reason:** {self.reason}" +
            (f"\n📆 Duration (days): {self.day}" if self.day else "")),
                                                embed=None,
                                                view=None)

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "⛔ You are not the one who initiated this action.",
                ephemeral=True)
            return

        await interaction.response.edit_message(
            content="❌ Action has been cancelled.", embed=None, view=None)


async def get_roblox_user_embed(userid: str, interaction_user: discord.User):
    # 1. Get Roblox user info
    user_info_url = f"https://users.roblox.com/v1/users/{userid}"
    user_response = requests.get(user_info_url)

    if user_response.status_code != 200:
        return None, None

    user_data = user_response.json()
    username = user_data.get("name", "Unknown")
    display_name = user_data.get("displayName", username)
    profile_link = f"https://www.roblox.com/users/{userid}/profile"

    # 2. Get avatar from Roblox Thumbnail API
    avatar_url = None
    thumb_url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png&isCircular=false"
    thumb_response = requests.get(thumb_url)

    if thumb_response.status_code == 200:
        thumb_data = thumb_response.json()
        if thumb_data.get("data") and len(thumb_data["data"]) > 0:
            avatar_url = thumb_data["data"][0].get("imageUrl")

    # 3. Create embed
    embed = discord.Embed(
        title="🔍 Confirm Roblox User",
        description=(f"**👤 Username:** {username}\n"
                     f"**📛 Display Name:** {display_name}\n"
                     f"**🆔 UserId:** `{userid}`\n"
                     f"🔗 [View Roblox Profile]({profile_link})"),
        color=discord.Color.orange())

    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.set_footer(text=f"Requested by {interaction_user}",
                     icon_url=interaction_user.display_avatar.url)
    return embed, username


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user} (slash commands synced)")


@tree.command(name="ban", description="Ban a player by UserId")
@app_commands.describe(userid="Roblox UserId",
                       reason="Reason for ban",
                       day="Number of days (e.g., 7)")
async def ban(interaction: discord.Interaction, userid: str, reason: str,
              day: int):
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True)
        return

    embed, username = await get_roblox_user_embed(userid, interaction.user)
    if not embed:
        await interaction.response.send_message(
            "❌ Could not retrieve user information.", ephemeral=True)
        return

    view = ConfirmActionView("ban", userid, reason, day, username,
                             interaction.user)
    await interaction.response.send_message(embed=embed, view=view)


@tree.command(name="kick", description="Kick a player by UserId")
@app_commands.describe(userid="Roblox UserId", reason="Reason for kick")
async def kick(interaction: discord.Interaction, userid: str, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True)
        return

    embed, username = await get_roblox_user_embed(userid, interaction.user)
    if not embed:
        await interaction.response.send_message(
            "❌ Could not retrieve user information.", ephemeral=True)
        return

    view = ConfirmActionView("kick", userid, reason, None, username,
                             interaction.user)
    await interaction.response.send_message(embed=embed, view=view)


@tree.command(name="unban", description="Unban a player by UserId")
@app_commands.describe(userid="Roblox UserId", reason="Reason for unban")
async def unban(interaction: discord.Interaction, userid: str, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True)
        return

    embed, username = await get_roblox_user_embed(userid, interaction.user)
    if not embed:
        await interaction.response.send_message(
            "❌ Could not retrieve user information.", ephemeral=True)
        return

    view = ConfirmActionView("unban", userid, reason, None, username,
                             interaction.user)
    await interaction.response.send_message(embed=embed, view=view)


@tree.command(
    name="check",
    description="Check how many players are currently online in the game")
async def check(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True)
        return

    try:
        res = requests.get(f"{API_URL}/get_players")
        data = res.json()
        await interaction.response.send_message(
            f"👥 There are currently `{data['count']}` players online in the game."
        )
    except Exception as e:
        await interaction.response.send_message(
            f"⚠️ Failed to fetch data from server: {e}", ephemeral=True)


# Run bot
if __name__ == "__main__":
    bot.run(TOKEN)

# MADE BY DAI VIET
