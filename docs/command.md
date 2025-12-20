```sh
*/10 * * * * cursor-agent -p " "

cursor-agent --api-key your_api_key_here "实现用户认证" --endpoint http://localhost:8000/api/v1/chat/completions

```