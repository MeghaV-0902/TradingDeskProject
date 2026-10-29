# agent.py -- the starting point. Rename this file to agent.py and build from here.
#
# This is a legal, complete agent. It does nothing (it holds every day), which is exactly
# what you want on day one: run it and the checks name what is missing, your group code
# (a FAIL) and your names (a warning). Fill both in and everything goes green, with one
# warning left: an agent that never has 10% of its money in shares is not placed.
# Everything else is built around this method.
#
#   python3 agent_unittest.py    protocol check, no data needed (on Windows: python)
#   python3 selfcheck.py         the same plus a real run on your group's market
#
# First, put your group code in the line below. It arrived by email at the group lock (a tutor can re-send it),
# and it looks like G07-4KQT. It is the line the checks read to know whose file this is,
# so they refuse to do much until it is there. It also decides which of the four training
# markets your report's self-check figures come from, which is why you never type a ticker
# anywhere; you build and test your agent on all four. Then replace the two lines under
# it: every member of your group, and the member who is this file's reference, the one who
# makes any live change to it at the interview.
#
# Keep agent.py, agent_unittest.py and selfcheck.py in the same folder.

GROUP_CODE = "G15-MRPW"       # <- replace this with your group's code
# Group: Vasu Megha, Ambre Rugved Suresh Puri Harshita, Shaikh Mohammed Arsalan, Kakade Subodh Sunil
# Reference: Vasu Megha


class TradingAgent:
    def decide(self, bar, headlines, cash, shares, last_response):
        """Called once per trading day. Return one order: (action, amount).

        bar           today's prices, a dict with open/high/low/close/volume,
                      or None in the news-only run
        headlines     today's news, a list of strings (possibly empty),
                      or None in the OHLCV-only run
        cash          your cash right now, a float
        shares        the shares you hold right now, a float
        last_response the desk's reply to your PREVIOUS order: None on the first
                      call, then "ACCEPT" or a "REJECT ..." string

        action is "BUY", "SELL" or "HOLD"; amount is a number of shares, and -1
        means buy as much as you can afford or sell everything you hold.

        You only ever see TODAY. If you want history, store it yourself: append to
        a list here and it will still be there tomorrow.
        """
        return ("HOLD", 0)
