from urllib.request import urlopen
import json

SECONDS_IN_24_HOURS = 60*60*24

class Players():
    def __init__(self):
        """init google drive management objects"""
        self.all_players = None
        self.player_names = None
        self.minutes_cached = 0
        self.refresh_players()

    def update_time_stale(self, seconds=0):
        """updates the time that this list/object has been cached for. Once it hits 24 hours we will update
        the players lists
        """

        self.minutes_cached += seconds
        if self.minutes_cached >= SECONDS_IN_24_HOURS:
            self.minutes_cached = 0
            self.refresh_players()

    def _get_player_picture(self, player_id, player_name):
        """Returns a link to the players headshot"""

        return "[" + player_name + " Face](https://nhl.bamcontent.com/images/headshots/current/168x168/" + str(player_id) + ".jpg)  \n"

    def _get_player_actionshot(self, player_id, player_name):
        """gets the current players action shot from NHL.com.

        returns a link to the image"""

        return "[" + player_name + " in action](https://nhl.bamcontent.com/images/actionshots/" + str(player_id) + ".jpg)  \n"

    def _get_player_stats(self, player, season_type="regular"):
        """Gets a players stats for either the regular season, or playoffs"""

        if season_type == "regular":
            season_type = "yearByYear,careerRegularSeason"
        else:
            season_type = "yearByYearPlayoffs,careerPlayoffs"
        """gets the current players and teams list for all players on all teams

        returns a list of dicts containing team details"""

        try:
            data = urlopen("https://statsapi.web.nhl.com/api/v1/people/" + str(player) + "?expand=person.stats&stats=" + season_type)
            data = json.load(data)
            return data['people'][0]
            
        except Exception as e:
            print ("")
            print ("exception occurred in players._get_player_stats")
            print (str(e))
            return None

    def _get_new_players(self):
        """gets the current players and teams list for all players on all teams

        returns a list of dicts containing team details"""
        try:
            data = urlopen("https://statsapi.web.nhl.com/api/v1/teams?expand=team.roster")
            data = json.load(data)
            return data['teams']
            
        except Exception as e:
            print ("")
            print ("exception occurred in players._get_new_players")
            print (str(e))
            return None

    def refresh_players(self):
        """Takes raw data and transforms it into a player list."""

        data = self._get_new_players()

        new_player_list = {}
        new_id_list = {}

        for team in data:
            for player in team['roster']['roster']:

                #add this person to their first, last, and first and last name hash list.
                names = player['person']['fullName'].lower().replace(".", "")
                name_parts = names.split()

                # parts of their name
                for name in name_parts:
                    if name not in new_player_list:
                        new_player_list[name] = [player['person']['id']]
                    else:
                        new_player_list[name].append(player['person']['id'])
                # full name
                if names not in new_player_list:
                    new_player_list[names] = [player['person']['id']]
                else:
                    new_player_list[names].append(player['person']['id'])

                # id to full name look up
                new_id_list[player['person']['id']] = player['person']['fullName']

        self.all_players = new_player_list
        self.player_names = new_id_list

        print ("Players updated!")

    def get_player(self, player_name):
        """Takes player_name and trys to return a list of players that have said name."""
        return self.all_players.get(player_name)

    def get_player_name(self, player_id):
        """attempts to return a players name based on the player_id passed"""

        return self.player_names.get(player_id)

    def get_players_names(self, players):
        """takes a list of players and returns their names in a nice list"""
        names = []
        for player in players:
            names.append(self.get_player_name(player))

        return ", ".join(names)

    def _gen_tablerow(self, key, value):
        """takes a key and value and returns a table row reddit formatted"""
        return str(key) + "|" + str(value) + "\n"

    def _generate_player_bio(self, stats):
        """takes a stats object for a certain player and returns a short player bio"""
        bio = "|Description|Details|\n"
        bio += "|:--:|:--:|\n"
        bio += self._gen_tablerow("Name", stats['fullName'])
        bio += self._gen_tablerow("Current Team", stats['currentTeam']['name'])
        bio += self._gen_tablerow("Position", stats['primaryPosition']['name'])
        bio += self._gen_tablerow("Number", "#" + stats['primaryNumber'])
        bio += self._gen_tablerow("Birthday", stats['birthDate'])
        bio += self._gen_tablerow("Age", stats['currentAge'])
        bio += self._gen_tablerow("Nationality", stats['nationality'])
        bio += self._gen_tablerow("Height", stats['height'])
        bio += self._gen_tablerow("Weight", stats['weight'])
        bio += self._gen_tablerow("Shoots", stats['shootsCatches'])
        bio += "  \n\n"
        return bio

    def _format_player_stats(self, stat, all_stats=None):
        """Takes stats and returns them in the fashion we defined"""

        new_line = ""
        if all_stats:
            new_line += str(stat.get('games', "N/A")) + "|"
            new_line += str(stat.get('goals', "N/A")) + "|"
            new_line += str(stat.get('assists', "N/A")) + "|"
            new_line += str(stat.get('points', "N/A")) + "|"
            new_line += str(stat.get('pim', "N/A")) + "|"
            new_line += str(stat.get('timeOnIce', "N/A")) + "|"
            new_line += str(stat.get('plusMinus', "N/A")) + "|"
            new_line += str(stat.get('shots', "N/A")) + "|"
            new_line += str(stat.get('hits', "N/A")) + "|"
            new_line += str(stat.get('powerPlayGoals', "N/A")) + "|"
            new_line += str(stat.get('powerPlayPoints', "N/A")) + "|"
            new_line += str(stat.get('powerPlayTimeOnIce', "N/A")) + "|"
            new_line += str(stat.get('evenTimeOnIce', "N/A")) + "|"
            new_line += str(stat.get('faceOffPct', "N/A")) + "%|"
            new_line += str(stat.get('shotPct', "N/A")) + "%|"
            new_line += str(stat.get('gameWinningGoals', "N/A")) + "|"
            new_line += str(stat.get('overTimeGoals', "N/A")) + "|"
            new_line += str(stat.get('shortHandedGoals', "N/A")) + "|"
            new_line += str(stat.get('shortHandedPoints', "N/A")) + "|"
            new_line += str(stat.get('shortHandedTimeOnIce', "N/A")) + "|"
            new_line += str(stat.get('blocked', "N/A")) + "|"
            new_line += str(stat.get('shifts', "N/A")) + "|"
            new_line += "\n"
        else:
            new_line += str(stat.get('games', "N/A")) + "|"
            new_line += str(stat.get('goals', "N/A")) + "|"
            new_line += str(stat.get('assists', "N/A")) + "|"
            new_line += str(stat.get('points', "N/A")) + "|"
            new_line += str(stat.get('pim', "N/A"))
            new_line += "\n"

        return new_line

    def _player_has_playoff_games(self, stats):
        """Checks if this player has playoff games played. Returns true is they have played in playoffs"""

        return stats != []

    def _generate_player_yearly_stats(self, player, league="National Hockey League", season_type="regular", season=None, all_stats=False):
        """takes a players stats and returns a history of their results in a certain league.
        defaults to NHL.
        """

        # if they don't have career stats for playoffs, they haven't played NHL playoff games.
        results = ""
        career_stats = None
        yearly_stats = player['stats'][0]['splits']
        if self._player_has_playoff_games(player['stats'][1]['splits']):
            career_stats = player['stats'][1]['splits'][0]['stat']
        else:
            return str(player['fullName']) + " hasn't played in the playoffs yet... Maybe they will soon!  \n"
        
        if all_stats:
            results += "Team|Season|Games|Goals|Assists|Points|PIMS|TOI|+/-|Shots|Hits|PP Goals|PP Points|PP TOI|ES TOI|FO%|S%|GWG|OT Goals|SH Goals|SH Points|SH TOI|Blocked Shots|Shifts\n"
            results +="|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n"
        else:
            results += "Team|Season|Games|Goals|Assists|Points|PIM|\n"
            results +="|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n"

        for year in yearly_stats:
            stat = year['stat']

            if year['league']['name'] != league:
                continue
            # format the year from 19992000 to 1999-2000
            new_line = year['team']['name'] + "|" + year['season'][:4] + "-" + year['season'][4:] + "|"
            new_line += self._format_player_stats(stat, all_stats=all_stats)
            results += new_line

        new_line = "NHL|Career|"
        new_line += self._format_player_stats(career_stats, all_stats=all_stats)
        results += new_line

        return results + "  \n"

    def get_formated_player_stats(self, player, season_type="regular", all_stats=False):
        """gets the stats for a certain player and returns the formated list of all stats."""

        stats = self._get_player_stats(player, season_type=season_type)

        results = self._generate_player_bio(stats)
        results += "&nbsp;  \n\n"
        results += self._generate_player_yearly_stats(stats, all_stats=all_stats)

        return results

    def validate_remaining_words(self, words):
        """Take a word list and trys to figure out if we want regular season or playoffs
        (regualr season by default) as well as if they want their full stats or just their
        basic stats.

        returns values for what we think they are requesting.
        """

        #default to minor stats and regular season
        all_stats = False
        season = "regular"

        for word in words:
            word = word.lower()
            if word in ["playoff", "poffs", "playoffs"]:
                season = "playoffs"

            if word in ["all", "full", "everything", "complete"]:
                all_stats = True

        print ("returning %s and %s " %(season, all_stats))

        return season, all_stats

    def get_players_profile(self, player, words):
        """builds the requested players profile. and returns the reddit formatted data"""

        season_type, all_stats = self.validate_remaining_words(words)

        player_name = self.get_player_name(player)

        player_headshot = self._get_player_picture(player, player_name)
        player_action = self._get_player_actionshot(player, player_name)

        player_stats = self.get_formated_player_stats(player, season_type=season_type, all_stats=all_stats)

        return player_headshot + player_action + player_stats

    def get_response(self, players, remaining_words):

        if len(players) > 1:
            names = self.get_players_names(players)
            result = "Sorry, there are too many players with that name! Which player were you trying to get stats about?  \n"
            result += names + "  \n"
            result += "Please make another request with the full name or a unique last name.  \n"
            return result
        else:
            return self.get_players_profile(players[0], remaining_words)

# testing/sanity code
if __name__ == '__main__':
    players = Players()
    
    print ("Testing ehler by default...")
    # Ehlers
    print (players.get_response([8477940], []))
    print ("Done...")
