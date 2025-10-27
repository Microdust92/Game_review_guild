class GameSession:
    def __init__(self):
        self.score = 0
        self.final_score = 0
        self.stage = "intro"
        self.fae_name = ""
        self.fae_skill = ""
        self.output = ""

    def showScore(self):
        return f"[Current Score: {self.score}]"

    def endScore(self):
        self.final_score = self.score
        self.stage = "end"
        return f"\nYour final score: {self.score} points\nGame Over!"

    # --- ENDINGS ---
    def theBadEnd(self):
        self.stage = "end"
        return (
            "\nYour choice has led you to a beast much greater than your skill."
            "\nYou could not win... Goodbye.\n"
            "YOU LOSE!!!"
            + self.endScore()
        )

    def forestMonsterEnd(self):
        self.stage = "end"
        return (
            "\nYou lost focus and the monster got the upper hand, striking a deadly blow."
            "\nYOU LOSE!!!"
            + self.endScore()
        )

    def didNotAdventure(self):
        self.stage = "end"
        return (
            "\nYou chose not to adventure into a new land."
            "\nYour home was crushed by an asteroid. You failed to survive!"
            "\nYOU LOSE!!!"
            + self.endScore()
        )

    def surviveAdventure(self):
        self.stage = "end"
        self.final_score = self.score
        return (
            "\nYou have managed to survive in this new world. Enjoy your new home!"
            "\nYOU WIN!!!"
            + self.endScore()
        )

    # --- COMBAT / ACTIONS ---
    def fightAction(self, faeSkillChoice, ui):
        if faeSkillChoice == "magic":
            moves = ["Fireball", "Lightning", "Waterball", "Wind Strike"]
            try:
                c = int(ui)
                if c in [1, 2, 3, 4]:
                    move = moves[c - 1]
                    self.score += 25
                    self.stage = "victory"
                    return (
                        f"\nYou cast {move} and strike the monster!"
                        f"\n{self.showScore()}"
                    )
                else:
                    return self.forestMonsterEnd()
            except ValueError:
                return self.forestMonsterEnd()

        elif faeSkillChoice == "sword":
            moves = ["Parry forward", "Running slash", "Leaping strike"]
            try:
                c = int(ui)
                if c in [1, 2, 3]:
                    move = moves[c - 1]
                    self.score += 25
                    self.stage = "victory"
                    return (
                        f"\nYou perform {move} and strike the monster!"
                        f"\n{self.showScore()}"
                    )
                else:
                    return self.forestMonsterEnd()
            except ValueError:
                return self.forestMonsterEnd()
        else:
            return self.forestMonsterEnd()

    # --- GAME FLOW ---
    def next(self, user_input=None):
        ui = (user_input or "").strip().casefold()

        # --- Intro ---
        if self.stage == "intro":
            self.stage = "choose_name"
            return (
                "█▓▒░░ Welcome to: Reborn in a New World ░░▒▓█\n"
                "The world fades to black, and suddenly a bright light appears.\n"
                "Your eyes open—you awaken in a new world.\n\n"
                "You have been Reborn! You are now in a world called Faefolk,\n"
                "a world of magic and survival. You have some choices to make before your journey begins.\n\n"
                "Do you want to pick a name? (y/n): "
            )

        # --- Choose name ---
        if self.stage == "choose_name":
            if ui == "n":
                return self.didNotAdventure()
            elif ui == "y":
                self.stage = "ask_name"
                return "What shall your name be?: "
            else:
                return "Please enter 'y' or 'n'."

        # --- Enter name ---
        if self.stage == "ask_name":
            self.fae_name = user_input or "Nameless One"
            self.score += 10
            self.stage = "choose_skill"
            return (
                f"\nWelcome to Faefolk, {self.fae_name}!\n"
                "Now you must choose your life skill.\n"
                "Will you be a wielder of Magic or a master of the Sword?"
            )

        # --- Choose skill ---
        if self.stage == "choose_skill":
            if ui in ("magic", "sword"):
                self.fae_skill = ui
                self.score += 20
                self.stage = "choose_path"
                return (
                    f"\nYou have chosen the {self.fae_skill.capitalize()} class."
                    f"\n{self.showScore()}"
                    "\nNow that you are ready, it is time to set out on your adventure."
                    "\nThere is a fork in the road: East and West.\n"
                    "Which direction will you travel? (east/west/home): "
                )
            else:
                return "Please choose 'magic' or 'sword'."

        # --- Choose path ---
        if self.stage == "choose_path":
            if ui == "east":
                self.score += 50
                self.stage = "fight_decision"
                return (
                    "\nYou travel east into the forest. The trees whisper ancient secrets..."
                    "\nSuddenly, a monster emerges from the shadows!"
                    "\nDo you stay and fight? (y/n): "
                )
            elif ui == "west":
                self.score -= 50
                return self.theBadEnd()
            elif ui == "home":
                self.score -= 100
                return self.didNotAdventure()
            else:
                return "Please choose east, west, or home."

        # --- Fight or flee ---
        if self.stage == "fight_decision":
            if ui == "n":
                self.score -= 50
                return self.theBadEnd()
            elif ui == "y":
                self.stage = "fight_action"
                if self.fae_skill == "magic":
                    return (
                        "\nYou stand your ground and ready your magic.\n"
                        "Choose your spell:\n"
                        "1: Fireball\n2: Lightning\n3: Waterball\n4: Wind Strike\n"
                        "Enter number: "
                    )
                else:
                    return (
                        "\nYou grip your sword tightly and prepare for battle.\n"
                        "Choose your sword technique:\n"
                        "1: Parry forward\n2: Running slash\n3: Leaping strike\n"
                        "Enter number: "
                    )
            else:
                return "Please enter 'y' or 'n'."

        # --- Fight result ---
        if self.stage == "fight_action":
            result = self.fightAction(self.fae_skill, ui)
            if self.stage == "victory":
                self.stage = "continue_after_victory"
                return (
                    result +
                    "\n\nYou have made a direct hit! The monster falls to the ground."
                    "\nYou escape the forest and make it to a nearby village."
                    "\nPress Enter to continue."
                )
            else:
                return result

        # --- Continue after win ---
        if self.stage == "continue_after_victory":
            self.score += 1000
            return self.surviveAdventure()

        # --- End of game ---
        if self.stage == "end":
            return f"Game Over.\nFinal Score: {self.final_score}"

        return "Unexpected input."
