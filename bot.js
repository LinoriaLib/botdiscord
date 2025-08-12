const { Client, GatewayIntentBits } = require('discord.js');
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// Replace this with your bot token
const TOKEN = 'MTQwNDc0MjY2MTQyMzc2MzU3Nw.GaSTtA.rWpVpTo8uhQGA0p4rQyscItZjW50Ss38xuxkgo';

client.once('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

client.on('messageCreate', message => {
  // Ignore messages from bots
  if (message.author.bot) return;

  // Check if the message content is "hello"
  if (message.content.toLowerCase() === 'hello') {
    message.channel.send('Hello!');
  }
});

client.login(TOKEN);
