import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Poker Game",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SIMPLE CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }

    h1 {
        font-size: 1.6rem !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-size: 1.25rem !important;
        margin-top: 0.8rem !important;
        margin-bottom: 0.5rem !important;
    }

    h3 {
        font-size: 1.05rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.4rem !important;
    }

    div[data-testid="stMetric"] {
        padding: 8px 12px;
        border-radius: 8px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.25rem;
    }

    div.stButton > button {
        min-height: 38px;
        padding: 4px 10px;
    }

    hr {
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS
# ============================================================

MIN_PLAYERS = 2
MAX_PLAYERS = 10
DEFAULT_MONEY = 100


# ============================================================
# PLAYER
# ============================================================

class Player:

    def __init__(self, name, money):

        self.name = name
        self.money = money
        self.bet = 0
        self.is_playing = True

    def raise_bet(self, new_bet, current_bet):

        if new_bet <= current_bet:
            return False

        if new_bet > self.money:
            return False

        self.bet = new_bet

        return True

    def match(self, current_bet):

        if current_bet > self.money:
            return False

        self.bet = current_bet

        return True

    def hold(self):

        self.is_playing = False

    def reset_match(self):

        self.bet = 0
        self.is_playing = self.money > 0


# ============================================================
# INITIALIZE PLAYERS
# ============================================================

def init_players(
    n_players=4,
    init_amt=DEFAULT_MONEY,
):

    names = [
        "Player A",
        "Player B",
        "Player C",
        "Player D",
        "Player E",
        "Player F",
        "Player G",
        "Player H",
        "Player I",
        "Player J",
    ]

    players = []

    for i in range(n_players):

        players.append(
            Player(
                names[i],
                init_amt,
            )
        )

    return players


# ============================================================
# NEW GAME
# ============================================================

def new_game():

    return {

        "players": init_players(),

        "match_number": 1,

        "round_number": 1,

        "initial_bet": 10,

        "current_bet": 10,

        "max_raises": 2,

        "raises_used": 0,

        "turn_index": 0,

        "match_started": False,

        "waiting_for_winner": False,

        "game_over": False,

        "overall_winner": None,

        "match_winner": None,

        "last_action": "Ready.",

        "history": [],
    }


# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if "game" not in st.session_state:

    st.session_state.game = new_game()


game = st.session_state.game

players = game["players"]


# ============================================================
# PLAYER SETUP FUNCTIONS
# ============================================================

def add_player():

    if len(players) >= MAX_PLAYERS:
        return

    next_number = len(players) + 1

    players.append(
        Player(
            f"Player {next_number}",
            DEFAULT_MONEY,
        )
    )


def remove_player(index):

    if len(players) <= MIN_PLAYERS:
        return

    players.pop(index)


# ============================================================
# HELPERS
# ============================================================

def active_players():

    return [
        player
        for player in players
        if player.is_playing
    ]


def affordable_players():

    return [
        player
        for player in players
        if player.money >= game["initial_bet"]
    ]


def get_current_player():

    for index in range(
        game["turn_index"],
        len(players),
    ):

        player = players[index]

        if player.is_playing:

            return player

    return None


def advance_turn():

    game["turn_index"] += 1

    while game["turn_index"] < len(players):

        if players[
            game["turn_index"]
        ].is_playing:

            return

        game["turn_index"] += 1


def reset_round_turn():

    game["turn_index"] = 0

    while game["turn_index"] < len(players):

        if players[
            game["turn_index"]
        ].is_playing:

            return

        game["turn_index"] += 1


# ============================================================
# MATCH CONTROL
# ============================================================

def start_match():

    for player in players:

        player.reset_match()

    game["current_bet"] = game["initial_bet"]

    game["round_number"] = 1

    game["raises_used"] = 0

    game["turn_index"] = 0

    game["match_started"] = True

    game["waiting_for_winner"] = False

    game["match_winner"] = None

    game["last_action"] = (
        f"Match {game['match_number']} started."
    )


def next_round():

    if game["round_number"] >= 4:

        game["match_started"] = False

        game["waiting_for_winner"] = True

        return

    game["round_number"] += 1

    game["raises_used"] = 0

    reset_round_turn()


def perform_action(
    player,
    action,
    new_bet=None,
):

    # ========================================================
    # MATCH
    # ========================================================

    if action == "match":

        if game["current_bet"] > player.money:

            game["last_action"] = (
                f"{player.name} "
                f"cannot afford "
                f"${game['current_bet']}."
            )

            return

        player.match(
            game["current_bet"]
        )

        game["last_action"] = (
            f"{player.name} "
            f"matched "
            f"${game['current_bet']}."
        )

        advance_turn()


    # ========================================================
    # RAISE
    # ========================================================

    elif action == "raise":

        if game["raises_used"] >= game["max_raises"]:

            game["last_action"] = (
                "No raises remaining this round."
            )

            return

        if new_bet is None:

            return

        if new_bet <= game["current_bet"]:

            game["last_action"] = (
                f"Raise must be greater than "
                f"${game['current_bet']}."
            )

            return

        if new_bet > player.money:

            game["last_action"] = (
                f"{player.name} "
                f"only has "
                f"${player.money}."
            )

            return

        success = player.raise_bet(
            new_bet,
            game["current_bet"],
        )

        if not success:

            return

        game["current_bet"] = new_bet

        game["raises_used"] += 1

        game["last_action"] = (
            f"{player.name} "
            f"raised to "
            f"${new_bet}."
        )

        advance_turn()


    # ========================================================
    # HOLD
    # ========================================================

    elif action == "hold":

        player.hold()

        game["last_action"] = (
            f"{player.name} held."
        )

        advance_turn()


    # ========================================================
    # END OF TURN CYCLE
    # ========================================================

    if game["turn_index"] >= len(players):

        next_round()


# ============================================================
# FINISH MATCH
# ============================================================

def finish_match(winner):

    total_received = 0

    for player in players:

        if player is winner:
            continue

        if player.bet > 0:

            player.money -= player.bet

            total_received += player.bet

    winner.money += total_received

    game["match_winner"] = winner.name

    game["history"].append(
        {
            "match": game["match_number"],
            "winner": winner.name,
            "amount": total_received,
        }
    )

    # --------------------------------------------------------
    # RESET MATCH STATE
    # --------------------------------------------------------

    for player in players:

        player.bet = 0

        player.is_playing = player.money > 0

    possible_players = affordable_players()

    # --------------------------------------------------------
    # GAME OVER
    # --------------------------------------------------------

    if (
        game["match_number"] >= 5
        or len(possible_players) < 2
    ):

        game["game_over"] = True

        game["match_started"] = False

        game["waiting_for_winner"] = False

        overall = max(
            players,
            key=lambda p: p.money,
        )

        game["overall_winner"] = overall.name

    # --------------------------------------------------------
    # NEXT MATCH
    # --------------------------------------------------------

    else:

        game["match_number"] += 1

        game["round_number"] = 1

        game["current_bet"] = game["initial_bet"]

        game["raises_used"] = 0

        game["turn_index"] = 0

        game["match_started"] = False

        game["waiting_for_winner"] = False

    game["last_action"] = (
        f"{winner.name} won "
        f"the match and received "
        f"${total_received}."
    )


# ============================================================
# RESTART GAME
# ============================================================

def restart_game():

    st.session_state.game = new_game()

    st.rerun()


# ============================================================
# PAGE HEADER
# ============================================================

header_left, header_right = st.columns(
    [5, 1]
)

with header_left:

    st.title("Betting Game")

with header_right:

    if st.button(
        "New Game",
        use_container_width=True,
    ):

        restart_game()


# ============================================================
# PLAYER SETUP / PLAYER INFORMATION
# ============================================================

st.subheader("Players")


# ============================================================
# PRE-GAME PLAYER SETUP
# ============================================================

if (
    not game["match_started"]
    and not game["game_over"]
    and not game["waiting_for_winner"]
):

    st.caption(
        "Add players and edit their names "
        "and starting money before the match starts."
    )

    # --------------------------------------------------------
    # ADD PLAYER
    # --------------------------------------------------------

    add_col, info_col = st.columns(
        [1, 4]
    )

    with add_col:

        if st.button(
            "➕ Add Player",
            use_container_width=True,
            disabled=len(players) >= MAX_PLAYERS,
        ):

            add_player()

            st.rerun()

    with info_col:

        st.caption(
            f"{len(players)} players • "
            f"Minimum {MIN_PLAYERS} • "
            f"Maximum {MAX_PLAYERS}"
        )

    st.divider()

    # --------------------------------------------------------
    # PLAYER SETUP ROWS
    #
    # 4 players per row
    # 10 players = 4 + 4 + 2
    # --------------------------------------------------------

    for start in range(
        0,
        len(players),
        4,
    ):

        row_players = players[
            start:start + 4
        ]

        columns = st.columns(4)

        for column_index, player in enumerate(
            row_players
        ):

            with columns[column_index]:

                with st.container(border=True):

                    st.markdown(
                        f"### Player {start + column_index + 1}"
                    )

                    new_name = st.text_input(
                        "Name",
                        value=player.name,
                        key=(
                            f"player_name_"
                            f"{start + column_index}"
                        ),
                    )

                    player.name = (
                        new_name.strip()
                        or (
                            f"Player "
                            f"{start + column_index + 1}"
                        )
                    )

                    new_money = st.number_input(
                        "Starting Money",
                        min_value=1,
                        value=int(player.money),
                        step=10,
                        key=(
                            f"player_money_"
                            f"{start + column_index}"
                        ),
                    )

                    player.money = new_money

                    if st.button(
                        "🗑️ Remove",
                        key=(
                            f"remove_player_"
                            f"{start + column_index}"
                        ),
                        disabled=len(players) <= MIN_PLAYERS,
                        use_container_width=True,
                    ):

                        remove_player(
                            start + column_index
                        )

                        st.rerun()


# ============================================================
# PLAYER INFORMATION AFTER MATCH STARTS
# ============================================================

else:

    current = (
        get_current_player()
        if game["match_started"]
        else None
    )

    # --------------------------------------------------------
    # PLAYER CARDS
    #
    # 4 players per row
    # 10 players = 4 + 4 + 2
    # --------------------------------------------------------

    for start in range(
        0,
        len(players),
        4,
    ):

        row_players = players[
            start:start + 4
        ]

        columns = st.columns(4)

        for column_index, player in enumerate(
            row_players
        ):

            with columns[column_index]:

                with st.container(border=True):

                    st.markdown(
                        f"### {player.name}"
                    )

                    money_col, bet_col = st.columns(2)

                    with money_col:

                        st.metric(
                            "Money",
                            f"${player.money}",
                        )

                    with bet_col:

                        st.metric(
                            "Bet",
                            f"${player.bet}",
                        )

                    if (
                        game["match_started"]
                        and current is player
                    ):

                        st.success(
                            "Your turn",
                            icon="🎯",
                        )

                    elif player.is_playing:

                        st.caption("Playing")

                    else:

                        st.caption("Held")


# ============================================================
# GAME STATUS
# ============================================================

st.divider()

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:

    st.metric(
        "Match",
        f"{game['match_number']} / 5",
    )

with status_col2:

    if game["match_started"]:

        st.metric(
            "Round",
            f"{game['round_number']} / 4",
        )

    else:

        st.metric(
            "Round",
            "-",
        )

with status_col3:

    st.metric(
        "Current Bet",
        f"${game['current_bet']}",
    )


# ============================================================
# START MATCH
# ============================================================

if (
    not game["match_started"]
    and not game["waiting_for_winner"]
    and not game["game_over"]
):

    possible = affordable_players()

    # --------------------------------------------------------
    # CHECK MINIMUM PLAYERS WITH ENOUGH MONEY
    # --------------------------------------------------------

    if len(possible) < MIN_PLAYERS:

        st.error(
            f"At least {MIN_PLAYERS} players need "
            f"${game['initial_bet']} to continue."
        )

    else:

        # ----------------------------------------------------
        # CHECK DUPLICATE NAMES
        # ----------------------------------------------------

        names = [
            player.name.strip().lower()
            for player in players
        ]

        if len(names) != len(set(names)):

            st.error(
                "Each player must have a unique name."
            )

        # ----------------------------------------------------
        # START BUTTON
        # ----------------------------------------------------

        else:

            if st.button(
                f"Start Match {game['match_number']}",
                type="primary",
                use_container_width=True,
            ):

                start_match()

                st.rerun()


# ============================================================
# CURRENT TURN
# ============================================================

if game["match_started"]:

    player = get_current_player()

    if player is None:

        game["match_started"] = False

        game["waiting_for_winner"] = True

        st.rerun()

    st.subheader(
        f"{player.name}'s Turn"
    )

    # --------------------------------------------------------
    # CURRENT BET INFORMATION
    # --------------------------------------------------------

    st.info(
        f"Current bet: ${game['current_bet']}   "
        f"|   Your bet: ${player.bet}   "
        f"|   Raises left: "
        f"{game['max_raises'] - game['raises_used']}"
    )

    # --------------------------------------------------------
    # ACTION COLUMNS
    # --------------------------------------------------------

    match_col, raise_col, hold_col = st.columns(3)


    # ========================================================
    # MATCH
    # ========================================================

    with match_col:

        st.markdown("**Match**")

        if player.money < game["current_bet"]:

            st.error(
                f"Cannot afford ${game['current_bet']}"
            )

        else:

            if st.button(
                f"Match ${game['current_bet']}",
                key=(
                    f"match_"
                    f"{game['match_number']}_"
                    f"{game['round_number']}_"
                    f"{game['turn_index']}"
                ),
                use_container_width=True,
            ):

                perform_action(
                    player,
                    "match",
                )

                st.rerun()


    # ========================================================
    # RAISE
    # ========================================================

    with raise_col:

        st.markdown("**Raise**")

        if (
            game["raises_used"]
            < game["max_raises"]
        ):

            minimum = (
                game["current_bet"] + 1
            )

            if player.money <= game["current_bet"]:

                st.caption(
                    "You cannot raise because "
                    "you do not have enough money."
                )

            else:

                default_amount = min(
                    game["current_bet"] + 10,
                    player.money,
                )

                amount = st.number_input(
                    "New total bet",
                    min_value=minimum,
                    max_value=player.money,
                    value=default_amount,
                    step=1,
                    key=(
                        f"raise_input_"
                        f"{game['match_number']}_"
                        f"{game['round_number']}_"
                        f"{game['turn_index']}"
                    ),
                )

                if st.button(
                    f"Raise to ${amount}",
                    key=(
                        f"raise_"
                        f"{game['match_number']}_"
                        f"{game['round_number']}_"
                        f"{game['turn_index']}"
                    ),
                    use_container_width=True,
                ):

                    perform_action(
                        player,
                        "raise",
                        amount,
                    )

                    st.rerun()

        else:

            st.caption(
                "No raises remaining this round."
            )


    # ========================================================
    # HOLD
    # ========================================================

    with hold_col:

        st.markdown("**Hold**")

        st.caption(
            "Leave the match. "
            "Your existing bet is preserved."
        )

        if st.button(
            "Hold",
            key=(
                f"hold_"
                f"{game['match_number']}_"
                f"{game['round_number']}_"
                f"{game['turn_index']}"
            ),
            use_container_width=True,
        ):

            perform_action(
                player,
                "hold",
            )

            st.rerun()


# ============================================================
# LAST ACTION
# ============================================================

if game["last_action"]:

    st.caption(
        game["last_action"]
    )


# ============================================================
# WINNER SELECTION
# ============================================================

if game["waiting_for_winner"]:

    st.divider()

    st.subheader("Select Winner")

    active = active_players()

    if not active:

        st.error(
            "No players are still playing."
        )

    else:

        # ----------------------------------------------------
        # WINNER CARDS
        # 4 per row
        # ----------------------------------------------------

        for start in range(
            0,
            len(active),
            4,
        ):

            row_players = active[
                start:start + 4
            ]

            columns = st.columns(4)

            for column_index, player in enumerate(
                row_players
            ):

                with columns[column_index]:

                    with st.container(border=True):

                        st.markdown(
                            f"### {player.name}"
                        )

                        st.metric(
                            "Money",
                            f"${player.money}",
                        )

                        st.metric(
                            "Bet",
                            f"${player.bet}",
                        )

                        if st.button(
                            f"Select {player.name}",
                            key=(
                                f"winner_"
                                f"{game['match_number']}_"
                                f"{player.name}"
                            ),
                            type="primary",
                            use_container_width=True,
                        ):

                            finish_match(player)

                            st.rerun()


# ============================================================
# GAME OVER
# ============================================================

if game["game_over"]:

    st.divider()

    st.subheader("Game Over")

    winner = next(
        (
            p
            for p in players
            if p.name == game["overall_winner"]
        ),
        None,
    )

    if winner:

        st.success(
            f"Overall winner: "
            f"{winner.name} — "
            f"${winner.money}"
        )

    # --------------------------------------------------------
    # FINAL STANDINGS
    # --------------------------------------------------------

    st.markdown("### Final Standings")

    ranking = sorted(
        players,
        key=lambda p: p.money,
        reverse=True,
    )

    for position, player in enumerate(
        ranking,
        start=1,
    ):

        col1, col2, col3 = st.columns(
            [1, 4, 2]
        )

        with col1:

            st.write(position)

        with col2:

            st.write(
                player.name
            )

        with col3:

            st.write(
                f"**${player.money}**"
            )


# ============================================================
# MATCH HISTORY
# ============================================================

if game["history"]:

    st.divider()

    st.subheader("Match History")

    for item in reversed(game["history"]):

        st.write(
            f"Match {item['match']} — "
            f"{item['winner']} won — "
            f"Received ${item['amount']}"
        )
