# Eigen Bot - Comprehensive Discord Community Bot

> **A feature-rich, production-ready Discord bot for community engagement, support tickets, entertainment, and powerful moderation tools.**

Eigen Bot is an all-in-one Discord bot designed for thriving communities. Built with modern async Python and discord.py, it offers a complete suite of features from support ticket systems and starboard highlights to voting systems and custom tags—all with hybrid command support (both prefix `?` and slash `/` commands).

---

## Developers
- [@youngcoder45](https://github.com/youngcoder45)
- [@1Frodox](https://github.com/1Frodox)

---

## Core Features

### **🎫 Ticket System**
Professional support ticket management using Discord threads:

**Features:**
- **Multiple Categories**: General Support, Bug Reports, Feature Requests, Partnership, Reports, Other Issues
- **Thread-Based Tickets**: Each ticket is a private thread with organized discussions
- **Interactive UI**: Button-based interface for creating and managing tickets
- **Ticket Controls**: Close tickets, claim tickets (for staff), automatic archiving
- **Customizable Roles**: Set different roles for support, reports, and partnerships
- **Ticket Logging**: Optional logging channel for all ticket actions
- **Persistent Panels**: Create ticket panels that survive bot restarts
- **Numbered Tickets**: Auto-incrementing ticket numbers for easy tracking

**Commands:**
- `/ticketpanel` - Create a persistent ticket panel
- `/ticketlog` - Configure ticket logging channel
- `/ticketsupport` - Set support team role
- `/ticketreport` - Set report team role
- `/ticketpartner` - Set partnership team role
- `/tickets` - List all tickets (open, closed, or all)
- `/ticketstats` - View ticket system statistics
- `/forceclose` - Force close a ticket (admin)

### **⭐ Starboard System**
Highlight the best messages in your community:
- **Automatic Highlighting**: Messages that reach a star threshold appear in starboard
- **Customizable**: Set custom star emoji, adjustable threshold, self-starring toggle
- **Beautiful Embeds**: Dynamic colors based on star count, author thumbnails, timestamps
- **Real-time Updates**: Starboard messages update as stars are added/removed
- **Smart Handling**: Tracks who starred what, prevents duplicates, handles uncached messages
- **Admin Tools**: `?starboard_cleanup` to remove invalid entries

### **🏷️ Tag System**
Create and share custom text snippets:
- **Create Tags**: `?tags create <name> <content>` - Store reusable text
- **Retrieve Tags**: `?tag <name>` - Quickly fetch stored content
- **Edit Tags**: `?tags edit <name> <new_content>` - Update existing tags
- **Delete Tags**: `?tags delete <name>` - Remove unwanted tags
- **List Tags**: `?tags list` - View all server tags
- **Usage Tracking**: Tracks how many times each tag is used

### **🗳️ Election/Voting System**
Democratic decision-making for your community:
- **Create Elections**: `?election create <title> <candidates> [duration]`
- **Weighted Voting**: Vote strength based on user roles/tenure
- **Multiple Candidates**: Support for 2-10 candidates per election
- **Live Results**: Real-time vote counting and display
- **Interactive Voting**: Button-based voting interface
- **Timed Elections**: Auto-close after specified duration

### **💻 CodeBuddy System**
Engage your community with coding challenges and leaderboards:
- **Coding Quizzes**: Test your knowledge with automated coding questions
- **Leaderboards**: Weekly, all-time, and streak tracking
- **Stats & Flex**: Personal statistics and shareable stat cards
- **Engagement**: Earn points for correct answers and climb the ranks

### **🎭 Fun Commands**
Entertainment and engagement features:
- **Programming Jokes**: `?joke` - Get a clean programming-related joke
- **Compliments**: `?compliment [@user]` - Give professional programming compliments
- **Fortune**: `?fortune` - Receive a programming-themed fortune
- **Trivia**: `?trivia` - Programming trivia questions
- **8-Ball**: `?8ball <question>` - Magic 8-ball responses
- **Coin Flip**: `?coinflip` - Heads or tails
- **Dice Roll**: `?roll [size] [count]` - Roll dice

### **👥 Community Engagement**
Build an active, engaged community:
- **Random Quotes**: `?quote` - Inspirational programming quotes
- **Random Questions**: `?question` - Programming discussion starters
- **Memes**: `?meme` - Programming humor
- **Suggestions**: Submit and discuss community ideas

### **🛠️ Utility Commands**
Helpful tools for server management:
- **Emote List**: `?emotes [search]` - Browse server emojis
- **Member Count**: `?membercount` - View current server member count
- **Random Color**: `?randomcolor` - Generate random hex colors
- **Reminders**: `?remindme <time> <message>` - Set personal reminders
- **User Info**: `?whois [@user]` - Detailed user information

### **💤 AFK System**
- Set AFK status with custom reasons
- Auto-respond to mentions
- Track time away
- Automatic AFK removal when you send a message

### **🎂 Birthday System**
- Set your birthday
- Automatic birthday announcements
- Birthday role assignment
- Birthday leaderboard

### **📈 Bump Reminder**
- Remind users to bump the server on listing sites
- Configurable bump intervals
- Automatic reminders

### **🔧 Admin & Moderation**
Powerful tools for server administrators:
- **Bot Management**: `?reload <cog>` - Reload cogs on the fly
- **Command Sync**: `?sync` - Sync slash commands
- **Permission-Based**: All admin commands restricted to administrators/bot owner

---

## Technical Excellence

### **Architecture & Design**
- **Async/Await**: Full async implementation for optimal performance
- **Hybrid Commands**: Every command works with both `?` prefix and `/` slash commands
- **Cog-Based Structure**: Modular design for easy maintenance and extensibility
- **Type Hints**: Comprehensive type annotations throughout codebase
- **Error Handling**: Graceful error handling with user-friendly messages

### **Database & Persistence**
- **SQLite**: File-based database for tags, starboard, invites, and tickets
- **aiosqlite**: Async SQLite operations for better performance
- **CodeBuddy Database**: Separate database for coding leaderboards
- **Data Integrity**: Proper constraints, indexes, and transaction handling

### **Performance & Reliability**
- **Connection Pooling**: Efficient database connection management
- **Caching**: Smart caching for starboard and invite systems
- **Rate Limiting**: Built-in cooldown management
- **Graceful Degradation**: Continues working even if some features fail
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

### **Security & Safety**
- **Environment Variables**: Secure token and config storage
- **Permission Checks**: Role-based command access control
- **Input Validation**: Sanitization of user inputs
- **SQL Injection Prevention**: Parameterized queries throughout

---

## Installation & Setup

### **Prerequisites**
- Python 3.11 or higher
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))
- Git (for cloning)

