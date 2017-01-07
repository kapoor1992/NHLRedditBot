API Findings

http://statsapi.web.nhl.com/api/v1/game/2015020741/feed/live
 - Resolves live game stats
 - form /game/<year><month><day><gameID?>/feed/live

Cooler things you can access:
 <game date data>/boxscore
  - recap of end game player/team stats VERY cool

 <game date data>/linescore
  - linescore 

 <game date data>/
 - 

 <game date data>/
 - 

 /teams/
 - returns all teams
 - pass number after teams/ for specific team

/divisions/
 - returns a;; divisions
 - pass number after divisions/ for specific division

/conferences/
 - returns all conferences
 - pass number after conferences/ for specific confrences

/franchises/
 - returns all franchises

/people/<number>
 - returns player details (no stats)
 - eg. /people/8469639

schedule?startDate=2016-10-01&endDate=2016-10-07&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,schedule.ticket,schedule.game.content.media.epg,schedule.decisions,schedule.scoringplays,schedule.game.content.highlights.scoreboard,team.leaders&site=en_nhlCA&teamId=52&season=20162017
 - returns a bunch of schedule <data>
     - https://statsapi.web.nhl.com/api/v1/schedule?site=en_nhlCA&expand=schedule.teams,schedule.linescore&startDate=2016-10-01&endDate=2016-10-31&teamId=52
     - trimmed form
 </data>

 https://statsapi.web.nhl.com/api/v1/teams/52?expand=team.roster,roster.person,person.stats,person.names&stats=yearByYear&season=20152016
  - returns stats for players on NHL jets

https://statsapi.web.nhl.com/api/v1/teams?site=en_nhlCA&season=20162017
 - returns teams active in <year><year>

http://www.nhl.com/stats/rest/grouped/skaters/basic/season/skatersummary?cayenneExp=seasonId=20162017%20and%20gameTypeId=2&factCayenneExp=gamesPlayed%3E=1&sort=[{%22property%22:%22goals%22,%22direction%22:%22ASC%22}]
 - returns data used on nhl.com all time point leader board


https://statsapi.web.nhl.com/api/v1/standings
 - standings

https://statsapi.web.nhl.com/api/v1/teams/TEAM_ID_GOES_HERE/roster
 - roster information
 
  Proper useage

  call https://statsapi.web.nhl.com/api/v1/teams

  find Winnipeg id, use that ID in all other calulations.

  (or we cache the ID's since the teams aren't going to change anytime soon... Vegas is already accounted for)
