import asyncio
import time


# 일반 함수
def 일반함수():
    return "결과"


result = 일반함수()
print(result)


# 비동기 함수
async def 비동기함수():  # 비동기 함수는 async 키워드가 있다
    return "결과2"


# 비동기 함수(async 키워드가 있는 함수)는 직접 호출해도 실행이 되지 않는다.
# 반드시 await를 붙이거나 asyncio.run()로 감싸야 실행된다
# result2 = 비동기함수() # 실행은 되지 않고, coroutine object만 생성되고 반환됨
result2 = asyncio.run(비동기함수())
print(result2)


# # 동기 버전 --------------------------------------------------------------
# def sync_task(name, delay):
#     time.sleep(delay)  # 기다리는 동안 아무 작업 못함 (CPU에서 작업을 대기 큐로 뺌)
#     print(f"{name} 완료")


# start = time.time()
# sync_task("작업A", 3)
# sync_task("작업B", 2)
# sync_task("작업C", 4)
# sync_task("작업D", 1)
# print(f"총 소요 :{time.time() - start:.1f} 초")


# 비동기 버전 ------------------------------------------------------------
async def async_task(name, delay):
    await asyncio.sleep(delay=delay)  # 기다리는 동안 다른 일 가능
    print(f"{name} 완료")


async def main():
    start = time.time()
    await asyncio.gather(
        async_task("작업A", 4),
        async_task("작업B", 2),
        async_task("작업C", 1),
        async_task("작업D", 3),
    )
    print(f"총 소요 :{time.time() - start:.1f} 초")


asyncio.run(main())
