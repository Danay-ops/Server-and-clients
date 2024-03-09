import asyncio
import random
import logging
import datetime

count_alive=0
count = 0
async def tcp_client(message,count):
    global count_alive
    logging.basicConfig(level=logging.INFO, filename='client1.log', filemode='w',encoding='utf-8')
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
  #  print(f"{message}")

    await asyncio.sleep(random.randint(300, 3000) / 1000)
    writer.write(message.encode())
    await writer.drain()
    request_time = datetime.datetime.now()
    data = await reader.read(100)

  #  print(f"Получено '{data.decode()}'")

    print(f'[{count_alive}]{data.decode()}' if 'keepalive' in data.decode() else data.decode() )

  #  print('Соединение завершенно')
    writer.close()
    await writer.wait_closed()
    response_time = datetime.datetime.now()  # время отправки ответа
    if 'keepalive' in data.decode():
        logging.info(
            f"keepalive")
        count_alive+=1
    if str('\n') not in data.decode() and 'keepalive' not in data.decode():
        logging.info(
            f"{request_time.strftime('%Y-%m-%d;%H:%M:%S.%f')};{message};{response_time.strftime('%H:%M:%S.%f')};{data}")
    else:
        t = 'таймаут'
        logging.info(
            f"{request_time.strftime('%Y-%m-%d;%H:%M:%S.%f')};{message};{response_time.strftime('%H:%M:%S.%f')};{t}")

async def main():
    global count
    while True:
        message = str(count) + ',' + 'PING' + ','+'1'
        await tcp_client(message, count)
        count += 1

async def stop_after_timeout():
    await asyncio.sleep(299)  # Остановка работы клиента через 10 секунд
    raise asyncio.TimeoutError

async def run_tasks():
    try:
        task1 = asyncio.create_task(main())
        task2 = asyncio.create_task(stop_after_timeout())
        await asyncio.gather(task1, task2, return_exceptions=True)
    except asyncio.TimeoutError:
        print("Программа будет остановлена.")

asyncio.run(run_tasks())
