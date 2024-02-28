import httpx
import asyncio
import requests

async def call_asset_ready_api(asset_guid):
    url = "url"
    data = {"asset_guid": asset_guid}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)

    if response.status_code == 200:
        print("API call successful!")
        print(response.json())
    else:
        print(f"API call failed with status code: {response.status_code}")
        print(response.text)

async def param_test():
    url = "url"
    params = {"asset_guid": "your_asset_guid_here"}

    response = requests.post(url, params=params)

    if response.status_code == 200:
        print("API call successful!")
    else:
        print(f"API call failed with status code: {response.status_code}")
        print(response.text)

async def main():
    asset_guid_to_send = "your_asset_guid_here"
    # await call_asset_ready_api(asset_guid_to_send)
    await param_test()

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())