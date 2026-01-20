import discord
from discord.ext import commands
import chess
import chess.svg

class ChessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # key: channel_id, value: game dict
        self.active_games = {}

    # -----------------------------
    # Start a game
    # -----------------------------
    @commands.command(name="chess")
    async def start_chess(self, ctx, opponent: discord.Member = None):
        """
        Start a chess game with another user or with Booper.
        """
        channel_id = ctx.channel.id

        if channel_id in self.active_games:
            return await ctx.send("A game is already active in this channel.")

        if opponent is None:
            opponent = self.bot.user  # play vs Booper

        if opponent.bot and opponent != self.bot.user:
            return await ctx.send("You can only play against Booper, not other bots.")

        board = chess.Board()

        self.active_games[channel_id] = {
            "board": board,
            "white": ctx.author.id,
            "black": opponent.id,
            "turn": "white"
        }

        await ctx.send(
            f"♟️ **Chess game started!**\n"
            f"White: {ctx.author.mention}\n"
            f"Black: {opponent.mention}\n"
            f"Use `!move e2e4` to play."
        )
        await ctx.send(f"```\n{board}\n```")

    # -----------------------------
    # Make a move
    # -----------------------------
    @commands.command(name="move")
    async def make_move(self, ctx, move: str):
        """
        Make a move in algebraic notation (e.g., e2e4).
        """
        channel_id = ctx.channel.id

        if channel_id not in self.active_games:
            return await ctx.send("No active chess game in this channel.")

        game = self.active_games[channel_id]
        board = game["board"]

        # Check turn
        is_white_turn = board.turn == chess.WHITE
        player_id = ctx.author.id

        if is_white_turn and player_id != game["white"]:
            return await ctx.send("It is **White's** turn.")
        if not is_white_turn and player_id != game["black"]:
            return await ctx.send("It is **Black's** turn.")

        # Validate move
        try:
            chess_move = board.parse_san(move)
        except:
            try:
                chess_move = board.parse_uci(move)
            except:
                return await ctx.send("Invalid move format. Try SAN (`Nf3`) or UCI (`g1f3`).")

        if chess_move not in board.legal_moves:
            return await ctx.send("Illegal move.")

        board.push(chess_move)

        await ctx.send(f"Move played: **{move}**")
        await ctx.send(f"```\n{board}\n```")

        # Check game end
        if board.is_checkmate():
            winner = "White" if board.turn == chess.BLACK else "Black"
            await ctx.send(f"🏆 **Checkmate! {winner} wins!**")
            del self.active_games[channel_id]
            return

        if board.is_stalemate():
            await ctx.send("🤝 **Stalemate! It's a draw.**")
            del self.active_games[channel_id]
            return

        if board.is_insufficient_material():
            await ctx.send("🤝 **Draw by insufficient material.**")
            del self.active_games[channel_id]
            return

        # If playing vs Booper
        if game["black"] == self.bot.user.id and board.turn == chess.BLACK:
            await self.bot_move(ctx, board, channel_id)

    # -----------------------------
    # Booper's automatic move
    # -----------------------------
    async def bot_move(self, ctx, board, channel_id):
        import random

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return

        move = random.choice(legal_moves)
        board.push(move)

        await ctx.send(f"🤖 Booper plays: **{move.uci()}**")
        await ctx.send(f"```\n{board}\n```")

        if board.is_checkmate():
            await ctx.send("🏆 **Checkmate! Booper wins!**")
            del self.active_games[channel_id]
        elif board.is_stalemate():
            await ctx.send("🤝 **Stalemate!**")
            del self.active_games[channel_id]

    # -----------------------------
    # End a game manually
    # -----------------------------
    @commands.command(name="endchess")
    async def end_chess(self, ctx):
        channel_id = ctx.channel.id

        if channel_id not in self.active_games:
            return await ctx.send("No active chess game to end.")

        del self.active_games[channel_id]
        await ctx.send("🛑 Chess game ended.")

async def setup(bot):
    await bot.add_cog(ChessCog(bot))
