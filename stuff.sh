# this script is to test syntax

curl -X PATCH \
"https://discord.com/api/v9/applications/1520592490942435469/users/449950252397494274/identities/0/profile" \
-H "Content-Type: application/json" \
-H "Authorization: Bot " \
-H "User-Agent: DiscordBot (https://github.com/discord/discord-api-docs, 1.0.0)" \
-d '{"data":{"dynamic":[{"type":3,"name":"profile_picture_url","value":{"url":"https://pyxfluff.dev/images/pfp_2026.png"}},{"type":1,"name":"header_1","value":"Pyx"},{"type":1,"name":"header_2","value":"@pyxfluff"},{"type":1,"name":"scrobbles_all_time","value":"123.45K"},{"type":2,"name":"loved_tracks","value":50},{"type":1,"name":"scrobbles_recently","value":"487"},{"type":1,"name":"tracks","value":"3031"},{"type":1,"name":"albums","value":"932"},{"type":1,"name":"artists","value":"533"},{"type":3,"name":"preview_background","value":{"url":"https://pyxfluff.dev/images/pfp_2026.png"}}]}}'
