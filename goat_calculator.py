#!/usr/bin/env python3
"""
GOAT Calculator
===============
Pick a sport. Get a ranked, math-backed top 10 of the greatest players of
all time, with a transparent score breakdown for every name on the list.

THE EQUATION
------------
Every player is scored 0-100 on six components, each of which is itself a
0-100 rating anchored to the best-ever performer in that sport for that
category. The final GOAT Score is a weighted sum:

    GOAT Score = 0.25 * Peak Dominance
               + 0.20 * Statistical Production
               + 0.20 * Championships & Team Success
               + 0.15 * Individual Hardware (major awards)
               + 0.10 * Longevity (years played at an elite level)
               + 0.10 * Historical Impact (influence on how the sport is
                                            played, watched, or grown)

Component definitions:
  peak_dominance        How dominant the player was at their absolute best,
                         relative to their peers at the time.
  stat_production       Career statistical output, adjusted for era and role
                         (counting stats + advanced/efficiency numbers).
  championships         Team titles won, weighted by the player's actual
                         role/impact in winning them (star vs. passenger).
  individual_hardware   Season MVPs, Ballon d'Or, Cy Youngs, majors, etc. -
                         the sport's marquee individual honors.
  longevity             Number of seasons played at a genuinely elite level.
  historical_impact     How much the player changed their sport - tactics,
                         style, global growth, cultural reach.

The component ratings below are pre-scored using real career facts
(titles, awards, records) as anchors; the code does no scraping and calls
no external service, so results are instant, offline, and reproducible.
Edit PLAYER_DATA to tune a rating or add a player, or WEIGHTS to change
what the equation values.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# The equation
# ---------------------------------------------------------------------------

WEIGHTS: dict[str, float] = {
    "peak_dominance": 0.25,
    "stat_production": 0.20,
    "championships": 0.20,
    "individual_hardware": 0.15,
    "longevity": 0.10,
    "historical_impact": 0.10,
}

COMPONENT_LABELS: dict[str, str] = {
    "peak_dominance": "Peak Dominance",
    "stat_production": "Statistical Production",
    "championships": "Championships & Team Success",
    "individual_hardware": "Individual Hardware",
    "longevity": "Longevity",
    "historical_impact": "Historical Impact",
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "WEIGHTS must sum to 1.0"


@dataclass
class Player:
    name: str
    peak_dominance: int
    stat_production: int
    championships: int
    individual_hardware: int
    longevity: int
    historical_impact: int
    note: str = ""

    def scores(self) -> dict[str, int]:
        return {
            "peak_dominance": self.peak_dominance,
            "stat_production": self.stat_production,
            "championships": self.championships,
            "individual_hardware": self.individual_hardware,
            "longevity": self.longevity,
            "historical_impact": self.historical_impact,
        }

    def goat_score(self) -> float:
        return sum(WEIGHTS[k] * v for k, v in self.scores().items())


@dataclass
class Sport:
    display_name: str
    players: list[Player] = field(default_factory=list)


# ---------------------------------------------------------------------------
# The dataset
# ---------------------------------------------------------------------------
# Ratings are 0-100 per component, anchored to real career achievements.

SPORTS: dict[str, Sport] = {
    "basketball": Sport("Basketball (NBA)", [
        Player("Michael Jordan", 99, 90, 95, 98, 80, 100,
               "6-0 in NBA Finals, 6 Finals MVPs, 5 MVPs, 10 scoring titles, "
               "never lost a Finals series."),
        Player("LeBron James", 96, 98, 85, 92, 99, 95,
               "All-time leading scorer, 4 titles with 3 different "
               "franchises, 4 MVPs, still elite 21+ seasons in."),
        Player("Kareem Abdul-Jabbar", 90, 93, 88, 90, 95, 85,
               "6 MVPs (record), 6 titles, NBA's career scoring leader for "
               "nearly 40 years, 20 elite seasons."),
        Player("Bill Russell", 92, 65, 100, 80, 78, 90,
               "11 championships in 13 seasons - the greatest winning "
               "record of any team-sport athlete ever."),
        Player("Magic Johnson", 93, 80, 90, 82, 65, 88,
               "5 titles, 3 MVPs, redefined the point guard position; "
               "prime cut short by HIV diagnosis."),
        Player("Larry Bird", 92, 82, 85, 82, 68, 85,
               "3 titles, 3 straight MVPs, one of the greatest shooters "
               "and clutch performers ever; back injuries shortened career."),
        Player("Wilt Chamberlain", 97, 99, 70, 78, 85, 80,
               "100-point game, averaged 50.4 ppg for a season - "
               "statistical records still considered unbreakable."),
        Player("Tim Duncan", 88, 85, 92, 78, 92, 75,
               "5 titles, 3 Finals MVPs, 2 MVPs, remarkably consistent "
               "excellence across 19 seasons."),
        Player("Shaquille O'Neal", 94, 88, 82, 75, 78, 82,
               "4 titles including a 3-peat with 3 straight Finals MVPs; "
               "most physically dominant force in league history."),
        Player("Kobe Bryant", 90, 87, 85, 72, 85, 90,
               "5 titles, 2 Finals MVPs, 81-point game, obsessive work "
               "ethic became its own cultural phenomenon."),
        Player("Stephen Curry", 89, 78, 78, 75, 80, 96,
               "Only unanimous MVP ever, 4 titles, single-handedly changed "
               "how the game is played by revolutionizing 3-point shooting."),
        Player("Hakeem Olajuwon", 87, 80, 75, 65, 82, 70,
               "Back-to-back titles and Finals MVPs in 1994-95, widely "
               "regarded as the most skilled big man ever."),
    ]),

    "soccer": Sport("Soccer / Football (World)", [
        Player("Lionel Messi", 97, 98, 90, 99, 92, 96,
               "Record 8 Ballon d'Or wins, 2022 World Cup title, all-time "
               "goal/assist production at the highest level for 20 years."),
        Player("Cristiano Ronaldo", 96, 97, 82, 96, 95, 95,
               "5 Champions League titles, 5 Ballon d'Ors, all-time "
               "leading scorer in men's international football."),
        Player("Pele", 95, 90, 98, 85, 80, 98,
               "Only player to win 3 World Cups (1958, 1962, 1970); "
               "global ambassador who globalized the sport."),
        Player("Diego Maradona", 98, 78, 85, 80, 60, 92,
               "Carried Argentina to the 1986 World Cup almost single-"
               "handedly - considered the greatest individual tournament "
               "performance ever."),
        Player("Johan Cruyff", 93, 75, 75, 80, 70, 95,
               "Pioneer of Total Football; 3 Ballon d'Ors; philosophy "
               "still shapes how the modern game is coached and played."),
        Player("Franz Beckenbauer", 88, 65, 90, 78, 75, 85,
               "Reinvented the sweeper/libero role; won the World Cup as "
               "both captain (1974) and head coach (1990)."),
        Player("Zinedine Zidane", 92, 72, 88, 82, 68, 88,
               "1998 World Cup and Euro 2000 winner with France; among "
               "the most technically gifted midfielders ever."),
        Player("Ronaldo Nazario", 96, 85, 82, 85, 55, 85,
               "Two World Cup titles (1994, 2002) and 3 FIFA World Player "
               "of the Year awards despite injuries cutting his prime short."),
        Player("Alfredo Di Stefano", 90, 82, 92, 78, 78, 80,
               "Led Real Madrid to 5 consecutive European Cups (1956-60), "
               "a feat no player has matched since."),
        Player("Michel Platini", 87, 78, 78, 85, 65, 75,
               "3 consecutive Ballon d'Ors (1983-85); dominant Euro 1984 "
               "with 9 goals in 5 games."),
        Player("Ronaldinho", 90, 75, 78, 78, 55, 88,
               "2002 World Cup and 2006 Champions League winner; his flair "
               "changed how a generation of players approached the game."),
        Player("Eusebio", 85, 80, 60, 75, 65, 70,
               "1965 Ballon d'Or; led Portugal to 3rd place at the 1966 "
               "World Cup as tournament top scorer."),
    ]),

    "american_football": Sport("American Football (NFL)", [
        Player("Tom Brady", 92, 90, 99, 90, 97, 92,
               "7 Super Bowl titles (most ever), 5 Super Bowl MVPs, 3 NFL "
               "MVPs, elite production across 23 seasons."),
        Player("Jerry Rice", 95, 99, 85, 80, 93, 88,
               "All-time leading receiver by a massive margin; records "
               "that may never be broken."),
        Player("Jim Brown", 98, 90, 70, 82, 55, 85,
               "Retired at his statistical peak after 9 seasons; still "
               "widely cited as the most dominant runner ever relative "
               "to his era."),
        Player("Lawrence Taylor", 97, 80, 75, 85, 70, 90,
               "Redefined the outside linebacker position and how "
               "defenses attack the quarterback; 1986 NFL MVP."),
        Player("Joe Montana", 93, 78, 92, 85, 75, 82,
               "4-0 in Super Bowls with 3 Super Bowl MVPs; defined "
               "clutch quarterback play for a generation."),
        Player("Peyton Manning", 88, 92, 78, 92, 85, 80,
               "Record 5 NFL MVPs, multiple career passing records, "
               "2 Super Bowl titles with 2 different franchises."),
        Player("Walter Payton", 90, 88, 68, 75, 85, 78,
               "Elite two-way back for 13 seasons, ironman durability, "
               "one of the most complete players in league history."),
        Player("Reggie White", 92, 85, 70, 72, 78, 75,
               "Career sack totals among the very best ever; feared as "
               "both a pass rusher and run defender."),
        Player("Barry Sanders", 96, 85, 40, 78, 65, 82,
               "Retired at the peak of his powers; widely regarded as "
               "the most elusive runner in NFL history."),
        Player("Deion Sanders", 90, 75, 75, 65, 70, 80,
               "Shut down entire sides of the field as a corner while "
               "also being an elite kick/punt returner; 2 Super Bowls."),
        Player("Aaron Donald", 93, 80, 68, 78, 60, 70,
               "3-time Defensive Player of the Year, arguably the most "
               "dominant interior defensive lineman ever."),
        Player("Randy Moss", 92, 85, 55, 65, 75, 80,
               "Redefined the deep-threat receiver; single-season "
               "touchdown record (23) still stands."),
    ]),

    "baseball": Sport("Baseball (MLB)", [
        Player("Babe Ruth", 99, 96, 90, 85, 85, 100,
               "Redefined the sport around power hitting; 7 World Series "
               "titles; still the sport's most iconic figure."),
        Player("Willie Mays", 95, 93, 60, 82, 90, 90,
               "Five-tool excellence for two decades; 2-time MVP, 12 Gold "
               "Gloves, 'The Catch' in the 1954 World Series."),
        Player("Barry Bonds", 98, 97, 30, 95, 92, 75,
               "Record 7 MVPs and single-season/career home run records, "
               "though tempered by steroid-era controversy."),
        Player("Hank Aaron", 88, 94, 65, 78, 95, 85,
               "Held the career home run record for 33 years; also holds "
               "the all-time RBI record."),
        Player("Ted Williams", 97, 92, 20, 75, 70, 82,
               "Last player to hit .400 in a season (1941); missed ~5 "
               "prime seasons serving in the military."),
        Player("Ty Cobb", 92, 90, 40, 70, 88, 78,
               "Career .366 batting average, the highest in MLB history, "
               "over a 24-season career."),
        Player("Walter Johnson", 90, 88, 55, 72, 85, 75,
               "417 career wins (2nd all-time) and a career that set the "
               "template for dominant pitching."),
        Player("Lou Gehrig", 90, 85, 88, 75, 55, 80,
               "6 World Series titles and a .340 career average before "
               "ALS ended his career and life prematurely."),
        Player("Mickey Mantle", 92, 85, 92, 80, 65, 82,
               "7 World Series titles, 3 MVPs, a Triple Crown season "
               "(1956); injuries limited a historic peak."),
        Player("Stan Musial", 85, 87, 70, 78, 90, 70,
               "3 MVPs and remarkable consistency across 22 seasons, "
               "almost entirely with one franchise."),
        Player("Honus Wagner", 84, 82, 55, 65, 82, 65,
               "8 batting titles in the dead-ball era; regarded as the "
               "best shortstop of the pre-modern game."),
        Player("Rickey Henderson", 86, 88, 60, 70, 92, 78,
               "All-time stolen base and runs scored leader by wide "
               "margins; played at a high level into his 40s."),
    ]),

    "hockey": Sport("Ice Hockey (NHL)", [
        Player("Wayne Gretzky", 100, 100, 90, 98, 90, 100,
               "Holds 60+ NHL records; his career assist total alone "
               "exceeds the career point total of every other player."),
        Player("Gordie Howe", 88, 90, 78, 80, 97, 85,
               "Played at an elite level into his 50s; 6 Hart Trophies "
               "and 4 Stanley Cups."),
        Player("Bobby Orr", 96, 80, 62, 82, 45, 90,
               "Reinvented the defenseman position as a scoring threat; "
               "career cut short at 30 by knee injuries."),
        Player("Mario Lemieux", 97, 90, 70, 82, 50, 85,
               "Arguably Gretzky's only rival at peak dominance; overcame "
               "cancer to keep playing at an elite level."),
        Player("Maurice Richard", 85, 75, 88, 60, 75, 82,
               "First player to score 50 goals in 50 games; 8 Stanley "
               "Cup titles with the Canadiens."),
        Player("Bobby Hull", 85, 82, 55, 68, 82, 78,
               "Popularized the slap shot and drew fans to the game with "
               "his speed and scoring power."),
        Player("Mark Messier", 82, 78, 92, 65, 88, 78,
               "Only player to captain two different franchises to "
               "Stanley Cup titles; 6 Cups overall."),
        Player("Patrick Roy", 88, 70, 90, 68, 85, 82,
               "4 Stanley Cups and 3 Conn Smythe Trophies; revolutionized "
               "the butterfly goaltending style."),
        Player("Sidney Crosby", 88, 82, 88, 75, 82, 80,
               "3 Stanley Cups, 2 Conn Smythe Trophies, 2 MVPs; face of "
               "the league for nearly two decades."),
        Player("Alexander Ovechkin", 90, 92, 55, 78, 88, 82,
               "Broke the all-time goal-scoring record; 3-time MVP and "
               "generational goal scorer."),
        Player("Jean Beliveau", 78, 72, 96, 60, 80, 70,
               "10 Stanley Cup titles as a player - the most of anyone "
               "on this list."),
        Player("Nicklas Lidstrom", 78, 65, 78, 70, 85, 65,
               "7 Norris Trophies as the league's best defenseman and "
               "4 Stanley Cups without ever missing the playoffs."),
    ]),

    "tennis_men": Sport("Tennis - Men's", [
        Player("Novak Djokovic", 96, 99, 98, 96, 95, 92,
               "Most men's Grand Slam titles ever (24), record weeks at "
               "world No. 1, winning record against every rival."),
        Player("Roger Federer", 93, 90, 90, 92, 90, 98,
               "20 Grand Slam titles, 237 consecutive weeks at No. 1, "
               "credited with growing tennis's global popularity."),
        Player("Rafael Nadal", 97, 91, 92, 90, 82, 90,
               "22 Grand Slam titles including a record 14 French Opens; "
               "unmatched peak intensity on clay."),
        Player("Rod Laver", 95, 75, 85, 70, 70, 80,
               "Only man with two calendar-year Grand Slams (1962, 1969), "
               "spanning both the amateur and Open eras."),
        Player("Pete Sampras", 88, 78, 80, 78, 72, 78,
               "Held the men's Grand Slam record (14) for years; 6 "
               "year-end world No. 1 finishes."),
        Player("Bjorn Borg", 92, 65, 78, 68, 45, 80,
               "Extraordinary win rate and 11 Grand Slam titles before "
               "retiring at just 26."),
        Player("Andre Agassi", 82, 68, 68, 65, 75, 78,
               "Career Grand Slam winner (all 4 majors) known for "
               "popularizing a more athletic, baseline style."),
        Player("John McEnroe", 85, 60, 65, 65, 55, 75,
               "7 Grand Slam singles titles and dominant doubles career; "
               "one of the most compelling personalities in the sport."),
        Player("Ivan Lendl", 82, 68, 65, 65, 78, 65,
               "8 Grand Slam titles and a record 270 weeks at world No. 1 "
               "across his career."),
        Player("Jimmy Connors", 80, 65, 60, 62, 85, 70,
               "Most ATP tour-level titles ever (109) and 8 Grand Slam "
               "singles titles across three different decades."),
    ]),

    "tennis_women": Sport("Tennis - Women's", [
        Player("Serena Williams", 97, 92, 92, 90, 92, 98,
               "23 Grand Slam singles titles in the Open Era (most ever); "
               "redefined power and athleticism in the women's game."),
        Player("Steffi Graf", 96, 88, 90, 85, 78, 85,
               "Only player (man or woman) to complete a Golden Slam "
               "(all 4 majors + Olympic gold in one year, 1988)."),
        Player("Margaret Court", 85, 90, 82, 70, 80, 65,
               "Holds the all-time record of 24 Grand Slam singles "
               "titles, though many came in the amateur era."),
        Player("Martina Navratilova", 92, 85, 82, 80, 92, 88,
               "18 singles majors plus a record haul of doubles majors; "
               "remained a top competitor into her 40s."),
        Player("Chris Evert", 87, 80, 78, 72, 82, 78,
               "18 Grand Slam titles and one of the best match-win "
               "percentages in the sport's history."),
        Player("Billie Jean King", 80, 65, 65, 65, 70, 95,
               "12 Grand Slam singles titles, but her larger legacy is "
               "the 'Battle of the Sexes' and fight for equality in sport."),
        Player("Monica Seles", 93, 60, 65, 65, 40, 75,
               "Dominant, era-defining prime cut short by an on-court "
               "stabbing attack in 1993."),
        Player("Suzanne Lenglen", 88, 60, 60, 55, 50, 80,
               "Pre-Open-era pioneer who drew unprecedented crowds and "
               "legitimized women's tennis as a spectator sport."),
        Player("Venus Williams", 82, 70, 68, 68, 85, 82,
               "7 Grand Slam singles titles and a driving force behind "
               "equal prize money for women at majors."),
        Player("Martina Hingis", 78, 62, 60, 60, 65, 68,
               "Youngest world No. 1 in history; 5 Grand Slam singles "
               "titles built on elite court IQ."),
    ]),

    "boxing": Sport("Boxing", [
        Player("Muhammad Ali", 95, 80, 92, 85, 80, 100,
               "3-time heavyweight champion; global cultural icon whose "
               "impact transcended the sport entirely."),
        Player("Sugar Ray Robinson", 96, 88, 85, 80, 85, 88,
               "173-19-6 record; the pound-for-pound standard by which "
               "all other fighters are still measured."),
        Player("Floyd Mayweather Jr.", 90, 95, 88, 85, 88, 80,
               "Retired 50-0; multi-division world champion known for "
               "defensive mastery and ring IQ."),
        Player("Mike Tyson", 97, 70, 75, 72, 50, 90,
               "Youngest heavyweight champion ever; one of the most "
               "feared punchers in boxing history at his peak."),
        Player("Joe Louis", 90, 82, 88, 75, 78, 82,
               "Held the heavyweight title for a record 25 title "
               "defenses over nearly 12 years."),
        Player("Rocky Marciano", 85, 90, 78, 68, 55, 70,
               "Only heavyweight champion to retire completely "
               "undefeated, at 49-0."),
        Player("Roberto Duran", 88, 82, 75, 70, 85, 75,
               "104 career wins and world titles across four different "
               "weight divisions."),
        Player("Manny Pacquiao", 90, 85, 82, 78, 85, 85,
               "Only boxer to win world titles in eight different weight "
               "divisions."),
        Player("Julio Cesar Chavez", 85, 88, 78, 68, 82, 72,
               "Started his career 89-0-1; 107 career wins and a Mexican "
               "boxing icon."),
        Player("Henry Armstrong", 88, 78, 82, 65, 70, 75,
               "The only boxer to simultaneously hold world titles in "
               "three different weight classes at once."),
    ]),

    "golf": Sport("Golf", [
        Player("Tiger Woods", 99, 92, 90, 95, 85, 100,
               "15 major titles, 82 PGA Tour wins (tied for most ever); "
               "the 'Tiger Slam' remains unmatched dominance."),
        Player("Jack Nicklaus", 93, 88, 98, 85, 92, 90,
               "Record 18 major championships plus a record 19 runner-up "
               "finishes across a 25-year prime."),
        Player("Ben Hogan", 92, 78, 78, 75, 60, 78,
               "Won the Triple Crown of golf in 1953 after nearly dying "
               "in a car accident two years earlier."),
        Player("Sam Snead", 80, 90, 65, 70, 90, 72,
               "82 PGA Tour wins (tied for most ever) across a "
               "remarkably long competitive career."),
        Player("Arnold Palmer", 82, 78, 68, 72, 78, 92,
               "7 major titles, but his charisma and 'Arnie's Army' "
               "fanbase built modern golf's TV-era popularity."),
        Player("Bobby Jones", 88, 60, 82, 65, 40, 80,
               "Completed the original Grand Slam in 1930 as an amateur, "
               "then retired at 28 at the peak of his powers."),
        Player("Gary Player", 78, 70, 72, 68, 88, 78,
               "Completed the career Grand Slam; built one of the most "
               "traveled and enduring international careers in golf."),
        Player("Tom Watson", 80, 72, 68, 68, 80, 68,
               "8 major titles and a near-miss at the 2009 Open "
               "Championship at age 59."),
        Player("Walter Hagen", 82, 68, 78, 62, 75, 75,
               "11 major championships (2nd all-time) and a key figure "
               "in legitimizing professional golfers socially."),
        Player("Byron Nelson", 90, 65, 62, 65, 45, 65,
               "Won 11 consecutive PGA Tour events in 1945 - a record "
               "considered untouchable."),
    ]),
}

SPORT_ALIASES: dict[str, str] = {
    "football": "american_football",
    "nfl": "american_football",
    "nba": "basketball",
    "soccer": "soccer",
    "futbol": "soccer",
    "mlb": "baseball",
    "nhl": "hockey",
    "tennis": "tennis_men",
    "mens_tennis": "tennis_men",
    "womens_tennis": "tennis_women",
    "boxing": "boxing",
    "golf": "golf",
}


def resolve_sport_key(user_input: str) -> str | None:
    key = user_input.strip().lower().replace(" ", "_").replace("-", "_")
    if key in SPORTS:
        return key
    if key in SPORT_ALIASES:
        return SPORT_ALIASES[key]
    for k, sport in SPORTS.items():
        if key in sport.display_name.lower():
            return k
    return None


# ---------------------------------------------------------------------------
# Ranking + rendering
# ---------------------------------------------------------------------------

def rank_players(sport_key: str) -> list[Player]:
    players = SPORTS[sport_key].players
    return sorted(players, key=lambda p: p.goat_score(), reverse=True)[:10]


def render_report(sport_key: str) -> str:
    sport = SPORTS[sport_key]
    ranked = rank_players(sport_key)
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append(f"GOAT CALCULATOR - Top 10: {sport.display_name}")
    lines.append(f"Generated: {_dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append("=" * 78)
    lines.append("")
    lines.append("EQUATION")
    lines.append("-" * 78)
    lines.append("GOAT Score = " + "\n           + ".join(
        f"{WEIGHTS[k]:.2f} x {COMPONENT_LABELS[k]}" for k in WEIGHTS
    ))
    lines.append("(each component scored 0-100; final score out of 100)")
    lines.append("")

    for rank, player in enumerate(ranked, start=1):
        total = player.goat_score()
        lines.append("-" * 78)
        lines.append(f"#{rank}  {player.name}  -  GOAT Score: {total:.2f} / 100")
        lines.append("-" * 78)
        for key in WEIGHTS:
            raw = player.scores()[key]
            weighted = raw * WEIGHTS[key]
            label = COMPONENT_LABELS[key]
            bar = "#" * (raw // 5)
            lines.append(f"  {label:<32} {raw:>3}/100  x{WEIGHTS[key]:.2f} "
                          f"= {weighted:5.2f}  {bar}")
        lines.append(f"  Why: {player.note}")
        lines.append("")

    lines.append("=" * 78)
    lines.append("Methodology note: component ratings are anchored to real career")
    lines.append("achievements (titles, awards, records) but the 0-100 values and the")
    lines.append("weights above are an original, editable formula, not an official")
    lines.append("statistic. Adjust WEIGHTS or PLAYER_DATA in this script to reflect")
    lines.append("your own view of what makes a player 'greatest ever'.")
    lines.append("=" * 78)
    return "\n".join(lines)


def save_report(sport_key: str, outfile: str | None = None) -> str:
    report = render_report(sport_key)
    path = outfile or f"{sport_key}_top10_goat.txt"
    with open(path, "w") as f:
        f.write(report + "\n")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def list_sports() -> str:
    lines = ["Available sports:"]
    for key, sport in SPORTS.items():
        lines.append(f"  {key:<20} {sport.display_name}")
    return "\n".join(lines)


def interactive_loop() -> None:
    print("GOAT CALCULATOR")
    print("Find the top 10 greatest players of all time for any sport.\n")
    print(list_sports())
    print()
    while True:
        choice = input("Enter a sport (or 'list' / 'quit'): ").strip()
        if choice.lower() in ("quit", "exit", "q"):
            break
        if choice.lower() == "list":
            print(list_sports())
            continue
        sport_key = resolve_sport_key(choice)
        if sport_key is None:
            print(f"Sport '{choice}' not recognized. Try 'list' to see options.\n")
            continue
        report = render_report(sport_key)
        print("\n" + report + "\n")
        path = save_report(sport_key)
        print(f"Saved full report to: {path}\n")
        again = input("Look up another sport? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            break


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rank the top 10 greatest players of all time for a sport "
                    "using a transparent, weighted scoring equation."
    )
    parser.add_argument("sport", nargs="?", help="Sport to rank (e.g. basketball, soccer, nfl)")
    parser.add_argument("--list", action="store_true", help="List available sports and exit")
    parser.add_argument("--outfile", help="Path to write the report file to")
    args = parser.parse_args(argv)

    if args.list:
        print(list_sports())
        return 0

    if not args.sport:
        interactive_loop()
        return 0

    sport_key = resolve_sport_key(args.sport)
    if sport_key is None:
        print(f"Sport '{args.sport}' not recognized.\n")
        print(list_sports())
        return 1

    print(render_report(sport_key))
    path = save_report(sport_key, args.outfile)
    print(f"\nSaved full report to: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
