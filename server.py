import asyncio
import copy
import random
import logging
import datetime

req_count = -1
req_count2 = -1
writers = []
async def handle_client(reader, writer ): #reader` и `writer` представляют собой объекты для чтения и записи данных на сетевом соединении
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO, filename='server.log', filemode='w', encoding='utf-8')

    global writers
    global req_count
    global req_count2
    global key

    addr = writer.get_extra_info('peername') #получаем информацию о адресе и порте удаленного клиента, подключенного к серверу, через writer
    writers.append(writer)
    data = await reader.read(100)  # получение до 100 байт данных от клиента через `reader`
    message = data.decode().split(',')  # декодирую

    request_time = datetime.datetime.now()
    if random.random() < 0.1:
        response_message = "\n"
        print(f"Ignored the request from {addr}")
        logging.info('{};{}'.format(request_time.strftime('%Y-%m-%d;%H:%M:%S.%f'),'проигнорировано'))
    else:
        if message and message[2] == '1':
            req_count += 1
            delay = random.uniform(0.1, 1)
            await asyncio.sleep(delay)
            response_message = f"[{req_count}]/{message[0]} PONG ({message[2]})"
        else:
            req_count2 += 1
            delay = random.uniform(0.1, 1)
            await asyncio.sleep(delay)
            response_message = f"[{req_count2}]/{message[0]} PONG ({message[2]})"

        if message != '\n':  # Проверка, что сообщение не является пустой строкой
            print(f'[{message[0]}] PING')

            response_time = datetime.datetime.now()
            logging.info(
                f"{request_time.strftime('%Y-%m-%d;%H:%M:%S.%f')};{message};{response_time.strftime('%H:%M:%S.%f')};{response_message}")

    writer.write(response_message.encode())

    await writer.drain()

    writer.close()


async def keepalive(writers):
    alive_count=0
    while True:
        await asyncio.sleep(5)
        for writer in writers:
                try:
                    writer.write('keepalive'.encode())
                 #   await writer.drain()
                except ConnectionError:
                    if writer in writers:
                        writers.remove(writer)
        alive_count += 1
async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Listening on {addr}')

    async with server:
        tasks = [asyncio.create_task(keepalive(writers))]
        await asyncio.sleep(300)
        for task in tasks:
            task.cancel() #отмена выполнения задач
        await asyncio.gather(*tasks, return_exceptions=True) # ожидания заврешения всех задач


asyncio.run(main())
