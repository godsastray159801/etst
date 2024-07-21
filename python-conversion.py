import asyncio
import aiohttp
import csv
from datetime import datetime

with open('authorization.csv', 'r', encoding='utf-8') as file:
    authorization_list = [line.strip() for line in file if line.strip()]

base_url = 'https://api.hamsterkombat.io'
timeout = aiohttp.ClientTimeout(total=10)

async def click_with_api(session, authorization):
    try:
        payload = {
            "count": 1,
            "availableTaps": 1500,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {authorization}'
        }
        async with session.post(f'{base_url}/clicker/tap', json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                clicker_user = data['clickerUser']
                required_fields = {
                    'Balance': clicker_user['balanceCoins'],
                    'Level': clicker_user['level'],
                    'availableTaps': clicker_user['availableTaps'],
                    'maxTaps': clicker_user['maxTaps']
                }
                print('Đang tap:', required_fields)
                return required_fields
            else:
                print('Không bấm được. Status code:', response.status)
    except Exception as error:
        print('Error:', str(error))
    return None

async def run_for_authorization(session, authorization):
    while True:
        tasks = [click_with_api(session, authorization) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        click_data = results[-1]
        if click_data and click_data['availableTaps'] < 10:
            print(f"Token {authorization} có năng lượng nhỏ hơn 10. Chuyển token tiếp theo...")
            break
        await asyncio.sleep(0.01)

async def main():
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            for authorization in authorization_list:
                await run_for_authorization(session, authorization)
            print('Đã chạy xong tất cả các token, nghỉ 1 giây rồi chạy lại từ đầu...')
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())