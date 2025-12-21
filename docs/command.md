```sh
*/10 * * * * cursor-agent -p " "

cursor-agent -p "Sun Dec 21 12:39:07 CST 2025" --print -f --output-format text

*/10 * * * * /Users/a/.local/bin/cursor-agent -p "$(date)" --print -f --output-format text >> /tmp/cursor-agent.log 2>&1


```