### **Quick Start**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/youngcoder45/Eigen-bot-In-Python.git
   cd Eigen-bot-In-Python
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   
   # Linux/macOS
   source .venv/bin/activate
   
   # Windows
   .venv\\Scripts\\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and settings
   ```

5. **Run the Bot**
   ```bash
   python bot.py
   ```

### **Environment Variables**

Create a `.env` file with the following:

```env
# Required
DISCORD_TOKEN=your_bot_token_here

# Bot Configuration
OWNER_ID=your_discord_user_id
LOG_LEVEL=INFO

# Development (optional)
GUILD_ID=your_test_server_id  # For faster slash command sync

# CodeBuddy (optional)
QUESTION_CHANNEL_ID=channel_id_for_coding_questions
```

---

## Usage Guide

### **Command Prefixes**
- **Prefix Commands**: `?command` (e.g., `?help`)
- **Slash Commands**: `/command` (e.g., `/help`)
- **Hybrid**: Most commands support both formats!

### **Ticket Commands**
```
/ticketpanel [#channel] [support_role]  - Create ticket panel
/ticketlog [#channel]                    - Set ticket log channel
/ticketsupport [role]                    - Set support team role
/tickets [status] [user]                 - List tickets
/ticketstats                             - View statistics
/forceclose <ticket_id> [reason]         - Force close ticket
```

### **Starboard Commands**
```
?starboard setup #channel <threshold> <emoji>  - Setup starboard
?starboard stats                               - View statistics
?starboard toggle                              - Enable/disable
```

### **Tag Commands**
```
?tag <name>                      - Retrieve a tag
?tags create <name> <content>    - Create new tag
?tags edit <name> <content>      - Edit existing tag
?tags delete <name>              - Delete a tag
?tags list                       - List all tags
```

### **CodeBuddy Commands**
```
/codeweek           - Weekly coding leaderboard
/codestreak         - View streak leaderboard
/codeleaderboard    - All-time leaderboard
/codestats [@user]  - View coding stats
/codeflex           - Generate stats card image
```

### **Fun Commands**
```
?joke                - Programming joke
?compliment [@user]  - Give compliment
?fortune            - Programming fortune
?trivia             - Programming trivia
?8ball <question>   - Magic 8-ball
?coinflip           - Flip a coin
?roll [size] [count] - Roll dice
```

---

## Economy Bot (Separated)

Economy and casino features have been moved to a separate bot. Check the `another-bot/` folder for:
- Economy system (balance, work, daily, weekly, etc.)
- Casino games (blackjack, roulette, slots, etc.)
- Economy admin commands

See `another-bot/README.md` and `another-bot/MIGRATION_SUMMARY.md` for setup instructions.

---

## Database Files

```
├── botdata.db        # Main database (tickets, codebuddy)
├── tags.db           # Tag system
├── starboard.db      # Starboard system
└── invites.db        # Invite tracker (if enabled)
```

---

## Docker Deployment

### **Using Docker**
```bash
# Build image
docker build -t eigen-bot .

# Run container
docker run -d --env-file .env eigen-bot
```

### **Using Docker Compose**
```bash
docker-compose up -d
```

---

## Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch
3. **Commit** your changes
4. **Push** to the branch
5. **Open** a Pull Request

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Support & Documentation

### **Getting Help**
- **Bug Reports**: [Open an issue](https://github.com/youngcoder45/Eigen-bot-In-Python/issues)
- **Feature Requests**: [Open an issue](https://github.com/youngcoder45/Eigen-bot-In-Python/issues)

---

## Acknowledgments

Built with:
- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Async SQLite
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment management

Special thanks to the discord.py community and all contributors!

---

<div align="center">

**Eigen Bot** - Where Community Meets Support

[GitHub](https://github.com/youngcoder45/Eigen-bot-In-Python) • [Issues](https://github.com/youngcoder45/Eigen-bot-In-Python/issues)

Made with ❤️ for Discord communities

</div>
