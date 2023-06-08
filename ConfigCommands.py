import disnake
from disnake.ext import commands
from disnake.ext.commands import has_permissions
import yaml

class Global(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @has_permissions(manage_channels=True)
    async def get(self, interaction):
        pass

    @get.sub_command(description="Сохраняет айди канала для создания приваток")
    async def channel(self, interaction, channel: disnake.VoiceChannel):
        channel_id = channel.id

        with open('config.yml', 'r') as f:
            existing_data = yaml.safe_load(f)

        existing_data['channel_id'] = channel_id

        with open('config.yml', 'w') as f:
            yaml.dump(existing_data, f)

        await interaction.response.send_message(f"Айди канала <#{channel_id}> сохранен в config.yml")

    @get.sub_command(description="Сохраняет айди категории для создания приваток")
    async def category(self, interaction, category: disnake.CategoryChannel):
        category_id = category.id

        with open('config.yml', 'r') as f:
            existing_data = yaml.safe_load(f)

        existing_data['category_id'] = category_id

        with open('config.yml', 'w') as f:
            yaml.dump(existing_data, f)

        await interaction.response.send_message(f"Айди категории <#{category_id}> сохранен в config.yml")

def setup(bot):
    bot.add_cog(Global(bot))